from yaml import load, dump
from apcmm.api.actions import Action

from mnd.dispatch import Dispatcher
from mnd.handler import bind_instancemethod
from actions import ActionCollection

from six import with_metaclass


class Mapping(object):
    """
    A mapping, is the link between sources (buttons / controls)
    and actions.
    """
    def __init__(self, profile, name, sources, actioncollection):
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

        self.profile = profile
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
    def from_dict(profile, d):
        """ construct Mapping from dict """
        d = dict(**d)
        name = d.pop("name")

        actions_params = d.pop("actions")
        actions = ActionCollection.from_dict(profile, actions_params)

        sources = d.get("sources", list())
        mapping = Mapping(profile, name, sources, actions)
        return mapping

    def __dict__(self):
        d = {
            "name": self.name,
            "sources": self.sources,
            "events": self.events,
            "action": dict(self.action),
        }
        return d
