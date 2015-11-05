from __future__ import print_function

from collections import OrderedDict, defaultdict

from six import with_metaclass
from mnd.dispatch import Dispatcher
from mnd.handler import Handler
from enum import Enum

from six.moves import range
from actions import EVENT_PRESS, EVENT_RELEASE, EVENT_LONG_PRESS, EVENT_CHANGE, SingleAction, StartStopAction

import mido

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

EVENT_SOURCES = {}  # ca;

def register_source(klass):
    """
    Add an event emitter

    :param klass: class that can emit events
    """
    EVENT_SOURCES[klass.__name__] = klass


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
    # TODO - make GridButton a MetaClass so type and colors are baked in
    #        for the others subclasses.

    ##triggers = ButtonSource   # events button can trigger
    emits = frozenset({EVENT_PRESS, EVENT_LONG_PRESS, EVENT_RELEASE})
    action_collection_t = StartStopAction

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

    def event(self, event_t, *data):
        """
        :param event_t:
        :return: event_str

        """
        # TODO - seperate out event creation, once
        #        GridButton is a metaclass
        # TODO - make midi event it's own thing
        if event_t == EVENT_PRESS:
            self.pressed = True
        if event_t == EVENT_LONG_PRESS:
            self.pressed = True
            self.held = True
        elif event_t == EVENT_RELEASE:
            self.pressed = False
            self.held = False
        return "%s_%s" % (self.type, event_t)

    def to_midi(self):
        if self.held or self.pressed:
            return mido.Message(type="note_on", note=self.note)
        else:
            return mido.Message(type="note_off", note=self.note)

    def midi_event(self, event_t, *data):
        """
        Synthesize a midi message to go with an event
        :param event_t:
        :param data:
        :return: event, message
        """
        ev = self.event(event_t, *data)
        msg = self.to_midi()
        return ev, msg

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

    ##triggers = ControlSource   # events control can trigger
    emits = frozenset({EVENT_CHANGE})
    action_collection_t = SingleAction

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

    def event(self, event_t, *data):
        """
        :param event_t:
        :return: return event string
        """
        if event_t == EVENT_CHANGE:
            self.value = data
        return "%s_%s" % (self.type, event_t)

    def to_midi(self):
        # this will always set type to control_change
        return mido.Message(type="control_change", control=self.n)

    def midi_event(self, event_t, *data):
        """
        Synthesize a midi message to go with an event
        :param event_t:
        :param data:
        :return: event, message
        """
        ev = self.event(event_t, *data)
        msg = self.to_midi()
        return ev, msg

    @property
    def name(self):
        return "%s_%d" % (self.type, self.n)

# Control types  (name is type_id)
CLIP_LAUNCH = "clip"
SCENE_LAUNCH = "scene"
CONTROL = "control"
SHIFT = "shift"
SLIDER = "slider"

BUTTON_TYPES = [CLIP_LAUNCH, CONTROL, SCENE_LAUNCH, SHIFT]

# Button event type
#BUTTON_PRESS = "press"
#BUTTON_RELEASE = "release"
#BUTTON_HOLD = "hold"

# Control event types
#CONTROL_CHANGE = "change"

# class APCMiniLayout(object):
#     def __init__(self):
#         # TODO - find out what control buttons are for in Ableton
#
#         # 8x8 grid of clip launch buttons, and column of
#         # scene launch buttons on the right
#         scenes = zip(xrange(8), Button.SCENE).__iter__()
#         for row in xrange(7, -1, -1):
#             for col in xrange(0, 8):
#                 note = (row * 8) + col
#                 btn = GridButton(CLIP_LAUNCH, note, note, col, row, ClipColors)
#                 self.clip_buttons.append(btn)
#                 self.add_grid_button(btn)
#
#             # last column is scene launch
#             scene_no, note = next(scenes)
#             btn = GridButton(SCENE_LAUNCH, scene_no, note, 9, note, SceneColors)
#             self.scene_buttons[note] = btn
#             self.add_grid_button(btn)
#
#         # row 8 - control buttons and shift
#         for n, note in enumerate(Button.CONTROL):
#             btn = GridButton(CONTROL, n, note, n, 8, ControlColors)
#             self.control_buttons[n] = btn
#             self.add_grid_button(btn)
#         else:
#             btn = GridButton(SHIFT, 0, Button.SHIFT, n, 8)
#             self.add_grid_button(btn)
#             self.shift_button = btn
#
#         # row 9 - sliders
#         for n, control in enumerate(Slider.SLIDER):
#             slider = GridSlider(n, control, n, 9)
#             self.control_sliders[n] = slider
#             self.add_grid_slider(slider)


