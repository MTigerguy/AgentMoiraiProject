# Desktop To-Do Widget

A lightweight, persistent desktop to-do list widget built with Python and tkinter. Perfect for keeping your daily tasks and upcoming deadlines visible on your desktop.

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 📋 Features

### Core Functionality
- **Dual Task Sections**: Separate areas for daily recurring tasks and dated tasks
- **Smart Sorting**: Automatically sorts tasks by due date (earliest first)
- **Full Task Management**: Add, edit, mark complete, and delete tasks
- **Persistent Storage**: All tasks saved locally in JSON format
- **Always Visible**: Widget stays on top of other windows

### Visual Features
- **Color-Coded Priority System**:
  - 🔴 **Red**: Overdue tasks
  - 🟡 **Yellow**: Tasks due today
  - 🔵 **Light Blue**: Tasks due tomorrow
  - ⬜ **White**: Future tasks
- **Clean, Minimal Design**: Easy to read at a glance
- **Visual Task Separation**: Daily tasks have distinct blue background
- **Intuitive Date Display**: Shows "Today", "Tomorrow", or formatted dates like "Jan 15"

### Smart Features
- **Overdue Notifications**: Title bar shows count of overdue tasks
- **Quick Date Selection**: Radio buttons for Today/Tomorrow/Next Week
- **Strikethrough Completed Tasks**: Visual indication of completed items
- **Scrollable Task List**: Handles unlimited tasks while showing top 10 upcoming

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher
- tkinter (usually comes with Python)

### Installation

1. **Clone or download the repository**:
   ```bash
   git clone https://github.com/yourusername/todo-widget.git
   cd todo-widget
   ```
   Or simply download `todo_widget.py` directly.

2. **Run the application**:
   ```bash
   python todo_widget.py
   ```

That's it! No additional packages required.

## 💻 Platform-Specific Setup

### Windows

#### Method 1: Direct Run
- Double-click `todo_widget.py` if Python is associated with .py files

#### Method 2: Batch File
1. Create `launch_todo.bat`:
   ```batch
   @echo off
   python "C:\path\to\your\todo_widget.py"
   ```
2. Double-click the batch file to run

#### Auto-Start on Windows
1. Press `Win + R`, type `shell:startup`
2. Copy `todo_widget.py` or your batch file to this folder
3. The widget will launch automatically when Windows starts

### macOS

#### Run from Terminal
```bash
python3 todo_widget.py
```

#### Create an App Bundle (Optional)
1. Use Automator to create an Application
2. Add "Run Shell Script" action
3. Enter: `/usr/bin/python3 /path/to/todo_widget.py`
4. Save as an application

### Linux

#### Run from Terminal
```bash
python3 todo_widget.py
```

#### Create Desktop Entry
1. Create `~/.local/share/applications/todo-widget.desktop`:
   ```ini
   [Desktop Entry]
   Type=Application
   Name=To-Do Widget
   Exec=python3 /path/to/todo_widget.py
   Icon=task-due
   Terminal=false
   ```

## 📖 Usage Guide

### Adding Tasks

#### Daily Tasks
1. Click the **"+"** button in the blue "Daily Tasks" section
2. Enter your task description
3. Press Enter or click "Add"
4. These tasks persist day-to-day (perfect for routines)

#### Dated Tasks
1. Click the **"+"** button in "Upcoming Tasks"
2. Enter task description
3. Choose due date:
   - Select quick option (Today/Tomorrow/Next Week)
   - Or enter custom date as MM/DD/YYYY
4. Press Enter or click "Add"

### Managing Tasks

- **Complete a task**: Click the checkbox next to the task
- **Delete a task**: Click the red "×" button
- **View more tasks**: Scroll in the upcoming tasks section
- **Check overdue count**: Look at the window title bar

### Keyboard Shortcuts

- `Enter` - Save task when adding (in dialog)
- `Esc` - Close add task dialog (when focused)

## 📁 Data Storage

Your tasks are automatically saved to:
- **Windows**: `C:\Users\YourName\todo_widget_data.json`
- **macOS**: `/Users/YourName/todo_widget_data.json`
- **Linux**: `/home/YourName/todo_widget_data.json`

The data file is human-readable JSON, making it easy to backup or manually edit if needed.

### Data Structure
```json
{
  "daily_tasks": [
    {"text": "Review emails", "completed": false},
    {"text": "Daily standup", "completed": true}
  ],
  "dated_tasks": [
    {"text": "Project deadline", "due_date": "2025-01-15T00:00:00", "completed": false}
  ]
}
```

## 🎨 Customization

### Modifying Colors
Edit these values in the `__init__` method:
```python
self.bg_color = "#f0f0f0"        # Main background
self.daily_bg = "#e8f4f8"        # Daily tasks background
self.overdue_color = "#ffcccc"   # Overdue tasks
self.today_color = "#fff3cd"     # Today's tasks
self.tomorrow_color = "#f0f8ff"  # Tomorrow's tasks
```

### Changing Window Size
Modify the geometry in `__init__`:
```python
self.root.geometry("400x600")  # Width x Height
```

### Adjusting Task Display Limit
Change the slice value in `refresh_display`:
```python
for i, task in enumerate(self.dated_tasks[:10]):  # Change 10 to your preference
```

## 🐛 Troubleshooting

### Widget doesn't stay on top
- Some window managers may not support the "topmost" attribute
- Try running with administrator/sudo privileges

### Can't see all my tasks
- The widget shows only the first 10 upcoming dated tasks
- Completed or deleted tasks are removed from view
- Check your data file directly if tasks seem missing

### Date parsing errors
- Ensure dates are entered as MM/DD/YYYY format
- Use the radio buttons for quick date selection to avoid errors

### Widget won't start
- Verify Python 3.6+ is installed: `python --version`
- Check that tkinter is available: `python -c "import tkinter"`
- Look for error messages in terminal/command prompt

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

This project is released under the MIT License. Feel free to use, modify, and distribute as needed.

## 🔮 Future Enhancements

Potential features for future versions:
- [ ] Task categories/tags
- [ ] Recurring task templates
- [ ] Task priorities (High/Medium/Low)
- [ ] Time-based reminders
- [ ] Dark mode
- [ ] Export to calendar apps
- [ ] Cloud sync capability
- [ ] Multiple lists/projects
- [ ] Task notes/descriptions
- [ ] Drag-and-drop reordering

## 📧 Support

For issues, questions, or suggestions, please:
1. Check the Troubleshooting section
2. Review existing issues
3. Create a new issue with details about your problem

---

**Made with ❤️ using Python and tkinter**