import os
import tkinter as tk
from typing import Union
from datetime import datetime
import stat 

import settings

class makePopup:
    def __init__(self, root, button: tk.Button, popup_type: str,
                 filepath: str = None, sftpInstance = None, filesystem: str = None):
        self.root = root
        self.button = button
        self.popup_type = popup_type
        self.popup_after_id = None  # Store the after() ID for canceling
        self.filepath = filepath 
        self.sftpInstance = sftpInstance
        self.filesystem = filesystem
        
        if self.popup_type == 'file':
            self.create_file_popup()

    def create_file_popup(self):

        # Create a label for the popup (initially hidden)
        self.popup_frame = tk.Frame(master=self.root, 
                                    background=settings.window_bg2, 
                                    padx=10, 
                                    pady=10,
                                    highlightbackground=settings.button_highlight_bg2,
                                    highlightthickness=3)
        

        self.popup_frame.place_forget()

        # Bind events to the button
        self.button.bind("<Enter>", self.start_popup_timer)
        self.button.bind("<Leave>", self.cancel_popup_timer)

    def start_popup_timer(self, event):
        # Start a timer to show the popup after 1 second (1000ms)
        self.popup_after_id = self.root.after(1000, self.show_popup, event)
    
    def show_popup(self, event):
        
        if not self.popup_frame.winfo_exists():
            return 
        
        if self.popup_type == 'file':
            tk.Label(master=self.popup_frame,
                text=os.path.basename(self.filepath),
                font=("Helvetica", 14),
                background=settings.window_bg2,
                padx=2, 
                pady=5,
                wraplength=300,
                borderwidth=1
            ).pack(anchor='w')

            file_mode, mtime = self.get_file_info()

            tk.Label(master=self.popup_frame,
                text=f"File Mode: {file_mode}",
                font=("Helvetica", 12),
                background=settings.window_bg2,
                padx=2, 
                pady=2,
                borderwidth=1
            ).pack(anchor='w')

            tk.Label(master=self.popup_frame,
                        text=f"Last Modification Time: {mtime}",
                        font=("Helvetica", 12),
                        background=settings.window_bg2,
                        padx=2,
                        pady=2,
                        borderwidth=1
            ).pack(anchor='w')


        self.popup_frame.place(x=20, y=20)

    def cancel_popup_timer(self, event):
        # Cancel the timer and hide the popup if it was shown
        if self.popup_after_id:
            self.root.after_cancel(self.popup_after_id)
            self.popup_after_id = None
            self.popup_frame.place_forget()
    
    def get_file_info(self) -> Union[str, str]:
        if self.filesystem == 'remote':
            info = self.sftpInstance.client_session.stat(self.filepath)
            file_mode: str = stat.filemode(info.st_mode)
            mtime: str = datetime.fromtimestamp(info.st_mtime)

            return file_mode, mtime
            

        elif self.filesystem == 'local':
            info = os.stat(path=self.filepath)
            file_mode: str = info.st_mode
            mtime: str = datetime.fromtimestamp(info.st_mtime)
            

            return file_mode, mtime
