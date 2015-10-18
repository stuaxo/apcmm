import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from os.path import abspath, dirname

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from apcmm.api.model import APCMiniModel, ClipColors, ControlColors, SceneColors
from buttons import ClipButton, ControlButton, SceneButton
from widgets import APCMiniWidget

TOGGLE = 1
GATE = 2

__dir__ = dirname(abspath(__file__))
Builder.load_string("""
<ClipButton>:
    Image:
        source: '{__dir__}/clip-button-grey.png'

<SceneButton>:
    Image:
        source: '{__dir__}/round-button-grey.png'

<RoundButton>:
    Image:
        source: '{__dir__}/round-button-grey.png'
""".format(__dir__=__dir__))

class ApcMiniEmu(App):
    def __init__(self):
        App.__init__(self)
        self.virtual_apc = APCMiniModel()

    def build(self):
        layout = BoxLayout(orientation="vertical")

        apcmw = APCMiniWidget(self.virtual_apc)
        layout.add_widget(apcmw)
        # for color in ClipColors:
        #     layout.add_widget(ClipButton(color.value, color.name))
        # for i in xrange(5, 8):
        #     layout.add_widget(ClipButton(i+5))
        #
        # #layout.add_widget(SceneButton(SceneColors.green))
        # layout.add_widget(ControlButton(ControlColors.red))

        #layout.add_widget(SceneButton(SceneColors.grey))
        #layout.add_widget(ControlButton(ControlColors.grey))

        return layout
        

def main():
    try:
        ApcMiniEmu().run()
    except Exception as e:
        print e
        logger.exception(e)
        raise e

if __name__ == "__main__":
    main()
