import threading
from loginWindow import makeLoginWindow
import authenticate
import getUserConfigs

from selectionWindow import selectionWindow
from selectFiles import selectFiles
import tkinter as tk
import settings 
from transferFiles import TransferFiles
from downloadingWindow import DownloadWindow


testing_only: bool = False # allow access to the GUI without connection to E3 

# create sftpInstance
sftpInstance: authenticate.Sftp = authenticate.Sftp()

# show login window and login here if not using private key
login: makeLoginWindow = None 
if not getUserConfigs.config['private_key_path'] or not getUserConfigs.config['username']:
    login: makeLoginWindow = makeLoginWindow(sftpInstance=sftpInstance, using_private_key=False, testing_only=testing_only)
else:
    login = 'using_private_key'

# show selection window and login if not already
if login == 'using_private_key' or login.is_logged_in():

    # get transfer direction (upload/download) - login here if using private key
    selection: selectionWindow = selectionWindow(already_logged_in=False if login == 'using_private_key' else True, 
                                                 sftpInstance=sftpInstance if login == 'using_private_key' else None,
                                                 testing_only=testing_only)

    transfer_direction: str = selection.get_transfer_direction()

    if transfer_direction == "upload" or transfer_direction == "download":

        # select the files to transfer
        fileSelector = selectFiles(sftpInstance=sftpInstance, transfer_direction=transfer_direction)
        selected_files: dict = fileSelector.get_selected_info()

        if selected_files:

            download_window = DownloadWindow()
            
            # initiate transfer on another thread 
            transfer = TransferFiles(sftpInstance=sftpInstance,
                        direction=selected_files['direction'],
                        sending_files=selected_files['sending'],
                        receiving_dir=selected_files['receiving'],
                        progress_callback=download_window.update_from_transfer_progress)
            threading.Thread(target=transfer.start).start()

            # show fun gifs while transfering
            download_window.start()
            
# close sftp connection
sftpInstance.close_session()