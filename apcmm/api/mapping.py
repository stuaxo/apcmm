from mnd.handler import bind_instancemethod
from yaml import load, dump
from apcmm.api.actions import Action

from mnd.dispatch import Dispatcher

class Mapping(object):
    """
    A mapping, is the link between sources (buttons / controls)
    and actions.
    """
    def __init__(self, name, sources, events, action):
        """
        :param sources: list of source filters
        :param action: class and params

        example source
        {
            "type": "control"
        }

        example action
        {
            "class": "SendOSC",
            "start": "press",
            "end": "release",
            "path": "/vis/smilies/{control.id}/amount"
        }
        """
        self.name = name
        self.sources = sources
        self.action = action

        d = Dispatcher()
        for source in sources:
            for event in events:
                bind_instancemethod(action.run, d, source=source, event=event) ## accept_args

        self.dispatchers = [d]

    def dispatch_event(self, source, event, data):
        for d in self.dispatchers:
            d.dispatch(source=source, event=event, data=data)

    @staticmethod
    def from_dict(d):
        """ construct Mapping from dict """
        d = dict(**d)
        name = d.pop("name")
        action_params = d.pop("action")
        action = Action.from_dict(action_params)
        sources = d.get("sources", list())
        events = d.get("events", list())

        mapping = Mapping(name, sources, events, action)
        return mapping

    def __dict__(self):
        d = {
            "name": self.name,
            "sources": self.sources,
            "events": self.events,
            "action": dict(self.action),
        }
        return d


def load_mappings(filename="default.yaml"):
    """
    :param filename:
    :return: list of mappings
    """

    # TODO
    _mappings = [
        {
            "name": "Smiley Control",
            "sources": [{
                "type": "slider",  # this will be ANY slider
            }],
            "events": [{
                "type": "control_change",  # receive any control change
            }],
            "action": {
                "class": "SendOSC",
                "path": "/vis/smilies/{source.id}/amount"
            },
        }
    ]

    mappings = []
    for mapping in _mappings:
        mappings.append(Mapping.from_dict(mapping))

    return mappings

def save_mappings(mappings, filename="default.yaml"):
    """
    :param mappings: list of mappings
    :param filename: filename to save
    :return:
    """
    print dump(mappings, default_flow_style=False)
