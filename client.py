import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import shelve
import os

def watcherToStartup():
    #Add the watcher script to startup folder so it runs automatically after restart.
    # Get Windows Startup folder path
    startup_dir = os.path.join(
        os.getenv('APPDATA'),
        r'Microsoft\Windows\Start Menu\Programs\Startup'
    )
    
    # Define path for the new shortcut
    shortcut_path = os.path.join(startup_dir, "background.exe")
    return shortcut_path   


def get_db_path():
    dir_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    db_file = 'database.db'
    return os.path.join(dir_path, db_file)


class FileFilterApp:
    """
    The main application class for the File Filter GUI.
    It sets up the window, defines custom styles, and handles user interaction.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("File Filter Tool")
        
        # Increased height slightly to accommodate the new input field
        self.root.geometry("500x500")
        
        # Color Palette (Dark Theme inspired by Nord)
        # We define these variables here to make it easy to change the theme later.
        self.colors = {
            'bg': '#2E3440',        # Main Window Background (Dark Grey/Blue)
            'fg': '#D8DEE9',        # Primary Text Color (Off-white)
            'accent': '#88C0D0',    # Accent Color for highlights (Soft Blue)
            'button': '#5E81AC',    # Button Background (Darker Blue)
            'button_hover': '#81A1C1', # Button Hover State (Lighter Blue)
            'input_bg': '#3B4252',  # Background for input fields (Lighter Grey)
            'success': '#A3BE8C'    # Success Message Color (Green)
        }

        # Apply the background color to the main root window immediately
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize styles and build the UI
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        """
        Configures the ttk styles. 
        'ttk' widgets are styled differently than standard tk widgets; 
        they use a theme engine.
        """
        style = ttk.Style()
        
        # 'clam' is a theme that allows us to change colors more freely than native themes
        style.theme_use('clam')

        # Configure the default Label style
        style.configure('TLabel', 
                        background=self.colors['bg'], 
                        foreground=self.colors['fg'], 
                        font=('Helvetica', 11))

        # Create a custom style for the Header (Larger, bold, accent color)
        style.configure('Header.TLabel', 
                        font=('Helvetica', 18, 'bold'), 
                        foreground=self.colors['accent'])

        # Configure the Dropdown (Combobox) style
        style.configure('TCombobox', 
                        fieldbackground=self.colors['input_bg'], # Input area bg
                        background=self.colors['input_bg'],      # Dropdown list bg
                        foreground=self.colors['fg'],            # Text color
                        arrowcolor=self.colors['accent'])        # Arrow icon color
        
        # Configure the Main Button style
        style.configure('Accent.TButton',
                        background=self.colors['button'],
                        foreground='white',
                        font=('Helvetica', 10, 'bold'),
                        borderwidth=0,
                        focuscolor=self.colors['button'])
        
        # Define dynamic behavior for the button (change color on hover)
        style.map('Accent.TButton',
                  background=[('active', self.colors['button_hover'])])

        # Configure the Frame background to match the window
        style.configure('TFrame', background=self.colors['bg'])

    def create_widgets(self):
        """
        Creates and places all the GUI elements (widgets) onto the window.
        """
        # Main Container Frame: Holds everything centered with padding
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # 1. Title Label
        title_label = ttk.Label(main_frame, text="Filter Configuration", style='Header.TLabel')
        title_label.pack(pady=(0, 30), anchor='w') # anchor='w' aligns it to the West (Left)

        # 2. File Type Dropdown Section
        type_label = ttk.Label(main_frame, text="Select File Type")
        type_label.pack(anchor='w', pady=(0, 5))

        self.file_types = ["All Files (*.*)", "Python (*.py)", "Text (*.txt)", "Images (*.png, *.jpg)", "Data (*.csv, *.json)"]
        self.type_var = tk.StringVar()
        
        # Helper widget for selecting from a list
        self.combo = ttk.Combobox(main_frame, 
                                  textvariable=self.type_var, 
                                  values=self.file_types,
                                  state="readonly", # User can only select, not type
                                  font=('Helvetica', 10))
        self.combo.current(0) # Select the first item by default
        self.combo.pack(fill='x', pady=(0, 20), ipady=5) # ipady adds internal padding (height)

        # 3. UPDATED: Folder Selection Section (Target Directory)
        # Text changed from "Target File" to "Target Folder"
        path_label = ttk.Label(main_frame, text="Target Folder")
        path_label.pack(anchor='w', pady=(0, 5))

        # Container for the folder selection UI to keep button and text aligned
        file_select_frame = ttk.Frame(main_frame, style='TFrame')
        file_select_frame.pack(fill='x', pady=(0, 20))

        # Variable to store the selected path
        # Initial value changed to reflect folder selection
        self.selected_path_var = tk.StringVar(value="No folder selected")

        # Browse Button
        browse_btn = ttk.Button(file_select_frame, 
                                text="Browse Folder", # Text changed to reflect folder selection
                                command=self.browse_folder)
        browse_btn.pack(side='left', padx=(0, 10))

        # Label to display selected path (truncated visually if too long)
        self.path_display = ttk.Label(file_select_frame, 
                                      textvariable=self.selected_path_var,
                                      font=('Helvetica', 9, 'italic'),
                                      foreground=self.colors['fg'])
        self.path_display.pack(side='left', fill='x', expand=True)

        # 4. Keyword Input Section
        keyword_label = ttk.Label(main_frame, text="Filter by Keyword")
        keyword_label.pack(anchor='w', pady=(0, 5))

        self.keyword_entry = tk.Entry(main_frame, 
                                      bg=self.colors['input_bg'], 
                                      fg=self.colors['fg'],
                                      insertbackground=self.colors['accent'],
                                      relief='flat',
                                      font=('Helvetica', 11))
        self.keyword_entry.pack(fill='x', pady=(0, 30), ipady=8)

        # 5. Add Button
        # Triggers the self.on_add function when clicked
        add_btn = ttk.Button(main_frame, text="ADD FILTER", style='Accent.TButton', command=self.on_add)
        add_btn.pack(fill='x', ipady=10)

        # 6. Status Label 
        # Initially empty, used to show success or error messages
        self.status_label = ttk.Label(main_frame, text="", font=('Helvetica', 9))
        self.status_label.pack(pady=(15, 0))

    def browse_folder(self):
        """Opens a file dialog for the user to select a directory (folder)."""
        # Changed to use askdirectory() instead of askopenfilename()
        directory = filedialog.askdirectory(
            title="Select a Folder"
        )
        if directory:
            self.selected_path_var.set(directory)

    def on_add(self):
        """
        Callback function executed when the 'ADD FILTER' button is clicked.
        """
        # Retrieve values from inputs
        file_type = self.type_var.get()
        path = self.selected_path_var.get()
        keyword = self.keyword_entry.get().strip()

        # Basic Validation Logic
        # Updated validation message to reference 'folder'
        if path == "No folder selected" or not path:
             # Error if path is missing
            self.status_label.configure(text="Please select a folder first.", foreground="#BF616A") # Red color
        elif not keyword:
            # Error if keyword is missing
            self.status_label.configure(text="Please enter a keyword.", foreground="#BF616A") 
        else:
            # Success Logic
            print(f"Action: Adding Filter | Type: {file_type} | Path: {path} | Keyword: {keyword}")
            
            self.status_label.configure(text=f"Filter added for '{keyword}' in folder: {path}", foreground=self.colors['success'])
            
            # Optional: Clear inputs after successful add
            self.keyword_entry.delete(0, tk.END)

        with shelve.open(get_db_path()) as db:
            if 'keywords' not in db.keys():
                print("No keywords added yet")
                db['keywords'] = {}

            keywords = db['keywords']

            if keyword not in keywords:
                keywords[keyword] = path
            else:
                self.status_label.configure(text=f"Keyword '{keyword}' already exists.", foreground="#EBCB8B") # Yellow color for warning

            db['keywords'] = keywords
            print(keywords)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileFilterApp(root)
    root.mainloop()
