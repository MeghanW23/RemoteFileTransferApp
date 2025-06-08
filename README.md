# Remote File Transfer App 
This application transfer files to and from remote servers via a graphical user interface. It was designed to make the transfer of files to and from Boston Children's Hospital's High Performance Computing Cluster, E3, easier for those without a firm handle on command line file transfer tools like `rsync`.

The application is written fully in python, using `tkinter` for graphics and `paramiko` for transfering files. 

Users can configure their own remote server information (username, private key path, hostname) in User Settings. Users can login using either their password or a private key. 
![login_private_key](assets/README_screenshots/Screenshot 2025-06-08 at 2.11.34 PM.png)
