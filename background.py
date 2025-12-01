#WINDOWS ONLY!

import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import shelve
import shutil

def moveFile( source, dest ):
    print(f'Moving {source} -> {dest}')
    if os.path.isdir(dest): #Prevent overwriting directory
        dest = os.path.join( dest, os.path.basename(source) )

    try:
        shutil.move(source, dest)
        print(f"Successfully moved '{source}' to '{dest}'")
    except FileNotFoundError:
        print(f"Error: Source '{source}' not found.")
    except PermissionError:
        print(f"Error: Permission denied to move '{source}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            newFile = event.src_path
            print(f"✅ New file downloaded: {newFile}")
            time.sleep(0.5)
            db_path = os.path.join(Path(__file__).resolve().parent, "database.db") #Make dictionary path absolute and in same folder as this script.
            with shelve.open("database") as db:
                if "keywords" not in db: #check if db has been created yet.
                    db["keywords"] = []
                for i in db['keywords']:
                    if i in str(newFile):
                        destinationPath = db["keywords"][i]
                        moveFile( newFile, destinationPath )


watchFolder = Path.home() / "Downloads"
observer = Observer()
observer.schedule(DownloadHandler(), watchFolder, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print("Stopped")
observer.join()
