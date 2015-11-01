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

        # TODO TODO TODO

        # construct action
        self.action = Action.from_dict(action)

    #@staticmethod
    #def from_dict(self, d):
    #    d = dict(**d)
    #    name = d.pop("name")

    def __dict__(self):
        d = {
            "name": self.name,
            "sources": self.sources,
            "action": self.action,
        }
        return d


def load_mappings(filename="default.yaml"):
    """
    :param filename:
    :return: list of mappings
    """
    pass

def save_mappings(mappings, filename="default.yaml"):
    """
    :param mappings: list of mappings
    :param filename: filename to save
    :return:
    """
    pass
