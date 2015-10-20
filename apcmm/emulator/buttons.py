from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.button import Button
from kivy.uix.slider import Slider

from apcmm.api.model import ClipColors, ControlColors, SceneColors, GridButton, GridSlider, CLIP_LAUNCH, CONTROL, SCENE_LAUNCH, SHIFT


class ClipButton(ButtonBehavior, BoxLayout):
    def __init__(self, widget_data, light_color=ClipColors.grey):
        self.id = widget_data.name
        super(ClipButton, self).__init__()
        self.widget_data = widget_data
        self.light_color = light_color
        self.set_color(light_color)

    def set_color(self, color):
        """
        :param color: one of the values of the ClipColor enum
        """
        self.light_color = color
        self.children[0].source = 'clip-button-%s.png' % color

    def on_press(self):
        #print "%s %s" % (self.note, self.color)
        print "press clip ", self


class RoundButton(ButtonBehavior, BoxLayout):
    def __init__(self, widget_data, valid_colors, light_color):
        self.id = widget_data.name
        super(RoundButton, self).__init__()
        #ButtonBehavior.__init__(self)
        #FloatLayout.__init__(self)
        self.widget_data = widget_data
        self.light_color = light_color
        self.valid_colors = valid_colors
        self.set_color(light_color)

    def set_color(self, color):
        """
        :param color: one of the values in valid_colors enum
        :return:
        """
        assert color in self.valid_colors
        self.light_color = color
        self.children[0].source = "round-button-%s.png" % color.name

    def on_press(self):
        print self.light_color

    def on_release(self):
        print self.light_color


class ControlButton(RoundButton):
    def __init__(self, widget_data, light_color=ControlColors.grey):
        RoundButton.__init__(self, widget_data, ControlColors, light_color)


class SceneButton(RoundButton):
    def __init__(self, widget_data, light_color=SceneColors.grey):
        RoundButton.__init__(self, widget_data, SceneColors, light_color)


class ShiftButton(Button):
    def __init__(self, widget_data):
        self.widget_data = widget_data
        Button.__init__(self, id=str(widget_data.id), text="shift")



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
