import datetime
import json
import pickle
import uuid


def op_wrap(*args, **kwargs):
    def op(o):
        if isinstance(o, Serializable):
            return o.get_dict(*args, **kwargs)
        elif isinstance(o, uuid.UUID):
            return str(o)
        elif hasattr(o, "__dict__"):
            return o.__dict__
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        else:
            return str(o)

    return op


def json_dumps(
    data, sort_keys=True, indent=None, separators=(",", ":"), *args, **kwargs
):
    """
        Wrapper for json.dumps, with some handy default params, and which uses our own serialization function to enable
        converting a few extra common types to JSON.
        Specifically, 'fixes' TypeError: Object of type 'datetime' is not JSON serializable.
    """
    return json.dumps(
        data,
        default=op_wrap(*args, **kwargs),
        sort_keys=sort_keys,
        indent=indent,
        separators=separators,
    )


class Serializable(object):
    """
        Convenience class for converting between dictionary and JSON representation.
        Uses our own json_dumps function to allow converting additional builtin types into JSON.
        To enable deserializing from JSON containing non-standard types, override the from_json method.
    """

    def to_json(self, *args, **kwargs):
        json_str = json_dumps(self, *args, **kwargs)
        return json_str

    def get_dict(self, *args, **kwargs):
        """
        by default ignore private attributes
        :return:
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def to_json_dict(self, *args, **kwargs):
        return json.loads(self.to_json(*args, **kwargs))

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.get_dict() == other.get_dict()

    def __hash__(self):
        return hash(freeze(self.to_json_dict()))

    @classmethod
    def from_dict(cls, dictionary):
        """override in child classes for deserializing from dictionary"""
        return cls(**dictionary)

    @classmethod
    def from_json(cls, json_str):
        """override in child classes for deserializing from json"""
        json_dict = json.loads(json_str)
        obj = cls.from_dict(json_dict)
        return obj

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return self.to_json()

    def copy(self):
        return self.from_dict(self.get_dict())

    def to_pickle_dict(self):
        return pickle.dumps(self.get_dict())

    @classmethod
    def from_pickle_dict(cls, pick):
        return cls.from_dict(pickle.loads(pick))


def freeze(d):
    if isinstance(d, dict):
        return frozenset((key, freeze(value)) for key, value in d.items())
    elif isinstance(d, list):
        return tuple(freeze(value) for value in d)
    return d
