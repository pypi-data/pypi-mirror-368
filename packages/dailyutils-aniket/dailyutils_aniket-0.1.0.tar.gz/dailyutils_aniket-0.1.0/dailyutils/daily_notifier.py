import json
import os
from datetime import datetime

REMINDER_FILE = "reminders.json"

def _load_reminders():
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r") as f:
            return json.load(f)
    return []

def _save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

def set_reminder(time_str, message):
    """
    Set a reminder.
    time_str: Format "HH:MM" (24-hour)
    message: Reminder text
    """
    reminders = _load_reminders()
    reminders.append({
        "time": time_str,
        "message": message
    })
    _save_reminders(reminders)
    return {"status": "saved", "time": time_str, "message": message}

def list_reminders():
    """
    Returns all saved reminders.
    """
    return _load_reminders()

def check_due_reminders():
    """
    Returns reminders due at or before current time.
    """
    now = datetime.now().strftime("%H:%M")
    reminders = _load_reminders()
    due = [r for r in reminders if r["time"] <= now]
    return due
