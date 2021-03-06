from __future__ import print_function

import re

"""
Which sources (controls) can trigger what sort of actions and how (actiontriggers)

Source - a collection of triggers, ie PRESS, RELEASE - TODO - consider merging into ClipButton etc
"""


EVENT_PRESS = "press"
EVENT_LONG_PRESS = "long_press"
EVENT_RELEASE = "release"
EVENT_CHANGE = "control_change" # matches midi event name, don't change
EVENT_TIMEOUT = "timeout"
## EVENT_SLIDE_START = "start_change" # TODO
## EVENT_SLIDE_START = "stop_change" # TODO

ALL_EVENTS = {EVENT_PRESS, EVENT_LONG_PRESS, EVENT_RELEASE, EVENT_CHANGE, EVENT_TIMEOUT}

ACTIONS = {}   # { name: klass }
TRIGGERS = {}  # { name: klass }

ACTION_COLLECTIONS = {}  # { name: klass }

def register_actioncollection(klass):
    """
    Make action available for mappings

    :param klass:
    """
    global ACTION_COLLECTIONS
    ACTION_COLLECTIONS[klass.__name__] = klass


class ActionCollection(object):
    """
    ActionCollections are used by the GUI to group actions,
    e.g. StartStopAction
    """
    def __init__(self, available_actions, **actions):
        self.available_actions = available_actions
        self.actions = {}
        for name, action in actions.items():
            assert name in available_actions
            self.actions[name] = action

    def run_action(self, name):
        ## TODO - needed ??
        action = self.actions.get(name)
        if not action:
            raise ValueError("ActionCollection has no action %s" % name)
        action.run()

    @staticmethod
    def from_dict(profile, d):
        """ construct ActionCollection from dict """
        try:
            args = dict(**d)
            classname = args.pop("class")
            klass = ACTION_COLLECTIONS[classname]
            actions = {}
            for name in klass.ACTION_NAMES:
                action_data = d.get(name)
                if action_data is not None:
                    args[name] = Action.from_dict(profile, action_data)

            return klass(**args)
        except KeyError as e:
            raise ValueError("from_dict missing arg %s " % str(e))


class SingleAction(ActionCollection):
    """
    One action called 'action'
    """
    ACTION_NAMES = ["action"]

    def __init__(self, action=None):
        ActionCollection.__init__(self, self.ACTION_NAMES, action=action)


class StartStopAction(ActionCollection):
    """
    Two actions 'start' and 'end'
    """
    ACTION_NAMES = ["start", "end"]

    def __init__(self, start=None, end=None):
        ActionCollection.__init__(self, self.ACTION_NAMES, start=start, end=end)


register_actioncollection(SingleAction)
register_actioncollection(StartStopAction)

def register_action(klass):
    """
    Make action available for mappings

    :param klass:
    """
    global ACTIONS
    ACTIONS[klass.__name__] = klass


def register_trigger(klass):
    """
    Make trigger available for mappings

    :param klass:
    """
    global TRIGGERS
    TRIGGERS[klass] = klass.get_name()


# ActionTriggers - different ways of triggering actions
#
# e.g. OneShot, Gate, Toggle
class ActionTriggers(object):
    # base class
    def __init__(self, start=None, end=None):
        """
        :param start: triggers that can trigger start
        :param end:   triggers that can trigger end
        :return:
        """
        self.start = start
        self.end = end

    @classmethod
    def get_name(cls):
        return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', cls.__name__)


class OneShot(ActionTriggers):
    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[EVENT_PRESS, EVENT_LONG_PRESS, EVENT_RELEASE, EVENT_CHANGE]
        )


class Gate(ActionTriggers):
    """
    Gate is holding down a button it has a start and end
    """
    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[EVENT_PRESS, EVENT_LONG_PRESS],
            end=[EVENT_RELEASE])


class Toggle(ActionTriggers):
    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[EVENT_PRESS, EVENT_LONG_PRESS],
            end=[EVENT_PRESS, EVENT_LONG_PRESS])


# TODO - rename this lifecycle
register_trigger(Gate)
register_trigger(Toggle)
register_trigger(OneShot)


class Action(object):
    """
    Action base class
    """

    def __init__(self, profile, event):
        self.profile = profile
        self.event = event  # event that triggers this action
        assert event in ALL_EVENTS

    @classmethod
    def get_name(cls):
        return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', cls.__name__)

    @staticmethod
    def from_dict(profile, d):
        """ construct Action from dict """
        try:
            args = dict(**d)
            classname = args.pop("class")
            klass = ACTIONS[classname]
            return klass(profile, **args)
        except KeyError as e:
            raise ValueError("from_dict missing arg %s " % str(e))



##from kivy.lib.osc import oscAPI
import liblo

class SendOSC(Action):
    def __init__(self, profile, event=None, path=None, led=None, data=None):
        """

        :param profile:
        :param event:
        :param path:
        :param led:
        :param data: messages format tuples of fmt, source e.g. ("float", "msg.value")
        :return:
        """
        ## TODO - add list of what to send - "msg.velocity:float"
        Action.__init__(self, profile, event)
        self.path = path
        self.led = led

        settings = self.profile.settings.get("send_osc", {})
        target = settings.get("target")
        if target is not None:
            self.addr, _, self.port = target.partition(":")
        else:
            self.addr, self.port = None, None

        self.target = liblo.Address(self.addr, self.port)
        # TODO - verify path is OK here

        msg_templates = []
        for fmt_str, src_str in data or []:
            if fmt_str == "float":
                fmt = float
            else:
                raise ValueError("Unknown message format %s" % fmt_str)
            msg_templates.append((fmt, src_str))

        self.msg_templates = msg_templates

    def run(self, model, control, event, msg, *args):
        """
        :param source: control that triggered the action
        """
        path = self.path.format(control=control, event=event, msg=msg)
        ##oscAPI.sendMsg(path, dataArray=['answer'], ipAddr=self.addr, port=self.port)

        if self.target:
            osc_msg = liblo.Message(path)

            print("OSC: ", path)
            for fmt, src in self.msg_templates:
                #print("src: '%s'" % src)
                data_str = ("{%s}" % src).format(control=control, event=event, msg=msg)
                #print("src: '%s' data_str: '%s' fmt: '%s' " % (src, data_str, fmt))
                try:
                    data = fmt(data_str)
                    osc_msg.add(data)
                    print(" - ", data)
                except Exception as e:
                    print("Problem converting '%s' to '%s'" % (data_str, fmt))
                    print("- template: '%s'" % src)
            liblo.send(self.target, osc_msg)
        else:
            print("No target address for OSC")

        if self.led:
            try:
                led_color = control.valid_colors[self.led]
                control.set_color(led_color)
            except KeyError:
                print("Invalid LED color ", self.led)
                print("  valid colors: " + ", ".join(color.name for color in control.valid_colors))

register_action(SendOSC)
