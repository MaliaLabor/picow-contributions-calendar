# picow-contributions-calendar
This is a Micropython project for Raspberry Pi Pico W to get contributions and display values on Neopixel LEDs like the contributions calendar on user GitHub profile pages

# Setup
### Setup Pico W and IDE
The easiest way to get started with the Pico W is to follow this guide on the Raspberry Pi website to [install Thonny](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2) and [add the MicroPython Firmware](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/3).

### Edit `secrets.py` 
- Change `ssid` and `pw` to match your Wi-fi credentials
- Change `username` to match the Git username you want data for.
- Neopixel configurations:
  - `color_rgb` = (red, green, blue) values of color to show
  - `pixels_width` = width of neopixel array (32 pixels wide for my example)
  - `pixels_height` = height of neopixel array (8 pixels tall for my example)
  - `leds_pin` = pin number that neopixel data is connected to
- Additional configurations:
  - `max_contributions_number` = number that will show max LED brightness
  - `refresh_time_hours` = frequency to refresh data from GitHub
  - `brightness` = optional brightness modifier

### Upload code to Pico W
Save `main.py` and edited `secrets.py` to Pico W.
