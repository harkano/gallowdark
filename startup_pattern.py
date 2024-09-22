import time
import os
import pygame
from led_utils import init_strip, clear_leds, LED_COUNT_A, LED_PIN_A, LED_CHANNEL_A, LED_COUNT_B, LED_PIN_B, LED_CHANNEL_B, load_led_mapping, get_leds_for_tile
from rpi_ws281x import *

# Set the SDL audio driver to alsa
os.environ['SDL_AUDIODRIVER'] = 'alsa'
# Specify the ALSA device
os.environ['AUDIODEV'] = 'hw:1,0' #1,0 works for USB
os.environ['XDG_RUNTIME_DIR'] = '/run/user/0'


# Initialize Pygame mixer for audio playback
pygame.mixer.init()

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

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

    play_audio(intro_file)
    time.sleep(2.410)
    # Light up diagonally
    for row in grid_tiles:
        play_audio(audio_file)  # Play audio for each row
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

    # Turn off diagonally
    for row in grid_tiles:
        for tile in row:
            leds_a = get_leds_for_tile(tile, 'a')
            leds_b = get_leds_for_tile(tile, 'b')
            for led in leds_a:
                strip_a.setPixelColor(led - 1, Color(0, 0, 0))  # Turn off
            for led in leds_b:
                strip_b.setPixelColor(led - 1, Color(0, 0, 0))  # Turn off

        strip_a.show()
        strip_b.show()
        time.sleep(0.750)  # Adjust the speed of the demo here

