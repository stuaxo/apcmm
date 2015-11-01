import re

"""
Which sources (controls) can trigger what sort of actions and how (actiontriggers)

Source - a collection of triggers, ie PRESS, RELEASE - TODO - consider merging into ClipButton etc


"""


TRIGGER_PRESS = "press"
TRIGGER_LONG_PRESS = "long_press"
TRIGGER_RELEASE = "release"
TRIGGER_CHANGE = "change"

ACTIONS = {}   # { name: klass }
TRIGGERS = {}  # { name: klass }


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


class ButtonSource(object):
    name = "Button"
    triggers = frozenset({TRIGGER_PRESS, TRIGGER_LONG_PRESS, TRIGGER_RELEASE})


class ControlSource(object):
    name = "Control"
    triggers = frozenset({TRIGGER_CHANGE})


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
            start=[TRIGGER_PRESS, TRIGGER_LONG_PRESS, TRIGGER_RELEASE]
        )


class Gate(ActionTriggers):
    """
    Gate is holding down a button it has a start and end
    """
    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[TRIGGER_PRESS, TRIGGER_LONG_PRESS],
            end=[TRIGGER_RELEASE])


class Toggle(ActionTriggers):
    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[TRIGGER_PRESS, TRIGGER_LONG_PRESS],
            end=[TRIGGER_PRESS, TRIGGER_LONG_PRESS])


register_trigger(Gate)
register_trigger(Toggle)
register_trigger(OneShot)


class Action(object):
    """
    Action base class
    """

    def __init__(self):
        #print("set name to ", self.name)
        pass

    @classmethod
    def get_name(cls):
        return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', cls.__name__)

    @staticmethod
    def from_dict(d):
        # construct Action from dict
        try:
            args = dict(**d)
            classname = args.pop("class")
            klass = ACTIONS[classname]
            return klass(**args)
        except KeyError as e:
            raise ValueError("from_dict missing arg %s " % str(e))


class SendOSC(Action):
    def __init__(self, start=None, end=None, path=None):
        Action.__init__(self)
        self.start = start
        self.end = end
        self.path = path

    def start_action(self, source):
        """
        :param source: what triggered the action
        """
        print("send an osc message")
        print source.note

    def stop_action(self, source):
        """
        :param source: what triggered the action
        """
        print("stop ")


register_action(SendOSC)
