from yaml import load, dump
from apcmm.api.actions import Action


class Mapping(object):
    """
    A mapping, is the link between sources (buttons / controls)
    and actions.
    """
    def __init__(self, name, sources, action):
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

        # TODO - create dispatchers to dispatch events to the actions
        self.dispatchers = []

    @staticmethod
    def from_dict(d):
        """ construct Mapping from dict """
        d = dict(**d)
        name = d.pop("name")
        action_params = d.pop("action")
        action = Action.from_dict(action_params)
        sources = d.get("sources", list())

        mapping = Mapping(name, sources, action)
        return mapping

    def __dict__(self):
        d = {
            "name": self.name,
            "sources": self.sources,
            "action": dict(self.action),
        }
        return d


def load_mappings(filename="default.yaml"):
    """
    :param filename:
    :return: list of mappings
    """

    # TODO
    mappings = [
        {
            "name": "Smiley Control",
            "sources": [{
                "type": "control",  # this will be ANY slider
            }],
            "events": [{
                "type": "control_change",  # recieve any control change
            }],
            "action": {
                "class": "SendOSC",
                "path": "/vis/smilies/{control.id}/amount"
            },
        }
    ]

    print("load mappings...")
    for mapping in mappings:
        print Mapping.from_dict(mapping)

def save_mappings(mappings, filename="default.yaml"):
    """
    :param mappings: list of mappings
    :param filename: filename to save
    :return:
    """
    print dump(mappings, default_flow_style=False)
