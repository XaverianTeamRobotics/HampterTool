# Hampter Analysis Tool

Run `main.py` to use the tool.

To program a hampter, copy the `esp32_code.py`file to an ESP32-S2 or S3 Feather TFT or Reverse TFT.

Also, the following libraries are needed:
 - adafruit_bitmap_font
 - adafruit_bus_device
 - adafruit_display_text
 - adafruit_register
 - adafruit_lc709203f OR adafruit_max1704x (code bust be changed based on the battery monitor model)

Libraries can be downloaded from the [CircuitPython website](https://circuitpython.org/libraries)

The code is designed for CircuitPython 9.x