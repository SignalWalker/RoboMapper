import math
import numpy as np
from util import *

class Map(object):
    '''
    A WiFi map.
    '''
    def __init__(self,
        freq=2.4, power=20,
        trans_gain=0, recv_gain=0,
        size=(24, 24, 24), src_amt=1,
        shadow_dev=2, path_loss=3,
        ):
        '''
        Creates a new WiFi map.

        Args:
        * src_amt: Amount of signal sources.
        * Everything else: Parameters for wifi signal strength equation.
        '''

        self.srcs = []
        for i in range(src_amt):
            self.srcs.append(
                Vector(
                    np.random.randint(0, size[0]),
                    0,
                    np.random.randint(0, size[2])
                )
            )

        self.rss0 = power + trans_gain + recv_gain + 20 * math.log10(3 / (4 * math.pi * freq * 10))
        self.path_loss = path_loss
        self.shadow_dev = shadow_dev
        self.cache = {}
        self.size = size

    def sample(self, pos):
        '''
        Takes a sample from the grid. This is cached so that all samples at a given position
        have the same error.
        '''
        if pos in self.cache:
            return self.cache[pos]
        val = 0
        for src in self.srcs:
            if src == pos:
                val += self.rss0
            else:
                dist = pos.distance(src)
                val += self.rss0 - (10 * self.path_loss * math.log10(dist)) \
                    + np.random.normal(0, self.shadow_dev)
        self.cache[pos] = val
        return val

    def sample_rgn(self, rgn):
        '''
        Runs self.sample() for every point in a Region.
        '''
        res = []
        if rgn.b.y > 0:
            for x in range(rgn.a.x, rgn.b.x):
                res.append([])
                xi = x - rgn.a.x
                for y in range(rgn.a.y, rgn.b.y):
                    res[xi].append([])
                    yi = y - rgn.a.y
                    for z in range(rgn.a.z, rgn.b.z):
                        rgn[xi][yi].append(self.sample(Vector(x, y, z)))
        else:
            for x in range(rgn.a.x, rgn.b.x):
                res.append([])
                xi = x - rgn.a.x
                for z in range(rgn.a.z, rgn.b.z):
                    res[xi].append(self.sample(Vector(x, 0, z)))
        return res

    def __getitem__(self, item):
        return self.sample(item)

class Region(object):
    '''
    A rectangular region.
    '''
    def __init__(self, a, b):
        '''
        Creates a new region.

        Args:
        * a: The first point in the rectangle.
        * b: The second point in the rectangle.
        '''
        if a is not Vector:
            a = Vector(a[0], a[1], a[2])
        if b is not Vector:
            b = Vector(b[0], b[1], b[2])
        self.a = a
        self.b = b

    def contains(self, p):
        '''
        Whether the region contains p, which should be a Vector, a tuple of three numbers, or a list of three numbers.
        '''
        return self.a.x <= p[0] <= self.b.x and self.a.y <= p[1] <= self.b.y and self.a.z <= p[2] <= self.b.z

    @property
    def size(self):
        return self.b - self.a

    def __eq__(self, o):
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.a, self.b))

    def __repr__(self):
        return f"Region({self.a}, {self.b})"

    def __str__(self):
        return f"[{self.a}, {self.b}]"