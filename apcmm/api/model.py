from __future__ import print_function

import weakref

from collections import namedtuple, OrderedDict

from six import with_metaclass
from six.moves import range
from mnd.dispatch import Dispatcher
from mnd.handler import Handler

from enum import Enum

from actions import TRIGGER_PRESS, TRIGGER_LONG_PRESS, TRIGGER_RELEASE, TRIGGER_CHANGE, ControlSource, ButtonSource

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
ClipColors.default = ClipColors.grey

class SceneColors(Enum):
    grey = 0
    green = 1
SceneColors.default = SceneColors.grey

class ControlColors(Enum):
    grey = 0
    red = 1
ControlColors.default = ControlColors.grey


class GridButton(object):

    triggers = ButtonSource

    action_fields = ["type", "n", "note", "x", "y"]

    def __init__(self, type, n, note, x, y, colors=None):
        """
        :param type: one of BUTTON_TYPES
        :param n:    number of this type of button
        :param note: midi note to trigger this button
        :param x:    x on grid
        :param y:    y on grid
        """
        self.type = type
        self.n = n
        self.note = note
        self.x = x
        self.y = y

        self.pressed = False
        self.held = False

        self.valid_colors = colors
        if colors is not None:
            self.light_color = colors.default

        self.color_change_cb = None

    def on_change_color(self, cb):
        self.color_change_cb = cb

    def set_color(self, color):
        """
        Set light color and call callback
        :param color:
        :return:
        """
        self.light_color = color
        f = self.color_change_cb
        if f is not None:
            f(self)

    @property
    def name(self):
        return "%s_%d" % (self.type, self.n)


class GridSlider(object):

    triggers = ControlSource

    action_fields = ["type", "n", "control", "x", "y", "value"]

    def __init__(self, n, control, x, y, value=0):
        """
        :param n: number of this type of button
        :param control: midi control id of this slider
        :param x: x on grid
        :param y: y on grid
        """
        self.type = SLIDER
        self.n = n
        self.control = control
        self.x = x
        self.y = y
        self.value = value

    # def update_value(self, value):
    #     """ :return: copy of slider, with different value """
    #     return GridSlider(self.n, self.control, self.x, self.y, value)

    @property
    def name(self):
        return "%s_%d" % (self.type, self.n)

# Control types  (name is type_id )
CLIP_LAUNCH = "clip"
SCENE_LAUNCH = "scene"
CONTROL = "control"
SHIFT = "shift"
SLIDER = "slider"

BUTTON_TYPES = [CLIP_LAUNCH, CONTROL, SCENE_LAUNCH, SHIFT]

# Button event type
BUTTON_PRESS = "press"
BUTTON_RELEASE = "release"
BUTTON_HOLD = "hold"

# Control event types
CONTROL_CHANGE = "change"


