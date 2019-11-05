import math

class Vector(object):
    def __init__(self, x, y, z):
        self.val = [x, y, z]

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def distance(self, other):
        return (other - self).length()

    def norm(self):
        return self / self.length()

    def in_circle(self, ctr, rad):
        return self.distance(ctr) <= rad

    def in_rgn(self, rgn):
        return rgn[0].x <= self.x < rgn[1].x \
        and rgn[0].y <= self.y < rgn[1].y \
        and rgn[0].z <= self.z < rgn[1].z

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, o):
        return Vector(self.x * o, self.y * o, self.z * o)

    def __truediv__(self, o):
        return Vector(self.x / o, self.y / o, self.z / o)

    def __getitem__(self, item):
        return self.val[item]

    def __setitem__(self, key, value):
        self.val[key] = value


def rand_point(size, pos=None, radius=None):
    if pos is not None and radius is not None:
        a = random.random() * 2 * math.pi
        r = radius * math.sqrt(random.random())
        return int(r * math.cos(a)), int(r * math.sin(a))
    else:
        return random.randrange(size[0]), random.randrange(size[1])


def rmse(grid, model):
    mean, var, m_mean, m_var = model.prediction
    acc = 0
    num = 0
    for x in range(grid.size[0]):
        for y in range(grid.size[1]):
            p = mean[x][y]
            o = grid[x][y]
            acc += (p - o)**2
            num += 1
    return math.sqrt(acc / num)


def deres(grid, amt=2):
    assert len(grid) == len(grid[0])
    s = len(grid)
    hs = int(s / amt)
    res = []
    for mx in range(0, hs):
        res.append([])
        for my in range(0, hs):
            avg = 0
            sx = mx * amt
            sy = my * amt
            for x in range(sx, sx + amt):
                for y in range(sy, sy + amt):
                    avg = avg + grid[x][y]
            res[mx].append(avg / (amt**2))
    return res


def std_dev(arr, mean):
    acc = 0
    for n in arr:
        acc += (n - mean)**2
    return acc / len(arr)