class APCMiniModel(with_metaclass(Handler)):
    # TODO - is model something like 'layout'
    def __init__(self, mappings=None, observers=None):
        """
        :param mappings: sequence of Mapping Objects or None
        :return:
        """
        if observers is None:
            self.observers = []
        else:
            self.observers = list(observers[:])

        # setup dicts of the widgets in the grid
        # so it's easy to retrieve them later 

        self.clip_buttons = []                  # indexed by scene no / note
        self.control_buttons = OrderedDict()    # indexed by control no
        self.scene_buttons = OrderedDict()      # indexed by scene no

        self.shift_button = None                # the shift button
        self.grid = OrderedDict()               # indexed by (x, y)
        
        self.note_buttons = OrderedDict()       # indexed by note
        self.control_sliders = OrderedDict()    # indexed by control id

        if mappings is None:
            self.mappings = []                  # { name: [actions]
        else:
            #self.mappings = {mapping.name: mapping for mapping in mappings}
            self.mappings = list(mappings)

        self.event_emitters = \
            defaultdict(list)  # { (klassname, w.type) : [widget_data, ...] }

        # TODO - find out what control buttons are for in Ableton

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
            self.shift_button = btn

        # row 9 - sliders
        for n, control in enumerate(Slider.SLIDER):
            slider = GridSlider(n, control, n, 9)
            self.control_sliders[n] = slider
            self.add_grid_slider(slider)

    def add_grid_button(self, w):
        """
        Add widget with x, y
        """
        self.event_emitters[(w.__class__.__name__, w.type)].append(w)
        self.grid[(w.x, w.y)] = w
        self.note_buttons[w.note] = w

    def add_grid_slider(self, w):
        """
        Add widget with x, y
        """
        self.event_emitters[(w.__class__.__name__, w.type)].append(w)
        self.grid[(w.x, w.y)] = w
        self.control_sliders[w.control] = w

    def add_observer(self, o):
        self.observers.append(o)

    def dispatch_event(self, source, event, data):
        for mapping in self.mappings:
            mapping.dispatch_event(source, event, data)

    def midi_control_event(self, event_t, msg):
        assert event_t == EVENT_CHANGE, "Unknown midi event %s" % event_t
        ctl = self.control_sliders[msg.control]
        ctl.value = msg.value ## TODO - should probably be returning a new instance
        for ob in self.observers:
            m = getattr(ob, "on_control_msg", None)
            m(self, ctl, msg)

            m = getattr(ob, "on_%s" % event_t, None)
            m(self, ctl, msg.value)

        self.dispatch_event(ctl, event_t, msg)

    def midi_button_event(self, btn_t, event_t, msg):
        """
        :param btn_t: button type (value in BUTTON_TYPES)
        :param ev_type: PRESS, RELEASE or HOLD
        :param msg: mido midi msg
        """
        assert btn_t in BUTTON_TYPES, "Unknown midi button event %s" % btn_t
        btn = self.note_buttons[msg.note]
        event = btn.event(event_t)
        for ob in self.observers:
            m = getattr(ob, "on_button_msg", None)
            m(self, btn, msg)

            m = getattr(ob, "on_%s" % event, None)
            m(self, btn)

        self.dispatch_event(btn, event_t, msg)

    ### handlers for midi data from APC    
    @midi.handle(dict(type="note_on", note__in=Button.CLIP))
    def recv_clip_press(self, msg):
        self.midi_button_event(CLIP_LAUNCH, EVENT_PRESS, msg)

    @midi.handle(dict(type="note_off", note__in=Button.CLIP))
    def recv_clip_release(self, msg):
        self.midi_button_event(CLIP_LAUNCH, EVENT_RELEASE, msg)

    @midi.handle(dict(type="note_on", note__in=Button.CONTROL))
    def recv_control_press(self, msg):
        self.midi_button_event(CONTROL, EVENT_PRESS, msg)

    @midi.handle(dict(type="note_off", note__in=Button.CONTROL))
    def recv_control_release(self, msg):
        self.midi_button_event(CONTROL, EVENT_RELEASE, msg)

    @midi.handle(dict(type="note_on", note__in=Button.SCENE))
    def recv_scene_press(self, msg):
        self.midi_button_event(SCENE_LAUNCH, EVENT_PRESS, msg)

    @midi.handle(dict(type="note_off", note__in=Button.SCENE))
    def recv_scene_release(self, msg):
        self.midi_button_event(SCENE_LAUNCH, EVENT_RELEASE, msg)

    @midi.handle(dict(type="note_on", note=Button.SHIFT))
    def recv_shift_press(self, msg):
        self.midi_button_event(SHIFT, EVENT_PRESS, msg)

    @midi.handle(dict(type="note_off", note=Button.SHIFT))
    def recv_shift_release(self, msg):
        self.midi_button_event(SHIFT, EVENT_RELEASE, msg)

    @midi.handle(dict(type="control_change", control__in=Slider.SLIDER))
    def recv_slide(self, msg):
        self.midi_control_event(EVENT_CHANGE, msg)


register_source(GridButton)
register_source(GridSlider)