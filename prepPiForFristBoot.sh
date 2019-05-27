#/bin/bash -eu
# prepPiForFristBoot.sh

# .... WIP ....

# This script will modify the cmdline.txt file on a freshly flashed Raspbian Stretch/Lite
# It readies it for SSH, USB OTG, USB networking, and Wifi

# massaged from https://github.com/cimryan/teslausb/blob/master/setup/macos_linux/setup-piForHeadlessConfig.sh

# Pass it the path to the location at which the "boot" filesystem is mounted.
# E.g. on a Mac:
#   ./setup-piForHeadlessConfig.sh /Volumes/boot
# or on Ubuntu:
#   ./setup-piForHeadlessConfig.sh /media/$USER/boot
# cd /Volumes/boot (or wherever the boot folder is mounted)
# chmod +x setup-piForHeadlessConfig.sh
# ./setup-piForHeadlessConfig.sh
#
# Put the card in your Pi, and reboot!

# Creates the ssh file if needed, since Raspbian now disables 
# ssh by default if the file isn't present

# if 2nd param exist, then decode as to what pi it will be and setup network appropriately
# teslapi, teslacampi, teslafrunkpi

# 2nd param will also be used to update the hostname

SSH_PUBLIC_NODE_KEY="id_teslapi.pub"
SSH_PRIVATE_NODE_KEY="id_teslapi"
WPA_SUPPLICANT_ALL="wpa_supplicant_all.conf"
WPA_SUPPLICANT_NODE="wpa_supplicant_node.conf"

BOOT_DIR="$1"

function verify_file_exists () {
  local file_name="$1"
  local expected_path="$2"
  
  if [ ! -e "$expected_path/$file_name" ]
    then
      echo "STOP: Didn't find $file_name at $expected_path."
      exit 1
  fi  
}

verify_file_exists "cmdline.txt" "$BOOT_DIR"
verify_file_exists "config.txt" "$BOOT_DIR"

CMDLINE_TXT_PATH="$BOOT_DIR/cmdline.txt"
CONFIG_TXT_PATH="$BOOT_DIR/config.txt"

if ! grep -q "dtoverlay=dwc2" $CONFIG_TXT_PATH
then
   echo "Updating $CONFIG_TXT_PATH ..."
   echo "" >> "$CONFIG_TXT_PATH"
   echo "dtoverlay=dwc2" >> "$CONFIG_TXT_PATH"
else
   echo "$CONFIG_TXT_PATH already contains the required dwc2 module"
fi

if ! grep -q "dwc2,g_ether" $CMDLINE_TXT_PATH
then
  echo "Updating $CMDLINE_TXT_PATH ..."
  sed -i'.bak' -e "s/rootwait/rootwait modules-load=dwc2,g_ether/" -e "s@ init=/usr/lib/raspi-config/init_resize.sh@@" "$CMDLINE_TXT_PATH"
else
  echo "$CMDLINE_TXT_PATH already updated with modules and removed initial resize script."
fi

echo "Enabling SSH ..."
touch "$BOOT_DIR/ssh"

SSH_KEY_PATH="$BOOT_DIR/sshkey"
mkdir $SSH_KEY_PATH

if [ -n "${2}" ]
then
    # inform hostname
    echo "Setting config file with hostname"
    echo $3 > "$BOOT_DIR/myconfig"
fi

# Sets up wifi credentials so wifi will be 
# auto configured on first boot
WPA_SUPPLICANT_CONF_PATH="$BOOT_DIR/wpa_supplicant.conf"

echo "Adding Wifi setup file (wpa_supplicant.conf)."

if [ -r "$WPA_SUPPLICANT_CONF_PATH" ]
then
  rm "$WPA_SUPPLICANT_CONF_PATH"
fi

# different Pi's need different network .. the hub needs all, but the nodes just talk to the hub so are more restrictive
case $2 in
    "teslacampi"|"teslafrunkpi")
    cp $WPA_SUPPLICANT_NODE $WPA_SUPPLICANT_CONF_PATH
    #copy the ssh public key to connect to the hub
    cp SSH_PUBLIC_NODE_KEY $SSH_KEY_PATH

    ;;

    "teslapi")    
    cp $WPA_SUPPLICANT_ALL $WPA_SUPPLICANT_CONF_PATH
    #copy the ssh PRIVATE key for nodes to connect to hub
    cp SSH_PRIVATE_NODE_KEY $SSH_KEY_PATH
    ;;
esac

echo ""
echo '-- Files updated and ready for Wifi and SSH over USB --'
echo ""
