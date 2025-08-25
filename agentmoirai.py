import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

class TodoWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do Widget")
        self.root.geometry("400x600")
        self.root.resizable(False, True)
        
        # Keep window on top
        self.root.attributes('-topmost', True)
        
        # Data file path
        self.data_file = Path.home() / "todo_widget_data.json"
        
        # Initialize data
        self.daily_tasks = []
        self.dated_tasks = []
        
        # Colors
        self.bg_color = "#f0f0f0"
        self.daily_bg = "#e8f4f8"
        self.overdue_color = "#ffcccc"
        self.today_color = "#fff3cd"
        self.tomorrow_color = "#f0f8ff"
        
        self.root.configure(bg=self.bg_color)
        
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
        
        # === DAILY TASKS SECTION ===
        daily_frame = tk.Frame(main_frame, bg=self.daily_bg, relief=tk.RIDGE, bd=1)
        daily_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Daily tasks header
        daily_header = tk.Frame(daily_frame, bg=self.daily_bg)
        daily_header.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(daily_header, text="📅 Daily Tasks", font=("Arial", 11, "bold"), 
                bg=self.daily_bg).pack(side=tk.LEFT)
        
        tk.Button(daily_header, text="+", font=("Arial", 10, "bold"),
                 command=lambda: self.add_task_dialog(is_daily=True),
                 width=2, height=1).pack(side=tk.RIGHT)
        
        # Daily tasks list
        self.daily_list_frame = tk.Frame(daily_frame, bg=self.daily_bg)
        self.daily_list_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # === DATED TASKS SECTION ===
        dated_frame = tk.Frame(main_frame, bg=self.bg_color)
        dated_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dated tasks header
        dated_header = tk.Frame(dated_frame, bg=self.bg_color)
        dated_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(dated_header, text="📋 Upcoming Tasks", font=("Arial", 11, "bold"),
                bg=self.bg_color).pack(side=tk.LEFT)
        
        tk.Button(dated_header, text="+", font=("Arial", 10, "bold"),
                 command=lambda: self.add_task_dialog(is_daily=False),
                 width=2, height=1).pack(side=tk.RIGHT)
        
        # Scrollable frame for dated tasks
        canvas = tk.Canvas(dated_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dated_frame, orient="vertical", command=canvas.yview)
        self.dated_list_frame = tk.Frame(canvas, bg=self.bg_color)
        
        self.dated_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.dated_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def add_task_dialog(self, is_daily=False):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Task description
        tk.Label(dialog, text="Task:", font=("Arial", 10)).pack(pady=5)
        task_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        task_entry.pack(pady=5)
        task_entry.focus()
        
        # Due date (only for dated tasks)
        date_frame = None
        date_var = tk.StringVar(value="today")
        
        if not is_daily:
            tk.Label(dialog, text="Due Date:", font=("Arial", 10)).pack(pady=5)
            date_frame = tk.Frame(dialog)
            date_frame.pack(pady=5)
            
            # Quick date options
            tk.Radiobutton(date_frame, text="Today", variable=date_var, 
                          value="today").pack(side=tk.LEFT, padx=5)
            tk.Radiobutton(date_frame, text="Tomorrow", variable=date_var, 
                          value="tomorrow").pack(side=tk.LEFT, padx=5)
            tk.Radiobutton(date_frame, text="Next Week", variable=date_var, 
                          value="next_week").pack(side=tk.LEFT, padx=5)
            
            # Custom date entry
            tk.Label(dialog, text="Or enter date (MM/DD/YYYY):", font=("Arial", 9)).pack()
            custom_date_entry = tk.Entry(dialog, width=15, font=("Arial", 10))
            custom_date_entry.pack()
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def save_task():
            task_text = task_entry.get().strip()
            if not task_text:
                messagebox.showwarning("Empty Task", "Please enter a task description.")
                return
            
            if is_daily:
                self.daily_tasks.append({
                    "text": task_text,
                    "completed": False
                })
            else:
                # Parse due date
                due_date = None
                if not is_daily and 'custom_date_entry' in locals():
                    custom_date = custom_date_entry.get().strip()
                    if custom_date:
                        try:
                            due_date = datetime.strptime(custom_date, "%m/%d/%Y")
                        except ValueError:
                            messagebox.showerror("Invalid Date", "Please enter date as MM/DD/YYYY")
                            return
                    else:
                        # Use radio button selection
                        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        if date_var.get() == "today":
                            due_date = today
                        elif date_var.get() == "tomorrow":
                            due_date = today + timedelta(days=1)
                        elif date_var.get() == "next_week":
                            due_date = today + timedelta(days=7)
                
                self.dated_tasks.append({
                    "text": task_text,
                    "due_date": due_date.isoformat() if due_date else None,
                    "completed": False
                })
            
            self.save_data()
            self.refresh_display()
            dialog.destroy()
        
        tk.Button(button_frame, text="Add", command=save_task, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10).pack(side=tk.LEFT)
        
        # Allow Enter key to save
        task_entry.bind('<Return>', lambda e: save_task())
    
    def create_task_widget(self, parent, task, index, is_daily=False):
        # Determine background color
        bg_color = self.daily_bg if is_daily else self.bg_color
        
        if not is_daily and task.get("due_date"):
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
                               command=lambda: self.toggle_task(index, is_daily))
        check.pack(side=tk.LEFT, padx=5)
        
        # Task text
        text_font = ("Arial", 10)
        if task.get("completed"):
            text_font = ("Arial", 10, "overstrike")
        
        task_label = tk.Label(task_frame, text=task["text"], font=text_font,
                             bg=bg_color, anchor="w", wraplength=250)
        task_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Due date label (for dated tasks)
        if not is_daily and task.get("due_date"):
            due_date = datetime.fromisoformat(task["due_date"])
            date_text = self.format_date(due_date)
            date_label = tk.Label(task_frame, text=date_text, font=("Arial", 9),
                                 bg=bg_color, fg="#666")
            date_label.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = tk.Button(task_frame, text="×", font=("Arial", 12, "bold"),
                              command=lambda: self.delete_task(index, is_daily),
                              fg="red", bd=0, bg=bg_color, cursor="hand2")
        delete_btn.pack(side=tk.RIGHT, padx=5)
    
    def format_date(self, date):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        if date.date() == today.date():
            return "Today"
        elif date.date() == tomorrow.date():
            return "Tomorrow"
        elif date < today:
            days_overdue = (today - date).days
            return f"{days_overdue}d overdue"
        else:
            return date.strftime("%b %d")
    
    def toggle_task(self, index, is_daily):
        if is_daily:
            self.daily_tasks[index]["completed"] = not self.daily_tasks[index]["completed"]
        else:
            self.dated_tasks[index]["completed"] = not self.dated_tasks[index]["completed"]
        
        self.save_data()
        self.refresh_display()
    
    def delete_task(self, index, is_daily):
        if is_daily:
            del self.daily_tasks[index]
        else:
            del self.dated_tasks[index]
        
        self.save_data()
        self.refresh_display()
    
    def refresh_display(self):
        # Clear existing widgets
        for widget in self.daily_list_frame.winfo_children():
            widget.destroy()
        for widget in self.dated_list_frame.winfo_children():
            widget.destroy()
        
        # Display daily tasks
        for i, task in enumerate(self.daily_tasks):
            self.create_task_widget(self.daily_list_frame, task, i, is_daily=True)
        
        # Sort dated tasks by due date
        self.dated_tasks.sort(key=lambda x: x.get("due_date") or "9999")
        
        # Display up to 10 upcoming dated tasks
        for i, task in enumerate(self.dated_tasks[:10]):
            self.create_task_widget(self.dated_list_frame, task, i, is_daily=False)
    
    def check_overdue_tasks(self):
        overdue_count = 0
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for task in self.dated_tasks:
            if task.get("due_date") and not task.get("completed"):
                due_date = datetime.fromisoformat(task["due_date"])
                if due_date < today:
                    overdue_count += 1
        
        if overdue_count > 0:
            self.root.title(f"To-Do Widget ({overdue_count} overdue)")
        else:
            self.root.title("To-Do Widget")
    
    def save_data(self):
        data = {
            "daily_tasks": self.daily_tasks,
            "dated_tasks": self.dated_tasks
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.daily_tasks = data.get("daily_tasks", [])
                    self.dated_tasks = data.get("dated_tasks", [])
            except:
                self.daily_tasks = []
                self.dated_tasks = []

def main():
    root = tk.Tk()
    app = TodoWidget(root)
    root.mainloop()

if __name__ == "__main__":
    main()