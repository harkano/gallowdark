import json
import time
import logging
import random
import math
import os
import threading
from rpi_ws281x import PixelStrip, Color
from led_utils import init_strip, clear_leds, LED_COUNT_A, LED_PIN_A, LED_CHANNEL_A, LED_COUNT_B, LED_PIN_B, LED_CHANNEL_B, load_led_mapping, get_leds_for_tile
import audio_controller
from audio_controller import load_audio_config, apply_audio_config, play_audio_once, audio_changed
import light_controller
from light_controller import load_light_config, get_base_color, apply_dynamic_ambient, apply_tile_overrides, start_demo_pattern, strip_a, strip_b, tile_to_leds_a, tile_to_leds_b
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Control threads in the controller.")
parser.add_argument('--skip-startup', action='store_true', help='Skip running the startup demo pattern.')

args = parser.parse_args()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the light controller
current_light_config = load_light_config()  # Load the initial configuration
brightness = current_light_config.get('brightness', 255)  # Default to 255 if brightness isn't specified
stop_event = threading.Event()

# Load the audio controller
current_audio_config = load_audio_config()  # Load the initial configuration
stop_audio_event = threading.Event()

# Only run start_demo_pattern if --skip-startup is NOT passed
if not args.skip_startup:
    start_demo_pattern()
else:
    print("Skipping startup demo pattern...")

# Begin audio
play_audio_once_flag = False
thread_audio = threading.Thread(target=apply_audio_config, args=(current_audio_config))
thread_audio.start()

# Apply initial light configuration
if strip_a is not None:
    thread_a = threading.Thread(target=apply_dynamic_ambient, args=(strip_a, get_base_color(current_light_config['ambient_mode']), tile_to_leds_a, stop_event, current_light_config.get('overrides', {}), current_light_config.get('show_override'), brightness))
    thread_a.start()
if strip_b is not None:
    thread_b = threading.Thread(target=apply_dynamic_ambient, args=(strip_b, get_base_color(current_light_config['ambient_mode']), tile_to_leds_b, stop_event, current_light_config.get('overrides', {}), current_light_config.get('show_override'), brightness))
    thread_b.start()

# Apply tile overrides initially
if 'overrides' in current_light_config:
    apply_tile_overrides(current_light_config['overrides'], brightness)

def thread_controller():
    global current_light_config, thread_a, thread_b, brightness, current_audio_config
    while not stop_event.is_set():
        config = load_light_config()
        audio_config = load_audio_config()
        if config != current_light_config:
            logging.info("Configuration changed.")
            stop_event.set()
            time.sleep(1)  # Give threads time to stop
            stop_event.clear()
            current_light_config = config
            brightness = current_light_config.get('brightness', 255)  # Update brightness

            # Start new threads for dynamic ambient
            if strip_a is not None:
                thread_a = threading.Thread(target=apply_dynamic_ambient, args=(strip_a, get_base_color(current_light_config['ambient_mode']), tile_to_leds_a, stop_event, current_light_config.get('overrides', {}), current_light_config.get('show_override'), brightness))
                thread_a.start()
            if strip_b is not None:
                thread_b = threading.Thread(target=apply_dynamic_ambient, args=(strip_b, get_base_color(current_light_config['ambient_mode']), tile_to_leds_b, stop_event, current_light_config.get('overrides', {}), current_light_config.get('show_override'), brightness))
                thread_b.start()

            # Apply tile overrides
            if 'overrides' in current_light_config:
                apply_tile_overrides(current_light_config['overrides'], brightness)
        audio_config = load_audio_config()
        if audio_config != current_audio_config:
            logging.info("Audio Configuration changed.")
            stop_event.set()
            time.sleep(1)
            stop_event.clear()
            current_audio_config = audio_config
            thread_audio = threading.Thread(target=apply_audio_config, args=(current_audio_config))
            thread_audio.start()
        time.sleep(1)

# Start the thread controller in the main thread
thread_controller()
