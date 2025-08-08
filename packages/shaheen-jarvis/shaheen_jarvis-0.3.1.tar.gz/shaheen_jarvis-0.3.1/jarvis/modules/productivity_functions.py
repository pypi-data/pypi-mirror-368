"""
Productivity functions for Shaheen-Jarvis framework.
Includes email, music player, alarm setting, and task management.
"""

import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from threading import Timer
import time
import subprocess
import webbrowser
import platform
import urllib.parse


def send_email(to_address: str, subject: str, body: str, attachments: Optional[List[str]] = None) -> str:
    """
    Send an email using SMTP.
    
    Args:
        to_address: Recipient email address
        subject: Email subject
        body: Email body
        attachments: List of file paths to attach
        
    Returns:
        Success or error message
    """
    try:
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))

        if not (email_address and email_password):
            return "Error: Email credentials not configured"

        # Create email
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))

        # Attach files
        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as f:
                        # Guess content type and set header accordingly
                        part = MIMEApplication(f.read(), Name=os.path.basename(file_path))

                    # After the file is closed
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
                except Exception as e:
                    return f"Error attaching file {file_path}: {str(e)}"

        # Connect to the server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)

        return f"Email sent successfully to {to_address}"

    except Exception as e:
        return f"Error sending email: {str(e)}"


def play_music(file_path: str) -> str:
    """
    Play a music file.
    
    Args:
        file_path: Path to the music file
        
    Returns:
        Success or error message
    """
    try:
        if not os.path.isfile(file_path):
            return f"Error: File not found - {file_path}"

        try:
            # Use the default media player to play music
            subprocess.Popen(['start', '', file_path], shell=True)
            return f"Playing music: {file_path}"
        except Exception as e:
            return f"Failed to play music: {str(e)}"

    except Exception as e:
        return f"Error playing music: {str(e)}"


class Alarm:
    """A simple alarm class."""
    
    def __init__(self, time: datetime, message: str):
        self.time = time
        self.message = message
        self.timer = Timer((time - datetime.now()).total_seconds(), self.alert)
        self.timer.start()

    def alert(self):
        print(f"Alarm: {self.message} at {self.time.strftime('%I:%M %p')}")


def set_alarm(time_string: str, message: str) -> str:
    """
    Set an alarm.
    
    Args:
        time_string: Time string in format 'HH:MM'
        message: Alarm message
        
    Returns:
        Success or error message
    """
    try:
        alarm_time = datetime.strptime(time_string, '%H:%M').replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

        if alarm_time < datetime.now():
            alarm_time += timedelta(days=1)

        Alarm(alarm_time, message)

        return f"Alarm set for {alarm_time.strftime('%I:%M %p')}: {message}"

    except Exception as e:
        return f"Error setting alarm: {str(e)}"


