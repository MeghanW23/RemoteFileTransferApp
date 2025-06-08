import os
import sys
import tkinter as tk
from tkinter import messagebox 

import settings
import getUserConfigs

class ShowUserSettings():
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config_window: tk.Toplevel = tk.Toplevel(master=self.root, bg=settings.window_bg, padx=5, pady=5)
        self.config_window.geometry(f"+{self.root.winfo_x()}+{self.root.winfo_y()}")
        self.config_window.title("Remote File Transfer")
        self.config_window.resizable(False, False)
        self.config_window.config(padx=20)
        self.entries: dict[str, tk.Entry] = {}
        self.new_username: str = False

        tk.Label(master=self.config_window, text="Your User Settings", font=("Helvetica", 22, "bold"), bg=settings.window_bg).pack(padx=10, pady=10)

        for key, value in getUserConfigs.config.items():
            key = key.strip()
            value = value.strip() if value.strip() != "" else None 

            if key.strip() == 'sort_by': 
                continue

            self.show_setting(conf_key=key, conf_value=value)
        
        submit_button: tk.Button = tk.Button(master=self.config_window,
                                             text="Save and Exit App",
                                             font=("Helvetica", 18),
                                             highlightbackground=settings.window_bg,
                                             command=self.on_submit_pressed,
                                             padx=2,
                                             pady=2)
        submit_button.pack(padx=5, pady=10)

        cancel_button: tk.Button = tk.Button(master=self.config_window,
                                             text="Cancel",
                                             font=("Helvetica", 18),
                                             highlightbackground=settings.window_bg,
                                             command=self.on_cancel_pressed,
                                             padx=2,
                                             pady=2)
        cancel_button.pack(padx=5)

        tk.Label(master=self.config_window, text="For changes to be enacted, the app needs to be shut down and re-open.", font=("Helvetica", 12), bg=settings.window_bg).pack(padx=10, pady=10)

        # set the settings window as modal
        self.config_window.overrideredirect(1)
        self.config_window.transient(self.root)
        self.config_window.grab_set()
        
        self.root.wait_window(self.config_window)

    def show_setting(self, conf_key: str, conf_value: str = None):
        setting_frame: tk.Frame = tk.Frame(master=self.config_window, padx=10, pady=10)
        
        tk.Label(master=setting_frame, 
                 text=f"{self.get_string_to_show_from_keyname(string=conf_key)}:",
                 font=("Helvetica", 18, "bold"),
                 padx=3, 
                 pady=5).grid(column=0, row=0, padx=5, sticky='w')

        entry: tk.Entry = tk.Entry(master=setting_frame, 
                                   font=("Helvetica", 16),
                                   width=40,
                                   highlightbackground=settings.window_bg2,
                                   highlightthickness=6)
        if conf_value:
            entry.insert(0, conf_value)
        else: 
            entry.config(highlightbackground=settings.lightred)
        entry.grid(column=0, row=1, padx=5, sticky='w')

        setting_frame.pack(padx=10, pady=10, anchor='w')

        self.entries[conf_key] = entry

    def get_string_to_show_from_keyname(self, string: str):
        if string == 'private_key_path': 
            return 'Path to Private Key'
        elif string == 'username':
            return 'Remote Username'
        elif string == 'host':
            return 'Remote Host'
        elif string == 'remote_home_dir':
            return 'Home Directory on Remote'
        elif string == 'local_home_dir':
            return 'Home Directory on Local'

    def on_submit_pressed(self):
        for conf_key, entry_widget in self.entries.items():
            new_value: str = entry_widget.get().strip()

            if not new_value in getUserConfigs.config.values():
                if conf_key in ['local_home_dir', 'private_key_path'] and not os.path.exists(new_value) and not new_value.strip() == "":

                    messagebox.showinfo("", f"The entered \n{self.get_string_to_show_from_keyname(conf_key)}\n does not exist on your computer.\nChange Not Saved.")
                    
                else:
                    print(f"Setting Change for {conf_key}: {new_value}")

                    getUserConfigs.edit_user_configs(key=conf_key, new_value=new_value)
                    entry_widget.insert(0, new_value)

                    if conf_key == 'username':
                        self.new_username: str = new_value
        
        os._exit(0)
    
    def check_for_new_username(self):
        return self.new_username

    def on_cancel_pressed(self):
        self.config_window.grab_release()  
        self.config_window.destroy()



if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    
    ShowUserSettings(root=root)

    root.mainloop()

