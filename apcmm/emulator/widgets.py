# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider

import apcmm.api as api
import apcmm.emulator.buttons as buttons

class MidiChooserPopup(Popup):
    def __init__(self, on_change_midi=None, midi_port=None, *args, **kwargs):
        # TODO - select current midi device
        self.on_change_midi = on_change_midi
        super(MidiChooserPopup, self).__init__(*args, **kwargs)
        adapter = self.ids['midi_devices'].adapter
        adapter.select_data_item(midi_port) ## TODO - IS this setting the selection ??
        adapter.bind(on_selection_change=self.select_midi_device)

    def select_midi_device(self, adapter, *args, **kwargs):
        if len(adapter.selection) and self.on_change_midi is not None:
            self.on_change_midi(adapter.selection[0].text)
            self.dismiss()

class PerformanceScreen(Screen):
    model = ObjectProperty()

    def __init__(self, *args, **kwargs):
        Screen.__init__(self, *args, **kwargs)

    def toggle_midi_dropdown(self, btn):
        app = App.get_running_app()
        p = MidiChooserPopup(on_change_midi=self.change_midi_device, midi_port=app.midi_port)
        p.open()

    def change_midi_device(self,  portname):
        app = App.get_running_app()
        app.connect_midi(portname)
        self.ids['toggle_midi_popup'].text = "> %s" % portname


class ActionTitleBar(BoxLayout):
    pass


class ActionEventWidget(BoxLayout):
    """
    one event in an action, e.g. 'start', 'stop'
    """
    name = ObjectProperty()
    action_type = ObjectProperty()

    def __init__(self, *args, **kwargs):
        BoxLayout.__init__(self, *args, **kwargs)
        self.bind(name=self.update_name)
        self.bind(action_type=self.update_trigger)

    def update_trigger(self, widget, trigger):
        assert trigger in ['start', 'end']
        if trigger == 'start':
            # press or long_press
            ## TODO - read this from somewhere
            self.ids['trigger'].text = 'press'
        else:
            # release
            ## TODO - read this from somewhere
            self.ids['trigger'].text = 'release'

    def update_name(self, widget, name):
        self.ids['action'].text = name

    #def update_name(self, widget, value):
    #    self.ids['action'].text = value


class SendOSCAction(ActionEventWidget):
    def __init__(self, *args, **kwargs):
        ActionEventWidget.__init__(self, *args, **kwargs)

    def build(self):
        print("build")


class ActionEditor(FloatLayout):
    pass


class EditScreen(Screen):
    ## profile_model = APCMiniModel()

    model = ObjectProperty()

    def __init__(self, *args, **kwargs):
        Screen.__init__(self, *args, **kwargs)

    def toggle_midi_dropdown(self, btn):
        app = App.get_running_app()
        p = MidiChooserPopup(on_change_midi=self.change_midi_device, midi_port=app.midi_port)
        p.open()

    def change_midi_device(self,  portname):
        app = App.get_running_app()
        app.connect_midi(portname)
        self.ids['toggle_midi_popup'].text = "> %s" % portname


class APCMiniWidget(GridLayout):
    """
    Widget holding all the controls on a real APC Mini.

    buttons are in a dict indexed by note
    sliders are in a dict indexed by control
    """

    def __init__(self, *args, **kwargs):
        GridLayout.__init__(self, cols=9, rows=10)   # chuck all the controls into one grid
        model = api.model.APCMiniModel()
        for widget_data in model.grid.values():
            widget = create_widget(widget_data)
            if widget:
                self.add_widget(widget)
        self.model = model

        #self.bind(thing=self.set_events)

    def set_events(self, *args, **kwargs):
        print "set_events"
        print "", args
        print "", kwargs


def create_widget(widget_data):
    """

    :param widget_data:  models.GridButton or models.GridSlider instance
    :return:
    """
    if isinstance(widget_data, api.model.GridButton):
        button_type = widget_data.type
        if button_type == api.model.CLIP_LAUNCH:
            return buttons.ClipButton(widget_data)
        elif button_type == api.model.SCENE_LAUNCH:
            return buttons.SceneButton(widget_data)
        elif button_type == api.model.CONTROL:
            return buttons.ControlButton(widget_data)
        elif button_type == api.model.SHIFT:
            return buttons.ShiftButton(widget_data)
        else:
            raise ValueError("Unknown button type", widget_data.type)
    elif isinstance(widget_data, api.model.GridSlider):
        return Slider(id=widget_data.name, min=0, max=127, value=63, orientation='vertical', size_hint=(.8, 6))
        ##         slider.bind(value_normalized=self.handle_slide)
    else:
        raise ValueError("Unknown widget type", widget_data.type)