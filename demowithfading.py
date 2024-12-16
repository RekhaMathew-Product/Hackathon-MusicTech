import logging
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import read
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
import random

logging.basicConfig(level=logging.DEBUG)

# Global variables
buffer_size = 22050
active_tracks = []  # List to store (audio data, current playback position)
samplerate = None
current_position = 0
stream = None  # Global stream object
fade_in_params = {}  #  save fade-in parameters
_ids = {'b', 'c', 'd'}  # save track ids
app = Flask(__name__)
CORS(app, resources={r"/state": {"origins": "*"}})
threads = []
selected_indexes = range(4)

def exponential_fade(input_vec):
    return np.exp(input_vec)

buffer_linspace = np.linspace(0, 1, buffer_size)
fade_in = exponential_fade(buffer_linspace)
fade_out = exponential_fade(buffer_linspace[::-1])

def load_audio(filename):
    global samplerate
    filename = "stem/" + filename
    print(f"Loading: {filename}")
    sr, data = read(filename)
    samplerate = sr if samplerate is None else samplerate
    data = data / np.max(np.abs(data), axis=0)  # Normalize
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)  # Convert to mono
    return data

# Load audio files
track1 = load_audio("Tides of Ocean_m1_1.wav")
track2 = load_audio("Tides of Ocean_m2_1.wav")
track3 = load_audio("Tides of Ocean_chord_1.wav")
track4 = load_audio("Tides of Ocean_bass_1.wav")
track_list = [track1, track2, track3, track4]


def callback(outdata, frames, time, status):
    if status:
        print(status)
    global active_tracks, current_position, fade_in_params
    mix = np.zeros(frames)

    for i, (track, position, track_id) in enumerate(active_tracks):
        remaining_frames = len(track) - position
        if remaining_frames >= frames:
            segment = track[position:position + frames]

            # fade-in
            if track_id in fade_in_params and fade_in_params[track_id] > 0:
                fade_in_frames = fade_in_params[track_id]
                # fade_curve = np.linspace(0, 1, min(fade_in_frames, frames))
                fade_curve = fade_in[:min(fade_in_frames, frames)]
                segment[:len(fade_curve)] *= fade_curve  
                fade_in_params[track_id] -= len(fade_curve)

                # if fade in is done, remove the track_id from the fade_in_params
                if fade_in_params[track_id] <= 0:
                    del fade_in_params[track_id]

            mix += segment
            active_tracks[i] = (track, position + frames, track_id)
        else:
            mix[:remaining_frames] += track[position:]
            active_tracks[i] = (track, 0, track_id)  # restart from the beginning

    current_position += frames
    outdata[:, 0] = mix


    # Remove completed tracks from the active list
    # active_tracks[:] = [(track, pos) for track, pos in active_tracks if pos < len(track)]

def start_playing(state):
    global active_tracks, stream, samplerate, track_list

    track = track_list.pop() if track_list else None
    if track is not None:
        active_tracks.append((track, 0, id(track)))  # start from 0 positions


    # if stream is None or not stream.active:
    stream = sd.OutputStream(callback=callback, samplerate=samplerate, channels=1, blocksize=buffer_size)
    stream.start()

def add_track(track):
    global current_position, active_tracks, samplerate, fade_in_params, buffer_size
    # fade_in_duration = 1 
    fade_in_frames = buffer_size

    print("Adding a new track with fade-in...")
    track_id = id(track)  # use the id of the track as the track_id
    fade_in_params[track_id] = fade_in_frames  

    to_add = (track, current_position, track_id)  
    active_tracks.append(to_add)
        
        
def remove_track():
    global active_tracks, track_list

    if active_tracks:
        print("Removing the last added track...")
        removed_track = active_tracks.pop()
        print("removed entry like: type={}, members={}".format(
            type(removed_track), type(removed_track[0]), type(removed_track[1]))
        )
        track_list.append(removed_track[0])
    else:
        print("No tracks to remove!")

def ensure_num_tracks(nums):
    global active_tracks, track_list
    diff = len(active_tracks) - nums
    print("starting with {} active".format(len(active_tracks)))
    to_change = min(abs(diff), 3)
    if diff < 0:
        print("Need to add {} tracks".format(to_change))
        for _ in range(to_change):
            if len(active_tracks) <= 3:
                track_i = random.randrange(len(track_list))
                add_track(track_list.pop(track_i))
    elif diff > 0:
        print("Need to remove {} tracks".format(to_change))
        for _ in range(to_change):
            if len(active_tracks) > 0:
                remove_track()

    return

def mod_layers(state):
    global active_tracks, stream, samplerate
    
    if state.lower() == 'rest':
        ensure_num_tracks(1)
    elif 'low' in state.lower():
        ensure_num_tracks(2)
    elif 'medium' in state.lower():
        ensure_num_tracks(3)
    elif 'high' in state.lower():
        ensure_num_tracks(4)


@app.route('/state', methods=['POST'])
def change_state():
    state = request.json.get('state')
    # if state:
    mod_layers(state)
    return jsonify({"message": "Tracks updated based on state", "state": state}), 200

def main():
    global samplerate
    # Load a dummy audio file to set the samplerate
    load_audio("Tides of Ocean_m1_1.wav")
    thread = Thread(start_playing('rest'))
    threads.append(thread)
    thread.start()

    app.run(debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
    
