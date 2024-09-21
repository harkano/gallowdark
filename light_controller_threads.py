import json
import time
import logging
import random
import math
import os
import threading
import subprocess
from rpi_ws281x import PixelStrip, Color
from led_utils import init_strip, clear_leds, LED_COUNT_A, LED_PIN_A, LED_CHANNEL_A, LED_COUNT_B, LED_PIN_B, LED_CHANNEL_B, load_led_mapping, get_leds_for_tile

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_light_config():
    #logging.info("Loading light configuration.")
    with open('light_config.json', 'r') as file:
        return json.load(file)

def get_base_color(ambient_mode):
    # Example function to get base color based on ambient mode
    if ambient_mode == 2: #Gallowdark
        color = (255, 68, 0)  # Dark Orange
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Dark Orange")
    elif ambient_mode == 3: #Gallowdeep
        color = (10, 176, 176)  # Blue
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Blue")
    elif ambient_mode == 4: #Gallowhive
        color = (48, 25, 52)  # Purple
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Dark Purple")
    elif ambient_mode == 5: # Gallowtomb
        color = (1, 80, 32)  # Dark Green
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Dark Green")
    else:
        color = (255, 255, 255)  # Default white
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Default White")
    return color

# Function to run startup_pattern.py as a subprocess
def start_demo_pattern():
    logging.info("Starting demo pattern")
    result = subprocess.run((["sudo", "python3", "startup_pattern.py"]), check=True)
    logging.info(f"Demo pattern finished with exit code {result.returncode}")
    

def apply_dynamic_ambient(strip, base_color, tile_mapping, stop_event, overrides, brightness):
    tiles = list(tile_mapping.keys())
    phases = {tile: random.random() * 2 * math.pi for tile in tiles}  # Random phase for each tile

    cycle_duration = 5  # Duration of one full cycle in seconds
    steps_per_cycle = 100  # Number of steps in one full cycle

    override_tiles = {tile for tiles in overrides.values() for tile in tiles}

    while not stop_event.is_set():  # Run the dynamic effect continuously
        for step in range(steps_per_cycle):
            if stop_event.is_set():
                break
            brightness_factor = (1 + math.sin(2 * math.pi * step / steps_per_cycle)) / 2  # Sinusoidal factor between 0 and 1
            for tile in tiles:
                if tile in override_tiles:
                    continue  # Skip tiles that have overrides
                leds = tile_mapping[tile]
                phase = phases[tile]
                brightness_factor = (1 + math.sin(2 * math.pi * step / steps_per_cycle + phase)) / 2  # Sinusoidal factor between 0 and 1
                # Adjust the base color based on the brightness factor and global brightness
                r = int(base_color[0] * brightness_factor * brightness / 255)
                g = int(base_color[1] * brightness_factor * brightness / 255)
                b = int(base_color[2] * brightness_factor * brightness / 255)
                for led in leds:
                    strip.setPixelColor(led - 1, Color(r, g, b))
            strip.show()
            time.sleep(cycle_duration / steps_per_cycle)  # Adjust the speed of the glow effect

        # Apply tile overrides continuously
        apply_tile_overrides(overrides, brightness)
        strip.show()

def apply_tile_overrides(overrides, brightness):
    for color, tiles in overrides.items():
        for tile in tiles:
            if tile in tile_to_leds_a:
                leds = get_leds_for_tile(tile, 'a')
                if color == "off":
                    color_value = Color(0, 0, 0)  # Turn off the LEDs
                else:
                    color_value = color_map.get(color, Color(0, 0, 0))
                # Apply brightness to the color
                r = int(color_value.r * brightness / 255)
                g = int(color_value.g * brightness / 255)
                b = int(color_value.b * brightness / 255)
                for led in leds:
                    strip_a.setPixelColor(led - 1, Color(r, g, b))
            elif tile in tile_to_leds_b:
                leds = get_leds_for_tile(tile, 'b')
                if color == "off":
                    color_value = Color(0, 0, 0)  # Turn off the LEDs
                else:
                    color_value = color_map.get(color, Color(0, 0, 0))
                # Apply brightness to the color
                r = int(color_value.r * brightness / 255)
                g = int(color_value.g * brightness / 255)
                b = int(color_value.b * brightness / 255)
                for led in leds:
                    strip_b.setPixelColor(led - 1, Color(r, g, b))
    strip_a.show()
    if strip_b is not None:
        strip_b.show()

# Define the color map for overrides
color_map = {
    'red': Color(255, 0, 0),
    'blue': Color(0, 0, 255),
    'green': Color(0, 255, 0),
    'yellow': Color(255, 255, 0),
    'off': Color(0, 0, 0)
}

# Load LED mappings
tile_to_leds_a = load_led_mapping('config/board_a_leds.txt')
tile_to_leds_b = load_led_mapping('config/board_b_leds.txt')

# Initialize the LED strips
strip_a = init_strip(LED_PIN_A, LED_COUNT_A, LED_CHANNEL_A)
strip_b = init_strip(LED_PIN_B, LED_COUNT_B, LED_CHANNEL_B)

# Check initialization
if strip_a is None:
    logging.error(f"Error initializing LED strip on pin {LED_PIN_A}")
else:
    logging.info(f"Successfully initialized LED strip on pin {LED_PIN_A}")

if strip_b is None:
    logging.error(f"Error initializing LED strip on pin {LED_PIN_B}")
else:
    logging.info(f"Successfully initialized LED strip on pin {LED_PIN_B}")

current_config = load_light_config()  # Load the initial configuration
brightness = current_config.get('brightness', 255)  # Default to 255 if brightness isn't specified
stop_event = threading.Event()

# Start subprocess
start_demo_pattern()

# Apply initial configuration
if strip_a is not None:
    thread_a = threading.Thread(target=apply_dynamic_ambient, args=(strip_a, get_base_color(current_config['ambient_mode']), tile_to_leds_a, stop_event, current_config.get('overrides', {}), brightness))
    thread_a.start()
if strip_b is not None:
    thread_b = threading.Thread(target=apply_dynamic_ambient, args=(strip_b, get_base_color(current_config['ambient_mode']), tile_to_leds_b, stop_event, current_config.get('overrides', {}), brightness))
    thread_b.start()

# Apply tile overrides initially
if 'overrides' in current_config:
    apply_tile_overrides(current_config['overrides'], brightness)

def light_controller():
    global current_config, thread_a, thread_b, brightness
    while not stop_event.is_set():
        config = load_light_config()
        if config != current_config:
            logging.info("Configuration changed.")
            stop_event.set()
            time.sleep(1)  # Give threads time to stop
            stop_event.clear()
            current_config = config
            brightness = current_config.get('brightness', 255)  # Update brightness

            # Start new threads for dynamic ambient
            if strip_a is not None:
                thread_a = threading.Thread(target=apply_dynamic_ambient, args=(strip_a, get_base_color(current_config['ambient_mode']), tile_to_leds_a, stop_event, current_config.get('overrides', {}), brightness))
                thread_a.start()
            if strip_b is not None:
                thread_b = threading.Thread(target=apply_dynamic_ambient, args=(strip_b, get_base_color(current_config['ambient_mode']), tile_to_leds_b, stop_event, current_config.get('overrides', {}), brightness))
                thread_b.start()

            # Apply tile overrides
            if 'overrides' in current_config:
                apply_tile_overrides(current_config['overrides'], brightness)

        time.sleep(1)

# Start the light controller in the main thread
light_controller()
