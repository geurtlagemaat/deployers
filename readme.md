Prepares Linux OS to run Bliknet Apps

Updates OS;
Install req. libs;
Creates user and group;
Installs Python Circus Process manager in own VirtualEnv.

Download and run:
curl -O https://raw.githubusercontent.com/geurtlagemaat/deployers/master/bliknet_base_rpi_installer.sh && sudo chown pi:pi bliknet_base_rpi_installer.sh && bash bliknet_base_rpi_installer.sh

fab file contains specific Bliknet App install targets
