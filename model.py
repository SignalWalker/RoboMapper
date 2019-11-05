class Model(object):
    def __init__(self, size):
        self.input = []
        self.output = []
        self.size = size
        # Cached versions of the GP model as well as posterior mean & variance,
        # so we don't have to recalculate them multiple times per iteration.
        self.__regression = None
        self.__p_mean = None
        self.__p_var = None
        self.__p_max_mean = None
        self.__p_max_var = None
        self.outdated = True
        self.p_outdated = True

    def sample(self, pos, val):
        self.input.append([pos[0], pos[1], pos[2]])
        self.output.append([val])
        self.outdated = True
        self.p_outdated = True

    @property
    def regression(self):
        if self.outdated:
            self.__regression = gp.models.GPRegression(np.array(self.input), np.array(self.output),
                                                       gp.kern.Exponential(3))
            # Optimization seems to give better results.
            self.__regression.optimize()
            self.outdated = False
        return self.__regression

    @property
    def prediction(self):
        if self.p_outdated:
            # I couldn't find a method in GPy that gives the derivative function,
            # so I'm just getting the posterior mean & variance at every point,
            # because it's fast enough to be usable and it seems like it's more
            # prudent to spend my time on other parts of the program.
            points = []
            for x in range(self.size[0]):
                for y in range(self.size[1]):
                    points.append([x, y])
            points = np.array(points)
            mean, var = self.regression.predict_noiseless(points)
            self.__p_mean = []
            self.__p_var = []
            self.__p_max_var = []
            self.__p_max_mean = []

            # Transforming the data into 2D arrays, so they can be displayed by matplotlib
            i = 0
            for x in range(self.size[0]):
                self.__p_mean.append([])
                self.__p_var.append([])
                for y in range(self.size[1]):
                    self.__p_mean[x].append(mean[i][0])
                    self.__p_var[x].append(var[i][0])
                    self.__p_max_mean.append([x, y, mean[i][0]])
                    self.__p_max_var.append([x, y, var[i][0]])
                    i = i + 1
            self.__p_max_mean.sort(key=lambda p: p[2], reverse=True)
            self.__p_max_var.sort(key=lambda p: p[2], reverse=True)
            self.p_outdated = False
        return self.__p_mean, self.__p_var, self.__p_max_mean, self.__p_max_var