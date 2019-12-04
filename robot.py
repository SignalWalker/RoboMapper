from model import *
from region import *
import math

class Robot(object):
    def __init__(self, grid, model, pos, move_range):
        assert(isinstance(grid, Map))
        assert(isinstance(model, Model))
        assert(isinstance(pos, Vector))
        self.model = model
        self.map = grid
        # The current position of the robot
        self.pos = pos
        self.dest = self.pos
        self.move_range = move_range
        self.sample_amt = 0

    def guess(self):
        # I don't know what happens if you try to make a GP model
        # without any inputs, and I don't trust Python to give me
        # helpful error messages.
        if len(self.model.input) == 0:
            return Vector(0, 0, 0), 0
        else:
            prediction = self.model.predict(Region((0,0,0), self.map.size))
            pos = prediction.sorted_mean[0][0]
            return pos, prediction.var[pos.x][pos.y][pos.z]

    def take_sample(self):
        self.model.sample(self.pos, self.map.sample(self.pos))
        self.sample_amt += 1

    def update_dest(self):
        print("Generic Point Selection Called!")

    def done(self):
        print("Generic done() called!")
        return True

    def move_towards_dest(self):
        dir_vec = self.dest - self.pos
        if dir_vec.length() <= self.move_range:
            self.pos = self.dest
        else:
            dir_vec = dir_vec.norm() * self.move_range
            self.pos += dir_vec

    def find_source(self, rmse_log=None, display=0):
        self.take_sample()
        i = 0
        while not self.done():
            self.move_towards_dest()
            print(self.pos)
            self.take_sample()
            if self.pos == self.dest:
                self.update_dest()
            if display is not True and display > 1 and i % display == 0:
                self.display()
            i += 1

        if display is True or display >= 1:
            self.display()

        if rmse_log is not None:
            rmse_log.append(rmse(self.map, self.model))

        return i

    def display(self):
        mean, var, max_mean, max_var = self.model.prediction
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)

        # [0,0] is the top left; Y increases as you move downward
        gimg = fig.add_subplot(gs[0, 0])
        gimg.imshow(self.grid.grid, origin='lower', label="WiFi Map")

        mimg = fig.add_subplot(gs[0, 1])
        mimg.imshow(mean, origin='lower', label="Mean")

        vimg = fig.add_subplot(gs[1, 0])
        vimg.imshow(var, origin='lower', label="Variance")

        # model.plot() gives a weird error when I try to use it like this, so I've
        # disabled it here for now. The mean plot displays mostly the same information,
        # anyway.

        # mplot = fig.add_subplot(gs[1, 1])
        # self.model.plot(mplot)


class UGV(Robot):
    def __init__(self, grid, model, pos, move_range, rgn, samples, rand=False):
        super(UGV, self).__init__(grid, model, pos, move_range)
        self.rgn = rgn
        self.rand = rand
        self.start = self.pos
        self.samples = samples

    def update_dest(self):
        if self.rand:
            self.dest = rand_in_circle(self.pos, self.move_range)
        else:
            pred = self.model.predict(self.rgn)
            self.dest = pred.sorted_mean[0][0]
            # print(f"Sorted: {pred.sorted_mean}")
            # print(f"UGV Dest: {self.dest}")
        self.samples -= 1

    def done(self):
        return self.samples == 0


class UAV(Robot):
    def __init__(self, grid, rgn, model, mv_radius, sample_rows):
        self.buf = rgn.size.x / sample_rows / 2
        self.step = rgn.size.z / sample_rows
        pos = Vector(self.buf, rgn.a.y + rgn.size.y / 2, self.step / 2)
        super(UAV, self).__init__(grid, model, pos, mv_radius)
        self.rgn = rgn
        self.row_state = True
        self.rows = sample_rows

    def update_dest(self):
        x, z = self.pos.x, self.pos.z
        if self.row_state:
            # Going left
            if self.pos[0] > self.rgn.size.x / 2:
                x = self.buf
            else:  # Going right
                x = self.rgn.size.x - self.buf
            self.rows = self.rows - 1
        else:
            z += self.step
        self.row_state = not self.row_state
        self.dest = Vector(x, self.pos.y, z)

    def done(self):
        return self.rows == 0

    def suggest(self):
        wsize = Vector(min(3, self.map.size[0]), min(1, self.map.size[1]), min(3, self.map.size[2]))
        rgn = Region(
            (self.rgn.a.x, self.rgn.a.y, self.rgn.a.z),
            (self.rgn.b.x, self.rgn.a.y, self.rgn.b.z)
        )
        pred = self.model.predict(rgn)
        highest = None
        h_rgn = rgn
        for wx in range(rgn.a.x, rgn.b.x - wsize.x):
            for wz in range(rgn.a.z, rgn.b.z - wsize.z):
                w_rgn = Region((wx, 0, wz), (wx + wsize.x, 0, wz + wsize.z))
                avg = 0
                i = 0
                for x in range(w_rgn.a.x, w_rgn.b.x):
                    for z in range(w_rgn.a.z,  w_rgn.b.z):
                        avg += pred.mean[x][0][z][1]
                        i += 1
                avg /= i
                if highest is None or abs(avg) > abs(highest):
                    h_rgn = w_rgn
                    highest = avg
        print(f"Suggestion: {highest} @ {h_rgn}")
        return h_rgn