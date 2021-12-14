# denfilm-pi-thermal-cam
# 1
# Terminal:
sudo nano /boot/config.txt

# Edit
dtparam=i2c_arm=on,i2c_arm_baudrate=400000

# Reboot
sudo reboot

# Check
sudo i2cdetect -y 1

# 2
sudo apt-get install libatlas-base-dev python-smbus i2c-tools
pip3 install pithermalcam
sudo pip3 install -U numpy

# 3 Check if this python script works
import pithermalcam as ptc
ptc.display_camera_live()

# 3
cd /home/pi/Desktop
git clone https://github.com/romantsiupa/denfilm-pi-thermal-cam.git

# 4
cd /home/pi/Desktop/denfilm-pi-thermal-cam
python3 denfilm_pi_thermal_cam.py
