import json
import time
import pygame
import logging
import os

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the SDL audio driver to alsa
os.environ['SDL_AUDIODRIVER'] = 'alsa'
# Specify the ALSA device
os.environ['AUDIODEV'] = 'hw:1,0' #1,0 works for USB
os.environ['XDG_RUNTIME_DIR'] = '/run/user/0'

# Initialize Pygame mixer for audio playback
pygame.mixer.init()

def load_audio_config():
    #logging.info("Loading audio configuration.")
    with open('audio_config.json', 'r') as file:
        return json.load(file)

def apply_audio_config(config):
    logging.info(f"Applying audio configuration: Music: {config['music']}, Volume: {config['volume']}")
    pygame.mixer.music.set_volume(config['volume'] / 100)
    pygame.mixer.music.load(config['music'])
    pygame.mixer.music.play(-1)

def play_audio_once(file_path):
    logging.info(f"Playing audio once: {file_path}")
    effect = pygame.mixer.Sound(file_path)
    effect.play()

def audio_changed(config, current_config):
    logging.info("Configuration changed.")
    if config['music'] != current_config['music']:
        logging.info("Music file changed.")
        apply_audio_config(config)
    if config['volume'] != current_config['volume']:
        logging.info(f"Volume changed to: {config['volume']}")
        pygame.mixer.music.set_volume(config['volume'] / 100)
    
    # Check if we need to play the one-time audio file
    if config['play_audio_once'] and not play_audio_once_flag:
        play_audio_once(config['audio'])
        play_audio_once_flag = True
    elif not config['play_audio_once']:
        play_audio_once_flag = False
