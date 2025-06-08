import os
import re
import socket
import stat
from typing import List, Tuple
import paramiko
from tkinter import messagebox

import settings 
import getUserConfigs

class Sftp:
    def __init__(self, 
                 remote_home_directory: str = getUserConfigs.config['remote_home_dir'], 
                 local_home_directory: str = getUserConfigs.config['local_home_dir'],
                 host: str = getUserConfigs.config['host']):
        self.client = None
        self.client_session = None
        self.current_files: list[str] = []
        self.remote_home_directory = remote_home_directory
        self.local_home_directory = local_home_directory
        self.host = host
        
    def login(self, username: str = None, password: str = None) -> bool: 

        self.client: paramiko.SSHClient = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        socket.setdefaulttimeout(5)

        try: 
            # connect to remote
            if getUserConfigs.config['private_key_path'] and getUserConfigs.config['username']:

                self.client.connect(self.host, username=getUserConfigs.config['username'], key_filename=getUserConfigs.config['private_key_path'])

            elif password: 

                self.client.connect(self.host, username=username, password=password)

            else:
                raise ValueError("To authenticate, you must provide a username plus either a password or private key path")
        
        except socket.timeout: 
            messagebox.showerror(title="Could Not Connect", message="Could not connect - please check your connection to the correct network and your user settings")
            return False
        
        except socket.gaierror as e:
            messagebox.showerror(title="Could Not Connect", message="Could not connect - please check your connection to the correct network and your user settings")
            return False
        
        except paramiko.ssh_exception.AuthenticationException as e:
            messagebox.showerror("", f"Authentication failed. Please check your username, hostname and {'private key path' if getUserConfigs.config['private_key_path'] else 'password'} in your user settings.")
            return False
        
        except ValueError as e:
            messagebox.showerror("", f"Authentication failed. Please check your username, hostname and {'private key path' if getUserConfigs.config['private_key_path'] else 'password'} in your user settings.")

        except Exception as e:
            messagebox.showerror("", f"Authentication failed. Please check your username,  hostname and {'private key path' if getUserConfigs.config['private_key_path'] else 'password'} in your user settings.")
        # open sftp connection
        self.client_session = self.client.open_sftp()

        return True
    

    def get_remote_home_dir(self) -> str:

        if self.remote_home_directory.strip() == "" or not self.remote_home_directory:

            if not self.client:
                raise ConnectionError("SSH client is not connected.")

            try:
                stdin, stdout, stderr = self.client.exec_command("echo $HOME")

                home_dir = stdout.read().decode().strip()
                if stderr.read().decode().strip():
                    raise RuntimeError("Failed to retrieve remote home directory.")
                return os.path.normpath(home_dir)
            
            except Exception as e:
                messagebox.showerror("", "We could not automatically find your remote home directory. Please check your user settings and add a remote directory manually.")
                return ""
        else:
            return os.path.normpath(self.remote_home_directory)
    
    def get_local_home_dir(self) -> str: 
        if not self.local_home_directory or self.local_home_directory.strip() == "":
            new_home_dir: str = os.getenv('HOME')
            if not new_home_dir or not os.path.exists(new_home_dir.strip()):
                messagebox.showerror("", "We could not automatically find your local home directory. Please check your user settings and add a home directory manually.")
                raise FileNotFoundError("We could not automatically find your local home directory. Please check your user settings and add a home directory manually.")
            else:
                return new_home_dir
        else:
            return os.path.normpath(self.local_home_directory)
    
    def list_remote_elements(self, directory: str, sort_by: str = None, file_batch: int = 0, show_hidden: bool = False) -> List[Tuple[str,bool]]:
        
        # iterate through elements and add to list_to_return
        list_to_return: List[Tuple[str,bool]] = []

        try: 
            self.client_session.chdir(directory)
        except IOError:
            if directory == self.remote_home_directory:
                messagebox.showerror("", f"The configured remote home directory ({directory}) does not exist on remote. \nPlease change your remote home directory in settings.")
            else:
                messagebox.showerror("", f"The Directory: {directory} does not exist")
            raise FileNotFoundError(f"The Directory: {directory} does not exist")
        
        # get list of files if not gotten already
        if file_batch == 0:
            
            self.current_files = [os.path.join(directory, filename) for filename in self.client_session.listdir(directory) if show_hidden or not show_hidden and filename[0] != '.']
            
            if sort_by == 'Alphabetic':
                # sort by the filename extracted from the filepath (ignore non-alphanumeric characters)
                self.current_files = sorted(self.current_files, key=lambda x: re.sub(r'[^a-zA-Z0-9]', '', x.split('/')[-1]).lower())
            elif sort_by == 'MostRecentModified':
                self.current_files = sorted(self.current_files, key=lambda x: self.client_session.stat(x).st_mtime, reverse=True)    
        # get file batch
        more_batches_to_show: bool = False
        file_batch_nums: bool = False 
        if len(self.current_files) > settings.max_files_to_show:
            file_batch_nums: tuple[int, int] = (settings.max_files_to_show * file_batch, (settings.max_files_to_show * file_batch) + settings.max_files_to_show)
            if len(self.current_files) > file_batch_nums[1]:
                more_batches_to_show = True
        for path in self.current_files if not file_batch_nums else self.current_files[file_batch_nums[0]:file_batch_nums[1]]:
            try: 
                # filter out filepaths (speed up process)
                if os.path.splitext(path)[1] in ['.png', '.txt', '.dcm', '.gz', '.nii', '.py', '.sh', '.java', '.class']:
                    list_to_return.append((path, False))
                else:
                    list_to_return.append((path, stat.S_ISDIR(self.client_session.stat(path).st_mode)))
            except IOError: 
                print(f"WARNING: Error when getting info on file: {path}. \nIt will not be added to the GUI")
        
        return list_to_return, more_batches_to_show

    def list_local_elements(self, directory: str, sort_by: str = None, file_batch: int = 0, show_hidden: bool = False) -> List[Tuple[str,bool]]:
        # iterate through elements 
        list_to_return: list[tuple[str,bool]] = []

        # get list of files
        if file_batch == 0:
            try: 
                self.current_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if show_hidden or not show_hidden and filename[0] != '.']
            except PermissionError:
                messagebox.showerror("", "Permission Error Accessing this Material")
            if sort_by == 'Alphabetic':
                # Sort by the filename extracted from the filepath (ignore non-alphanumeric characters)
                self.current_files = sorted(self.current_files, key=lambda x: re.sub(r'[^a-zA-Z0-9]', '', x.split('/')[-1]).lower())
            elif sort_by == 'MostRecentModified':
                self.current_files = sorted(self.current_files, key=lambda x: os.path.getmtime(x), reverse=True)
            
        # get file batch
        more_batches_to_show: bool = False
        file_batch_nums = False
        if len(self.current_files) > settings.max_files_to_show:
            file_batch_nums: tuple[int, int] = (settings.max_files_to_show * file_batch, (settings.max_files_to_show * file_batch) + settings.max_files_to_show)
            if len(self.current_files) > file_batch_nums[1]:
                more_batches_to_show = True

        try: 
            for path in self.current_files if not file_batch_nums else self.current_files[file_batch_nums[0]:file_batch_nums[1]]:
                if os.path.isdir(path):
                    list_to_return.append((path, True)) # return tuple containing path and bool value for wether or not they are a dir 
                else:
                    list_to_return.append((path, False))
       
        except PermissionError:
            messagebox.showerror("", f"Permission Error: Operation not permitted.")
            return False 

        return list_to_return, more_batches_to_show

    def list_elements(self, filesystem: str, directory: str, sort_by: str = None, file_batch: int = 0, show_hidden: bool = True) -> Tuple[List[Tuple[str,bool]], bool]:
        
        if filesystem == "local":
            local_elements, is_concatenated_list = self.list_local_elements(directory=directory, 
                                                                            sort_by=sort_by, 
                                                                            file_batch=file_batch, 
                                                                            show_hidden=show_hidden)
            if local_elements is False: 
                return False 
            else: 
                return local_elements, is_concatenated_list

                
        elif filesystem == "remote":
            return self.list_remote_elements(directory=directory, sort_by=sort_by, file_batch=file_batch, show_hidden=show_hidden)
    
    def close_session(self):
        print(f"Closing SFTP Session...")
        if self.client_session: 
            self.client_session.close()
            print(f"Closed SFTP Session Sucessfully.")
        else:
            print(f"No SFTP Session to Close")