class APCMiniModel(with_metaclass(Handler)):
    def __init__(self):
        self.observers = []

        # setup dicts of the widgets in the grid
        # so it's easy to retrieve them later 

        self.clip_buttons = []                # indexed by scene no / note
        self.control_buttons = OrderedDict()  # indexed by control no
        self.scene_buttons = OrderedDict()    # indexed by scene no

        self.shift_button = None              # the shift button
        self.grid = OrderedDict()             # indexed by (x, y)
        
        self.note_buttons = OrderedDict()     # indexed by note
        self.control_sliders = OrderedDict()  # indexed by control id

        #self.actions = {}                     # { SourceKlass: [actions]

        self.action_types = set()

        # TODO - find out about control buttons

        # 8x8 grid of clip launch buttons, and column of
        # scene launch buttons on the right
        scenes = zip(xrange(8), Button.SCENE).__iter__()
        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                note = (row * 8) + col
                btn = GridButton(CLIP_LAUNCH, note, note, col, row, ClipColors)
                self.clip_buttons.append(btn)
                self.add_grid_button(btn)

            # last column is scene launch
            scene_no, note = next(scenes)
            btn = GridButton(SCENE_LAUNCH, scene_no, note, 9, note, SceneColors)
            self.scene_buttons[note] = btn
            self.add_grid_button(btn)

        # row 8 - control buttons and shift
        for n, note in enumerate(Button.CONTROL):
            btn = GridButton(CONTROL, n, note, n, 8, ControlColors)
            self.control_buttons[n] = btn
            self.add_grid_button(btn)
        else:
            btn = GridButton(SHIFT, 0, Button.SHIFT, n, 8)
            self.add_grid_button(btn)
            self.shift_button = None

        # row 9 - sliders
        for n, control in enumerate(Slider.SLIDER):
            slider = GridSlider(n, control, n, 9)
            self.control_sliders[n] = slider
            self.add_grid_slider(slider)

    def add_grid_button(self, w):
        """
        Add widget with x, y
        """
        self.action_types.add(w.triggers)
        self.grid[(w.x, w.y)] = w
        self.note_buttons[w.note] = w

    def add_grid_slider(self, w):
        """
        Add widget with x, y
        """
        self.action_types.add(w.triggers)
        self.grid[(w.x, w.y)] = w
        self.control_sliders[w.control] = w

    def add_observer(self, o):
        self.observers.append(o)

    def midi_control_event(self, name, msg):
        assert name == "control_change", "Unknown midi event %s" % name
        ctl = self.control_sliders[msg.control]
        for ob in self.observers:
            m = getattr(ob, "on_%s" % name, None)
            m(self, ctl, msg.value)

    def midi_button_event(self, btn_t, event_t, msg):
        """
        :param btn_t: button type (value in BUTTON_TYPES)
        :param ev_type: PRESS, RELEASE or HOLD
        :msg: mido midi msg
        """
        assert btn_t in BUTTON_TYPES, "Unknown midi button event %s" % btn_t
        btn = self.note_buttons[msg.note]
        btn.state = ev_type
        event = "%s_%s" % (btn_t, event_t)
        for ob in self.observers:
            m = getattr(ob, "on_%s" % event, None)
            m(self, btn)

    ### handlers for midi data from APC    
    @midi.handle(dict(type="note_on", note__in=Button.CLIP))
    def recv_clip_press(self, msg):
        self.midi_button_event(CLIP_LAUNCH, BUTTON_PRESS, msg)

    @midi.handle(dict(type="note_off", note__in=Button.CLIP))
    def recv_clip_release(self, msg):
        self.midi_button_event(CLIP_LAUNCH, BUTTON_RELEASE, msg)

    @midi.handle(dict(type="note_on", note__in=Button.CONTROL))
    def recv_control_press(self, msg):
        self.midi_button_event(CONTROL, BUTTON_PRESS, msg)

    @midi.handle(dict(type="note_off", note__in=Button.CONTROL))
    def recv_control_release(self, msg):
        self.midi_button_event(CONTROL, BUTTON_RELEASE, msg)

    @midi.handle(dict(type="note_on", note__in=Button.SCENE))
    def recv_scene_press(self, msg):
        self.midi_button_event(SCENE_LAUNCH, BUTTON_PRESS, msg)

    @midi.handle(dict(type="note_off", note__in=Button.SCENE))
    def recv_scene_release(self, msg):
        self.midi_button_event(SCENE_LAUNCH, BUTTON_RELEASE, msg)

    @midi.handle(dict(type="note_on", note=Button.SHIFT))
    def recv_shift_press(self, msg):
        self.midi_button_event(SHIFT, BUTTON_PRESS, msg)

    @midi.handle(dict(type="note_off", note=Button.SHIFT))
    def recv_shift_release(self, msg):
        self.midi_button_event(SHIFT, BUTTON_RELEASE, msg)

    @midi.handle(dict(type="control_change", control__in=Slider.SLIDER))
    def recv_slide(self, msg):
        # TODO
        self.midi_control_event("control_change", msg)


class APCMiniObserver(object):
    """
    Extend to recieve events from the APC Mini
    """

    def on_press(self, source, btb):
        pass

    def on_hold(self, source, btb):
        pass

    def on_release(self, source, btb):
        pass

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
    Extend to receive events from the APC Mini
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
