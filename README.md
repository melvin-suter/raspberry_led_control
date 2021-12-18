# raspberry_led_control

This python script will allow you to control an array of LEDs to pulse or light up.
If you run it on a windows-machine, it won't try to load the libraries and just print out messages

```python
CONFIG = {
    "sets":( # Add multiple arrays, each array is a set of LEDs in the same color, the numbers represant the GPIO Pins
        (1,2),
        (3,4)
    ),
    "button_id": 10, # Which GPIO pin will the button to change mode be plugged in
    "interval": 6, # Interval for pulsing
    "loglevel": 4, # Log Level - Should be self explenatory
    "logFile": "blink.log", # Log File name/path
    "log2file": True, # if it should log to file
    "log2console": True # if it should log to console
}
```