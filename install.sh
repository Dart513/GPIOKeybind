cd $(readlink -f $(dirname "$0"))
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install build-essential python-dev python-smbus python-pip
sudo pip3 install virtualenv
virtualenv .GPIOBindEnv
. ./.GPIOBindEnv/bin/activate
pip3 install keyboard RPi.GPIO Adafruit-ADS1x15
