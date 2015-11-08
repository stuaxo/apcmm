# -*- coding: utf-8 -*-
import collections
from kivy.adapters.dictadapter import DictAdapter
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider

import apcmm.api as api
from apcmm.api.actions import EVENT_PRESS, EVENT_CHANGE, EVENT_RELEASE
from apcmm.api.model import SLIDER, CLIP_LAUNCH, SCENE_LAUNCH, CONTROL, BUTTON_TYPES
from apcmm.api.observers import APCMiniObserver
import apcmm.emulator.button as button

def mk_dictadapter(data=None, cls=None, *args, **kwargs):
    """
    Create a DictAdapter where .id of the selected item
    will be the the items key
    """
    items = data.items()

    def _args_converter(i, value):
        """ get key """
        key = items[i][0]
        d = {"id": key, "text": value, "height": 30}
        return d

    return DictAdapter(
        data=data,
        args_converter=_args_converter,
        cls=cls,
        *args,
        **kwargs
    )


class ActionPopup(Popup):
    def __init__(self, on_change_action=None, *args, **kwargs):
        # TODO - select current midi device
        self.on_change_action = on_change_action
        super(ActionPopup, self).__init__(*args, **kwargs)
        adapter = self.ids['items'].adapter
        adapter.bind(on_selection_change=self.select_action)

    def select_action(self, adapter, *args, **kwargs):
        print("select action...")
        if len(adapter.selection) and self.on_change_action is not None:
            self.on_change_action(adapter.selection[0].text)
            self.dismiss()


class MidiChooserPopup(Popup):
    def __init__(self, on_change_midi=None, midi_port=None, *args, **kwargs):
        # TODO - select current midi device
        self.on_change_midi = on_change_midi
        super(MidiChooserPopup, self).__init__(*args, **kwargs)
        adapter = self.ids['items'].adapter
        if midi_port:
            adapter.select_data_item(midi_port) ## TODO - IS this setting the selection ??
        adapter.bind(on_selection_change=self.select_midi_device)

    def select_midi_device(self, adapter, *args, **kwargs):
        if len(adapter.selection) and self.on_change_midi is not None:
            self.on_change_midi(adapter.selection[0].id)
            self.dismiss()


class PerformanceScreen(Screen):
    model = ObjectProperty()

    def __init__(self, *args, **kwargs):
        Screen.__init__(self, *args, **kwargs)

    def toggle_midi_dropdown(self, btn):
        app = App.get_running_app()
        p = MidiChooserPopup(on_change_midi=self.change_midi_device, midi_port=app.midi_port)
        p.open()

    def change_midi_device(self,  portname):
        app = App.get_running_app()
        app.connect_midi(portname)
        self.ids['toggle_midi_popup'].text = "> %s" % portname


# Bottom Bar components
class MappingTitleBar(BoxLayout):
    def __init__(self, *args, **kwargs):
        BoxLayout.__init__(self, *args, **kwargs)

class ActionEventWidget(BoxLayout):
    """
    one event in an action, e.g. 'start', 'stop'
    """
    name = ObjectProperty()
    action = ObjectProperty()

    led_color = ObjectProperty()
    modifier = ObjectProperty()
    #action_type = ObjectProperty()

    # def __init__(self, *args, **kwargs):
    #     BoxLayout.__init__(self, *args, **kwargs)
    #     self.bind(name=self.update_name)
    #     #self.bind(action_type=self.update_trigger)

    def __init__(self, name, action, led_color=None, modifier=None, *args, **kwargs):
        BoxLayout.__init__(self, id=name, *args, **kwargs)
        self.bind(name=self.update_name)
        self.bind(action=self.update_action)
        self.bind(led_color=self.update_led_color)
        self.bind(modifier=self.update_modifier)
        self.name = name
        self.action = action
        self.led_color = led_color
        self.modifier = modifier

    def update_name(self, widget, name):
        self.ids['action'].text = name

    def update_action(self, widget, action):
        self.ids['event'].text = action.event
        # TODO - highlight all affected controls by
        print("update action")
        self.ids["led_dropdown"].clear_widgets()
        self.ids["modifier_dropdown"].clear_widgets()

    def update_led_color(self, widget, led_color):
        #self.ids['action'].text = name
        print "update led color"

    def update_modifier(self, widget, modifier):
        #self.ids['action'].text = name
        print "update modifier"



