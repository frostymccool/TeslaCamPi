#!/usr/bin/python

# Auto uploader to dropbox
# Monitor TeslaCam, syncing up to dropbox
# Assumes to be run as a cronjob (every 5 mins)
# */5 * * * * /home/pi/dropbox-sync.py

# original reference source: https://www.raspberrypi.org/forums/viewtopic.php?t=164166
# requires: https://github.com/andreafabrizi/Dropbox-Uploader

#TODO: add wifi online checker before running check and upload section

import time
import os
import subprocess
from subprocess import Popen, PIPE

#The directory to sync
syncdir="/mnt/cam/TeslaCam"
#Path to the Dropbox-uploaded shell script
uploader = "/home/pi/dropbox_uploader.sh"

#If 1 then files will be uploaded. Set to 0 for testing
upload = 1
#If 1 then don't check to see if the file already exists just upload it, if 0 don't upload if already exists
overwrite = 0
#If 1 then crawl sub directories for files to upload
recursive = 1
#Delete local file on successfull upload
deleteLocal = 1
#complete list of filesCopied that are pending deletion (if deleteLocal is set)
filesCopied = list()

USB_CAM_SHARE_MOUNT_POINT = "/mnt/cam"
CMD_MOUNT_LOCAL = "mount "+USB_CAM_SHARE_MOUNT_POINT
CMD_UNMOUNT_LOCAL = "umount "+USB_CAM_SHARE_MOUNT_POINT
CMD_MOUNT_GADGET = "modprobe g_mass_storage" 
CMD_UNMOUNT_GADGET = "modprobe -r g_mass_storage"
CMD_SYNC = "sync"
CMD_FSCK = "fsck -a "+USB_CAM_SHARE_MOUNT_POINT # make sure fsck the filesystem - just in case :)


#Prints indented output
def print_output(msg, level):
    print((" " * level * 2) + msg)


#Gets a list of files in a dropbox directory
def list_files(path):
    p = Popen([uploader, "list", path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output = p.communicate()[0].decode("utf-8")

    fileList = list()
    lines = output.splitlines()

    for line in lines:
        if line.startswith(" [F]"):
            line = line[5:]
            line = line[line.index(' ')+1:]
            fileList.append(line)
                   
    return fileList


#Uploads a single file
def upload_file(localPath, remotePath):
    p = Popen([uploader, "upload", localPath, remotePath], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output = p.communicate()[0].decode("utf-8").strip()
    if output.startswith("> Uploading") and output.endswith("DONE"):
        return 1
    else:
        return 0

    
#Uploads files in a directory
def upload_files(path, level):
    fullpath = os.path.join(syncdir,path)
    print_output("Syncing " + fullpath,level)
    if not os.path.exists(fullpath):
        print_output("Path not found: " + path, level)
    else:

        #Get a list of file/dir in the path
        filesAndDirs = os.listdir(fullpath)

        #Group files and directories
        
        files = list()
        dirs = list()

        for file in filesAndDirs:
            filepath = os.path.join(fullpath,file)
            if os.path.isfile(filepath):
                files.append(file)       
            if os.path.isdir(filepath):
                dirs.append(file)

        print_output(str(len(files)) + " Files, " + str(len(dirs)) + " Directories",level)

        #If the path contains files and we don't want to override get a list of files in dropbox
        if len(files) > 0 and overwrite == 0:
            dfiles = list_files(path)

        #Loop through the files to check to upload
        for f in files:                                 
            print_output("Found File: " + f,level)   
            if upload == 1 and (overwrite == 1 or not f in dfiles):
                fullFilePath = os.path.join(fullpath,f)
                relativeFilePath = os.path.join(path,f)  
                print_output("Uploading File: " + f,level+1)   
                if upload_file(fullFilePath, relativeFilePath) == 1:
                    print_output("Uploaded File: " + f,level + 1)
                    filesCopied.append(fullFilePath)
                    #if deleteLocal == 1:
                    #    print_output("Deleting File: " + f,level + 1)
                    #    os.remove(fullFilePath)                        
                else:
                    print_output("Error Uploading File: " + f,level + 1)
                    
        #If recursive loop through the directories   
        if recursive == 1:
            for d in dirs:
                print_output("Found Directory: " + d, level)
                relativePath = os.path.join(path,d)
                upload_files(relativePath, level + 1)
            

                  

                
#Start

#get fresh update from gadget i/o, mount cycle the local mount point
os.system(CMD_UNMOUNT_LOCAL)
os.system(CMD_MOUNT_LOCAL)

# upload the new files to dropbox
upload_files("",1)

# copy all the files first then delete separately... break up to slot in the unload/load gadget sequence for speed
# umount the gadget before any local file update, otherwise unpredictable results can occur!
if (deleteLocal == 1) & (len(filesCopied)>0):
    gadgetStopped=1
    try:
        os.system(CMD_UNMOUNT_GADGET)
        print("Gadget stopped")
    except:
        gadgetStopped=0

    time.sleep(1)
    try:
        os.system(CMD_SYNC)
        time.sleep(1)
        os.system(CMD_FSCK)  # fsck will kick out sometimes
    except:
        time.sleep(1)
    
    # If gadget not stopped successfully then no deletes (otherwise potential fs corruption)
    if gadgetStopped:
        # remove all the files to complete the 'move'
        for f in filesCopied:
            print("Deleting File: " + f)
            os.remove(f)

    # remount the gadget for continued updates from TeslaCam/Sentry
    # There appears to be some catchup caching going on, so need to wait before re-mounting the gadget
    os.system(CMD_SYNC)
    time.sleep(2)
    os.system(CMD_MOUNT_GADGET)
    print("Gadget started")
else:
    print("No files uploaded, no files to delete")

    
