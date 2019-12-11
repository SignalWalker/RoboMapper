from model import *
from region import *
import math

class Robot(object):
    '''
    An abstract class for simulated robots.
    '''
    def __init__(self, grid, model, pos, move_range, update_per_sample, rmse_log_interval, plt_lbl=None):
        '''Create a new robot.
        Arguments:
        * grid: The region.Map on which to operate
        * model: The GP model to sample to/from
        * pos: Initial position
        * move_range: Movement radius of the robot
        * update_per_sample: Whether to update destination on each sample, or just on arrival at the previous destination
        * rmse_log_interval: How often to check RMSE. (It's slow to do so.)
        * plt_lbl: The label for matplotlib plots from this robot.
        '''
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
        self.update_per_sample = update_per_sample
        self.plt_lbl = plt_lbl

        self.log_interval = rmse_log_interval

    def guess(self):
        '''
        Make a guess about where the WiFi source is. This doesn't actually work right now;
        it's a holdover from an earlier version. It was easier to leave it in than to remove it.
        '''
        # I don't know what happens if you try to make a GP model
        # without any inputs, and I don't trust Python to give me
        # helpful error messages.
        if len(self.model.input) == 0:
            return Vector(0, 0, 0), 0
        else:
            prediction = self.model.predict(Region((0,0,0), self.map.size))
            pos = prediction.sorted_mean[0][0]
            if self.map.size[1] > 0:
                return pos, prediction.var[pos.x][pos.y][pos.z]
            else:
                return pos, prediction.var[pos.x][pos.z]

    def take_sample(self):
        '''
        Take a sample at the current position and add it to the model.
        '''
        self.model.sample(self.pos, self.map.sample(self.pos))
        self.sample_amt += 1
        if self.log_interval != 0 and self.sample_amt % self.log_interval == 0:
                self.model.log_rmse(self.map)


    def update_dest(self):
        '''
        Choose a destination to travel to.
        '''
        print("Generic Point Selection Called!")

    def done(self):
        '''
        Decide whether this robot is done taking samples.
        '''
        print("Generic done() called!")
        return True

    def move_towards_dest(self):
        '''
        Move the robot toward its current destination by {self.move_range} meters.
        '''
        dir_vec = self.dest - self.pos
        if dir_vec.length() <= self.move_range:
            self.pos = self.dest
        else:
            dir_vec = dir_vec.norm() * self.move_range
            self.pos += dir_vec

    def find_source(self, display=0):
        '''
        Simulate the robot.
        '''
        # Take a sample from the starting position
        self.take_sample()
        # Keep track of this for the random UGV
        # Until the robot is done taking samples (usually when it's reached a max sample amt)
        while not self.done():
            self.move_towards_dest()
            # Take a sample at each stop
            self.take_sample()
            if self.update_per_sample or self.pos == self.dest:
                # Update destination, if applicable
                self.update_dest()
            # Display a set of plots, if asked for
            if display is not True and display > 0 and self.sample_amt % display == 0:
                self.display(label=self.plt_lbl)

        # Display final plot
        if display is True or display > 0:
            self.display(label=self.plt_lbl)

        return self.sample_amt

    def display(self, rgn=None, label=None):
        '''
        Display current prediction and RMSE using matplotlib.
        '''
        import matplotlib.pyplot as plt
        # print(f"Label: {label}")
        if label is None:
            label = ""
        else:
            label = f": {label}"
        if rgn is None:
            rgn = Region((0, 0, 0), self.map.size)
        assert(rgn.b.y == 0)
        pred = self.model.predict(rgn)
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)

        gcon = fig.add_subplot(gs[0, 0], title=f"Real Map{label}")
        gcon.imshow(self.map.sample_rgn(rgn), origin="lower")

        mean, var = pred.cleaned_vals()

        mcon = fig.add_subplot(gs[0, 1], title=f"Predicted Mean{label}")
        mcon.imshow(mean, origin="lower")

        vcon = fig.add_subplot(gs[1, 0], title=f"Prediction Variance{label}")
        vcon.imshow(var, origin="lower")

        rplt = fig.add_subplot(gs[1, 1], title=f"RMSE{label}", xlabel="Samples", ylabel="RMSE")
        rplt.plot(self.model.rmse_log)

        fig.show()


