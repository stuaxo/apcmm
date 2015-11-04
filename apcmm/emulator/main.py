import argparse
import collections
import logging

import mido

from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from apcmm.api.mapping import load_mappings
import apcmm.api.model as model
import apcmm.emulator.widgets as widgets

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = None

class ApcMiniEmu(App):
    DISCONNECTED = "Disconnected"
    DEFAULT_PROFILE = "default"

    virtual_apc = ObjectProperty()

    def __init__(self, first_screen=None):
        self.first_screen = first_screen
        self.midi_port = None
        self.profile_name = ApcMiniEmu.DEFAULT_PROFILE

        mappings = load_mappings()
        self.virtual_apc = model.APCMiniModel(mappings=mappings)

        App.__init__(self)

    def build(self):
        sm = ScreenManager()
        sm.add_widget(widgets.PerformanceScreen(name="perform"))
        sm.add_widget(widgets.EditScreen(name="edit"))
        if self.first_screen:
            sm.current = self.first_screen
        return sm

    def set_virtual_apc(self, virtual_apc):
        self.virtual_apc = virtual_apc
        print("VIRTUAL_APC ", self.virtual_apc)

    @property
    def profile_list(self):
        return [ApcMiniEmu.DEFAULT_PROFILE, "test_profile"]

    @property
    def profile_model(self):
        print "return profile model", self.virtual_apc
        return self.virtual_apc

    @profile_model.setter
    def profile_model(self, model):
        print("Set model")
        self.virtual_apc = model

    @property
    def midi_devices(self):
        devices = collections.OrderedDict()
        devices[None] = ApcMiniEmu.DISCONNECTED
        for device in mido.get_ioport_names():
            devices[device] = device

        return devices

    def connect_midi(self, portname):
        if self.midi_port:
            self.midi_port.close()

        #def callback(msg):
        #    print(msg)
        #    model.midi.dispatch(msg)

        if portname is None:
            self.midi_port = None
        else:
            self.midi_port = mido.open_ioport(portname, callback=model.midi.dispatch, autoreset=True)

    @property
    def portname(self):
        """
        Midi port name or DISCONNECTED
        """
        if self.midi_port is None:
            return ApcMiniEmu.DISCONNECTED
        else:
            return self.midi_port.name

def main():
    """
    To use arguments they have to go after kivys ones so do

    apcmm -- -sedit

    (everything before -- is for kivy)
    :return:
    """
    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument("-s", action="store", dest="screen")
    args = parser.parse_args()
    if args.screen is not None:
        if args.screen not in ["edit", "perform"]:
            raise ValueError("Invalid screen")

    try:
        app = ApcMiniEmu(first_screen=args.screen)
        app.run()
    except Exception as e:
        print e
        logger.exception(e)
        raise e