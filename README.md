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
https://github.com/frostymccool/teslausb/master/setup/pi

boot into pi

curl --fail -o "/tmp/createfs.sh" "https://raw.githubusercontent.com/frostymccool/TeslaCamPi/master/createfs.sh"
chmod +x /tmp/createfs/sh
sudo /tmp/createfs.sh

# Filesystem created and ready to reboot to mount ota
sudo reboot

# ---- WIP....

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


