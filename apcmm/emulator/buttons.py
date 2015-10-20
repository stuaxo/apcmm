from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.button import Button
from kivy.uix.slider import Slider

from apcmm.api.model import ClipColors, ControlColors, SceneColors, GridButton, GridSlider, CLIP_LAUNCH, CONTROL, SCENE_LAUNCH, SHIFT


class ClipButton(ButtonBehavior, BoxLayout):
    def __init__(self, data):
        self.id = data.name
        self.data = data
        super(ClipButton, self).__init__()

    def set_color(self, color):
        """
        :param color: one of the values of the ClipColor enum
        """
        self.children[0].source = 'images/clip-button-%s.png' % color

    def on_press(self):
        print "press clip ", self


class RoundButton(ButtonBehavior, BoxLayout):
    def __init__(self, data):
        super(RoundButton, self).__init__()
        self.id = data.name
        self.data = data
        self.set_color(data)

        data.on_change_color(self.set_color)

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
        print self.data.set_color(ControlColors.red)

    def on_release(self):
        print self.data.light_color



class SceneButton(RoundButton):
    def __init__(self, data):
        RoundButton.__init__(self, data)

    def on_press(self):
        print self.data.set_color(SceneColors.green)

    def on_release(self):
        print self.data.light_color


class ShiftButton(Button):
    def __init__(self, data):
        self.widget_data = data
        Button.__init__(self, id=str(data.name), text="shift")



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
