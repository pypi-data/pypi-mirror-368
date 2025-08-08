# this class populates an attribute-style access dictionary (main.sub.subsub) from a dict object

class AttrDict(object):

    def __init__(self, inputDict):
        for key, value in inputDict.items():
            if isinstance(value, dict):
                setattr(self, key, AttrDict(value))
            elif isinstance(value, (list, tuple)):
                setattr(self, key, [AttrDict(x) if isinstance(x, dict) else x for x in value])
            else:
                setattr(self, key, value)

