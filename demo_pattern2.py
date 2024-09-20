import time
import pygame
from rpi_ws281x import *
import os

# LED strip configuration:
LED_COUNT_A = 271  # Total number of LEDs on board A
LED_PIN_A = 18  # GPIO pin for board A
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL_A = 0  # Channel for board A

# Set the SDL audio driver to alsa
os.environ['SDL_AUDIODRIVER'] = 'alsa'
# Specify the ALSA device
os.environ['AUDIODEV'] = 'hw:1,0' #1,0 works for USB
os.environ['XDG_RUNTIME_DIR'] = '/run/user/0'


# Initialize Pygame mixer for audio playback
pygame.mixer.init()

def load_led_mapping(file_path):
    mapping = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            tile, leds = line.strip().split(':')
            start, end = map(int, leds.split('-'))
            mapping[tile.strip()] = list(range(start, end + 1))
    return mapping

# Load LED mappings
tile_to_leds_a = load_led_mapping('config/board_a_leds.txt')

# Function to get LEDs for a specific tile
def get_leds_for_tile(tile, board):
    if board == 'a':
        return tile_to_leds_a.get(tile, [])

# Initialize the LED strip
strip_a = Adafruit_NeoPixel(LED_COUNT_A, LED_PIN_A, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL_A)
strip_a.begin()

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def diagonal_demo(strip):
    grid_tiles = [
        ['A1'],
        ['A2', 'B1'],
        ['A3', 'B2', 'C1'],
        ['A4', 'B3', 'C2', 'D1'],
        ['A5', 'B4', 'C3', 'D2', 'E1'],
        ['A6', 'B5', 'C4', 'D3', 'E2', 'F1'],
        ['B6', 'C5', 'D4', 'E3', 'F2', 'G1'],
        ['C6', 'D5', 'E4', 'F3', 'G2'],
        ['D6', 'E5', 'F4', 'G3'],
        ['E6', 'F5', 'G4'],
        ['F6', 'G5'],
        ['G6']
    ]

    # Path to the audio file
    audio_file = 'audio/breaker.m4a'

    # Light up diagonally
    for row in grid_tiles:
        play_audio(audio_file)  # Play audio for each row
        for tile in row:
            leds = get_leds_for_tile(tile, 'a')
            for led in leds:
                strip.setPixelColor(led - 1, Color(255, 0, 0))  # Red color
        strip.show()
        time.sleep(0.5)  # Adjust the speed of the demo here

    # Turn off diagonally
    for row in grid_tiles:
        for tile in row:
            leds = get_leds_for_tile(tile, 'a')
            for led in leds:
                strip.setPixelColor(led - 1, Color(0, 0, 0))  # Turn off
        strip.show()
        time.sleep(0.5)  # Adjust the speed of the demo here

# Run the demo pattern
diagonal_demo(strip_a)
