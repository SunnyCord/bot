import os


def docstring_parameter(*sub):
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj

    return dec


def list_module(directory) -> "list[str]":
    return (f for f in os.listdir(directory) if f.endswith(".py"))
