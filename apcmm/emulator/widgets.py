# -*- coding: utf-8 -*-
from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from apcmm.emulator.buttons import create_widget


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

class ApcMiniScreen(Screen):
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
    def __init__(self, model=None, *args, **kwargs):
        # TODO setup handlers..
        if model is None:
            # TOOD - this is kind of horrible..
            app = App.get_running_app()
            model = app.virtual_apc
        GridLayout.__init__(self, cols=9, rows=10)   # chuck all the controls into one grid

        self.model = model
        for widget_data in model.grid.values():
            widget = create_widget(widget_data)
            if widget:
                self.add_widget(widget)