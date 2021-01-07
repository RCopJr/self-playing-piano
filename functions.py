import numpy as np
from music21 import note, chord

# Used to apply temperature
def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype("float64")
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds[0], 1)
    return np.argmax(probas)


# https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


# Converts fraction object to float to be used in JS
def frac_to_dec(frac):
    return frac.numerator / float(frac.denominator)


# Creates the readable output sequence for the frontend given the model output
def create_output_sequence(prediction):
    output_sequence = []
    for time_step in prediction:
        # Keeps track of note and duration
        predicted_note = time_step[0]
        predicted_duration = time_step[1]
        # Chords are represented by x.x.x for example
        is_chord = ("." in predicted_note) or predicted_note.isdigit()
        notes = []
        if is_chord:
            chord_notes = predicted_note.split(".")
            # Stores all notes in the chord
            for current_note in chord_notes:
                new_note = note.Note(int(current_note)).name
                # Needed because in Music21, C is the same as C4
                if not hasNumbers(new_note):
                    new_note = new_note + "4"
                new_note = flat_to_sharp(new_note) if ("-" in new_note) else new_note
                notes.append(new_note)
        else:
            # Needed because in Music21, C is the same as C4
            if (hasNumbers(predicted_note) == False) and (predicted_note is not "rest"):
                predicted_note = predicted_note + "4"
            predicted_note = (
                flat_to_sharp(predicted_note)
                if ("-" in predicted_note)
                else predicted_note
            )
            notes = [predicted_note]
        # Convert duration to decimal if it is Fraction object
        if "/" in str(predicted_duration):
            predicted_duration = frac_to_dec(predicted_duration)
        output_sequence.append([notes, predicted_duration])
    return output_sequence


# Converts "-" notation to use sharps and be consistent with JS
def flat_to_sharp(note):
    half_step_down_notes = {
        "A": "G",
        "B": "A",
        "C": "B",
        "D": "C",
        "E": "D",
        "F": "E",
        "G": "F",
    }
    note_name = note[0]
    new_note = half_step_down_notes[note_name]
    if note_name == "F":
        return str(new_note) + str(note[-1])
    elif note_name == "C":
        return str(new_note) + str(note[-1] - 1)  # Because C-Flat goes down octave
    else:
        return str(new_note) + "#" + str(note[-1])


# Generates the output sequence with the models
def generate_predictions(network_input, unique_sounds, unique_durations, models):

    (
        full_input_sequence,
        reverse_sound_map,
        reverse_duration_map,
        num_unique_sounds,
        num_unique_durations,
    ) = setup_prediction_data(network_input, unique_sounds, unique_durations)
    output_sequence = []
    deep_note_test = models[0]
    deep_rhythm_test = models[1]
    for note_index in range(250):
        # Creates the input for the model to run prediction
        prediction_input = np.reshape(
            full_input_sequence, (1, len(full_input_sequence), 2)
        )

        # Retrieves the predicted sound and duration of the two models
        sound_prediction = deep_note_test.predict(prediction_input, verbose=0)
        duration_prediction = deep_rhythm_test.predict(prediction_input, verbose=0)

        # Uses temperature to find the correct index for sound and duration
        sound_index = sample(sound_prediction, 0.75)
        duration_index = sample(duration_prediction, 1.9)

        # Maps those indexes to both a known sound and a duration
        sound_result = reverse_sound_map[sound_index]
        duration_result = reverse_duration_map[duration_index]

        # If duration is 0, just make it 0.25
        if duration_result == 0:
            duration_result = 0.25

        # Appends this sound duration pair to the output sequece
        output_sequence.append([sound_result, duration_result])

        # Normalizes the prediction output
        sound_in = sound_index / num_unique_sounds
        duration_in = duration_index / num_unique_durations

        # Adds this prediction output to the input sequence for next prediction
        full_input_sequence = np.concatenate(
            (full_input_sequence, [[sound_in, duration_in]]), axis=0
        )

        # Deletes the first timestep in the input sequence
        full_input_sequence = np.delete(full_input_sequence, 0, axis=0)

    return output_sequence


def setup_prediction_data(network_input, unique_sounds, unique_durations):
    # Generates a random index to get first input sequence from
    start_index = np.random.randint(0, len(network_input) - 1)

    # Creates the dictionaries used to map numerical representation to sounds and durations
    reverse_sound_map = dict(
        (number, sound) for number, sound in enumerate(unique_sounds)
    )
    reverse_duration_map = dict(
        (number, duration) for number, duration in enumerate(unique_durations)
    )

    # Keeps track of sequential input being sent into the models
    full_input_sequence = network_input[start_index]

    # Values used to normalize
    num_unique_sounds = len(reverse_sound_map)
    num_unique_durations = len(reverse_duration_map)

    return (
        full_input_sequence,
        reverse_sound_map,
        reverse_duration_map,
        num_unique_sounds,
        num_unique_durations,
    )
