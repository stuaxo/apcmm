import argparse
import logging

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

import signal

import apcmm.api.model as model
import apcmm.emulator.widgets as widgets

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = None

class ApcMiniEmu(App):
    DISCONNECTED = "Disconnected"
    DEFAULT_PROFILE = "default"
    virtual_apc = model.APCMiniModel()  # singleton for kv lang
    m = model.APCMiniModel()

    def __init__(self, first_screen=None):
        self.first_screen = first_screen
        self.midi_port = ApcMiniEmu.DISCONNECTED
        self.profile_name = ApcMiniEmu.DEFAULT_PROFILE
        App.__init__(self)

    def build(self):
        sm = ScreenManager()
        sm.add_widget(widgets.PerformanceScreen(name="perform"))
        sm.add_widget(widgets.EditScreen(name="edit"))
        if self.first_screen:
            sm.current = self.first_screen
        return sm

    @property
    def profile_list(self):
        return [ApcMiniEmu.DEFAULT_PROFILE, "test_profile"]

    @property
    def profile_model(self):
        print "return profile model", self.m
        return self.m

    def connect_midi(self, portname):
        self.midi_port = portname

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