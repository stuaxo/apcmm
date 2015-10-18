# -*- coding: utf-8 -*-

from kivy.uix.gridlayout import GridLayout
from apcmm.api.model import GridButton, GridSlider
from apcmm.emulator.buttons import create_widget

class APCMiniWidget(GridLayout):
    """
    Widget holding all the controls on a real APC Mini.

    buttons are in a dict indexed by note
    sliders are in a dict indexed by control
    """
    def __init__(self, model, *args, **kwargs):
        GridLayout.__init__(self, cols=9, rows=10)   # chuck all the controls into one grid

        self.model = model
        for widget_data in model.grid.values():
            widget = create_widget(widget_data)
            print "add ", widget
            self.add_widget(widget)

        ## BOTTOM_LABELS = [[u"▲"], [u"▼"], [u"◀"], [u"▶"], ["volume", "pan", "send", "device"], ["shift"]]
        # self.note_buttons = {}
        # self.control_sliders = {}
        #
        # scene_ids = xrange(82, 90).__iter__()
        # for row in xrange(7, -1, -1):
        #     for col in xrange(0, 8):
        #         # first 8 cols are clip launchers
        #         note = (row * 8) + col
        #         self.add_widget( self.create_button("clip_launch_%d" % note, note) )
        #
        #     # last column is scene launch
        #     note = next(scene_ids)
        #     self.add_widget( self.create_button("scene_launch_%d" % row, note) )
        #
        # # row 8 - control buttons and shift
        # for i, note in enumerate(xrange(64, 72)):
        #     self.add_widget( self.create_button("control_%d" % i, note) )
        #
        # self.add_widget( self.create_button("shift", 98) )
        #
        # # row 9 - sliders
        # for i, note in enumerate(xrange(48, 57)):
        #     self.add_widget( self.create_slider("slider_%d" % i, note) )

    def create_button(self, id, note):
        button = MidiButton(note=note, id=id, text="")
        button.bind(on_press=self.handle_press)
        button.bind(on_release=self.handle_release)
        self.note_buttons[note] = button
        return button

    def create_slider(self, id, controller):
        slider = Slider(id=id, min=0, max=127, value=63, orientation='vertical', size_hint=(1. / 9, 8))
        slider.bind(value_normalized=self.handle_slide)
        self.control_sliders[controller] = slider
        return slider

    def clear_clip_lights(self):
        for button in self.note_buttons.values():
            if button.id.startswith('clip_launch_'):
                button.state = 'normal'

    def clear_all_lights(self):
        self.clear_clip_lights()
        

    # def recv_midi(self, msg):
    #     """
    #     Change the state of a button or slider in response to midi
    #     """
    #     if msg.type in ['note_on', 'note_off']:
    #         print 'got midi %s' % msg
    #         button = self.note_buttons.get(msg.note)
    #         if button.id == 'shift':
    #             app = App.get_running_app()
    #             app.do_action(button)
    #             return
    #         if button:
    #             if msg.type == 'note_on':
    #                 print 'set button %s %s' % (button.id, id(button))
    #                 button.state = 'down'
    #                 self.handle_press(button)
    #             elif msg.type == 'note_off':
    #                 button.state = 'normal'
    #                 self.handle_release(button)
    #             button.canvas.ask_update()
    #         else:
    #             print 'no button mapped to note {}'.format(msg.note)
    #     elif msg.type == 'control_change':
    #         slider = self.control_sliders.get(msg.control)
    #         if slider:
    #             slider.value = msg.value
    #             slider.canvas.ask_update()
    #         else:
    #             print 'no slider mapped to control {}'.format(msg.control)
    #
    # def handle_press(self, button):
    #     app = App.get_running_app()
    #     if app.light_behaviour == GATE:
    #         button.light_color = DEFAULT_COLOR
    #         m = mido.Message('note_on', note=button.note, velocity=button.light_color)
    #         app.midiport.send(m)
    #     elif app.light_behaviour == TOGGLE:
    #         if button.light_color is OFF:
    #             button.light_color = DEFAULT_COLOR
    #         else:
    #             curr_index = ALL_SOLID_COLORS.index(button.light_color)
    #             curr_index = (curr_index + 1) % (len(ALL_SOLID_COLORS))
    #             button.light_color = ALL_SOLID_COLORS[curr_index]
    #         m = mido.Message('note_on', note=button.note, velocity=button.light_color)
    #         app.midiport.send(m)
    #
    # def handle_release(self, button):
    #     app = App.get_running_app()
    #     if app.light_behaviour == GATE:
    #         m = mido.Message('note_on', note=button.note, velocity=OFF)
    #         app.midiport.send(m)
    #
    #
    # def handle_slide(self, slider, *args, **kwargs):
    #     try:
    #         print Fore.WHITE, 'slide %s %d' % (slider.id, slider.value)
    #         send_volume( slider.value )
    #         print Fore.WHITE, '/slide'
    #     except Exception as e:
    #         print  Fore.WHITE, '/slide exception HS', e