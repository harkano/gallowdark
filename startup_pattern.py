import time
import pygame
import logging
from rpi_ws281x import *
import os
from led_utils import init_strip, clear_leds, LED_COUNT_A, LED_PIN_A, LED_CHANNEL_A, LED_COUNT_B, LED_PIN_B, LED_CHANNEL_B, load_led_mapping, get_leds_for_tile

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the SDL audio driver to alsa
os.environ['SDL_AUDIODRIVER'] = 'alsa'
# Specify the ALSA device
os.environ['AUDIODEV'] = 'hw:1,0' #1,0 works for USB
os.environ['XDG_RUNTIME_DIR'] = '/run/user/0'


# Initialize Pygame mixer for audio playback
pygame.mixer.init()

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

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def diagonal_demo(strip):
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

    play_audio(intro_file)
    time.sleep(2.410)
    # Light up diagonally
    for row in grid_tiles:
        play_audio(audio_file)  # Play audio for each row
        for tile in row:
            leds = get_leds_for_tile(tile, 'a')
            for led in leds:
                strip.setPixelColor(led - 1, Color(255, 0, 0))  # Red color
        strip.show()
        time.sleep(0.750)  # Adjust the speed of the demo here

    # Turn off diagonally
    for row in grid_tiles:
        for tile in row:
            leds = get_leds_for_tile(tile, 'a')
            for led in leds:
                strip.setPixelColor(led - 1, Color(0, 0, 0))  # Turn off
        strip.show()
        time.sleep(0.750)  # Adjust the speed of the demo here

# Run the demo pattern
diagonal_demo(strip_a)
