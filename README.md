# TeslaCamPi
# Use your Raspberry Pi Zero W as a TeslaCam USB drive and upload your snapshots to DropBox on the fly within wifi 

References:
https://www.raspberrypi.org/magpi/pi-zero-w-smart-usb-flash-drive/
https://www.raspberrypi.org/forums/viewtopic.php?t=164166
https://github.com/andreafabrizi/Dropbox-Uploader
https://github.com/cimryan/teslausb/


<<WIP>>

Create Fresh Raspian sd card

Setup cmdline.txt and config.txt adding otg params - no resize in cmdline by using (from mac cmdline)
./prepPiForFristBoot.sh teslapi

https://github.com/frostymccool/teslausb/tree/master/setup/pi

# Reuse the partition/fs creation code from cimryan
curl --fail -o "/tmp/create-backingfiles-partition.sh"  "https://raw.githubusercontent.com/frostymccool/teslausb/tree/master/setup/pi/create-backingfiles-partition.sh"
chmod +x /tmp/create-backingfiles-partition.sh
curl --fail -o "/tmp/create-backingfiles.sh"  "https://raw.githubusercontent.com/frostymccool/teslausb/tree/master/setup/pi/create-backingfiles.sh"
chmod +x /tmp/create-backingfiles.sh

# Create folder for the partition housing for teslacam and music (will be /dev/mmcblk0p3)
USBFS_PARTITION_MNT=/usbfs-partition
sudo mkdir "USBFS_PARTITION_MNT"
# Create folder for the partition housing active scripts (main partition will be ro for protection of filesystem, so script partition used for rw)  (will be /dev/mmcblk0p4)
SCRIPT_PARTITION_MNT=/script-partition
sudo mkdir /script-partition

# create the partitions and setup fstab for automount
sudo /tmp/create-backingfiles-partition.sh "$USBFS_PARTITION_MNT" "$SCRIPT_PARTITION_MNT"
sudo mount -a

# create the fat filesystem and folder for the cam, allocating 100% to it (cimryan also creates music folder).. 
sudo /tmp/create-backingfiles.sh "100" "$USBFS_PARTITION_MNT"

# ….. Now filesystem created

# …. TBD Need to mount on the ota ..

# ----

# Add auto dropbox sync
curl "https://raw.githubusercontent.com/andreafabrizi/Dropbox-Uploader/master/dropbox_uploader.sh" -o /home/pi/dropbox_uploader.sh
chmod +x /home/pi/dropbox_uploader.sh

# run uploader configuration
# uploader config needs a oauth token, which you get from https://www.dropbox.com/developers/apps
echo <add your oauth key here > dppw.txt
echo y >> dppw.txt
/home/pi/dropbox_uploader.sh < dppw.txt
rm dppw.txt

# grab the folder sync script
curl --fail -o "/home/pi/dropbox-sync.py"  "https://raw.githubusercontent.com/frostymccool/TeslaCamPi/master/dropbox-sync.py"
chmod +x /home/pi/dropbox-sync.py

# Setup cron to run the script every 5 minutes
crontab -e
*/5 * * * * /home/pi/dropbox-sync.py

TBD: May need to unmount / remount to cleanly access cam drive
If need to unmount, then lower the crontab checking to 30mins
To add: Remove files that successfully upload - leave testing for a while first
If remove files on upload, may need to remount drive anyway


