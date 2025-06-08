import sys
import tkinter as tk
from typing import Tuple
from PIL import ImageTk, Image


import settings
import authenticate
import getUserConfigs
from showUserSettings import ShowUserSettings
class makeLoginWindow:
    def __init__(self, sftpInstance: authenticate.Sftp, using_private_key: bool, testing_only: bool = False):
        # skip login
        if testing_only:
            self.logged_in: bool = True
            return 
        
        self.logged_in: bool = False
        
        self.sftpInstance: authenticate.Sftp = sftpInstance

        if not using_private_key:
            root = tk.Tk()
            root.resizable(False, False)
            root.title("Remote File Transfer")
            root.configure(bg=settings.window_bg)
            root.geometry(f"+{settings.window_location['x']}+{settings.window_location['y']}")

            
                    
            # Title label
            title_label = tk.Label(
                root,
                text="Please Login to the Remote Server",
                font=("Helvetica", 20, "bold"),
                background=settings.window_bg,
            )
            title_label.pack(pady=10, padx=20)

            username_entry: str = None 
            password_entry: str = None 
        
            # Frame for input fields
            input_frame = tk.Frame(root, background=settings.window_bg)
            input_frame.pack(pady=10)

            # Username label and entry
            username_label = tk.Label(
                input_frame,
                text="Username:",
                font=("Helvetica", 18),
                background=settings.window_bg,
            )

            username_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            username_entry = tk.Entry(input_frame, width=25, font=("Helvetica", 18), highlightbackground=settings.button_highlight_bg)
            if getUserConfigs.config['username']:
                username_entry.insert(0, getUserConfigs.config['username'])
            username_entry.grid(row=0, column=1, padx=25, pady=5)


            password_label = tk.Label(
                input_frame,
                text="Password:",
                font=("Helvetica", 18),
                background=settings.window_bg, 
            )
            password_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            password_entry = tk.Entry(input_frame, width=25, font=("Helvetica", 18), show="*", highlightbackground=settings.button_highlight_bg)
            password_entry.grid(row=1, column=1, padx=25, pady=5)

            button_frame: tk.Frame = tk.Frame(background=settings.window_bg)
            login_button = tk.Button(
                button_frame,
                text="Login",
                font=("Helvetica", 18, "bold"),
                width=15,
                command=lambda: self.login(username_entry=username_entry, password_entry=password_entry, root=root),
                relief="raised",
                highlightbackground=settings.button_highlight_bg,
                bd=3,
                pady=2
            )
            login_button.grid(row=0, column=0)

            # Load the settings image
            settings_image = ImageTk.PhotoImage(Image.open(settings.settings_image_path).resize((27, 27), Image.LANCZOS))

            # Settings button
            settings_button: tk.Button = tk.Button(
                button_frame,
                image=settings_image,
                highlightbackground=settings.button_highlight_bg,
                bd=3,
                command=lambda: self.show_settings(root=root, username_entry=username_entry)
            )
            settings_button.grid(row=0, column=1, padx=10, pady=10)

            button_frame.pack()

            root.mainloop()
        else:
            self.login(username_entry=None, password_entry=None)

    def login(self, username_entry, password_entry, root=None):
        
        if username_entry is not None and password_entry is not None: 
            self.username = username_entry.get()
            self.password = password_entry.get()

            
            if self.sftpInstance.login(username=self.username, password=self.password):
                if root:
                    root.destroy() # destroy login window if logged in 
                    

                self.logged_in: bool = True

        else: 
            if self.sftpInstance.login():
                if root:
                    settings.window_location['x'] = root.winfo_x()
                    settings.window_location['y'] = root.winfo_y()
                    root.destroy()
                    
                self.logged_in: bool = True
            
    def get_username_and_password(self) -> Tuple[str, str]:
        return self.username, self.password
    
        
    def is_logged_in(self) -> bool:
        if self.logged_in:
            return True
        else:
            return False
    
    def on_closing(self):
        print("Exiting Now.")
        sys.exit(0)
    
    def show_settings(self, root: tk.Tk, username_entry: tk.Entry):
        settings.window_location['x'] = root.winfo_x()
        settings.window_location['y'] = root.winfo_y()
        ShowUserSettings(root=root) 
