from ..io.midi import MidiOutputDevice
from ..timelines import Timeline
from ..exceptions import DeviceNotFoundException
from ..globals import Globals
from .. import ALL_EVENT_PARAMETERS

try:
    from signalflow import *
    from ..io.signalflow import SignalFlowOutputDevice

    Globals.enable_interprocess_sync()

    midi_output_device = MidiOutputDevice()
    timeline = Timeline(120, midi_output_device, clock_source="link")
    # timeline.add_output_device(midi_output_device)

    graph = AudioGraph()
    signalflow_output_device = SignalFlowOutputDevice(graph)
    signalflow_output_device.added_latency_seconds = 0.00

    timeline.ignore_exceptions = True
    timeline.background()

except (ModuleNotFoundError, DeviceNotFoundException) as e:
    print("Warning: Could not set up shorthand mode: %s" % e)
    graph = None
    timeline = None

live_set = None
# Enable Ableton Link clock in current Live set
def enable_ableton_link():
    import live
    global live_set
    try:
        live_set = live.Set()
        if not live_set.is_ableton_link_enabled:
            live_set.is_ableton_link_enabled = True
            print("Ableton Link enabled in current Live set.")
    except (live.LiveConnectionError, OSError) as e:
        print(f"Error enabling Ableton Link: {e}")
enable_ableton_link()

def open_set(set_name):
    global live_set
    live_set.open(set_name)

def track(name, **kwargs):
    global timeline

    track_parameters = {
        "quantize": 1,
        "interpolate": None,
    }
    #--------------------------------------------------------------------------------
    # Unflatten the params list.
    # This has some perils (e.g. 'amp' is used as an Event keyword but is 
    # also often used as a Patch parameter).
    #--------------------------------------------------------------------------------
    params = {}
    for key in list(kwargs.keys()):
        if key in track_parameters:
            track_parameters[key] = kwargs[key]
            del kwargs[key]
        elif key in ALL_EVENT_PARAMETERS:
            pass
        else:
            params[key] = kwargs[key]
            del kwargs[key]
    
    if params:
        #--------------------------------------------------------------------------------
        # This caused the track to not generate any events when params was null,
        # not sure why
        #--------------------------------------------------------------------------------
        kwargs["params"] = params

    #--------------------------------------------------------------------------------
    # Automatically select the appropriate output device based on the event type.
    #--------------------------------------------------------------------------------
    if "patch" in kwargs:
        output_device = signalflow_output_device
    else:
        output_device = midi_output_device

    track = timeline.schedule(params=kwargs,
                              name=name,
                              replace=True,
                              output_device=output_device,
                              **track_parameters)
    #--------------------------------------------------------------------------------
    # Evaluating a cell with a track() command with mute() appended to it causes
    # the track to be silenced.
    #
    # Re-evaluating the cell without mute() should then unmute the track.
    #--------------------------------------------------------------------------------
    track.is_muted = False

    try:
        import signalflow_vscode
        cell_id = signalflow_vscode.vscode_get_this_cell_id()
        print("Added flash callback for cell ID:", cell_id)
        if cell_id is not None:
            track.add_event_callback(lambda e: signalflow_vscode.vscode_flash_cell_id(cell_id, track.name))
    except (ModuleNotFoundError, ImportError):
        # no signalflow_vscode module available
        pass


    return track
