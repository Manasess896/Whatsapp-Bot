import sys
import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(override=True)

print("Environment variables loaded from .env file")

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.run_script()
        
    def run_script(self):
        if self.process and self.process.poll() is None:
            print(f"Terminating existing {self.script} process...")
            self.process.terminate()
            self.process.wait(timeout=5)  
        env = os.environ.copy()
        print(f"Starting {self.script}...")
        self.process = subprocess.Popen([sys.executable, self.script], env=env)
        print(f"{self.script} is now running")

    def on_modified(self, event):
     
        if event.src_path.endswith(self.script):
            print(f'{self.script} has been modified. Restarting...')
            self.run_script()

if __name__ == "__main__":
    script_to_watch = "main.py"
    print("\n===== WhatsApp Bot Runner =====")
    print(f"Starting and monitoring {script_to_watch}")
    print("This script will automatically restart the bot when changes are detected")
  
    event_handler = ChangeHandler(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        print(f"\nWatching for changes in {script_to_watch}...")
        print("Press Ctrl+C to stop the bot")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping observer and bot process...")
        observer.stop()
      
        if event_handler.process and event_handler.process.poll() is None:
            event_handler.process.terminate()
            event_handler.process.wait(timeout=5)
        print("Bot stopped successfully")
    observer.join()