import os
import sys
from typing import List 


settings_script = os.path.abspath(__file__)

# icons, gifs, images
assets_dir = os.path.join(os.path.dirname(settings_script), 'assets')

# path to user's config files 
user_config_file: str = os.path.join(assets_dir, "user_configs.json")

file_image_path: str = os.path.join(assets_dir, "file.png")

file_clicked_image_path: str = os.path.join(assets_dir, "file_clicked.png")

file_nonclickable_image_path: str = os.path.join(assets_dir, "file_nonclickable.png")

opened_folder_image_path: str = os.path.join(assets_dir, "folder_opened2.png")

closed_folder_image_path: str = os.path.join(assets_dir, "folder_closed.png")

python_image_path: str = os.path.join(assets_dir, "python.png")

java_image_path: str = os.path.join(assets_dir, "java.png")

jupyter_image_path: str = os.path.join(assets_dir, "jupyter.png")

nifti_image_path: str = os.path.join(assets_dir, "nifti.png")

dicom_image_path: str = os.path.join(assets_dir, "dicom.png")

settings_image_path: str = os.path.join(assets_dir, "settings_icon.png")

download_image: str = os.path.join(assets_dir, "download_icon.png")

upload_image: str = os.path.join(assets_dir, "upload_icon.png")

gif_dir: str = os.path.join(assets_dir, "gifs")
gifs: List[str]  = [
   os.path.join(gif_dir, "loading_brain1.gif"),
   os.path.join(gif_dir, "loading_brain2.gif"),
   os.path.join(gif_dir, "loading_brain3.gif"),
   os.path.join(gif_dir, "loading_brain4.gif"), 
   os.path.join(gif_dir, "loading_brain5.gif"),
   os.path.join(gif_dir, "loading_brain6.gif"),
   os.path.join(gif_dir, "loading_brain7.gif"),
   os.path.join(gif_dir, "loading_brain8.gif"),
   os.path.join(gif_dir, "loading_brain9.gif"),
   os.path.join(gif_dir, "loading_brain10.gif"),
   os.path.join(gif_dir, "loading_brain11.gif"),
   os.path.join(gif_dir, "loading_brain12.gif")
]
# for finding window location 
window_location: dict = {
   "x": 100,
   "y": 50
}

# GUI configs 
folder_file_image_width: int = 105 

folder_file_image_height: int = 110

closed_folder_image_width: int = 105 

closed_folder_image_height: int = 110

button_height: int = 140

button_width: int = 115

max_files_to_show: int = 30

button_highlight_bg = "#b8c6d4"
button_highlight_bg_selected = "#558dc5"
window_bg = "#c2d4e3"
window_bg2 = "#d4d8dc"
button_highlight_bg2 = "#6496c7"
lightred = "#c79da6"


if __name__ == '__ main __':
   for path in gifs:
      if not os.path.exists(path):
         print(f"Gif path: {path} does not exist.")
   