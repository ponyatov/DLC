import config

class Object:
    def __init__(self, V):
        self.type = self.__class__.__name__.lower()
        self.value = V
        self.slot = {}
        self.nest = []

    def box(self, that):
        if isinstance(that, Object): return that
        raise TypeError(['box', type(that), that])

    ## @name dump

    def __repr__(self): return self.dump(test=False)

    def test(self): return self.dump(test=True)

    def dump(self, cycle=[], depth=0, prefix='', test=False):
        # head
        def pad(depth): return '\n' + '\t' * depth
        ret = pad(depth) + self.head(prefix, test)
        # cycle block
        if not depth: cycle = []
        if self in cycle: return ret + ' _/'
        else: cycle.append(self)
        # slot{}s
        for i in self.keys():
            ret += self[i].dump(cycle, depth + 1, f'{i} = ', test)
        # nest[]ed
        for j, k in enumerate(self):
            ret += k.dump(cycle, depth + 1, f'{j}: ', test)
        # subtree
        return ret

    def head(self, prefix='', test=False):
        gid = '' if test else f' @{id(self):x}'
        return f'{prefix}<{self.type}:{self.value}>{gid}'

    ## @name operator

    def keys(self): return sorted(self.slot.keys())

    def __iter__(self): return iter(self.nest)

    def __floordiv__(self, that):
        self.nest.append(self.box(that)); return self

    def __getitem__(self, key):
        if isinstance(key, str): return self.slot[key]
        if isinstance(key, int): return self.nest[key]
        raise TypeError(['__getitem__', type(key), key])

    def __setitem__(self, key, that):
        that = self.box(that)
        if isinstance(key, str): self.slot[key] = that; return self
        if isinstance(key, int): self.nest[key] = that; return self
        raise TypeError(['__setitem__', type(key), key])

    def __lshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.type, that)

    def __rshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.value, that)
