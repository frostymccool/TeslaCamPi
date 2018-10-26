#!/usr/bin/python3

# original source from aritcle : https://www.raspberrypi.org/magpi/pi-zero-w-smart-usb-flash-drive/
# original source : sudo wget http://rpf.io/usbzw -O usb_share.py

# to add: 
#    monitor for music folder
#    periodic remount and monitor for no change from writing from Tesla side, then fsck
#      gotta decide on the ro/rw handler for the TeslaCam folder ... 
#      i.e. monitor for TeslaCam to stop writing, fsck, change to ro, move saved files off, change back to rw 

import time
import os
from watchdog.observers import Observer
from watchdog.events import *

CMD_MOUNT = "modprobe g_mass_storage file=/piTeslaCam.bin,/piTeslaMusic.bin stall=0,0, ro=0,0 removable=1,1"
CMD_UNMOUNT = "modprobe -r g_mass_storage"
CMD_SYNC = "sync"
# make sure fsck the filesystem (tesla bug causing corruption sometimes)
CMD_FSCK = "fsck -a /mnt/usb_share"

WATCH_PATH = "/mnt/usb_share"
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

# check filesystem before presenting the gadget as currently Tesla s/w corrupts fs periodically on shutdown
os.system(CMD_FSCK)
os.system(CMD_MOUNT)

evh = DirtyHandler()
observer = Observer()
observer.schedule(evh, path=WATCH_PATH, recursive=True)
observer.start()

try:
    while True:
        while evh.dirty:
            time_out = time.time() - evh.dirty_time

            if time_out >= ACT_TIME_OUT:
                os.system(CMD_UNMOUNT)
                time.sleep(1)
                os.system(CMD_SYNC)
                time.sleep(1)
                os.system(CMD_FSCK)
                time.sleep(1)
                os.system(CMD_MOUNT)
                evh.reset()

            time.sleep(1)

        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()