class MappingEditor(FloatLayout):
    """
    Edit mapping of actions in an ActionCollection
    """

    # TODO - Have a blank mapping instead of manually handling mapping_name

    action_sidebar = ObjectProperty()

    mapping = ObjectProperty()
    mapping_name = StringProperty("")

    def __init__(self, *args, **kwargs):
        FloatLayout.__init__(self, *args, **kwargs)
        self.action_event_widgets = []
        self.mapping_name = ""

    def on_mapping(self, widget, mapping):
        """
        Update widget to show passed in action
        :param widget: source widget
        :param mapping: actioncollection
        :return:
        """
        self.mapping_name = mapping.name

        bottom_bar = self.ids['bottom_bar']
        for widget in self.action_event_widgets:
            bottom_bar.remove_widget(widget)

        for name, action in mapping.actioncollection.actions.items():
            # TODO - pass in led colors here, possibly should have other method for supplementary stuff like led color ??

            widget = ActionEventWidget(name, action)
            self.action_event_widgets.append(widget)
            bottom_bar.add_widget(widget)

    def set_mapping_name(self, name):
        if self.mapping:
            self.mapping_name = name
            self.mapping.name = name

            print self.action_sidebar
            print self.action_sidebar.update_mapping_name(self.mapping, name)


# # Side Bar
# class ActionList(ListView):
#     pass


class MappingAccordionItem(AccordionItem):
    pass

class ActionSideBar(Accordion):
    model = ObjectProperty(None)
    current_mapping = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        Accordion.__init__(self, *args, **kwargs)
        self.open_mapping = None
        #self.on_select(self.on_blah)

        self.mapping_lists = []  ## TODO rename
        self.mapping_buttons = {}

    def on_model(self, widget, model):
        """
        Now model is specified, sort out what types actions to add
        """
        for action_list in self.mapping_lists:
            self.remove_widget(action_list)
        self.mapping_buttons = {}

        # create index of mappings by class
        mapping_idx = collections.defaultdict(set)
        first_containing_item = None
        first_action = None

        for mapping in model.mappings:
            for source in mapping.sources:
                key = (source['class'], source['controls']['type'])
                mapping_idx[key].add(mapping)

        # create sidebar
        for (klassname, typename), emitters in model.event_emitters.items():
            # group accordions by widget type

            mapping_actions = mapping_idx.get((klassname, typename), list())

            pluralise = 's' if len(emitters) > 1 else ''
            if typename in BUTTON_TYPES:
                title = ("%s button%s >" % (typename, pluralise)).capitalize()
            else:
                title = ("%s%s >" % (typename, pluralise)).capitalize()

            accordion_item = MappingAccordionItem(title=title, text_size=(self.width, 0.7))
            if not len(mapping_actions):
                accordion_item.background_color = (0, 0, 0, 0)
            accordion_item.bind(collapse=self.open_group)

            content = BoxLayout(orientation="vertical")
            accordion_item.add_widget(content)
            self.mapping_lists.append(accordion_item)

            for mapping in mapping_actions:
                action_button = Button(text=mapping.name)
                self.mapping_buttons[action_button] = mapping
                action_button.bind(on_release=self.select_mapping)
                content.add_widget(action_button)
                if not first_containing_item:
                    first_containing_item = accordion_item
                    first_action = mapping.actioncollection
            self.add_widget(accordion_item)

        # open first accordion containing anything
        if first_containing_item:
            self.select(first_containing_item)
        if first_action:
            self.current_mapping = first_action

    def open_group(self, item, collapse):
        if collapse is False:
            print item.title
            ## TODO
            ## self.open_mapping

    def update_mapping_name(self, mapping, name):
        """
        Called by the bottom bar, to make the button title match
        the new name
        :param mapping:
        :param name:
        :return:
        """
        for button, button_mapping in self.mapping_buttons.items():
            if mapping == button_mapping:
                button.text = mapping.name

    def select_mapping(self, button):
        mapping = self.mapping_buttons[button]
        self.current_mapping = mapping
        self.action_editor.mapping = mapping


