import os
import tkinter as tk
from tkinter import ttk

import settings 
import getUserConfigs
from showUserSettings import ShowUserSettings

class MakeSettingsPanel:

    def __init__(self, root: tk.Tk, current_show_hidden: bool = False, current_sort_by: str = None):
        self.root = root
        self.sort_by_result = current_sort_by
        self.show_hidden: bool = current_show_hidden
        self.reconfigure: bool = False 
        self.reconfigure_key: str = None
        self.reconfigure_value: str = None
        
        self.settings_window: tk.Toplevel = tk.Toplevel(self.root, background=settings.window_bg, pady=15)
        self.settings_window.withdraw()
        self.settings_window.resizable(False, False)
        self.settings_window.overrideredirect(1)

        self.settings_window.title("Remote File Transfer")        
        login_info_frame: tk.Frame = tk.Frame(master=self.settings_window, padx = 10, pady=10)
        tk.Label(master=login_info_frame, text="User Settings: ", font=("Helvetica", 16, "bold")).pack(anchor='w')
        tk.Label(master=login_info_frame, text=f"Remote Host: {getUserConfigs.config['host']}", font=("Helvetica", 16)).pack(anchor='w')
        tk.Label(master=login_info_frame, text=f"Remote Username: {getUserConfigs.config['username']}", font=("Helvetica", 16)).pack(anchor='w')
        user_settings_button: tk.Button = tk.Button(
                        master=login_info_frame, 
                        text="Open User Settings",
                        command=lambda: self.on_open_settings())
        user_settings_button.pack(anchor='center', pady=10)
    
        login_info_frame.pack(fill='x', padx=15, pady=9)
    
        self.param_frame: tk.Frame = tk.Frame(master=self.settings_window, pady=10, padx=10)
    
        tk.Label(master=self.param_frame, text="Search Settings: ", font=("Helvetica", 16, "bold")).pack(anchor='w')

        sort_combobox: ttk.Combobox = self.make_sortby_button()

        checked_hidden: int = self.make_hidden_files_button(show_hidden=current_show_hidden)

        self.param_frame.pack(padx=15, pady=15)

        select_button: tk.Button = tk.Button(
                                master=self.settings_window, 
                                text="Save and Exit",
                                highlightbackground=settings.window_bg,
                                font=("Helvetica", 16),
                                command=lambda: self.on_submitted_for_filesystem_window(sort_combobox=sort_combobox,
                                                                                        checked_hidden=checked_hidden),
                                pady=3)
        select_button.pack(anchor='center')
        
        close_button: tk.Button = tk.Button(
                                master=self.settings_window, 
                                text="Close",
                                highlightbackground=settings.window_bg,
                                font=("Helvetica", 16),
                                command=lambda: self.on_close(),
                                pady=3)
        close_button.pack(anchor='center', pady=3)


        
        self.settings_window.transient(self.root)
        self.settings_window.grab_set()
        self.settings_window.deiconify()
        self.settings_window.update_idletasks()  # ensure dimensions are updated
        self.settings_window.geometry(f"+{self.root.winfo_x() + self.root.winfo_width() - self.settings_window.winfo_width()}+{self.root.winfo_y() + 28}") 
        
        self.root.wait_window(self.settings_window)

    def on_submitted_for_filesystem_window(self, sort_combobox:ttk.Combobox, checked_hidden: int):
        print(f"Saving Changes.")

        # Release grab
        self.settings_window.grab_release()
        
        # Remove focus
        self.root.focus_set()


        new_sory_by_result: str = 'Alphabetic' if sort_combobox.get().strip() == 'Alphabetic' else 'MostRecentModified'

        if not new_sory_by_result == self.sort_by_result:
            self.sort_by_result = new_sory_by_result
            getUserConfigs.edit_user_configs(key='sort_by', new_value=self.sort_by_result)
        
        self.show_hidden: bool = False if checked_hidden.get() == 0 else True

        self.settings_window.destroy()
    
    def make_sortby_button(self) -> ttk.Combobox:
        # create sort-by feature

        # configure the style for the Combobox dropdown
        style = ttk.Style()
        style.configure(
            'TCombobox', 
            font=("Helvetica", 16) 
        )
        style.map(
            'TCombobox',
            foreground=[('readonly', 'black')],
            background=[('readonly', 'white')]
        )

        sort_by_frame = tk.Frame(master=self.param_frame, width=300, height=400)

        label = tk.Label(
            master=sort_by_frame,
            text="Sort By: ",
            font=("Helvetica", 16)
        )
        label.grid(row=0, column=0)

        # create combobox
        combobox = ttk.Combobox(
            master=sort_by_frame,
            values=["Alphabetic", "Most Recently Modified"],
            state="readonly",
            style="TCombobox"
        )
        combobox.set("Alphabetic" if self.sort_by_result == "Alphabetic" else "Most Recently Modified")
        combobox.grid(row=0, column=1)

        sort_by_frame.pack(anchor="w")

        return combobox
    
    def make_hidden_files_button(self, show_hidden: bool) -> int:
        # create hide hidden files option 
        checked_hidden = tk.IntVar()
        show_hidden_button = tk.Checkbutton(self.param_frame, 
                                            text="Show Hidden Files", 
                                            variable=checked_hidden, 
                                            onvalue=1, 
                                            offvalue=0, 
                                            font=("Helvetica", 16))
        if show_hidden: 
            show_hidden_button.select()
        
        show_hidden_button.pack(anchor="w")

        return checked_hidden
    
    def get_if_show_hidden(self):
        return self.show_hidden
    

    def get_printable_string(self, string: str) -> str:
        if string == 'private_key_path':
            return 'Path To Private Key'
        elif string == 'username':
            return 'Remote Username'
        elif string == 'host':
            return 'Remote Hostname'
        elif string == 'remote_home_dir':
            return 'Remote Home Directory'
        elif string == 'local_home_dir':
            return 'Local Home Directory'

    def on_open_settings(self) -> str: 
        ShowUserSettings(root=self.root)

    def get_sort_by(self) -> str: 
        return self.sort_by_result
    
    def on_close(self):
        self.settings_window.destroy()
    

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    settings = MakeSettingsPanel(root=root)
