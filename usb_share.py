#!/usr/bin/python3

# original source from aritcle : https://www.raspberrypi.org/magpi/pi-zero-w-smart-usb-flash-drive/
# original source : sudo wget http://rpf.io/usbzw -O usb_share.py

# assumes the usb cam filesystem is mounted
# runs an fsck before mounting the gadget
# sets up a handler to monitor the for changed on the usb ota filesystem
# after a duration of x following the the first filesystem update, the filesystem is unmounted / cleaned / 
#  resynced and remounted
# that updates the local filesystem cache which will then allow follow on code to check for changes...

# to add: 
#   only run the unmount sequence if there is wifi present that we can use, otherwise no need to sync cache
#   monitor for the changes... if changed and wifi present, then continue with the unmount to run the upload cloud function

import time
import os
from watchdog.observers import Observer
from watchdog.events import *

USB_CAM_SHARE_MOUNT_POINT = "/mnt/cam"
CMD_MOUNT_GADGET = "modprobe g_mass_storage" # specifics moved into config file during create "file=/piTeslaCam.bin,/piTeslaMusic.bin stall=0,0, ro=0,0 removable=1,1"
CMD_UNMOUNT_GADGET = "modprobe -r g_mass_storage"
CMD_SYNC = "sync"
# make sure fsck the filesystem (although Tesla fixed bug, with power drops a non-clean unmount will often occur)
CMD_FSCK = "fsck -a $USB_CAM_SHARE_MOUNT_POINT"

WATCH_PATH = $USB_CAM_SHARE_MOUNT_POINT
ACT_EVENTS = [DirDeletedEvent, DirMovedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent]
ACT_TIME_OUT = 30

class DirtyHandler(FileSystemEventHandler):
    def __init__(self):
        self.reset()

    def on_any_event(self, event):
        if type(event) in ACT_EVENTS:
            self._dirty = True
            self._dirty_time = time.time()

    @property
    def dirty(self):
        return self._dirty

    @property
    def dirty_time(self):
        return self._dirty_time

    def reset(self):
        self._dirty = False
        self._dirty_time = 0
        self._path = None

# check filesystem before presenting the gadget
os.system(CMD_FSCK)
os.system(CMD_MOUNT_GADGET)

evh = DirtyHandler()
observer = Observer()
observer.schedule(evh, path=WATCH_PATH, recursive=True)
observer.start()

try:
    while True:
        while evh.dirty:
            time_out = time.time() - evh.dirty_time

            if time_out >= ACT_TIME_OUT:
                os.system(CMD_UNMOUNT_GADGET)
                time.sleep(1)
                os.system(CMD_SYNC)
                time.sleep(1)
                os.system(CMD_FSCK)
                time.sleep(1)
                os.system(CMD_MOUNT_GADGET)
                evh.reset()

            time.sleep(1)

        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()

