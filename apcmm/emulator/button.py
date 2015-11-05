from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import apcmm.api.model as model


class ClipButton(ButtonBehavior, BoxLayout):
    def __init__(self, data):
        self.id = data.name
        self.data = data
        super(ClipButton, self).__init__()

    def set_color(self, data):
        """
        :param color: one of the values of the ClipColor enum
        """
        self.children[0].source = 'images/clip-button-%s.png' % data.light_color.name

    def on_press(self):
        print "press clip ", self


class RoundButton(ButtonBehavior, BoxLayout):
    def __init__(self, data):
        super(RoundButton, self).__init__()
        self.id = data.name
        self.data = data
        self.set_color(data)

    def set_color(self, data):
        """
        :param color: one of the values in valid_colors enum
        :return:
        """
        self.children[0].source = "images/round-button-%s.png" % data.light_color.name

class ControlButton(RoundButton):
    def __init__(self, data):
        RoundButton.__init__(self, data)

    def on_press(self):
        print self.data.set_color(model.ControlColors.red)

    def on_release(self):
        print self.data.light_color



class SceneButton(RoundButton):
    def __init__(self, data):
        RoundButton.__init__(self, data)

    def on_press(self):
        print self.data.set_color(model.SceneColors.green)

    def on_release(self):
        print self.data.light_color


class ShiftButton(Button):
    def __init__(self, data):
        self.widget_data = data
        Button.__init__(self, id=str(data.name), text="shift")



