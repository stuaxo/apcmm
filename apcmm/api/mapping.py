from mnd.handler import bind_instancemethod
from yaml import load, dump
from apcmm.api.actions import Action

from mnd.dispatch import Dispatcher
from actions import ActionCollection

class Mapping(object):
    """
    A mapping, is the link between sources (buttons / controls)
    and actions.
    """
    def __init__(self, name, sources, actioncollection):
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

        # TODO - expand sources

        self.name = name
        self.sources = sources
        self.actioncollection = actioncollection

        d = Dispatcher()
        for source in sources:
            for action in actioncollection.actions.values():
                control = source.get("controls", {})
                bind_instancemethod(action.run, d, control=control, event=action.event) ## accept_args

        self.dispatchers = [d]

    def dispatch_event(self, model, control, event, data):
        for d in self.dispatchers:
            d.dispatch(model, control=control, event=event, data=data)

    @staticmethod
    def from_dict(d):
        """ construct Mapping from dict """
        d = dict(**d)
        name = d.pop("name")

        actions_params = d.pop("actions")
        actions = ActionCollection.from_dict(actions_params)

        sources = d.get("sources", list())
        mapping = Mapping(name, sources, actions)
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

    # TODO - validate that action.event is valid
    # TODO - make sure names are unique
    # TODO - controls needs to be dict

    _mappings = [
        {
            # mapping from sliders
            "name": "Smiley Control #1",
            "sources": [{ ## which controls
                "class": "GridSlider",  # GridSlider or GridButton
                "controls": {
                    "type": "slider",  # obligatory
                    "n__in": [1, 2, 3, 4]
                }
            }],
            "actions": {
                "class": "SingleAction",
                "action": {  ## < this is the key into the action
                "class": "SendOSC",
                "path": "/vis/smilies/{control.n}/amount",
                "event": "control_change"
                }
            },

        },

        {
            # mapping from clip buttons
            "name": "Smiley Control #2",
            "sources": [{ ## which controls
                "class": "GridButton",  # GridSlider or GridButton
                "controls": {
                    "type": "clip",  # obligatory
                }
            }],
            "actions": {
                "class": "StartStopAction",
                "start": {  ## < this is the key into the action
                "class": "SendOSC",
                "path": "/vis/smilies/{control.n}/start_emit",
                "event": "press",
                "led": "yellow",
                },
                "end": {  ## < this is the key into the action
                "class": "SendOSC",
                "path": "/vis/smilies/{control.n}/stop_emit",
                "event": "release",
                "led": "grey",
                },
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
