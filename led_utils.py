from rpi_ws281x import *

# LED strip configuration
LED_COUNT_A = 271  # Total number of LEDs on board A
LED_PIN_A = 18  # GPIO pin for board A
LED_COUNT_B = 271  # Total number of LEDs on board B
LED_PIN_B = 13  # GPIO pin for board B
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 65  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL_A = 0  # Channel for board A
LED_CHANNEL_B = 1  # Channel for board B



def load_led_mapping(file_path):
    mapping = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            tile, leds = line.strip().split(':')
            start, end = map(int, leds.split('-'))
            mapping[tile.strip()] = list(range(start, end + 1))
    return mapping

# Initialize the LED strips
def init_strip(pin, count, channel):
    try:
        strip = Adafruit_NeoPixel(count, pin, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, channel)
        strip.begin()
        return strip
    except RuntimeError as e:
        print(f"Error initializing LED strip on pin {pin}: {e}")
        return None
		
# Function to clear LEDs on a specified strip
def clear_leds(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
	
# Function to get LEDs for a specific tile
def get_leds_for_tile(tile, board):
    if board == 'a':
        return tile_to_leds_a.get(tile, [])
    elif board == 'b':
        return tile_to_leds_b.get(tile, [])
    else:
        return []

# Load LED mappings
tile_to_leds_a = load_led_mapping('config/board_a_leds.txt')
tile_to_leds_b = load_led_mapping('config/board_b_leds.txt')
