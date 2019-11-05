class Robot(object):
    def __init__(self, grid, pos, model, move_range):
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
            return 0, 0, 0
        else:
            pm, p_var, m_mean, mv = self.model.prediction
            x, y = m_mean[0][0], m_mean[0][1]
            return (x, y), p_var[x][y]

    def take_sample(self):
        self.model.sample(self.pos, self.map.sample(self.pos))
        self.sample_amt += 1

    def update_dest(self):
        print("Generic Point Selection Called!")

    def done(self):
        print("Generic done() called!")
        return True

    def move_towards_dest(self):
        dir_vec = vector(self.pos, self.dest)
        if length(dir_vec) <= self.move_range:
            self.pos = self.dest
        else:
            dir_vec = normal(dir_vec)
            dir_vec[0] = dir_vec[0] * self.move_range
            dir_vec[1] = dir_vec[1] * self.move_range
            dir_vec[2] = dir_vec[2] * self.move_range
            self.pos = self.pos[0] + dir_vec[0], self.pos[1] + dir_vec[1], self.pos[2] + dir_vec[2]

    def find_source(self, stops, rmse_log=None, display=0):
        self.take_sample()
        i = 0
        while not self.done():
            self.move_towards_dest()
            self.take_sample()
            if self.pos == self.dest:
                self.update_dest()
            if display is not True and display > 1 and i % display == 0:
                self.display()
            i += 1

        if display is True or display >= 1:
            self.display()

        if rmse_log is not None:
            rmse_log.append(rmse(self.grid, self.model))

        return self.guess()

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
        super(UGV, self).__init__(grid, pos, model, move_range)
        self.rgn = rgn
        self.rand = rand
        self.start = self.pos
        self.samples = samples

    def select_point(self, stops):
        if self.rand:
            dest = rand_point(self.grid.size, self.pos, self.mv_radius)
        else:
            dest = list(v for v in self.model.prediction[3] if in_rgn((v[0], v[1], v[2]), self.rgn))[0]
        self.samples -= 1
        return 1, dest

    def done(self):
        return self.samples == 0


class UAV(Robot):
    def __init__(self, grid, model, sample_rows):
        self.buf = grid.size[0] / sample_rows / 2
        self.step = grid.size[1] / sample_rows
        pos = self.buf, self.step / 2
        super(UAV, self).__init__(grid, pos, model)
        self.row_state = True
        self.rows = sample_rows

    def select_point(self, stops):
        x, y = self.pos[0], self.pos[1]
        if self.row_state:
            # Going left
            if self.pos[0] > self.grid.size[0] / 2:
                x = self.buf
            else:  # Going right
                x = self.grid.size[0] - self.buf
            self.rows = self.rows - 1
        else:
            y = y + self.step
            stops = 2
        self.row_state = not self.row_state
        return stops, (int(x), int(y))

    def done(self):
        return self.rows is 0

    def suggest(self):
        amt = int(self.grid.size[1] / 3)
        meta = deres(self.model.prediction[0], amt)
        highest = None
        mx = 0
        my = 0
        for x in range(0, len(meta)):
            for y in range(0, len(meta[x])):
                if highest is None or meta[x][y] > highest:
                    highest = meta[x][y]
                    mx = x
                    my = y
        rx = mx * amt
        ry = my * amt
        return (rx, ry), (rx + amt, ry + amt)