class UGV(Robot):
    '''
    A simulated ground vehicle that either chooses destinations randomly or chooses the least certain point.
    '''
    def __init__(self, grid, model, pos, move_range, rgn, samples, rand=False, rmse_log_interval=0):
        '''
        Create a new UGV.
        Args (that aren't in the Robot class):
        * rgn: Region in which to operate (usually smaller than the grid)
        * samples: Total samples to take.
        * rand: Whether to choose destinations randomly
        '''
        if rand:
            lbl = "Random"
        else:
            lbl = f"UGV"
        super(UGV, self).__init__(grid, model, pos, move_range, True, rmse_log_interval, plt_lbl=lbl)
        self.rgn = rgn
        self.rand = rand
        self.start = self.pos
        self.samples = samples
        self.total_samples = samples

    def update_dest(self):
        if self.rand:
            self.dest = rand_point(self.rgn)
        else:
            pred = self.model.predict(self.rgn)
            self.dest = pred.sorted_var[0][0]
        self.samples -= 1

    def done(self):
        if self.rand:
            return self.sample_amt == self.total_samples
        else:
            return self.samples == 0


class UAV(Robot):
    '''
    A simulated air vehicle that takes samples along an algorithmically determined path.
    '''
    def __init__(self, grid, rgn, model, y_pos, sample_rows, rmse_log_interval=0):
        '''
        Create a new UAV. Move radius is (rgn.size.z / sample_rows) / 2
        Args (that aren't in the robot class):
        * rgn: Region in which to operate
        * y_pos: Height of the UAV (if none, half the height of the region)
        * sample_rows: Number of rows of samples to take.
        '''
        self.buf = rgn.size.x / sample_rows / 2
        self.step = rgn.size.z / sample_rows
        if y_pos is None:
            y_pos = rgn.a.y + rgn.size.y / 2
        pos = Vector(self.buf, y_pos, self.step / 2)
        mv_radius = self.step / 2
        super(UAV, self).__init__(grid, model, pos, mv_radius, False, rmse_log_interval, plt_lbl="UAV")
        self.rgn = rgn
        self.row_state = True
        self.rows = sample_rows
        self.total_rows = sample_rows

    def update_dest(self):
        '''
        Chooses destinations such that the UAV follows a series of rows on the grid.
        '''
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
        '''
        True if the UAV is at the end of its last row.
        '''
        if self.total_rows % 2 == 0:
            return self.rows == 0 and self.pos.x == self.buf
        else:
            return self.rows == 0 and self.pos.x == self.rgn.size.x - self.buf

    def suggest(self, w_width=None, w_depth=None):
        '''
        Suggests a region in which a UGV could search. Currently, this is done by using a moving window
        to take the average mean of subregions in the UAV's search region, then returning the region of
        the window with the highest mean.

        This assumes that the UGV can only search on the ground, and, therefore, its search region is
        essentially two-dimensional.

        Args:
        * w_width: Width of the window. (x)
        * w_depth: Depth of the window. (z)
        '''
        if w_width is None:
            w_width = int(self.map.size[0] / 3)
        if w_depth is None:
            w_depth = int(self.map.size[2] / 3)

        wsize = Vector(min(w_width, self.map.size[0]), 0, min(w_depth, self.map.size[2]))
        rgn = Region(
            self.rgn.a,
            (self.rgn.b.x, self.rgn.a.y, self.rgn.b.z)
        )
        pred = self.model.predict(rgn)
        highest = None
        h_rgn = rgn
        d3 = self.map.size[1] > 0
        for wx in range(rgn.a.x, rgn.b.x - wsize.x):
            for wz in range(rgn.a.z, rgn.b.z - wsize.z):
                w_rgn = Region((wx, 0, wz), (wx + wsize.x, 0, wz + wsize.z))
                avg = 0
                i = 0
                for x in range(w_rgn.a.x, w_rgn.b.x):
                    xi = x - rgn.a.x
                    for z in range(w_rgn.a.z,  w_rgn.b.z):
                        zi = z - rgn.a.z
                        if d3:
                            avg += pred.mean[xi][0][zi][1]
                        else:
                            avg += pred.mean[xi][zi][1]
                        i += 1
                avg /= i
                if highest is None or avg > highest:
                    # print(f"{avg} @ {w_rgn} > {highest} @ {h_rgn}")
                    h_rgn = w_rgn
                    highest = avg
        print(f"Suggestion: {highest} @ {h_rgn}")
        return h_rgn