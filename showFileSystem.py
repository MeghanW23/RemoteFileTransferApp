import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import List, Union
from PIL import ImageTk, Image

import authenticate
from makeSettingsPanel import MakeSettingsPanel
from makePopup import makePopup
import settings
import getUserConfigs

class showFileSystem:
    def __init__(self, sftpInstance: authenticate.Sftp,  selected_files: List[str] = [], receiving_dir: str = None, show_hidden_files: bool = False):
        self.settings_panel = None 
        self.sort_by=getUserConfigs.config['sort_by']

        self.root = tk.Tk()
        self.root.title("Remote File Transfer") 
        self.root.resizable(False, False)
        self.root.config(background=settings.window_bg)
        self.root.geometry(f"+{settings.window_location['x']}+{settings.window_location['y']}")
        
        
        
        # load icons 
        self.icons: dict = {
            "closed_folder_image": self.load_image(image_path=settings.closed_folder_image_path),
            "file_image": self.load_image(image_path=settings.file_image_path),
            "file_nonclickable_image": self.load_image(image_path=settings.file_nonclickable_image_path),
            "python_image": self.load_image(image_path=settings.python_image_path),
            "jupyter_image": self.load_image(image_path=settings.jupyter_image_path),
            "nifti_image": self.load_image(image_path=settings.nifti_image_path),
            "java_image": self.load_image(image_path=settings.java_image_path),
            "dicom_image": self.load_image(image_path=settings.dicom_image_path),
            'settings_image': self.load_image(image_path=settings.settings_image_path, desired_height=35, desired_width=35)
        }

        self.sftpInstance = sftpInstance

        self.selected_files: list[str] = selected_files # for sending files

        self.receiving_dir: str = receiving_dir # for receiving files

        self.selection_confirmed: bool = False 

        self.load_more_button: tk.Button = None

        self.show_hidden_files: bool = show_hidden_files

    def make_file_gui(self, filesystem: str, current_role: str, current_directory: str = None):
        # clear window
        for widget in self.root.winfo_children():
            if widget.winfo_exists:
                widget.destroy()

        # do home directory if not given a path or is home dir
        is_home_directory: bool = False
        if current_directory:
            current_directory = os.path.normpath(current_directory)
        if not current_directory or current_directory == self.sftpInstance.get_local_home_dir() or current_directory == self.sftpInstance.get_remote_home_dir(): 
            if filesystem == "local":
                current_directory: str = self.sftpInstance.get_local_home_dir()
                is_home_directory: bool = True
            elif filesystem == "remote":
                current_directory: str = self.sftpInstance.get_remote_home_dir()
                is_home_directory: bool = True
        
        title_frame: tk.Frame = tk.Frame(master=self.root, background=settings.window_bg)
        title_frame.pack(fill=tk.X)  # Fill the frame horizontally

        # create empty frames for spacers
        left_spacer = tk.Frame(master=title_frame, width=1)
        left_spacer.grid(row=0, column=0)

        right_spacer = tk.Frame(master=title_frame, width=1)
        right_spacer.grid(row=0, column=2)

        # configure column weights
        title_frame.grid_columnconfigure(0, weight=6)  # Left spacer
        title_frame.grid_columnconfigure(1, weight=0)  # Center column for the label
        title_frame.grid_columnconfigure(2, weight=4)  # Right spacer

        # select and show the title label
        main_label_text: str = None
        if current_role == "sender":
            main_label_text: str = f"Select {filesystem.capitalize()} Folders and Files to Send"
        elif current_role == "receiver":
            main_label_text: str = f"Select a {filesystem.capitalize()} Folder to Put the Transferred Files"
        filesystem_label: tk.Label = tk.Label(master=title_frame,
                                            text=main_label_text,
                                            font=("Helvetica", 18, "bold"),
                                            background=settings.window_bg)
        filesystem_label.grid(row=0, column=1)  # Place label in the center column

        # Settings button
        settings_button = tk.Button(title_frame, 
                                    image=self.icons['settings_image'],
                                    highlightbackground=settings.button_highlight_bg,
                                    command=lambda: self.make_settings_frame(filesystem=filesystem, current_role=current_role, current_directory=current_directory))
        settings_button.grid(row=0, column=2, sticky="e", padx=5)  # Align button to the right

    
        # button menu frame 
        button_menu_frame: tk.Frame = tk.Frame(master=self.root, background=settings.window_bg)
        button_menu_frame.pack()

        # add the select button
        select_button:tk.Button = tk.Button(master=button_menu_frame, 
                                            text="Select", 
                                            font=("Helvetica", 16),
                                            highlightbackground=settings.button_highlight_bg,
                                            command=lambda: self.on_selected(current_role=current_role))
        
        select_button.grid(column=0, row=0, padx=10)
        

        # go back button if its not the home directory
        if not is_home_directory:
            go_back_button:tk.Button = tk.Button(master=button_menu_frame, 
                                                text="Go Back", 
                                                font=("Helvetica", 16),
                                                highlightbackground=settings.button_highlight_bg,
                                                command=lambda: self.on_go_back_clicked(filesystem=filesystem,
                                                                                        current_role=current_role,
                                                                                        current_directory=os.path.dirname(current_directory)))
        
            go_back_button.grid(column=1, row=0, padx=10)

        # add exit back button 
        exit_button:tk.Button = tk.Button(master=button_menu_frame, 
                                          text="Close", 
                                          font=("Helvetica", 16),
                                          highlightbackground=settings.button_highlight_bg,
                                          command=lambda: self.on_close_clicked())
        exit_button.grid(column=2, row=0, padx=10)

        # make frame for the buttons 
        button_frame: ttk.Frame = self.make_scrollable_frame(parent_frame=self.root)

        self.make_all_buttons(filesystem=filesystem, 
                              current_directory=current_directory, 
                              current_role=current_role,
                              button_frame=button_frame)
        

        # show current directory as a label 
        tk.Label(
            master=self.root,
            text=f"Current Directory: {current_directory}",
            font=("Helvetica", 16),
            wraplength=700,
            background=settings.window_bg,
            ).pack(padx=5, pady=10, anchor='center')

        self.root.mainloop()

    def make_all_buttons(self, filesystem: str, current_directory: str, current_role: str, button_frame: ttk.Frame, 
                         current_row: int = 0, current_column: int = -1, file_batch: int = 0):
        
        # destroy button if it already exists
        if self.load_more_button: 
            self.load_more_button.destroy()
        
        # get the list of files to make buttons for 
        paths_in_dir, is_concatenated_list = self.sftpInstance.list_elements(filesystem=filesystem,
                                                                             directory=current_directory,
                                                                             sort_by=self.sort_by, 
                                                                             file_batch=file_batch,
                                                                             show_hidden=self.show_hidden_files)
        if paths_in_dir is False or os.path.dirname(paths_in_dir[0][0]) != current_directory: 
            self.make_file_gui(filesystem=filesystem, 
                               current_role=current_role, 
                               current_directory=os.path.dirname(current_directory))

        # add the buttons 
        for path, isdir in paths_in_dir:
            current_column += 1
            if current_column > 4:
                current_column = 0
                current_row += 1    

            self.make_button(button_frame=button_frame,
                             current_role=current_role,
                             is_dir=isdir,
                             path=path,
                             filesystem=filesystem,
                             column=current_column,
                             row=current_row)
        
        # add 'load more files' button if only some files are shown
        # TODO edit so it doesn't show the same files
        if is_concatenated_list:
            self.load_more_button: tk.Button = tk.Button(master=button_frame,
                                                    text="Load More Files",
                                                    font=("Helvetica", 16),
                                                    highlightbackground=settings.button_highlight_bg,
                                                    command= lambda: self.make_all_buttons(filesystem=filesystem, current_directory=current_directory, 
                                                                                           current_role=current_role, button_frame=button_frame, 
                                                                                           current_row=current_row, current_column=current_column, 
                                                                                           file_batch=file_batch + 1))
            self.load_more_button.grid(column=2, row=current_row + 1, pady=5)            

    def make_scrollable_frame(self, parent_frame: tk.Frame) -> tk.Frame:
        # Container Frame with a consistent background
        container = tk.Frame(parent_frame, background=settings.window_bg, bd=0, highlightthickness=0)
        container.pack(expand=True, fill="both", padx=20, pady=5)

        # Canvas with matching background and no borders
        canvas = tk.Canvas(container, width=685, height=500, background=settings.window_bg, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        # Scrollable Frame with matching background
        scrollable_frame = tk.Frame(canvas, background=settings.window_bg)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Add the scrollable frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Configure canvas scroll
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame

    
    def make_button(self, button_frame: ttk.Frame, current_role: str, is_dir: bool, path: str, column: int, row:int, filesystem: str):
        image: ImageTk.PhotoImage = None 
        button: tk.Button = None

        if is_dir:
            image: ImageTk.PhotoImage = self.icons['closed_folder_image']
        elif os.path.splitext(os.path.basename(path))[1] == ".py":
            image: ImageTk.PhotoImage = self.icons['python_image']
        elif os.path.splitext(os.path.basename(path))[1] == ".java":
            image: ImageTk.PhotoImage = self.icons['java_image']
        elif os.path.splitext(os.path.basename(path))[1] == ".ipynb":
            image: ImageTk.PhotoImage = self.icons['jupyter_image']
        elif os.path.splitext(os.path.basename(path))[1] == ".nii" or path.endswith(".nii.gz"):
            image: ImageTk.PhotoImage = self.icons['nifti_image']
        elif os.path.splitext(os.path.basename(path))[1] == ".dcm":
            image: ImageTk.PhotoImage = self.icons['dicom_image']
        elif current_role == "receiver":
            image: ImageTk.PhotoImage = self.icons['file_nonclickable_image']
        elif current_role == "sender":
            image: ImageTk.PhotoImage = self.icons['file_image']

        if current_role == "sender" or is_dir:
            button = tk.Button(master=button_frame,
                            image=image,
                            text=self.make_filename_button_label(filename=os.path.basename(path), length="short"),
                            compound="top",
                            highlightthickness = 4,
                            bd = 0,
                            highlightbackground=settings.button_highlight_bg,
                            height = 140,
                            width= 115,
                            font=("Serif", 12))
            
            # configure buttons 
            if is_dir:
                button.bind(
                    '<Double-Button-1> ',
                    lambda event: self.on_double_clicked(filesystem=filesystem, path=path, current_role=current_role, button=button, current_directory=path)
                ) 
            button.bind(
                '<Button-1> ',
                lambda event: self.on_clicked(path=path, 
                                            current_role=current_role, 
                                            isdir=is_dir, 
                                            button=button, 
                                            button_frame=button_frame,)
                ) 

            makePopup(root=self.root, 
                      button=button, 
                      popup_type='file',
                      filepath=path,
                      sftpInstance=self.sftpInstance, 
                      filesystem=filesystem)
            
            # select if already selected
            if path in self.selected_files:
                button.configure(highlightbackground=settings.button_highlight_bg_selected)
            
            
        else:
            button = tk.Label(master=button_frame,
                            image=image,
                            text=self.make_filename_button_label(filename=os.path.basename(path), length="short"),
                            compound="top",
                            bd = 0,
                            highlightbackground=settings.button_highlight_bg,
                            background = settings.button_highlight_bg,
                            height = 140,
                            width= 115,
                            font=("Helvetica", 12)).grid(column=column, row=row, padx=5, pady=5)
            return 

        button.grid(column=column, row=row, padx=5, pady=5)
        
    def load_image(self, image_path: str, desired_width: int = 105, desired_height: int  = 110) -> ImageTk.PhotoImage:
        image = Image.open(image_path).resize((desired_width, desired_height), Image.LANCZOS)
        print(f"Loaded image: {image_path}, Size: {image.size}")
        return ImageTk.PhotoImage(image)

    def on_clicked(self, path: str, current_role: str, isdir: bool, button: tk.Button, button_frame: ttk.Frame):
        if current_role == "sender":
            if not path in self.selected_files:
                self.selected_files.append(path)
                button.configure(highlightbackground=settings.button_highlight_bg_selected)
                button.configure(text=self.make_filename_button_label(filename=os.path.basename(path), length="full", button=button))
            else:
                self.selected_files.remove(path)
                button.configure(text=self.make_filename_button_label(filename=os.path.basename(path), length="short"))
                button.configure(highlightbackground=settings.button_highlight_bg)
        
            print("Currently selected files: ")
            print(self.selected_files)
        
        elif current_role == "receiver":
            self.receiving_dir = path

            # clear window
            for widget in button_frame.winfo_children():
                if widget.winfo_exists():
                    if isinstance(widget, tk.Button):
                        widget.configure(text=self.make_filename_button_label(filename=widget['text'], length="short"))
                        widget.configure(highlightbackground=settings.button_highlight_bg)

            button.configure(highlightbackground=settings.button_highlight_bg_selected)
            button.configure(text=self.make_filename_button_label(filename=os.path.basename(path), length="full", button=button))

            print("Receiving Directory:")
            print(self.receiving_dir)

    def on_double_clicked(self, filesystem: str, path: str, current_role: str, button: tk.Button, current_directory: str = None):
        button.configure(highlightbackground="SystemButtonFace")
        if path in self.selected_files:
            self.selected_files.remove(path)

        self.make_file_gui(filesystem=filesystem, current_role=current_role, current_directory=current_directory)
    
    def on_close_clicked(self):
        sys.exit(0)
    
    def on_go_back_clicked(self, filesystem: str, current_role: str, current_directory: str = None):
        self.make_file_gui(filesystem=filesystem, current_role=current_role, current_directory=current_directory)
    
    def on_selected(self, current_role: str):
        if current_role == "sender" and not self.selected_files: 
            messagebox.showinfo("", "Please select at least one file or folder.")
        elif current_role == "receiver" and not self.receiving_dir:
            messagebox.showinfo("", "Please select a directory to put your files/folders.")
        else:   
            self.selection_confirmed: bool = True 
            settings.window_location['x'] = self.root.winfo_x()
            settings.window_location['y'] = self.root.winfo_y()
            self.root.destroy()
    
    def get_selected(self):
        if self.receiving_dir and self.selection_confirmed:
            return self.receiving_dir
    
        elif self.selected_files != [] and self.selection_confirmed:
            return self.selected_files
          
    def make_filename_button_label(self, filename:str, length: str, button: Union[tk.Button, tk.Label] = None): 
        if length == "short": 
            if len(filename) < 16: 
                return filename
            else: 
                return f"{filename[0:12]}..."
        elif length == "full":
            button.configure(wraplength=100)

            if len(filename) < 28:
                return filename 
            else: 
                return f"{filename[0:12]}...{filename[-12:]}"

    def make_settings_frame(self, filesystem: str, current_role: str, current_directory: str): 
        make_new: bool = False 
        self.settings_panel = MakeSettingsPanel(root=self.root,
                                           current_show_hidden=self.show_hidden_files,
                                           current_sort_by=self.sort_by)
        new_sort_by: str = self.settings_panel.get_sort_by()
        if new_sort_by != self.sort_by:
            print(f"Sort By Method Chosen: {new_sort_by}")
            self.sort_by = new_sort_by
            make_new: bool = True

        if self.settings_panel.get_if_show_hidden() != None: 
            hidden_file_result = self.settings_panel.get_if_show_hidden()

            if hidden_file_result != self.show_hidden_files:
                self.show_hidden_files = hidden_file_result
                make_new: bool = True
                print(f"{'Not' if hidden_file_result is False else 'Now'} Showing Hidding Files")
                
        if make_new:
            self.make_file_gui(filesystem=filesystem, current_role=current_role, current_directory=current_directory)








                