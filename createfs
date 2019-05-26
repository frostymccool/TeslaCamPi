#!/bin/bash -eu

# setup dedicated partition for sole use with TeslaCam

# references:
#    https://github.com/cimryan/teslausb


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

#create the partitions and setup fstab for automount
sudo /tmp/create-backingfiles-partition.sh "$USBFS_PARTITION_MNT" "$SCRIPT_PARTITION_MNT"
sudo mount -a

#create the fat filesystem and folder for the cam, allocating 100% to it (cimryan also creates music folder).. 
sudo /tmp/create-backingfiles.sh "100" "$USBFS_PARTITION_MNT"
