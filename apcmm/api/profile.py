from apcmm.api.mapping import Mapping
from yaml import load, dump
from apcmm.api.model import APCMiniModel


class Profile(object):
    def __init__(self, virtual_apc, settings=None, plugins=None):
        self.virtual_apc = virtual_apc
        self.settings = settings
        self.plugins = plugins

    @classmethod
    def load(cls, filename="settings.yaml"):
        with open(filename) as f:
            data = load(f)
            plugins = data.pop("plugins", {})
            settings = data.pop("settings", {})

            # meh, we need a profile to load the mappings :/
            profile = Profile(None, settings=settings, plugins=plugins)
            mappings = []
            for mapping in data.pop("mappings", []):
                mappings.append(Mapping.from_dict(profile, mapping))

            profile.virtual_apc = APCMiniModel(mappings=mappings)

        return profile

    def save(self, filename="settings-output.yaml"):
        data = {}
        mappings_data = [
            dict(mapping) for mapping in self.virtual_apc.mappings
            ]

        data["mappings"] = mappings_data
        data["settings"] = self.settings
        with open(filename, 'rb') as f:
            f.write(dump(data))
