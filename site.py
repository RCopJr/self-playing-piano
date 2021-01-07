from flask import Flask, render_template, jsonify
from tensorflow.keras.models import load_model
import pickle
import numpy as np
import functions as f

# Created env with python 3.8.6, then installed tensorflow, then music21, then pickle

app = Flask(__name__)

# Retrieve needed data for inference
deep_note_test = load_model("models\deepNote-25-0.1222.hdf5")
deep_rhythm_test = load_model("models\deepRhythm-45-0.1190.hdf5")

with open("music_data\\net_in_CLBM_L10E_160", "rb") as filepath:
    test_input = np.load(filepath)
with open("music_data\\unique_sounds_CLBM_L10E", "rb") as filepath:
    unique_sounds = pickle.load(filepath)
with open("music_data\\unique_durations_CLBM_L10E", "rb") as filepath:
    unique_durations = pickle.load(filepath)

# Main Page
@app.route("/")
def home():
    return render_template("base.html")


# REST API to create musical sequence and send back to frontend
@app.route("/play", methods=["GET"])
def play():
    models = [deep_note_test, deep_rhythm_test]
    # Generate prediction
    output_sequence = f.generate_predictions(
        test_input, unique_sounds, unique_durations, models
    )
    # Create JS readable form of prediictions
    output_sequence = f.create_output_sequence(output_sequence)

    # Return output sequence in JSON format
    return jsonify(output_sequence)


if __name__ == "__main__":
    app.run(debug=True)
