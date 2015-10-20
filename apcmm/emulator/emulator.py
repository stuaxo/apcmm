import logging

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager

from apcmm.api.model import APCMiniModel
from apcmm.emulator.widgets import ApcMiniScreen

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ApcMiniEmu(App):
    DISCONNECTED = "Disconnected"
    virtual_apc = APCMiniModel()  # singleton for kv lang

    def __init__(self):
        self.midi_port = ApcMiniEmu.DISCONNECTED
        App.__init__(self)

    def build(self):
        sm = ScreenManager()
        sm.add_widget(ApcMiniScreen(name="main_screen"))
        return sm

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
