cd $(readlink -f $(dirname "$0"))
. ./.GPIOBindEnv/bin/activate
sudo ./.GPIOBindEnv/bin/python3 GPIOKeybind.py