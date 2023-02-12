from secrets import secrets
from machine import Pin
import network
import time
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

# Setup neopixel matrix
pixel_pin = secrets['leds_pin']
pixel_width = secrets['pixels_width']
pixel_height = secrets['pixels_height']

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
    start_date_secs = current_time - (days_to_show * seconds_in_day)
    end_date = time.gmtime(current_time)
    start_date = time.gmtime(start_date_secs)
    print("Getting data...")
    nums_list = []
    end_index = end_date[7] + 1
    start_index = start_date[7] + 1

    # Get previous year's data if range spans 2 years
    if (start_date[0] < end_date[0]):
        nums_list = nums_list + get_year_data(start_date[0])
        end_index += len(nums_list)
        start_index += 1
    # Get current year data
    nums_list = nums_list + get_year_data(end_date[0])
    day_numbers = nums_list[start_index:end_index]
    
    print("Writing pixels...")
    for x in range(len(day_numbers)):
        if (x < len(pixels)):
            scaled_color = get_color_values(day_numbers[x])
            set_color(pixels, x, scaled_color)
    pixels.write()
    time.sleep(refresh_time_in_seconds)
