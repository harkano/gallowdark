from rpi_ws281x import PixelStrip, Color
from led_utils import init_strip, clear_leds, LED_COUNT_A, LED_PIN_A, LED_CHANNEL_A, LED_COUNT_B, LED_PIN_B, LED_CHANNEL_B, load_led_mapping, get_leds_for_tile
from audio_controller import play_audio_once
import json
import time
import logging
import random
import math
import os


def load_light_config():
    #logging.info("Loading light configuration.")
    with open('light_config.json', 'r') as file:
        return json.load(file)

def get_base_color(ambient_mode):
    # Example function to get base color based on ambient mode
    logging.info(f"Received ambient_mode: {ambient_mode}")

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
        color = (1, 100, 32)  # Dark Green
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Dark Green")
    elif ambient_mode == 6: # Gallowforge
        color = (219, 208, 55)  # Yellow
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Yellow")
    elif ambient_mode == 7: # Gallowstone
        color = (55, 66, 59)  # Off Black
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Off Black")
    elif ambient_mode == 8: # Gallowstorm
        color = (162, 236, 245)  # Bright Blue
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Bright blue")
    elif ambient_mode == 9: # Gallowwar
        color = (255, 10, 10)  # Dark Red
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Dark Red")
    # Gallowstorm
    # Gallowhaunt
    # Gallowforge
    # Gallowprison
    # Gallowvoid
    # Gallowchaos
    # Gallowsiege
    # Gallowsanctum
    # Gallowplague
    #  Colorpicker mode
    else:
        color = (255, 255, 255)  # Default white
        logging.info(f"Ambient Mode {ambient_mode} - Base Color: Default White")
    return color

# Function to run startup_pattern.py as a subprocess
def start_demo_pattern():
    diagonal_demo(strip_a,  strip_b)    

def apply_dynamic_ambient(strip, base_color, tile_mapping, stop_event, overrides, show_override, brightness, effect_type="pulse"):
    tiles = list(tile_mapping.keys())
    phases = {tile: random.random() * 2 * math.pi for tile in tiles}  # Random phase for each tile

    cycle_duration = 5  # Duration of one full cycle in seconds
    steps_per_cycle = 100  # Number of steps in one full cycle

    override_tiles = []
    if show_override:
        override_tiles = {tile for tiles in overrides.values() for tile in tiles}

    while not stop_event.is_set():  # Run the dynamic effect continuously
        for step in range(steps_per_cycle):
            if stop_event.is_set():
                break

            brightness_factor = (1 + math.sin(2 * math.pi * step / steps_per_cycle)) / 2  # Default pulsing

            if effect_type == "flicker":
                # Random flicker effect (intensity changes per tile)
                brightness_factor = random.random()
            elif effect_type == "wave":
                # Wave effect: A sinusoidal brightness factor based on the tile index
                wave_position = (step / steps_per_cycle) * len(tiles)
                brightness_factor = math.sin((tiles.index(tile) - wave_position) * 2 * math.pi / len(tiles)) / 2 + 0.5

            for tile in tiles:
                if tile in override_tiles:
                    continue  # Skip tiles that have overrides
                leds = tile_mapping[tile]
                phase = phases[tile]

                if effect_type == "pulse" or effect_type == "flicker":
                    brightness_factor = (1 + math.sin(2 * math.pi * step / steps_per_cycle + phase)) / 2

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


def diagonal_demo(strip_a, strip_b):
    grid_tiles = [
        ['A1', 'A-1'],
        ['A2', 'A-2', 'B1', 'B-1'],
        ['A3', 'A-3', 'B2', 'B-2', 'C1', 'C-1'],
        ['A4', 'A-4', 'B3', 'B-3', 'C2', 'C-2', 'D1', 'D-1'],
        ['A5', 'A-5', 'B4', 'B-4', 'C3', 'C-3', 'D2', 'D-2', 'E1', 'E-1'],
        ['A6', 'A-6', 'B5', 'B-5', 'C4', 'C-4', 'D3', 'D-3', 'E2', 'E-2', 'F1', 'F-1'],
        ['B6', 'B-6', 'C5', 'C-5', 'D4', 'D-4', 'E3', 'E-3', 'F2', 'F-2', 'G1', 'G-1'],
        ['C6', 'C-6', 'D5', 'D-5', 'E4', 'E-4', 'F3', 'F-3', 'G2', 'G-2'],
        ['D6', 'D-6', 'E5', 'E-5', 'F4', 'F-4', 'G3', 'G-3'],
        ['E6', 'E-6', 'F5', 'F-5', 'G4', 'G-4'],
        ['F6', 'F-6', 'G5', 'G-5'],
        ['G6', 'G-6']
    ]

    # Path to the audio file
    audio_file = 'audio/breaker_trimmed.ogg'
    intro_file = 'audio/uplink_established.ogg'

    play_audio_once(intro_file)
    time.sleep(2.410)
    # Light up diagonally
    for row in grid_tiles:
        play_audio_once(audio_file)  # Play audio for each row
        for tile in row:
            leds_a = get_leds_for_tile(tile, 'a')
            leds_b = get_leds_for_tile(tile, 'b')
            for led in leds_a:
                strip_a.setPixelColor(led - 1, Color(255, 0, 0))  # Red color
            for led in leds_b:
                strip_b.setPixelColor(led - 1, Color(255, 0, 0))  # Red color
        strip_a.show()
        strip_b.show()
        time.sleep(0.750)  # Adjust the speed of the demo here

    audio_file = 'audio/breaker_powerdown.ogg'
    end_file = 'audio/breaker_powerdown_end.ogg'
    # Turn off diagonally
    for row in grid_tiles:
        play_audio_once(audio_file)  # Play audio for each row
        for tile in row:
            leds_a = get_leds_for_tile(tile, 'a')
            leds_b = get_leds_for_tile(tile, 'b')
            for led in leds_a:
                strip_a.setPixelColor(led - 1, Color(0, 0, 0))  # Turn off
            for led in leds_b:
                strip_b.setPixelColor(led - 1, Color(0, 0, 0))  # Turn off

        strip_a.show()
        if strip_b is not None:
            strip_b.show()
        time.sleep(0.375)  # Adjust the speed of the demo here
    play_audio_once(end_file)


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

