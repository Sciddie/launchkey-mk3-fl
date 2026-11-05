"""User options. Edit this file in the installed script folder, then reload the script in FL Studio
(Options > MIDI settings > "Update MIDI scripts", or restart FL Studio)."""

# Force a model instead of auto-detecting it with a Device Inquiry: None (auto), 25, 37, 49, 61 or 88.
MODEL = None

# Soft takeover ("pickup") for pots and faders: a control only starts changing a value once it reaches or crosses
# the value's current position, so nothing jumps when you switch banks, plugins or modes.
SOFT_TAKEOVER = True
# How close (0..127 controller steps) a control must come to the current value to pick it up.
PICKUP_THRESHOLD = 3

# Pot / fader modes selected when the script starts (the surface remembers its own choice otherwise).
# Pots: "volume", "device", "pan", "send_a", "send_b". Faders: "volume", "device", "send_a", "send_b".
START_POT_MODE = "pan"
START_FADER_MODE = "volume"

# Send A / Send B pot and fader modes control the level of the route from each bank track to these mixer tracks.
# Negative numbers count from the last insert (-1 = the last insert track, 125 in FL 20.9+).
SEND_A_TRACK = -2
SEND_B_TRACK = -1
# Create the route when you turn a send control on a track that is not routed yet (off: only existing routes move).
SEND_CREATE_ROUTE = False

# Seconds a temporary message ("Metronome On", parameter values, ...) stays on the default display.
MESSAGE_SECONDS = 1.5

# Capture MIDI: how many seconds of recently played notes to write into the selected pattern.
CAPTURE_SECONDS = 30

# Quantise button: True = quantise note starts only (keeps lengths), False = starts and lengths.
QUANTISE_START_ONLY = True

# Show a moving playhead on the step-sequencer pads while FL Studio plays.
STEP_PLAYHEAD = True
# Playhead colours (Launchkey palette indices 0..127, see the colour chart in Novation's programmer's reference).
# The playhead must show whether the step under it is set:
# - over a SET step: bright white (3); if the channel colour itself is white / grey, PLAYHEAD_SET_ALT_COLOUR is used
# - over an EMPTY step: mid blue (46), clearly different from the white playhead, the dim-white beat grid and "off"
PLAYHEAD_SET_COLOUR = 3
PLAYHEAD_SET_ALT_COLOUR = 13  # yellow
PLAYHEAD_EMPTY_COLOUR = 46

# Pad layer selected when the script starts: "steps", "patterns", "channels" or "mixer".
START_PAD_LAYER = "steps"

# Mirror short status messages to FL Studio's hint bar as well.
HINTS = True
