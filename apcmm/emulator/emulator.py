import logging
from kivy.uix.screenmanager import Screen, ScreenManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from kivy.config import Config

from os.path import abspath, dirname

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from apcmm.api.model import APCMiniModel, ClipColors, ControlColors, SceneColors
from buttons import ClipButton, ControlButton, SceneButton
from widgets import APCMiniWidget

import logging
logging.getLogger("kivy").disabled = True

# TOGGLE = 1
# GATE = 2
#
# __dir__ = dirname(abspath(__file__))
# Builder.load_string("""
# <ClipButton>:
#     Image:
#         source: '{__dir__}/clip-button-grey.png'
#
# <SceneButton>:
#     Image:
#         source: '{__dir__}/round-button-grey.png'
#
# <RoundButton>:
#     Image:
#         source: '{__dir__}/round-button-grey.png'
# """.format(__dir__=__dir__))


class ApcMiniScreen(Screen):
    pass

class ApcMiniEmu(App):
    def __init__(self):
        ApcMiniEmu.virtual_apc = APCMiniModel()  # singleton :/
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
