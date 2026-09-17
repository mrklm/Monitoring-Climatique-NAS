# Règle udev pour fixer le nom du port série de l'Arduino
# Crée un symlink /dev/arduino_nas vers le bon port /dev/ttyUSBx ou /dev/ttyACMx
#
#identifier votre Arduino pour ne garder que la bonne ligne:
# Sur le NAS, lancez -> lsusb | grep -i "arduino\|ch340\|1a86\|2341\|0403"
#
#
# Installation :
#   sudo cp nas/99-arduino-nas.rules /etc/udev/rules.d/
#   sudo udevadm control --reload-rules
#   sudo udevadm trigger

# Arduino Uno officiel (Vendor 2341 / Product 0043)
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", SYMLINK+="arduino_nas"

# Arduino Nano / clones CH340 (Vendor 1a86 / Product 7523)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="arduino_nas"

# Arduino Mega 2560 officiel (Vendor 2341 / Product 0042)
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0042", SYMLINK+="arduino_nas"

# FTDI FT232 (utilisé par certaines cartes compatibles)
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="arduino_nas"