class EditScreen(Screen):
    ## profile_model = APCMiniModel()

    model = ObjectProperty()
    action_editor = ObjectProperty()

    def __init__(self, *args, **kwargs):
        Screen.__init__(self, *args, **kwargs)
        self.actions_dropdown = None
        #self.bind(model=self.update_model)
        #self.model = api.model.APCMiniModel()

    def toggle_add_action_dropdown(self, btn):
        app = App.get_running_app()
        p = ActionPopup(on_change_action=self.add_action)
        p.open()

    def toggle_midi_dropdown(self, btn):
        app = App.get_running_app()
        p = MidiChooserPopup(on_change_midi=self.change_midi_device, midi_port=app.midi_port)
        p.open()

    def add_action(self, action):
        print("add action %s" % action)
        print(self.model)
        #model.add_action(action)

    def change_midi_device(self,  portname):
        app = App.get_running_app()
        try:
            app.connect_midi(portname)
        except Exception as e:
            print(e)
        self.ids['toggle_midi_popup'].text = "> %s" % app.portname

    def on_model(self, widget, model):
        #self.ids['model'].value = model
        print("ES: model changed", widget, model)



class WidgetUpdater(APCMiniObserver):

    def __init__(self, buttons, controls):
        """
        :param buttons: dict {note:button widget}
        :param controls: dict {id:control widget}
        """
        self.buttons = buttons
        self.controls = controls
        APCMiniObserver.__init__(self)

    def on_control_msg(self, event, ctl, msg):
        self.controls[ctl.control].value = msg.value

    #def on_button_msg(self, event, btn, msg):
    #    pass


def mk_event_dispatch(model, widget_data, event_t):
    """
    Create function to dispatch events of event_t
    :param model:
    :param widget_data:
    :param event_t:
    :return:
    """
    def f(widget, *args):
        ev, msg = widget_data.midi_event(event_t)
        model.dispatch_event(widget_data, event_t, msg)
    return f

class APCMiniWidget(GridLayout):
    """
    Widget holding all the controls on a real APC Mini.

    buttons are in a dict indexed by note
    sliders are in a dict indexed by control
    """

    model = ObjectProperty()

    def __init__(self, *args, **kwargs):
        GridLayout.__init__(self, cols=9, rows=10)   # chuck all the controls into one grid

        model = App.get_running_app().profile.virtual_apc
        buttons = {}
        controls = {}

        for widget_data in model.grid.values():
            widget = create_widget(widget_data)
            if widget:
                self.add_widget(widget)

                if widget_data.type == SLIDER:
                    controls[widget_data.control] = widget
                    widget.bind(value=mk_event_dispatch(model, widget_data, EVENT_CHANGE))
                else:
                    buttons[widget_data.note] = widget
                    widget.bind(on_press=mk_event_dispatch(model, widget_data, EVENT_PRESS))
                    widget.bind(on_release=mk_event_dispatch(model, widget_data, EVENT_RELEASE))

                    if widget_data.type in [CLIP_LAUNCH, SCENE_LAUNCH, CONTROL]:
                        widget_data.on_change_color(widget.set_color)

        # WidgetObserver will update gui widgets on midi events
        widget_updater = WidgetUpdater(buttons, controls)
        model.add_observer(widget_updater)

        self.widget_updater = widget_updater
        self.model = model


def create_widget(widget_data):
    """

    :param widget_data:  models.GridButton or models.GridSlider instance
    :return:
    """
    if isinstance(widget_data, api.model.GridButton):
        button_type = widget_data.type
        if button_type == api.model.CLIP_LAUNCH:
            return button.ClipButton(widget_data)
        elif button_type == api.model.SCENE_LAUNCH:
            return button.SceneButton(widget_data)
        elif button_type == api.model.CONTROL:
            return button.ControlButton(widget_data)
        elif button_type == api.model.SHIFT:
            return button.ShiftButton(widget_data)
        else:
            raise ValueError("Unknown button type", widget_data.type)
    elif isinstance(widget_data, api.model.GridSlider):
        return Slider(id=widget_data.name, min=0, max=127, value=63, orientation='vertical', size_hint=(.8, 6))
        ##         slider.bind(value_normalized=self.handle_slide)
    else:
        raise ValueError("Unknown widget type", widget_data.type)