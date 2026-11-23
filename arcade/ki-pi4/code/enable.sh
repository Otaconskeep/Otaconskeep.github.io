# 1. copy the scripts to the Pi
scp power_switch.py gpio_volume.py pi@<your-pi>:/home/pi/

# 2. install the two service files
sudo cp power-switch.service gpio-volume.service /etc/systemd/system/

# 3. turn them on now and on every boot
sudo systemctl daemon-reload
sudo systemctl enable --now power-switch gpio-volume

# 4. check they're running
systemctl status power-switch gpio-volume --no-pager
