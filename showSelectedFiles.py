import tkinter as tk
from tkinter import ttk
from typing import List

import settings

class ShowSelectedFiles:
    def __init__(self, sending_files: List[str], receiving_directory: str, sending_filesystem: str):
        self.root = tk.Tk()
        self.root.configure(bg=settings.window_bg)
        self.root.title("Remote File Transfer")
        self.root.geometry(f"+{settings.window_location['x']}+{settings.window_location['y']}")

        self.sending_files = sending_files
        self.receiving_directory = receiving_directory

        self.replace_files_direction: str = None

        self.transfer_intiated: bool = False

        # Title Label
        tk.Label(
            self.root,
            text="Uploading to E3" if sending_filesystem == "local" else "Downloading from E3",
            font=("Serif", 23, "bold"),
            bg=settings.window_bg,
        ).pack(padx=20, pady=10)


        self.make_sending_frame()

        self.make_receiving_frame()

        # Transfer Button
        tk.Button(
            self.root,
            command=self.on_transfer_clicked,
            text="Transfer Files",
            font=("Serif", 18),
            bg="#4CAF50",
            activebackground="#45A049",
            activeforeground="white",
            padx=10,
            pady=5,
        ).pack(pady=20)

        self.root.mainloop()

    def make_scrollable_frame(self, parent_frame: tk.Frame) -> ttk.Frame:
        # Calculate canvas dimensions based on the content
        item_height = 20  # Approximate height for each item
        max_item_width = max(len(file) for file in self.sending_files) * 6.5  # Estimate width based on string length
        canvas_height = min(len(self.sending_files) * item_height, 200) * 1.3  # Limit to a maximum height
        canvas_width = max(max_item_width, 100) * 1.2 # Limit to a maximum width

        # Container for scrollable content
        container = ttk.Frame(parent_frame)
        container.pack(expand=True, fill="both", padx=10)

        canvas = tk.Canvas(container, height=canvas_height, width=canvas_width)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame
    
    def make_sending_frame(self): 
        sending_outer_frame: tk.Frame = tk.Frame(master=self.root, bg=settings.window_bg)
        sending_outer_frame.pack(fill="x", padx=10, pady=10)

        # Sending Files Section
        tk.Label(
            sending_outer_frame,
            text="Sending These Folders/Files:",
            font=("Serif", 16),
            bg=settings.window_bg,
        ).pack(padx=10, pady=5)


        sending_frame = self.make_scrollable_frame(parent_frame=sending_outer_frame)

        for file in self.sending_files:
            tk.Label(
                sending_frame,
                text=file,
                font=("Serif", 14),
                anchor="w",
                padx=5,
            ).pack(fill="x", pady=2)
        
        tk.Button(
            sending_outer_frame,
            command=lambda: self.on_replace_files(file_direction="sending"),
            text="Add or Replace",
            font=("Serif", 15),
            bg="#4CAF50",
            highlightthickness=10,
            activebackground="#45A049",
            activeforeground="white",
        ).pack()
    
    def make_receiving_frame(self):
        receiving_outer_frame: tk.Frame = tk.Frame(master=self.root, bg=settings.window_bg)
        receiving_outer_frame.pack(fill="x", padx=20, pady=10)
        # Receiving Directory Section
        tk.Label(
            receiving_outer_frame,
            text="To This Folder:",
            font=("Serif", 16),
            bg=settings.window_bg,
        ).pack()

        receiving_frame = tk.Frame(receiving_outer_frame, relief="solid", padx=10, pady=10)
        receiving_frame.pack(fill="both")

        tk.Label(
            receiving_frame,
            text=self.receiving_directory,
            font=("Serif", 14),
            anchor="w",
            padx=5,
        ).pack(fill="x", pady=2)

        tk.Button(
            receiving_outer_frame,
            command=lambda: self.on_replace_files(file_direction="receiving"),
            text="Add or Replace",
            font=("Serif", 15),
            bg="#4CAF50",
            highlightthickness=10,
            activebackground="#45A049",
            activeforeground="white",
        ).pack()
        

    def on_transfer_clicked(self):
        settings.window_location['x'] = self.root.winfo_x()
        settings.window_location['y'] = self.root.winfo_y()
        self.transfer_intiated: bool = True
        self.root.destroy()
    
    def on_replace_files(self, file_direction: str):
        self.replace_files_direction = file_direction

        self.files_to_replace: List[str] = self.sending_files if self.replace_files_direction == "sending" else self.receiving_directory

        settings.window_location['x'] = self.root.winfo_x()
        settings.window_location['y'] = self.root.winfo_y()
        self.root.destroy()

if __name__ == "__main__":
    ShowSelectedFiles(
        sending_files=['/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB/subject_level_data_analysis/p001', '/Users/meghan/.zshrc.save', '/Users/meghan/.Rhistory', '/Users/meghan/.eclipse', '/Users/meghan/rsa_encrypt.py', '/Users/meghan/repos', '/Users/meghan/.python_history-31581.tmp', '/Users/meghan/Music', '/Users/meghan/python_gui', '/Users/meghan/.config', '/Users/meghan/.wine', '/Users/meghan/.docker', '/Users/meghan/.%068EFE59.png', '/Users/meghan/DOMYHW.py', '/Users/meghan/.DS_Store', '/Users/meghan/.CFUserTextEncoding', '/Users/meghan/ANTs', '/Users/meghan/.python_history-84658.tmp', '/Users/meghan/eclipse', '/Users/meghan/3ddcm2niix_results.png', '/Users/meghan/bin', '/Users/meghan/.bashrc.save', '/Users/meghan/E3_GUI_Application', '/Users/meghan/.hawtjni', '/Users/meghan/.vnc', '/Users/meghan/.local', '/Users/meghan/workdir', '/Users/meghan/.adobe', '/Users/meghan/newclnf', '/Users/meghan/.zshrc'],
        receiving_directory="/Users/meghan/target_folder",
        sending_filesystem="remote",
    )