def create_todo(task: str) -> str:
    """
    Add a task to the to-do list.
    
    Args:
        task: Task description
        
    Returns:
        Success message
    """
    try:
        todos_file = "jarvis_todos.json"
        
        # Load existing todos
        todos = []
        if os.path.exists(todos_file):
            with open(todos_file, 'r', encoding='utf-8') as f:
                todos = json.load(f)
        
        # Create new task
        new_todo = {
            'id': len(todos) + 1,
            'task': task,
            'status': 'pending',
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        todos.append(new_todo)
        
        # Save todos
        with open(todos_file, 'w', encoding='utf-8') as f:
            json.dump(todos, f, indent=2, ensure_ascii=False)
        
        return f"Task '{task}' added to the to-do list"
    
    except Exception as e:
        return f"Error creating to-do: {str(e)}"


def show_todos(limit: int = 10) -> str:
    """
    Show tasks in the to-do list.
    
    Args:
        limit: Maximum number of tasks to show
        
    Returns:
        List of tasks or message
    """
    try:
        todos_file = "jarvis_todos.json"
        
        if not os.path.exists(todos_file):
            return "No tasks found."
        
        with open(todos_file, 'r', encoding='utf-8') as f:
            todos = json.load(f)
        
        if not todos:
            return "No tasks found."
        
        # Sort by most recent
        todos.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit results
        todos = todos[:limit]
        
        # Format output
        result = [f"Found {len(todos)} task(s):"]
        for todo in todos:
            result.append(f"\nID: {todo.get('id', 'N/A')}")
            result.append(f"Date: {todo.get('date', 'N/A')}")
            result.append(f"Task: {todo.get('task', '')}")
            result.append(f"Status: {todo.get('status', 'pending')}")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error showing to-dos: {str(e)}"


def play_youtube_song(song_query: str) -> str:
    """
    Play a song on YouTube by searching for it.
    
    Args:
        song_query: Song name or artist and song to search for
        
    Returns:
        Success or error message
    """
    try:
        # Encode the search query for URL
        encoded_query = urllib.parse.quote_plus(song_query)
        
        # Create YouTube search URL
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        # Open in default browser
        webbrowser.open(youtube_url)
        
        return f"Opening YouTube search for: {song_query}"
        
    except Exception as e:
        return f"Error playing YouTube song: {str(e)}"


def play_youtube_music(artist: str, song: str = None) -> str:
    """
    Play music on YouTube with artist and optional song name.
    
    Args:
        artist: Artist name
        song: Optional song name
        
    Returns:
        Success or error message
    """
    try:
        if song:
            query = f"{artist} {song}"
        else:
            query = f"{artist} songs"
            
        return play_youtube_song(query)
        
    except Exception as e:
        return f"Error playing YouTube music: {str(e)}"


def open_whatsapp() -> str:
    """
    Open WhatsApp Web in browser.
    
    Returns:
        Success or error message
    """
    try:
        # Open WhatsApp Web directly in browser
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp Web in browser"
            
    except Exception as e:
        return f"Error opening WhatsApp: {str(e)}"


def open_whatsapp_desktop() -> str:
    """
    Try to open WhatsApp desktop app, fallback to web.
    
    Returns:
        Success or error message
    """
    try:
        system = platform.system().lower()
        
        if system == "windows":
            try:
                subprocess.Popen(["start", "whatsapp://"], shell=True)
                return "Opening WhatsApp desktop app"
            except:
                webbrowser.open("https://web.whatsapp.com")
                return "WhatsApp desktop not found, opening WhatsApp Web"
                
        elif system == "darwin":  # macOS
            try:
                subprocess.Popen(["open", "-a", "WhatsApp"])
                return "Opening WhatsApp desktop on macOS"
            except:
                webbrowser.open("https://web.whatsapp.com")
                return "WhatsApp desktop not found, opening WhatsApp Web"
                
        else:  # Linux and others
            webbrowser.open("https://web.whatsapp.com")
            return "Opening WhatsApp Web in browser"
            
    except Exception as e:
        return f"Error opening WhatsApp: {str(e)}"


def open_app(app_name: str) -> str:
    """
    Open an application by name.
    
    Args:
        app_name: Name of the application to open
        
    Returns:
        Success or error message
    """
    try:
        system = platform.system().lower()
        app_name_lower = app_name.lower()
        
        # Common app mappings
        app_mappings = {
            "whatsapp": lambda: open_whatsapp(),
            "notepad": "notepad.exe" if system == "windows" else "gedit",
            "calculator": "calc.exe" if system == "windows" else "gnome-calculator",
            "chrome": "chrome.exe" if system == "windows" else "google-chrome",
            "firefox": "firefox.exe" if system == "windows" else "firefox",
            "telegram": "telegram://" if system == "windows" else "telegram-desktop",
            "spotify": "spotify://" if system == "windows" else "spotify",
            "discord": "discord://" if system == "windows" else "discord",
        }
        
        if app_name_lower in app_mappings:
            app_command = app_mappings[app_name_lower]
            
            # If it's a function, call it
            if callable(app_command):
                return app_command()
            
            # Otherwise, it's a command to run
            if system == "windows":
                subprocess.Popen(["start", "", app_command], shell=True)
            elif system == "darwin":
                subprocess.Popen(["open", "-a", app_command])
            else:
                subprocess.Popen([app_command])
                
            return f"Opening {app_name}"
        else:
            # Try to open the app directly
            if system == "windows":
                subprocess.Popen(["start", "", app_name], shell=True)
            elif system == "darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
                
            return f"Attempting to open {app_name}"
            
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"


def open_website(url: str) -> str:
    """
    Open a website in the default browser.
    
    Args:
        url: Website URL to open
        
    Returns:
        Success or error message
    """
    try:
        # Add https:// if not present
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        webbrowser.open(url)
        return f"Opening website: {url}"
        
    except Exception as e:
        return f"Error opening website: {str(e)}"


# For compatibility with the module loading system
__all__ = [
    "send_email",
    "play_music",
    "play_youtube_song",
    "play_youtube_music",
    "open_whatsapp",
    "open_whatsapp_desktop",
    "open_app",
    "open_website",
    "set_alarm",
    "create_todo",
    "show_todos"
]

