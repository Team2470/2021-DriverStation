# 2021 Driver Station

This Driver Station is currently under construction.

## Supported Platforms
* macOS Catalina
    * Logitech USB Gamepad

Support for additional platforms will be coming at a later time.

## Supported Robot platforms
* Arduino Uno with USB Serial

Support for Bluetooth (or other wireless communication coming later).

## Running
### Install deps
```
~/Documents/Arduino/DriverStation]$ python3 -m venv venv
[~/Documents/Arduino/DriverStation]$ pip3                                                   
[~/Documents/Arduino/DriverStation]$ . ./venv/bin/activate                                  
(venv) [~/Documents/Arduino/DriverStation]$
```

```
pip install -r requirements.txt
```

### Configuration
__TODO__ Adjust `config.yaml` to your robot and system.

### Run the driver station
__TODO__ Currently only `ds_serial.py` is functional.