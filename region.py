import math
import numpy as np
from util import *

class Map(object):
    def __init__(self,
        freq=2.4, power=20,
        trans_gain=0, recv_gain=0,
        size=(24, 24, 24), src_amt=1,
        shadow_dev=2, path_loss=3
        ):

        self.pos = []
        for i in range(src_amt):
            self.pos.append(
                Vector(
                    np.random.randint(0, size[0]),
                    np.random.randint(0, size[1]),
                    np.random.randint(0, size[2])
                )
            )

        # This is where the WiFi map is generated. I had to modify the original algorithm
        # to make it work without rospy, but I'm pretty sure I didn't do anything that would
        # affect the math (intentionally, at least).

        self.rss0 = power + trans_gain + recv_gain + 20 * math.log10(3 / (4 * math.pi * freq * 10))
        normal_dist = np.random.normal(0, shadow_dev, size=[size[0], size[1], size[2]])

        self.grid = []
        for x in range(size[0]):
            self.grid.append([])
            for y in range(size[1]):
                if (x, y) in self.pos:
                    val = power
                else:
                    val = rss0
                    for pos in self.pos:
                        distance = dist((x, y), pos)
                        power = 10 * path_loss * math.log10(distance)
                        if distance > 1:
                            val = val - power + normal_dist[x][y]
                self.grid[x].append(val)
        return self

    def __getitem__(self, item):
        return self.grid[item]

    def __setitem__(self, key, value):
        self.grid[key] = value

    def __delitem__(self, key):
        del self.grid[key]


class Signal(object):
    def __init__(self, pos, freq, power, trans_gain, recv_gain, shadow_dev, path_loss):
        self.pos = pos
        self.freq = freq
        self.power = power
        self.trans_gain = trans_gain
        self.recv_gain = recv_gain
        self.shadow_dev = shadow_dev
        self.path_loss = path_loss

    def sample(self, pos):
        print(f"Unimplemented: Signal.sample({pos})")
        return 0


class Map(object):
    def __init__(self, src_amt, freq=2.4, power=20, trans_gain=0, recv_gain=0, shadow_dev=2, path_loss=3):
        self.signals = []
        for i in range(src_amt):
            self.signals.append(Signal(freq, power, trans_gain, recv_gain, shadow_dev, path_loss))

    def sample(self, pos):
        res = 0
        for signal in self.signals:
            res += signal.sample(pos)
        return res

    def __getitem__(self, item):
        return self.sample(item)

    # def __setitem__(self, key, value):
    #     self.grid[key] = value

    # def __delitem__(self, key):
    #     del self.grid[key]