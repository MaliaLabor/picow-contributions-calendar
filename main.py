from secrets import secrets
from machine import Pin
import network
import time
import utime
import urequests as requests
import neopixel

# Get secrets from file
ssid = secrets['ssid']
pw = secrets['pw']
username = secrets['username']
color = secrets['color_rgb']
max_contributions_number = secrets['max_contributions_number']
refresh_time_in_seconds = secrets['refresh_time_hours'] * 3600
brightness = secrets['brightness']

# Date variables
days_to_show = secrets['pixels_width'] * secrets['pixels_height']
seconds_in_day = 86400
next_refresh_time_seconds = time.time()

# Setup neopixel matrix
pixel_pin = secrets['leds_pin']
pixel_width = secrets['pixels_width']
pixel_height = secrets['pixels_height']

# LED breathing variables
day_numbers = []
breathing_modifiers = [0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
breathing_head_index = 0

pixels = neopixel.NeoPixel(
    machine.Pin(pixel_pin),
    pixel_width * pixel_height
)

############# Functions #############
def get_color_values(number):
    ratio = number / max_contributions_number
    if (ratio > 1.0):
        ratio = 1.0
    # apply brightness value
    ratio = ratio * brightness
    red = round(color[0] * ratio)
    green = round(color[1] * ratio)
    blue = round(color[2] * ratio)
    return (red, green, blue)

def modify_colors(scaled_color, modifier):
    red = round(scaled_color[0] * modifier)
    green = round(scaled_color[1] * modifier)
    blue = round(scaled_color[2] * modifier)
    return (red, green, blue)

def fill_pixels(pixels, color):
    for x in range(len(pixels)):
        set_color(pixels, x, color)
    pixels.write()

def set_color(pixels, index, color):
    pixels[index] = (color[0], color[1], color[2])
    
def get_year_data(year):
    nums_list = [0]
    url = "https://skyline.github.com/{}/{}.json".format(username, year)
    response = requests.get(url).json()
    weeks_list = response["contributions"]
    for week_data in weeks_list:
        for day in week_data['days']:
            nums_list.append(day['count'])
    return nums_list
    
############# Connect to Wi-fi #############
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, pw)

onboard_led = Pin("LED", Pin.OUT)

while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    onboard_led.on()
    time.sleep(0.5)
    onboard_led.off()
    time.sleep(0.5)

print("Wi-fi connected!")
onboard_led.on()

############# Main Program #############
fill_pixels(pixels, (0,0,0))
while True:
    current_time = time.time()
    if (current_time >= next_refresh_time_seconds):
        print("Getting data...")
        next_refresh_time_seconds = time.time() + refresh_time_in_seconds
        start_date_secs = current_time - (days_to_show * seconds_in_day)
        end_date = time.gmtime(current_time)
        start_date = time.gmtime(start_date_secs)
        nums_list = []
        # index 7 in tuples is days into the year
        end_index = end_date[7] + 1 
        start_index = start_date[7] + 1
        
        # Get previous year's data if range spans 2 years
        if (start_date[0] < end_date[0]):
            nums_list = nums_list + get_year_data(start_date[0])
            end_index += len(nums_list)
            start_index += 1
        # Get current year data
        time.sleep(2)
        nums_list = nums_list + get_year_data(end_date[0])
        day_numbers = nums_list[start_index:end_index]
        
        for x in range(len(day_numbers)):
            if (x < len(pixels)):
                scaled_color = get_color_values(day_numbers[x])
                set_color(pixels, x, scaled_color)
    else:
        if (breathing_head_index >= 0 and breathing_head_index - len(breathing_modifiers) < days_to_show):
            for x in range(len(breathing_modifiers)):
                current_index = breathing_head_index - x
                if (current_index >= 0 and current_index < len(day_numbers)):
                    scaled_color = get_color_values(day_numbers[current_index])
                    modified_color = modify_colors(scaled_color, breathing_modifiers[x])
                    set_color(pixels, current_index, modified_color)
            breathing_head_index += 1
        elif (breathing_head_index > days_to_show):
            breathing_head_index = 0
    pixels.write()
    utime.sleep_ms(150)
    