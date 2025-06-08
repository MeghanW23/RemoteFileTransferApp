import tkinter as tk
from PIL import ImageTk, Image

import authenticate
import settings 
from loginWindow import makeLoginWindow
from showUserSettings import ShowUserSettings

class selectionWindow:
    def __init__(self, already_logged_in: bool, sftpInstance:  authenticate.Sftp = None, testing_only: bool = False):
        self.transfer_direction: str = None
        self.already_logged_in = already_logged_in
        self.sftpInstance = sftpInstance
        self.testing_only = testing_only
    
        # Create the main window
        self.root = tk.Tk()
        self.root.geometry(f"+{settings.window_location['x']}+{settings.window_location['y']}")
        self.root.resizable(False, False)
        self.root.title("Remote File Transfer")
        
        # Style the window
        self.root.configure(bg=settings.window_bg)
        self.root.configure(padx=20)
        self.root.configure(pady=10)

        # Title label
        if not already_logged_in:
            title_label = tk.Label(
            self.root,
            text="Welcome! Select an Option.",
            font=("Helvetica", 20, "bold"),
            background=settings.window_bg,
            pady=5
            )
            title_label.pack(pady=10, padx=20, anchor="center")


        download_image = ImageTk.PhotoImage(Image.open(settings.download_image).resize((50, 50), Image.LANCZOS))
        upload_image = ImageTk.PhotoImage(Image.open(settings.upload_image).resize((50, 50), Image.LANCZOS))
        settings_image = ImageTk.PhotoImage(Image.open(settings.settings_image_path).resize((50, 50), Image.LANCZOS))

        # Create buttons
        upload_button = tk.Button(
                    self.root,
                    text="Upload To Remote         ",
                    image=upload_image,
                    font=("Helvetica", 18, "bold"),
                    command=self.upload_to_remote,
                    highlightbackground=settings.button_highlight_bg,
                    bd=3,
                    padx=20, 
                    pady=20,
                    width=310,
                    compound='left'
                )
        upload_button.pack(padx=10, pady=5, anchor="w")

        download_button = tk.Button(
                    self.root,
                    text="Download From Remote",
                    image=download_image,
                    font=("Helvetica", 18, "bold"),
                    command=self.download_from_remote,
                    highlightbackground=settings.button_highlight_bg,
                    bd=3,
                    padx=20,
                    pady=20, 
                    width=310,
                    compound='left'
                )
        download_button.pack(padx=10, pady=5, anchor='w')

        settings_button = tk.Button(
                    self.root,
                    text="Open Your User Settings",
                    image=settings_image,
                    font=("Helvetica", 18, "bold"),
                    command=lambda: self.show_settings(root=self.root),
                    highlightbackground=settings.button_highlight_bg,
                    bd=3,
                    padx=20,
                    pady=20, 
                    width=310,
                    compound='left'
                )
        settings_button.pack(padx=10, pady=5, anchor='w')

        # run the main loop
        self.root.mainloop()
    
    def show_settings(self, root: tk.Tk,):
        settings.window_location['x'] = root.winfo_x()
        settings.window_location['y'] = root.winfo_y()
        settings_window: ShowUserSettings = ShowUserSettings(root=root) 
       

    def upload_to_remote(self):
        settings.window_location['x'] = self.root.winfo_x()
        settings.window_location['y'] = self.root.winfo_y()
        if not self.already_logged_in:
            login = makeLoginWindow(sftpInstance=self.sftpInstance, using_private_key=True, testing_only=self.testing_only)

            if login.is_logged_in():
                self.transfer_direction: str = "upload"
                self.root.destroy()
        else:
            self.transfer_direction: str = "upload"
            self.root.destroy()
        
    def download_from_remote(self):
        settings.window_location['x'] = self.root.winfo_x()
        settings.window_location['y'] = self.root.winfo_y()
        if not self.already_logged_in:
            login = makeLoginWindow(sftpInstance=self.sftpInstance, using_private_key=True, testing_only=self.testing_only)
            if login.is_logged_in():
                self.transfer_direction: str = "download"
                self.root.destroy()
        else:
            self.transfer_direction: str = "download"
            self.root.destroy()
 
    def get_transfer_direction(self) -> str:
        return self.transfer_direction
    