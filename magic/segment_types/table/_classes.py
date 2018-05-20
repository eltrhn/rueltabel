import random

import bidict

class CoordOutOfBoundsError(Exception):
    """
    Raised when |one of a coord's values| > 1
    """
    pass


class Coord(tuple):
    """
    Represents a 'unit coordinate' of a cell.
    """
    _NAMES = bidict.bidict({
      'N': (0, 1),
      'NE': (1, 1),
      'E': (1, 0),
      'SE': (1, -1),
      'S': (0, -1),
      'SW': (-1, -1),
      'W': (-1, 0),
      'NW': (-1, 1)
      })
    _DIRS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
    
    def __init__(self, _):
        if any(i not in {-1, 0, 1} for i in self):
            raise CoordOutOfBoundsError(self)
    
    def __repr__(self):
        return f'Coord({tuple(self)})'
    
    @classmethod
    def from_name(cls, cd):
        return cls(cls._NAMES[cd])
    def diagonal(self):
        return all(self)
    def center(self):
        return not any(self)
    def move(self, cd):
        return getattr(self, cd.lower())
    
    @property
    def name(self):
        return self._NAMES.inv[self]
    @property
    def inv(self):
        return Coord(-i for i in self)
    @property
    def cw(self):
        idx = (1 + self._DIRS.index(self.name)) % 8
        return _MaybeCallableCW(self._NAMES[self._DIRS[idx]])
    @property
    def ccw(self):
        idx = self._DIRS.index(self.name) - 1
        return _MaybeCallableCCW(self._NAMES[self._DIRS[idx]])
    
    @property
    def n(self):
        return Coord((self[0], 1+self[1]))
    @property
    def ne(self):
        return Coord((1+self[0], 1+self[1]))
    @property
    def e(self):
        return Coord((1+self[0], self[1]))
    @property
    def se(self):
        return Coord((1+self[0], self[1]-1))
    @property
    def s(self):
        return Coord((self[0], self[1]-1))
    @property
    def sw(self):
        return Coord((self[0]-1, self[1]-1))
    @property
    def w(self):
        return Coord((self[0]-1, self[1]))
    @property
    def nw(self):
        return Coord((self[0]-1, 1+self[1]))


class _MaybeCallableCW(Coord):
    """
    Allows Coord.cw.cw.cw.cw to be replaced by Coord.cw(4), and so on.
    (The former will still work, however.)
    """
    def __call__(self, num):
        new = self.cw(num-1) if num > 1 else self
        return Coord(new)


class _MaybeCallableCCW(Coord):
    """
    Ditto above, but counterclockwise.
    """
    def __call__(self, num):
        new = self.ccw(num-1) if num > 1 else self
        return Coord(new)


class Variable:
    """
    Represents a variable and how many times it should be
    redefined (to avoid binding) in a Golly table.
    
    Also overrides __hash__ and __eq__ in order to
    allow a Variable in a dict to be referred to by its name.
    """
    __slots__ = 'name', 'rep'
    def __init__(self, name, rep=0):
        self.name = str(name)
        self.rep = rep
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'{type(self).__name__}({self.name!r}, rep={self.rep})'
    
    @classmethod
    def random_name(cls):
        """
        Generates a Variable with a random name.
        Method of random generation liable to change.
        """
        return cls(f'_{random.randrange(10**15)}')


class TabelRange:
    """
    Proxy for a range object.
    TODO: Make this into a proper range subclass whose objects have self.bounds()
    """
    def __new__(cls, span, *, shift=0):
        """
        Returns a workable range object from a tabel's range notation.
        Has to use __new__ like this because range in Python is not an
        acceptable base type.
        """
        # There will only ever be two numbers in the range; offset
        # will be 0 on first pass and 1 on second, so adding it to
        # the given integer will account for python's ranges being
        # exclusive of the end value (it adds one on the 2nd pass)
        return range(*(offset+int(bound.strip()) for offset, bound in enumerate(span.split('..'), shift)))
    
    @staticmethod
    def bounds(span, *, shift=0):
        return [offset+int(bound.strip()) for offset, bound in enumerate(span.split('..'), shift)]