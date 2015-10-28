import re

TRIGGER_PRESS = "press"
TRIGGER_LONG_PRESS = "long_press"
TRIGGER_RELEASE = "release"
TRIGGER_CHANGE = "change"


class ButtonSource(object):
    name = "Button"
    triggers = frozenset({TRIGGER_PRESS, TRIGGER_LONG_PRESS, TRIGGER_RELEASE})


class ControlSource(object):
    name = "Control"
    triggers = frozenset({TRIGGER_CHANGE})


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
        self.name = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', self.__class__.__name__)


class GateTriggers(ActionTriggers):
    """
    Gate is holding down a button it has a start and end
    """

    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[TRIGGER_PRESS, TRIGGER_LONG_PRESS],
            end=[TRIGGER_RELEASE])


class ToggleTriggers(ActionTriggers):
    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[TRIGGER_PRESS, TRIGGER_LONG_PRESS],
            end=[TRIGGER_PRESS, TRIGGER_LONG_PRESS])


class OneShotTriggers(ActionTriggers):
    def __init__(self):
        ActionTriggers.__init__(
            self,
            start=[TRIGGER_PRESS, TRIGGER_LONG_PRESS, TRIGGER_RELEASE]
        )


TRIGGER_TYPES = [GateTriggers, ToggleTriggers, OneShotTriggers]


class Action(object):
    """
    Action base class
    """

    def __init__(self):
        print("set name to ", self.name)

    @classmethod
    def get_name(cls):
        return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', cls.__name__)


class SendOSC(Action):
    def __init__(self, settings=None):
        Action.__init__(self)
        self.settings = settings

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


ACTIONS = [SendOSC]
