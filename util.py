import math
import numpy as np

class Vector(object):
    '''
    A 3D vector.
    '''
    def __init__(self, x, y=None, z=None):
        if y is None or z is None:
            self.val = [x[0], x[1], x[2]]
        else:
            self.val = [x, y, z]

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def distance(self, other):
        return (other - self).length()

    def norm(self):
        return self / self.length()

    def in_circle(self, ctr, rad):
        return self.distance(ctr) <= rad

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    @property
    def xy(self):
        return (self[0], self[1])

    @property
    def xz(self):
        return (self[0], self[2])

    @property
    def yz(self):
        return (self[1], self[2])

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, o):
        if o is Vector:
            return Vector(self.x * o.x, self.y * o.y, self.z * o.z)
        else:
            return Vector(self.x * o, self.y * o, self.z * o)

    def __truediv__(self, o):
        return Vector(self.x / o, self.y / o, self.z / o)

    def __floordiv__(self, o):
        return Vector(self.x // o, self.y // o, self.z // o)

    def __eq__(self, o):
        return self.x == o[0] and self.y == o[1] and self.z == o[2]

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __getitem__(self, item):
        return self.val[item]

    def __setitem__(self, key, value):
        self.val[key] = value

    def __repr__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"

    def __str__(self):
        return f"[{self.x}, {self.y}, {self.z}]"


def rand_in_circle(pos, radius, y_radius=0):
    '''
    Returns a random point in a circle. Not implemented for
    spheres.

    Args:
    * pos: Center of the circle.
    * radius: Radius of the circle on the xz plane.
    * y_radius: Radius of the circle on the yz plane. Not implemented.
    '''
    a = np.random.random() * 2 * math.pi
    r = np.random.random() * radius
    if y_radius > 0:
        # unimplemented
        assert(False)
    else:
        y = 0
    return Vector(r * math.cos(a), y, r * math.sin(a))


def rand_point(rgn):
    '''
    Returns a random point in a region.
    '''
    x = np.random.random() * rgn.size.x - rgn.a.x
    if rgn.a.y == rgn.b.y:
        y = rgn.a.y
    else:
        y = np.random.random() * rgn.size.y - rgn.a.y
    z = np.random.random() * rgn.size.z - rgn.a.z
    return Vector(x, y, z)


def std_dev(arr, mean):
    '''
    Gets the standard deviation of objects in a list, given the mean.
    '''
    acc = 0
    for n in arr:
        acc += (n - mean)**2
    return acc / len(arr)