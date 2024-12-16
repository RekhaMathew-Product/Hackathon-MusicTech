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
buffer_size = 1024
active_tracks = []  # List to store (audio data, current playback position)
samplerate = None
current_position = 0
stream = None  # Global stream object

app = Flask(__name__)
CORS(app, resources={r"/state": {"origins": "*"}})
threads = []
selected_indexes = range(4)

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
    global active_tracks, current_position
    mix = np.zeros(frames)

    for i, (track, position) in enumerate(active_tracks):
        remaining_frames = len(track) - position
        if remaining_frames >= frames:
            mix += track[position:position + frames]
            active_tracks[i] = (track, position + frames)
        else:
            try:
                mix[:remaining_frames] += track[position:]
                active_tracks[i] = (track, 0)  # Loop back to the start
            except ValueError:
                pass

    current_position += frames
    outdata[:, 0] = mix

def start_playing(state):
    global active_tracks, stream, samplerate, track_list
    # active_tracks.clear()

    # if state == 'rest':
    # track1 = load_audio("Tides of Ocean_m1_1.wav")
    track = track_list.pop() if track_list else None
    if track is not None:
        active_tracks.append((track, 0))
    # elif state == 'stress':
    #     track1 = load_audio("Tides of Ocean_m1_1.wav")
    #     track2 = load_audio("Tides of Ocean_m2_1.wav")
    #     active_tracks.append((track1, 0))
    #     active_tracks.append((track2, 0))

    # if stream is None or not stream.active:
    stream = sd.OutputStream(callback=callback, samplerate=samplerate, channels=1, blocksize=buffer_size)
    stream.start()
    
def add_track(track):
    global current_position, active_tracks
    print("Adding a new track...")
    active_tracks.append((track, current_position))  # Set the start position as the current 
        
        
def remove_track():
    global active_tracks
    if active_tracks:
        print("Removing the last added track...")
        track_list.append(active_tracks.pop())
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

    # if state.lower() == 'stress':
    #     if len(active_tracks) <= 3:
    #         track_i = random.randrange(len(track_list))
    #         add_track(track_list.pop(track_i))
    # elif state.lower() == 'rest':
    #     if len(active_tracks) > 0:
    #         remove_track()
    
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
    
# import logging
# import sounddevice as sd
# import numpy as np
# from scipy.io.wavfile import read
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# logging.basicConfig(level=logging.DEBUG)

# # Global variables
# buffer_size = 1024
# active_tracks = []  # List to store (audio data, current playback position)
# samplerate = None
# current_position = 0

# app = Flask(__name__)

# # Enable CORS for all routes
# CORS(app, resources={r"/state": {"origins": "*"}})

# @app.route('/state', methods=['POST'])
# def update_state():
#     logging.info("Called update_state()")
#     return jsonify(message="State updated")

# if __name__ == '__main__':
#     app.run(port=5000)

# # Function to load audio files
# def load_audio(filename):
#     print("Load Audio called")
#     global samplerate
#     filename = "stem/" + filename
#     print(f"Loading: {filename}")
#     sr, data = read(filename)
#     samplerate = sr if samplerate is None else samplerate
#     data = data / np.max(np.abs(data), axis=0)  # Normalize
#     if len(data.shape) > 1:
#         data = np.mean(data, axis=1)  # Convert to mono
#     return data

# # Real-time callback for playback
# def callback(outdata, frames, time, status):
#     print("Call back function called")
#     if status:
#         print(status)
#     global active_tracks, current_position
#     mix = np.zeros(frames)  # Initialize the mix buffer

#     for i, (track, position) in enumerate(active_tracks):
#         remaining_frames = len(track) - position
#         if remaining_frames >= frames:
#             mix += track[position:position + frames]
#             active_tracks[i] = (track, position + frames)
#         else:
#             mix[:remaining_frames] += track[position:]
#             active_tracks[i] = (track, 0 + (frames - remaining_frames))

#     current_position += frames
#     outdata[:, 0] = mix

#     # Remove completed tracks from active list
#     active_tracks[:] = [(track, pos) for track, pos in active_tracks if pos < len(track)]

# # Function to start playing based on the state
# def start_playing(state):
#     print("Start Playing called")
#     global active_tracks
#     active_tracks.clear()  # Clear any existing tracks

#     if state == 'rest':
#         track1 = load_audio("Tides of Ocean_m1_1.wav")
#         active_tracks.append((track1, 0))  # Add track for rest
#     elif state == 'stress':
#         track1 = load_audio("Tides of Ocean_m1_1.wav")
#         track2 = load_audio("Tides of Ocean_m2_1.wav")
#         active_tracks.append((track1, 0))  # Add first track for stress
#         active_tracks.append((track2, 0))  # Add second track for stress

