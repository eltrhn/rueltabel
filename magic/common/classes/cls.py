import re

import bidict

from .. import utils
from . import errors


class AdditiveDict(dict):
    def __init__(self, it):
        for key, val in it:
            self[str(key)] = self.get(key, 0) + int(val or 1)
    
    def expand(self):
        return (i for k, v in self.items() for i in k*v)


class ConflictHandlingBiDict(bidict.bidict):
    """
    A dict allowing for key-conflict handling.
    """
    @staticmethod
    def __conflict_handler(self, key, value):
        """
        Meant to be overwritten.
        A function replacing this needs to have a type signature of
        
        self, key, value
        
        It also needs to return a (key, value) tuple or if not then
        raise some fatal exception.
        """
        raise errors.KeyConflict(f"Key '{key}' already has a value of {value!r}")
    
    def __init__(self, seq=None, **kwargs):
        super().__init__()
        self.reset_handler()
        self.update(seq, **kwargs)
    
    def __setitem__(self, key, value):
        if key in self:
            key, value = self.conflict_handler(self, key, value)
        super().__setitem__(key, value)
    
    def update(self, seq=None, **kwargs):
        if seq:
            for key, value in dict(seq).items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value
    
    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]
    
    def flip(self):
        self, self.inv = self.inv, self

    def reset_handler(self):
        self.conflict_handler = self.inv.conflict_handler = self.__conflict_handler    

    def set_handler(self, handler: callable):
        self.conflict_handler = self.inv.conflict_handler = handler

    
class Variable:
    __slots__ = 'name', 'reps'
    def __init__(self, name, reps=0):
        self.name = name
        self.reps = reps
