import sys

#------------------------------------------------------------------------
# Determines how frequently clock ticks are processed.
# At 120bpm:
#  - 24 ticks per beat means that events are processed every 21ms
#  - 480 ticks per beat means that events are processed every ~1ms
#------------------------------------------------------------------------
DEFAULT_TICKS_PER_BEAT = 480

#------------------------------------------------------------------------
# Ticks per beat used by MIDI devices, as per the MIDI 1.0 standard.
#------------------------------------------------------------------------
MIDI_CLOCK_TICKS_PER_BEAT = 24

#------------------------------------------------------------------------
# If the Timeline scheduling clock runs behind schedule, output
# a warning if the delay exceeds <MIN_CLOCK_DELAY_WARNING_TIME> seconds.
#------------------------------------------------------------------------
MIN_CLOCK_DELAY_WARNING_TIME = 0.02

#------------------------------------------------------------------------
# Used when scheduling neverending events.
#------------------------------------------------------------------------
FOREVER = sys.maxsize

#------------------------------------------------------------------------
# Default BPM
#------------------------------------------------------------------------
DEFAULT_TEMPO = 120

#------------------------------------------------------------------------
# Very fast clock rate, used for quickly running through a timeline.
#------------------------------------------------------------------------
MAX_CLOCK_RATE = 1e6

#------------------------------------------------------------------------
# Parameters used in Timeline event dictionaries.
#------------------------------------------------------------------------
EVENT_TYPE = "type"
EVENT_ACTIVE = "active"
EVENT_CHANNEL = "channel"
EVENT_AMPLITUDE = "amplitude"
EVENT_DURATION = "duration"
EVENT_GATE = "gate"
EVENT_NOTE = "note"
EVENT_DEGREE = "degree"
EVENT_KEY = "key"
EVENT_SCALE = "scale"
EVENT_OCTAVE = "octave"
EVENT_TRANSPOSE = "transpose"
EVENT_PITCHBEND = "pitchbend"
EVENT_EVENT = "event"
EVENT_ACTION = "action"
EVENT_ACTION_ARGS = "args"
EVENT_CONTROL = "control"
EVENT_OSC_ADDRESS = "osc_address"
EVENT_OSC_PARAMS = "osc_params"
EVENT_GLOBAL = "globals"
EVENT_VALUE = "value"
EVENT_TIME = "time"
EVENT_PATCH = "patch"
EVENT_PATCH_PARAMS = "params"
EVENT_PATCH_OUTPUT = "output"
EVENT_TRIGGER_NAME = "trigger_name"
EVENT_TRIGGER_VALUE = "trigger_value"
EVENT_PROGRAM_CHANGE = "program_change"
EVENT_SUPERCOLLIDER_SYNTH = "synth"
EVENT_SUPERCOLLIDER_SYNTH_PARAMS = "params"

#------------------------------------------------------------------------
# Quantize is used to beat-align events, so should not be included
# directly in the dictionary.
#------------------------------------------------------------------------
EVENT_QUANTIZE = "quantize"
EVENT_DELAY = "delay"

#------------------------------------------------------------------------
# Legacy keys.
#------------------------------------------------------------------------

EVENT_KEY_SYNONYMS = {
    "dur": "duration",
    "amp": "amplitude",
    "on": "active",
    "velocity": "amplitude",
}

#------------------------------------------------------------------------
# Synonym keys
#------------------------------------------------------------------------
EVENT_VELOCITY = "velocity"

ALL_EVENT_PARAMETERS = [
    EVENT_TYPE, EVENT_ACTIVE, EVENT_CHANNEL, EVENT_AMPLITUDE, EVENT_DURATION, EVENT_PITCHBEND,
    EVENT_GATE, EVENT_NOTE, EVENT_DEGREE, EVENT_KEY, EVENT_SCALE, EVENT_OCTAVE,
    EVENT_TRANSPOSE, EVENT_EVENT, EVENT_ACTION, EVENT_ACTION_ARGS, EVENT_CONTROL,
    EVENT_OSC_ADDRESS, EVENT_OSC_PARAMS, EVENT_VALUE, EVENT_TIME, EVENT_PATCH,
    EVENT_PATCH_PARAMS, EVENT_PATCH_OUTPUT, EVENT_PROGRAM_CHANGE, EVENT_SUPERCOLLIDER_SYNTH,
    EVENT_SUPERCOLLIDER_SYNTH_PARAMS, EVENT_QUANTIZE, EVENT_DELAY, EVENT_VELOCITY,
    EVENT_TRIGGER_NAME, EVENT_TRIGGER_VALUE, EVENT_GLOBAL,
    *EVENT_KEY_SYNONYMS.keys()
]

#------------------------------------------------------------------------
# Event types
#------------------------------------------------------------------------
EVENT_TYPE_UNKNOWN = "unknown"
EVENT_TYPE_NOTE = "note"
EVENT_TYPE_CONTROL = "control"
EVENT_TYPE_PROGRAM_CHANGE = "program_change"
EVENT_TYPE_OSC = "osc"
EVENT_TYPE_ACTION = "action"
EVENT_TYPE_PATCH_CREATE = "patch"
EVENT_TYPE_PATCH_TRIGGER = "trigger"
EVENT_TYPE_PATCH_SET = "set"
EVENT_TYPE_SUPERCOLLIDER = "supercollider"
EVENT_TYPE_GLOBAL = "global"

#------------------------------------------------------------------------
# Default parameter values
#------------------------------------------------------------------------
DEFAULT_EVENT_CHANNEL = 0
DEFAULT_EVENT_DURATION = 1
DEFAULT_EVENT_GATE = 1.0
DEFAULT_EVENT_AMPLITUDE = 64
DEFAULT_EVENT_OCTAVE = 0
DEFAULT_EVENT_TRANSPOSE = 0
DEFAULT_EVENT_QUANTIZE = 0
DEFAULT_EVENT_DELAY = 0

#------------------------------------------------------------------------
# Interpolation modes for continuous signals.
#------------------------------------------------------------------------
INTERPOLATION_NONE = "none"
INTERPOLATION_LINEAR = "linear"
INTERPOLATION_COSINE = "cosine"