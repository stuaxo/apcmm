import argparse
import collections
import logging
from apcmm.api.profile import Profile

import mido

from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

import apcmm.api.model as model
import apcmm.emulator.widgets as widgets

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = None

try:
    import colored_traceback
    colored_traceback.add_hook()
except ImportError:
    pass

class ApcMiniEmu(App):
    DISCONNECTED = "Disconnected"
    DEFAULT_PROFILE = "default"

    profile = ObjectProperty()

    def __init__(self, first_screen=None):
        self.first_screen = first_screen
        self.midi_port = None
        self.profile_name = ApcMiniEmu.DEFAULT_PROFILE

        self.connected_apc = None
        self.profile = Profile.load()

        App.__init__(self)

    def build(self):
        sm = ScreenManager()
        sm.add_widget(widgets.PerformanceScreen(name="perform"))
        sm.add_widget(widgets.EditScreen(name="edit"))
        if self.first_screen:
            sm.current = self.first_screen
        return sm

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
            if self.connected_apc is not None:
                pass  ## send reset
        else:
            self.midi_port = mido.open_ioport(portname, callback=model.midi.dispatch, autoreset=True)
            self.connected_apc = self.profile.virtual_apc.connect_slave(self.midi_port)

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