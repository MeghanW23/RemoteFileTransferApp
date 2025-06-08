import os
import sys

from showFileSystem import showFileSystem
import authenticate
import settings
from showSelectedFiles import ShowSelectedFiles

class selectFiles:
    def __init__(self, sftpInstance: authenticate.Sftp, transfer_direction: str):

        for path in [settings.closed_folder_image_path, 
                     settings.file_image_path, 
                     settings.file_nonclickable_image_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{path} does not exist")
            
        # initialize the information to get 
        self.files_selected: dict = {
            "direction": transfer_direction,
            "sending": [],
            "receiving": None
        }

        # get directions 
        sending_filesystem = "local" if transfer_direction == "upload" else "remote"
        remote_filesystem = "remote" if transfer_direction == "upload" else "local"

        # show the filesystem for the sending directory
        sending_file_session: showFileSystem = showFileSystem(sftpInstance=sftpInstance)
        sending_file_session.make_file_gui(filesystem=sending_filesystem, current_role="sender")

        # show the filesystem for the receiving directory only if sending files were selected
        if sending_file_session.get_selected():
            receiving_file_session: showFileSystem = showFileSystem(sftpInstance=sftpInstance)
            receiving_file_session.make_file_gui(filesystem=remote_filesystem, current_role="receiver")

            while True:

                # show selected files only if the sending and receiving file(s) were selected
                if sending_file_session.get_selected() and receiving_file_session.get_selected():
                            
                    # show all selected files and confirm transfer 
                    confirmFiles: ShowSelectedFiles =  ShowSelectedFiles(sending_files=sending_file_session.get_selected(),
                                                                        receiving_directory=receiving_file_session.get_selected(),
                                                                        sending_filesystem=sending_filesystem)

                    # exit if they didnt either confirm transfer or opt to replace files
                    if confirmFiles.transfer_intiated is False and not confirmFiles.replace_files_direction:
                        print(f"Transfer Not Confirmed. Exiting.")
                        sys.exit(0)
                    
                    # re-get files if opted in 
                    if confirmFiles.replace_files_direction:
                        if confirmFiles.replace_files_direction == "sending":
                            sending_file_session: showFileSystem = showFileSystem(sftpInstance=sftpInstance,
                                                                                  selected_files=confirmFiles.files_to_replace)
                            sending_file_session.make_file_gui(filesystem=sending_filesystem,
                                                               current_role="sender",
                                                               current_directory=os.path.dirname(confirmFiles.files_to_replace[-1]))

                        elif confirmFiles.replace_files_direction == "receiving":
                            receiving_file_session: showFileSystem = showFileSystem(sftpInstance=sftpInstance, 
                                                                                    receiving_dir=confirmFiles.files_to_replace[0])
                            receiving_file_session.make_file_gui(filesystem=remote_filesystem, 
                                                                current_role="receiver", 
                                                                current_directory=os.path.basename(confirmFiles.files_to_replace[0]))
                        else: 
                            print(f"confirmFiles.replace_files_direction must equal 'sending' or 'receiving'")
                            sys.exit(0)
                    else:

                        # update selected files if not getting new 
                        # initialize the information to get 
                        self.files_selected: dict = {
                            "direction": transfer_direction,
                            "sending": sending_file_session.get_selected(),
                            "receiving": receiving_file_session.get_selected()
                        }
                        break
                else:
                    # exit if not selected any files 
                    sys.exit(0)

    def get_selected_info(self):
        if self.files_selected['sending'] == []:
           print(f"No Sending Files Selected after closing")
        elif self.files_selected['receiving'] is None: 
             print(f"No Receiving Directory Selected after closing")
        else:
            return self.files_selected
