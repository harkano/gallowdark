from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# Function to log data
def log_data(updated_data, filename):
    # Load existing data from the file
    existing_data = load_config(filename)

    # Update the existing data with the new data
    existing_data.update(updated_data)

    # Write the updated data back to the file
    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=4)

    print(f"Updated {filename} with data: {updated_data}")

def load_config(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

@app.route('/')
def index():
    # Load the current audio and light configuration
    audio_config = load_config('audio_config.json')
    light_config = load_config('light_config.json')
    missions = load_config('missions.json')
    
    return render_template('index.html', audio_config=audio_config, light_config=light_config, missions=missions)

@app.route('/update_audio', methods=['POST'])
def update_audio():
    data = request.json
    log_data(data, 'audio_config.json')
    return jsonify({"status": "success"})

@app.route('/update_lights', methods=['POST'])
def update_lights():
    data = request.json
    light_config = load_config('light_config.json')
    
    # Update brightness, show_override, and effect_type
    light_config['brightness'] = data.get('brightness', light_config.get('brightness', 128))
    light_config['effect_type'] = data.get('effect_type', light_config.get('effect_type', 'pulse'))  # Default to 'pulse'
    light_config['show_override'] = bool(data.get('show_override', light_config.get('show_override', False)))

    log_data(light_config, 'light_config.json')
    
    # Signal the lights controller that there's been a change
    with open('lights_changed', 'w') as f:
        f.write("1")
    
    return jsonify({"status": "success"})

@app.route('/get_missions', methods=['POST'])
def get_missions():
    selected_pack = request.json.get('pack')
    missions = load_config('missions.json')
    filtered_missions = missions.get(selected_pack, [])
    return jsonify(filtered_missions)

@app.route('/apply_mission', methods=['POST'])
def apply_mission():
    mission = request.json
    # Update light_config.json with overrides from the mission
    light_config = load_config('light_config.json')
    light_config['overrides'] = mission['overrides']
    log_data(light_config, 'light_config.json')
    
    # Update audio_config.json with the mission's audio file
    audio_config = load_config('audio_config.json')
    audio_config['audio'] = mission['audio']
    log_data(audio_config, 'audio_config.json')
    
    # Signal the controllers
    with open('lights_changed', 'w') as f:
        f.write("1")
    with open('audio_changed', 'w') as f:
        f.write("1")
    
    return jsonify({"status": "Mission applied successfully"})

@app.route('/update_ambience', methods=['POST'])
def update_ambience():
    data = request.json
    ambient_mode = data.get('ambient_mode')
    music = data.get('music')

    # Update light_config.json with the selected ambient_mode
    light_config = load_config('light_config.json')
    light_config['ambient_mode'] = ambient_mode
    log_data(light_config, 'light_config.json')

    # Update audio_config.json with the selected music track
    audio_config = load_config('audio_config.json')
    audio_config['music'] = music
    log_data(audio_config, 'audio_config.json')

    # Signal the controllers for lights and audio changes
    with open('lights_changed', 'w') as f:
        f.write("1")
    with open('audio_changed', 'w') as f:
        f.write("1")

    return jsonify({"status": "Ambience applied successfully"})

@app.route('/get_music_tracks', methods=['GET'])
def get_music_tracks():
    music_dir = 'music/'
    # List all files ending with .ogg in the music directory
    music_files = [f for f in os.listdir(music_dir) if f.endswith('.ogg')]
    return jsonify(music_files)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
