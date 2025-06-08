import os
import sys
import threading
from typing import List, Union
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import paramiko

import authenticate
from downloadingWindow import DownloadWindow

class TransferFiles:
    def __init__(self, sftpInstance: authenticate.Sftp, direction: str, sending_files: List[str], receiving_dir: str, progress_callback):
        self.sftpInstance: authenticate.Sftp = sftpInstance
        self.direction: str = direction
        self.sending_files: List[str] = sending_files
        self.receiving_dir: str = receiving_dir
        self.progress_callback = progress_callback
        

        print(f"\n{'Uploading To' if self.direction == 'upload' else 'Downloading From'} Remote")
        print(f"Sending Files: ")
        for file in self.sending_files:
            print(f"  {file}")
        print(f"To Directory:")
        print(f"  {self.receiving_dir}")        

    def start(self):
        if self.direction == "upload":
            self.upload_files(self.sending_files, self.receiving_dir)

        elif self.direction == "download":
            self.download_files(self.sending_files, self.receiving_dir)
        
        # report that the transfer is done to main thread
        self.progress_callback(action="done")

    def upload_files(self, files_to_send: Union[List[str], str], receiving_dir: str):

        # if its a string, it must be the parent dir and we can extract the files from it 
        if isinstance(files_to_send, str):
            files_to_send: List[str] = [os.path.join(files_to_send, file) for file in os.listdir(files_to_send)]

        for i, path in enumerate(files_to_send, start=1):
            
            if os.path.isdir(s=path):

                # make the directory on remote that was found and then copy the files to it
                remote_dir_to_make: str = os.path.join(receiving_dir, os.path.basename(path))
                print(f"Making Dir: {path} as {remote_dir_to_make}")
                if not self.mkdir_on_remote(dir=remote_dir_to_make): 
                    print(f"Could not make dir: {path}. Skipping.")
                    continue 
                
                # use the same function to send all the files 
                self.upload_files(files_to_send=path, 
                                  receiving_dir=remote_dir_to_make)
                
            else:
                if os.path.isfile(path=path):

                    remote_file_to_make: str = os.path.join(receiving_dir, os.path.basename(path))
                    print(f"Sending File: {path} as: {remote_file_to_make}")
                    if self.send_file_to_remote(localpath=path, remotepath=remote_file_to_make) is False:
                        print(f"Could not send file.")
                    
                else:

                    print(f"Could not find local file or dir: {path}")
            

    def download_files(self, files_to_send: Union[List[str], str], receiving_dir: str, ignore_existing_dir: bool = False):

        # if its a string, it must be the parent dir and we can extract the files from it 
        if isinstance(files_to_send, str):
            files_to_send: List[str] = [f"{files_to_send}/{file}" for file in self.sftpInstance.client_session.listdir(files_to_send)]
        
        for i, path in enumerate(files_to_send, start=1):
            if self.exists_on_remote(path):
                if self.is_remote_dir(remotepath=path):

                    # make the directory on local that was found and then copy the files to it
                    local_dir_to_make: str = os.path.join(receiving_dir, os.path.basename(path))
                    print(f"Making Dir: {path} as {local_dir_to_make}")
                    try:
                        os.makedirs(local_dir_to_make)
                    except FileExistsError:
                        
                        if ignore_existing_dir is False:
                            if messagebox.askyesno("", f"Directory: {local_dir_to_make} Already Exists Locally. \nSkip this directory and continue?"):
                                print(f"Failed to make dir: {local_dir_to_make} as it already exists locally.")
                                continue
                            else: 
                                # exiting 
                                os._exit(1)
                            
                
                    # use the same function to send all the files 
                    self.download_files(files_to_send=path,
                                        receiving_dir=local_dir_to_make)

                else:   
                    local_file_to_make: str = os.path.join(receiving_dir, os.path.basename(path))
                    print(f"Sending File: {path} as: {local_file_to_make}")
                    if self.copy_file_to_local(remotepath=path, localpath=local_file_to_make) is False:
                        print(f"Could not send file")
            else: 
                continue 
    def mkdir_on_remote(self, dir: str, mode:int=511, ignore_existing:bool=False) -> bool:
        # mkdir but ignore existing 
        try:
            print(f"Making Dir: {dir}")
            self.sftpInstance.client_session.mkdir(path=dir, mode=mode)
            return True
        except IOError:
            # ignore error if ignore_existing
            if ignore_existing:
                pass 
            else:
                if messagebox.askyesno("", f"Cannot overwrite already existing directory: \n {dir} \nSkip this Directory and Continue?"):
                    return False 
                
                else: 
                    # exit 
                    print(f"Exiting...")
                    
                    os._exit(1)  # Forcefully exit the application
                    
                raise IOError(f"Cannot overwrite already existing directory: \n {dir}")
    
    def send_file_to_remote(self, localpath: str, remotepath: str, ignore_existing:bool=False):
        is_already_existing: bool = False
        try: 
            self.sftpInstance.client_session.stat(remotepath)
            is_already_existing: bool = True 
        except IOError:
            pass 

        if is_already_existing:
            if ignore_existing is False:
                    if messagebox.askyesno("", f"Cannot overwrite already existing file: \n {remotepath}. \nSkip this Directory and Continue?"):
                        return False 
                    else: 
                        os._exit(1)  # Forcefully exit the application
                    
            

        self.sftpInstance.client_session.put(localpath=localpath,
                                             remotepath=remotepath)
        
    def is_remote_dir(self, remotepath:str) -> bool:
        
        try:
            self.sftpInstance.client_session.chdir(remotepath)
            return True
        
        except paramiko.sftp.SFTPError:
            return False 

    def exists_on_remote(self, remotepath:str) -> bool:

        try: 
            self.sftpInstance.client_session.stat(remotepath)
        except paramiko.sftp.SFTPError:
            if messagebox.askyesno("", f"Remote File to Transfer Does not Exist on Remote: \n {remotepath}. \nSkip File and Continue?"): 
                return False 
            else:
                os._exit(1)

        return True 
            
    def copy_file_to_local(self, remotepath: str, localpath: str, ignore_existing:bool=False) -> bool:
        if os.path.exists(localpath):
            if ignore_existing is False:
                if messagebox.askyesno("", f"Local Path: {localpath} Already Exists Locally. \nSkip File and Continue?"):
                    return False 
                else: 
                    self.progress_callback(action="done")
                    os._exit(1)
            
        self.sftpInstance.client_session.get(remotepath=remotepath, localpath=localpath)