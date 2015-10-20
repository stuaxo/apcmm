from __future__ import print_function

from collections import namedtuple, OrderedDict

from six import with_metaclass
from six.moves import range
from mnd.dispatch import Dispatcher
from mnd.handler import Handler

from enum import Enum


RECV_MIDI = "APC MINI MIDI 1"
SEND_MIDI = "APC MINI MIDI 1"

midi = Dispatcher()


APC_BUTTON_EVENTS = [
    "clip_press",
    "clip_release",
    "control_change",
    "control_press",
    "control_release",
    "shift_press",
    "shift_release",
    "scene_press",
    "scene_release"
    ]


class Button:
    # midi notes for each kind of button
    CLIP = range(0, 64)
    CONTROL = range(64, 73) ## ???
    SCENE = range(82, 90)
    SHIFT = 98


class Slider:
    # midi controls for sliders
    SLIDER = range(48, 57)


class ClipColors(Enum):
    # midi note values to set clip button colors
    grey = 0
    green = 1
    # green_blink = 2
    red = 3
    # red_blink = 4
    yellow = 5
    # yellow_blink = 6

class SceneColors(Enum):
    grey = 0
    green = 1

class ControlColors(Enum):
    grey = 0
    red = 1


class GridButton(object):
    def __init__(self, type, id, note, x, y):
        self.type = type
        self.id = id
        self.note = note
        self.x = x
        self.y = y

        self.pressed = False
        self.held = False

    @property
    def name(self):
        return "%s_%d" % (self.type, self.id)


class GridSlider(object):
    def __init__(self, type, id, control, x, y):
        self.type = type
        self.id = id
        self.control = control
        self.x = x
        self.y = y

    @property
    def name(self):
        return "%s_%d" % (self.type, self.id)

CLIP_LAUNCH = "clip_launch"
SCENE_LAUNCH = "scene_launch"
CONTROL = "control"
SHIFT = "shift"
SLIDER = "slider"

BUTTON_TYPES = [CLIP_LAUNCH, CONTROL, SCENE_LAUNCH, SHIFT]


class APCMiniModel(with_metaclass(Handler)):
    def __init__(self):
        self.observers = []

        # setup dicts of the widgets in the grid
        # so it's easy to retrieve them later 

        self.clip_buttons = []
        self.control_buttons = OrderedDict()
        self.scene_buttons = OrderedDict()
        self.shift_button = OrderedDict()
        self.grid = OrderedDict()
        
        self.note_buttons = OrderedDict()
        self.control_sliders = OrderedDict()

        # TODO - find out about control buttons

        # 8x8 grid of clip launch buttons, and column of
        # scene launch buttons on the right
        scenes = zip(xrange(8), Button.SCENE).__iter__()
        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                note = (row * 8) + col
                btn = GridButton(CLIP_LAUNCH, note, note, col, row)
                self.clip_buttons.append(btn)
                self.add_grid_button(btn)

            # last column is scene launch
            scene_no, note = next(scenes)
            btn = GridButton(SCENE_LAUNCH, scene_no, note, 9, note)
            self.scene_buttons[note] = btn
            self.add_grid_button(btn)

        # row 8 - control buttons and shift
        for i, note in enumerate(Button.CONTROL):
            btn = GridButton(CONTROL, i, note, i, 8)
            self.control_buttons[i] = btn
            self.add_grid_button(btn)
        else:
            btn = GridButton(SHIFT, 0, Button.SHIFT, i, 8)
            self.add_grid_button(btn)

        # row 9 - sliders
        for i, control in enumerate(Slider.SLIDER):
            slider = GridSlider(SLIDER, i, control, i, 9)
            self.control_sliders[i] = slider
            self.add_grid_slider(slider)

    def add_grid_button(self, w):
        """
        Add widget with x, y
        """
        self.grid[(w.x, w.y)] = w
        self.note_buttons[w.note] = w

    def add_grid_slider(self, w):
        """
        Add widget with x, y
        """
        self.grid[(w.x, w.y)] = w
        self.control_sliders[w.control] = w

    def add_button_handlers(self, btn):
        ## TODO yagni ?
        pass

    def add_slider_handlers(self, slider):
        ## TODO yagni ?
        pass

    def add_observer(self, o):
        self.observers.append(o)

    def midi_control_event(self, name, msg):
        assert name == "control_change", "Unknown midi event %s" % name
        ctl = self.control_sliders[msg.control]
        for ob in self.observers:
            m = getattr(ob, "on_%s" % name, None)
            m(self, ctl, msg.value)

    def midi_button_event(self, name, msg):
        assert name in APC_BUTTON_EVENTS, "Unknown midi event %s" % name
        btn = self.note_buttons[msg.note]
        for ob in self.observers:
            m = getattr(ob, "on_%s" % name, None)
            m(self, btn)

    ### handlers for midi data from APC    
    @midi.handle(dict(type="note_on", note__in=Button.CLIP))
    def recv_clip_press(self, msg):
        self.midi_button_event("clip_press", msg)

    @midi.handle(dict(type="note_off", note__in=Button.CLIP))
    def recv_clip_release(self, msg):
        self.midi_button_event("clip_release", msg)

    @midi.handle(dict(type="note_on", note__in=Button.CONTROL))
    def recv_control_press(self, msg):
        self.midi_button_event("control_press", msg)

    @midi.handle(dict(type="note_off", note__in=Button.CONTROL))
    def recv_control_release(self, msg):
        self.midi_button_event("control_release", msg)

    @midi.handle(dict(type="note_on", note__in=Button.SCENE))
    def recv_scene_press(self, msg):
        self.midi_button_event("scene_press", msg)

    @midi.handle(dict(type="note_off", note__in=Button.SCENE))
    def recv_scene_release(self, msg):
        self.midi_button_event("scene_release", msg)

    @midi.handle(dict(type="note_on", note=Button.SHIFT))
    def recv_shift_press(self, msg):
        self.midi_button_event("shift_press", msg)

    @midi.handle(dict(type="note_off", note=Button.SHIFT))
    def recv_shift_release(self, msg):
        self.midi_button_event("shift_release", msg)

    @midi.handle(dict(type="control_change", control__in=Slider.SLIDER))
    def recv_slide(self, msg):
        self.midi_control_event("control_change", msg)


class APCMiniObserver(object):
    """
    Extend to recieve events from the APC Mini
    """
    def on_clip_press(self, source, btn):
        """
        clip button was pressed
        """
        pass

    def on_clip_release(self, source, btn):
        pass

    def on_control_press(self, source, btn):
        pass

    def on_control_release(self, source, btn):
        pass

    def on_shift_press(self, source, btn):
        pass

    def on_shift_release(self, source, btn):
        pass

    def on_scene_press(self, source, btn):
        pass

    def on_scene_release(self, source, btn):
        pass

    def on_control_change(self, source, ctl, value):
        pass


class APCMiniDebugObserver(APCMiniObserver):
    """
    Extend to recieve events from the APC Mini
    """
    def on_clip_press(self, source, btn):
        print("clip_press", btn)

    def on_clip_release(self, source, btn):
        print("clip_release", btn)

    def on_control_press(self, source, btn):
        print("control_press", btn)

    def on_control_release(self, source, btn):
        print("control_release", btn)

    def on_shift_press(self, source, btn):
        print("shift_press", btn)

    def on_shift_release(self, source, btn):
        print("shift_release", btn)

    def on_scene_press(self, source, btn):
        print("scene_press", btn)

    def on_scene_release(self, source, btn):
        print("scene_release", btn)

    def on_control_change(self, source, ctl, value):
        print("control_change", ctl, value)
