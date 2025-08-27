import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import csv
import json
from pathlib import Path


class TodoWidget:
    def import_csv(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        def try_parse_date(s):
            if not s:
                return None
            s = s.strip()
            for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt)
                except Exception:
                    continue
            # fallback: try ISO parse
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None

        imported = 0
        try:
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                sample = csvfile.read(4096)
                csvfile.seek(0)
                # Detect delimiter (assume CSV has a header)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ','

                # Always treat the file as having a header row
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                for row in reader:
                    # normalize keys and values
                    norm = { (k or '').strip().lower(): (v or '').strip() for k, v in row.items() }
                    # Map expected headers: Course, Date, Name, Description
                    task_text = norm.get('name') or norm.get('task') or norm.get('title') or ''
                    description = norm.get('description') or norm.get('notes') or ''
                    due_date_str = norm.get('date') or norm.get('due date') or norm.get('due_date') or norm.get('due') or ''
                    course = norm.get('course') or norm.get('class') or ''
                    # If headers are present but the task column wasn't recognized, try first non-empty value
                    if not task_text:
                        task_text = next((v for v in norm.values() if v), '')
                    due_date = try_parse_date(due_date_str)
                    if task_text:
                        self.tasks.append({
                            "text": task_text,
                            "description": description,
                            "due_date": due_date.isoformat() if due_date else None,
                            "course": course,
                            "completed": False,
                        })
                        imported += 1

            if imported > 0:
                self.save_data()
                self.refresh_display()
                messagebox.showinfo("Import Complete", f"Imported {imported} tasks from CSV.")
            else:
                messagebox.showinfo("Import", "No tasks found in the selected CSV.")

        except Exception as e:
            messagebox.showerror("Import Failed", f"Could not import CSV: {e}")

    def __init__(self, root):
        self.root = root
        self.root.title("Agent MoiRai")
        self.root.geometry("420x620")
        self.root.resizable(False, True)
        # Keep window on top
        self.root.attributes('-topmost', True)
        # Data file path
        self.data_file = Path.home() / "todo_widget_data.json"
        # Initialize data
        self.tasks = []
        # Colors
        self.bg_color = "#f0f0f0"
        self.overdue_color = "#ffcccc"
        self.today_color = "#fff3cd"
        self.tomorrow_color = "#f0f8ff"
        # Create UI
        self.create_widgets()
        # Load saved data
        self.load_data()
        # Refresh display
        self.refresh_display()
        # Check for overdue tasks on startup
        self.check_overdue_tasks()

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Task list label
        tk.Label(main_frame, text="Tasks", font=("Arial", 12, "bold"), bg=self.bg_color).pack(anchor="w", pady=(0, 5))

        # Scrollable frame for tasks
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.task_list_frame = tk.Frame(canvas, bg=self.bg_color)
        self.task_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.task_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Import CSV and Add Task buttons at the bottom
        button_color = "#d1e7dd"
        import_btn = tk.Button(self.root, text="Import CSV", font=("Arial", 10), command=self.import_csv, bg=button_color)
        # give a small bottom padding so the buttons sit ~1/4" above the window bottom
        import_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 6))
        clear_btn = tk.Button(self.root, text="Clear Done", font=("Arial", 10), command=self.clear_done_tasks, bg=button_color)
        clear_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 6))
        add_btn = tk.Button(self.root, text="Add Task", font=("Arial", 11, "bold"), command=self.add_task_dialog, bg=button_color)
        # increase bottom padding to raise both buttons slightly
        add_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(10, 16))

    def add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("350x320")
        dialog.transient(self.root)
        dialog.grab_set()
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        # Task name
        tk.Label(dialog, text="Task:", font=("Arial", 10)).pack(pady=5)
        task_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        task_entry.pack(pady=5)
        task_entry.focus()
        # Task description
        tk.Label(dialog, text="Description:", font=("Arial", 10)).pack(pady=5)
        desc_text = tk.Text(dialog, width=40, height=4, font=("Arial", 10))
        desc_text.pack(pady=5)
        # Due date
        tk.Label(dialog, text="Due Date (MM/DD/YYYY):", font=("Arial", 10)).pack(pady=5)
        date_entry = tk.Entry(dialog, width=15, font=("Arial", 10))
        date_entry.pack()
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=15)

        def save_task():
            task_text = task_entry.get().strip()
            date_text = date_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            if not task_text:
                messagebox.showwarning("Empty Task", "Please enter a task name.")
                return
            try:
                due_date = datetime.strptime(date_text, "%m/%d/%Y") if date_text else None
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date as MM/DD/YYYY")
                return
            self.tasks.append({
                "text": task_text,
                "description": description,
                "due_date": due_date.isoformat() if due_date else None,
                "completed": False,
            })
            self.save_data()
            self.refresh_display()
            dialog.destroy()

        tk.Button(button_frame, text="Add", command=save_task, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10).pack(side=tk.LEFT)
        # Allow Enter key to save
        task_entry.bind('<Return>', lambda e: save_task())

    def create_task_widget(self, parent, task, index):
        # Alternate row background colors
        alt_bg1 = "#f0f0f0"
        alt_bg2 = "#e6e6e6"
        bg_color = alt_bg1 if index % 2 == 0 else alt_bg2

        # Override for overdue/today/tomorrow
        if task.get("due_date"):
            due_date = datetime.fromisoformat(task["due_date"])
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if due_date < today:
                bg_color = self.overdue_color
            elif due_date.date() == today.date():
                bg_color = self.today_color
            elif due_date.date() == (today + timedelta(days=1)).date():
                bg_color = self.tomorrow_color

        # Task frame
        task_frame = tk.Frame(parent, bg=bg_color, relief=tk.FLAT, bd=1)
        task_frame.pack(fill=tk.X, pady=2)

        # Checkbox
        check_var = tk.BooleanVar(value=task.get("completed", False))
        check = tk.Checkbutton(task_frame, variable=check_var, bg=bg_color,
                               command=lambda: self.toggle_task(index))
        check.pack(side=tk.LEFT, padx=5)

        # Task text + description container (vertical)
        # Meta (date + course) will sit between checkbox and text
        meta_frame = tk.Frame(task_frame, bg=bg_color)
        meta_frame.pack(side=tk.LEFT, padx=5)

        text_container = tk.Frame(task_frame, bg=bg_color)
        text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        text_font = ("Arial", 10)
        if task.get("completed"):
            text_font = ("Arial", 10, "overstrike")
        task_label = tk.Label(text_container, text=task["text"], font=text_font,
                             bg=bg_color, anchor="w", justify="left", wraplength=260)
        task_label.pack(anchor="w", fill=tk.X)

        # Small description under the task name
        desc_text_val = (task.get("description") or "").strip()
        if desc_text_val:
            desc_label = tk.Label(text_container, text=desc_text_val, font=("Arial", 9),
                                  bg=bg_color, fg="#666", anchor="w", justify="left", wraplength=260)
            desc_label.pack(anchor="w", fill=tk.X, pady=(2, 0))

        # Date and Course displayed to the left of the name (date above course)
        # Show date in DD/MM/YY and make meta text slightly larger and bold
        if task.get("due_date"):
            try:
                due_date_obj = datetime.fromisoformat(task["due_date"])
                date_display = due_date_obj.strftime("%d/%m/%y")
            except Exception:
                date_display = task["due_date"]
            # Make date larger, bold and darker for visibility
            date_label = tk.Label(meta_frame, text=date_display, font=("Arial", 18, "bold"),
                                  bg=bg_color, fg="#000")
            date_label.pack(anchor="w", pady=2)
        else:
            tk.Label(meta_frame, text="", font=("Arial", 18, "bold"), bg=bg_color).pack()

        course_val = (task.get("course") or "").strip()
        if course_val:
            # Slightly larger and darker course label
            course_label = tk.Label(meta_frame, text=course_val, font=("Arial", 18, "bold"),
                                    bg=bg_color, fg="#111")
            course_label.pack(anchor="w", pady=(0,2))
        else:
            tk.Label(meta_frame, text="", font=("Arial", 18, "bold"), bg=bg_color).pack()

    # Description button removed per request

        # Delete button
        delete_btn = tk.Button(task_frame, text="\u00d7", font=("Arial", 12, "bold"),
                               command=lambda: self.delete_task(index),
                               fg="red", bd=0, bg=bg_color, cursor="hand2")
        delete_btn.pack(side=tk.RIGHT, padx=5)

    def show_description(self, task):
        desc = task.get("description", "No description provided.")
        desc_win = tk.Toplevel(self.root)
        desc_win.title("Task Description")
        desc_win.geometry("350x200")
        desc_win.transient(self.root)
        desc_win.grab_set()
        tk.Label(desc_win, text="Description:", font=("Arial", 11, "bold")).pack(pady=8)
        desc_text = tk.Text(desc_win, width=40, height=6, font=("Arial", 10))
        desc_text.pack(padx=10, pady=5)
        desc_text.insert(tk.END, desc)
        desc_text.config(state=tk.DISABLED)
        tk.Button(desc_win, text="Close", command=desc_win.destroy).pack(pady=10)

    def format_date(self, date):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        if date.date() == today.date():
            return "Today"
        elif date.date() == tomorrow.date():
            return "Tomorrow"
        elif date.date() == day_after.date():
            return "Day After"
        elif date < today:
            days_overdue = (today - date).days
            return f"{days_overdue}d overdue"
        else:
            return date.strftime("%m/%d/%y")

    def toggle_task(self, index):
        self.tasks[index]["completed"] = not self.tasks[index]["completed"]
        self.save_data()
        self.refresh_display()

    def delete_task(self, index):
        del self.tasks[index]
        self.save_data()
        self.refresh_display()

    def refresh_display(self):
        # Clear existing widgets
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        # Sort tasks by due date (earliest first). Tasks without a date go last.
        def _sort_key(item):
            d = item.get("due_date")
            if not d:
                return (1, datetime.max)
            try:
                return (0, datetime.fromisoformat(d))
            except Exception:
                return (1, datetime.max)

        self.tasks.sort(key=_sort_key)
        # Display all tasks
        for i, task in enumerate(self.tasks):
            self.create_task_widget(self.task_list_frame, task, i)

    def check_overdue_tasks(self):
        overdue_count = 0
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        for task in self.tasks:
            if task.get("due_date") and not task.get("completed"):
                due_date = datetime.fromisoformat(task["due_date"])
                if due_date < today:
                    overdue_count += 1
        if overdue_count > 0:
            self.root.title(f"Agent MoiRai ({overdue_count} overdue)")
        else:
            self.root.title("Agent MoiRai")

    def save_data(self):
        data = {"tasks": self.tasks}
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
            except Exception:
                self.tasks = []
        else:
            self.tasks = []

    def clear_done_tasks(self):
        done_count = sum(1 for t in self.tasks if t.get('completed'))
        if done_count == 0:
            messagebox.showinfo("Clear Done", "No completed tasks to clear.")
            return
        if not messagebox.askyesno("Clear Done", f"Remove {done_count} completed task(s)?"):
            return
        self.tasks = [t for t in self.tasks if not t.get('completed')]
        self.save_data()
        self.refresh_display()
        messagebox.showinfo("Clear Done", f"Removed {done_count} completed task(s).")


# Launch the widget if run directly
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoWidget(root)
    root.mainloop()
        