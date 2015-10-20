import logging

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager

from apcmm.api.model import APCMiniModel
from apcmm.emulator.widgets import EditScreen, PerformanceScreen

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ApcMiniEmu(App):
    DISCONNECTED = "Disconnected"
    DEFAULT_PROFILE = "default"
    virtual_apc = APCMiniModel()  # singleton for kv lang
    m = APCMiniModel()

    def __init__(self):
        self.midi_port = ApcMiniEmu.DISCONNECTED
        self.profile_name = ApcMiniEmu.DEFAULT_PROFILE
        App.__init__(self)

    def build(self):
        sm = ScreenManager()
        sm.add_widget(PerformanceScreen(name="perform"))
        sm.add_widget(EditScreen(name="edit"))
        return sm

    @property
    def profile_list(self):
        return [ ApcMiniEmu.DEFAULT_PROFILE, "test_profile"]

    @property
    def profile_model(self):
        print "return profile model", self.m
        return self.m

    def connect_midi(self, portname):
        self.midi_port = portname

def main():
    try:
        app = ApcMiniEmu()
        app.run()
    except Exception as e:
        print e
        logger.exception(e)
        raise e

if __name__ == "__main__":
    main()
