// Constant variables
const keys = document.querySelectorAll(".key");
const white_pkeys = document.querySelectorAll(".key.white");
const black_pkeys = document.querySelectorAll(".key.black");
var piano_keys_mapping = {};

// Sets up the piano_keys object that maps key to index
function setup_piano_key_mapping() {
  index = 0;
  mapping = {};
  keys.forEach((element) => {
    mapping[element.dataset.note] = index;
    ++index;
  });
  return mapping;
}

// https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Play the given output sequence
async function play(output_sequence) {
  for (i = 0; i < output_sequence.length; i++) {
    notes = output_sequence[i]["notes"];
    duration = output_sequence[i]["duration"];
    if (notes[0] !== "rest") {
      // Needs to be forEach for chords
      notes.forEach((note) => {
        play_note(keys[note], duration);
      });
    }
    await sleep(600 * duration);
  }
}

// Play a note given its key name
function play_note(key, duration = 0, comp_key = null) {
  const note_audio = document.getElementById(key.dataset.note);
  note_audio.currentTime = 0;
  note_audio.play();
  key.classList.add("active");

  // Stops playing of note and lighting of key once duration ends
  if (duration > 0) {
    setTimeout(function () {
      note_audio.pause();
      note_audio.currentTime = 0;
      key.classList.remove("active");
    }, 600 * duration);
  }

  note_audio.addEventListener("ended", () => {
    key.classList.remove("active");
  });
}

// Used to "excercise" keys making them not be delayed duriing actual generation
async function excercise_piano() {
  for (var i = 0; i < white_pkeys.length; i++) {
    play_note(white_pkeys[i], 0.1815);
    await sleep(600 * 0.1815);
  }
  for (var i = 0; i < black_pkeys.length; i++) {
    play_note(black_pkeys[i], 0.1815);
    await sleep(600 * 0.1815);
  }
}

$(document).ready(function () {
  // Sets up mapping
  piano_keys_mapping = setup_piano_key_mapping();
  // Mapped to play button on site
  $("#play").click(function () {
    excercise_piano(); // Quickly plays all keys to make sure no ugly delay when actually playing
    $.get("/play", function (data) {
      output_sequence = [];
      // Creates a list that stores the output sequence to be used in the JS
      data.forEach((time_step) => {
        notes = [];
        duration = time_step[1];
        time_step[0].forEach((note) => {
          notes.push(note === "rest" ? "rest" : piano_keys_mapping[note]);
        });
        output_sequence.push({
          notes: notes,
          duration: duration,
        });
      });
      play(output_sequence);
    });
  });
});
