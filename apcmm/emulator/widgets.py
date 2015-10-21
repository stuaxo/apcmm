# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty

from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider

from apcmm.api.model import APCMiniModel, GridButton, CLIP_LAUNCH, SCENE_LAUNCH, CONTROL, SHIFT, GridSlider
from apcmm.emulator.buttons import ClipButton, SceneButton, ControlButton, ShiftButton

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

    def blah(self, *args, **kwargs):
        print "blah"
        print "", args
        print "", kwargs



class APCMiniWidget(GridLayout):
    """
    Widget holding all the controls on a real APC Mini.

    buttons are in a dict indexed by note
    sliders are in a dict indexed by control
    """

    #thing = ObjectProperty()

    def __init__(self, *args, **kwargs):
        GridLayout.__init__(self, cols=9, rows=10)   # chuck all the controls into one grid
        model = APCMiniModel()
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
    if isinstance(widget_data, GridButton):
        button_type = widget_data.type
        if button_type == CLIP_LAUNCH:
            return ClipButton(widget_data)
        elif button_type == SCENE_LAUNCH:
            return SceneButton(widget_data)
        elif button_type == CONTROL:
            return ControlButton(widget_data)
        elif button_type == SHIFT:
            return ShiftButton(widget_data)
        else:
            raise ValueError("Unknown button type", widget_data)
    elif isinstance(widget_data, GridSlider):
        return Slider(id=widget_data.name, min=0, max=127, value=63, orientation='vertical', size_hint=(.8, 6))
        ##         slider.bind(value_normalized=self.handle_slide)
    else:
        raise ValueError("Unknown widget type", widget_data)