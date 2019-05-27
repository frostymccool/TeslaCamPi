#!/bin/bash -eu

# setup dedicated partition for sole use with TeslaCam

# references:
#    https://github.com/cimryan/teslausb

RCL_PATH="/etc/rc.local"
RCAPP_NAME="rc.l.append"
RCAPP_PATH="/tmp/$RCAPP_NAME"
USBFS_PARTITION_MNT=/usbfs-partition
SCRIPT_PARTITION_MNT=/script-partition


# Reuse the partition/fs creation code from cimryan
curl --fail -o "/tmp/create-backingfiles-partition.sh"  "https://raw.githubusercontent.com/frostymccool/teslausb/tree/master/setup/pi/create-backingfiles-partition.sh"
chmod +x /tmp/create-backingfiles-partition.sh
curl --fail -o "/tmp/create-backingfiles.sh"  "https://raw.githubusercontent.com/frostymccool/teslausb/tree/master/setup/pi/create-backingfiles.sh"
chmod +x /tmp/create-backingfiles.sh

# Grab updates to rc.local
curl --fail -o "$RCAPP_PATH" "https://raw.githubusercontent.com/frostymccool/TeslaCamPi/tree/master/$RCAPP_NAME"
 

# Create folder for the partition housing for teslacam and music (will be /dev/mmcblk0p3)
mkdir "USBFS_PARTITION_MNT"
# Create folder for the partition housing active scripts (main partition will be ro for protection of filesystem, so script partition used for rw)  (will be /dev/mmcblk0p4)
mkdir /script-partition

#create the partitions and setup fstab for automount
/tmp/create-backingfiles-partition.sh "$USBFS_PARTITION_MNT" "$SCRIPT_PARTITION_MNT"
mount -a

#create the fat filesystem and folder for the cam, allocating 100% to it (cimryan also creates music folder).. 
/tmp/create-backingfiles.sh "100" "$USBFS_PARTITION_MNT"

#Update rc.local to mount the cam filesystem, fsck and then mount it clean to the usb gadget
if ! grep -q "needm" $RCL_PATH
then
  echo "updating $RCL_PATH"
  sed -i'.bak' -e "s/exit 0//" "$RCL_PATH"
  cat $RCAPP_PATH >> $RCL_PATH
else
  echo "$RCL_PATH already up to date"
fi