# # Flask route to handle state changes
# @app.route('/state', methods=['POST'])
# def change_state():
#     print("Change state called")
#     state = request.json.get('state')
#     if state:
#         start_playing(state)
#         return jsonify({"message": "Tracks updated based on state", "state": state}), 200
#     return jsonify({"error": "Invalid state"}), 400

# # Main function to start the audio stream
# def main():
#     print("main called")
#     global samplerate
#     # Start the audio stream
#     stream = sd.OutputStream(callback=callback, samplerate=samplerate, channels=1, blocksize=buffer_size)
#     with stream:
#         app.run(debug=True, use_reloader=False)

# if __name__ == "__main__":
#     print("going to start main")
#     main()


# import sounddevice as sd
# import numpy as np
# import random
# from scipy.io.wavfile import read
# from flask import Flask, request, jsonify

# # Global variables
# buffer_size = 1024  # Number of frames per callback
# active_tracks = []  # List to store (audio data, current playback position)
# samplerate = None
# current_position = 0  # Global synchronized playback position

# # Flask App setup
# app = Flask(__name__)

# # Function to load audio files
# def load_audio(filename):
#     global samplerate
#     filename = "stem/" + filename  # Add path prefix
#     print(f"Loading: {filename}")
#     sr, data = read(filename)
#     samplerate = sr if samplerate is None else samplerate
#     data = data / np.max(np.abs(data), axis=0)  # Normalize to range [-1, 1]
#     if len(data.shape) > 1:  # Convert to mono if audio is stereo
#         data = np.mean(data, axis=1)
#     return data

# # Real-time callback for playback
# def callback(outdata, frames, time, status):
#     if status:
#         print(status)
#     global active_tracks, current_position

#     mix = np.zeros(frames)  # Initialize the mixing buffer
    

#     for i, (track, position) in enumerate(active_tracks):
#         remaining_frames = len(track) - position  # Number of frames remaining
#         if remaining_frames >= frames:
#             mix += track[position:position + frames]
#             active_tracks[i] = (track, position + frames)  # Update playback position
#         else:
#             mix[:remaining_frames] += track[position:]
#             active_tracks[i] = (track, 0 + (frames - remaining_frames))  # Restart track

#     current_position += frames  # Update global position
#     # print(len(active_tracks))
#     # print(current_position)
#     # print(mix.shape)
#     outdata[:, 0] = mix  # Write the mixed audio into the output buffer

#     # Remove completed tracks from the active list
#     active_tracks[:] = [(track, pos) for track, pos in active_tracks if pos < len(track)]

# # Function to add a track at the current position
# def add_track(track):
#     global current_position
#     print("Adding a new track...")
#     active_tracks.append((track, current_position))  # Set the start position as the current global position

# # Function to remove the last track
# def remove_track():
#     global active_tracks
#     if active_tracks:
#         print("Removing the last added track...")
#         track_list.append(active_tracks.pop())
#     else:
#         print("No tracks to remove!")

# # Main function
# def main():
#     global samplerate, current_position, track_list
#     # Load audio files
#     track1 = load_audio("Tides of Ocean_m1_1.wav")
#     track2 = load_audio("Tides of Ocean_m2_1.wav")
#     track3 = load_audio("Tides of Ocean_chord_1.wav")
#     track4 = load_audio("Tides of Ocean_bass_1.wav")
#     track_list = [track1, track2, track3, track4]

#     # Start the audio stream
#     print("Press '+' to add a track, '-' to remove the last track, and 'q' to quit.")
#     stream = sd.OutputStream(callback=callback, samplerate=samplerate, channels=1, blocksize=buffer_size)

#     try:
#         with stream:
#             while True:
#                 user_input = input("Enter command (+/-/q): ").strip()
#                 if user_input == "+":
#                     if len(active_tracks) <= 3:
#                         track_i = random.randrange(len(track_list))
#                         add_track(track_list.pop(track_i))
#                 elif user_input == "-":
#                     remove_track()
#                 elif user_input == "q":
#                     print("Exiting program...")
#                     break
#                 else:
#                     print("Invalid input. Use '+' to add, '-' to remove, 'q' to quit.")
#     except KeyboardInterrupt:
#         print("\nPlayback stopped.")
#     finally:
#         print("Program exited.")

# # Run the program
# if __name__ == "__main__":
#     main()