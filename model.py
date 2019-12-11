import GPy as gp
import numpy as np
from region import *

class Prediction(object):
    '''
    An object holding the prediected mean and variance,
    as well as the sorted versions of each.
    '''
    def __init__(self, mean, var, d3=False):
        '''
        Create a new prediction.

        Args:
        * mean: 2- or 3-d list of tuples of [(position, predicted mean)]
        * var: As with mean, but with variance instead of mean.
        * d3: Whether this is a 3D prediction or not.
        '''
        self.mean = mean
        self.var = var
        self.d3 = d3
        self.__m_mean = None
        self.__m_var = None

    @property
    def sorted_mean(self):
        '''
        self.mean sorted by highest mean.
        '''
        if self.__m_mean is None:
            self.calc_sorted()
        return self.__m_mean

    @property
    def sorted_var(self):
        '''
        self.var sorted by highest variance.
        '''
        if self.__m_var is None:
            self.calc_sorted()
        return self.__m_var

    def cleaned_vals(self):
        '''
        Returns self.mean and self.var without the position values.
        '''
        mean = []
        var = []
        if self.d3:
            for x in range(len(self.mean)):
                mean.append([])
                var.append([])
                for y in range(len(self.mean[x])):
                    mean[x].append([])
                    var[x].append([])
                    for z in range(len(self.mean[x][y])):
                        mean[x][y].append(self.mean[x][y][z][1])
                        var[x][y].append(self.var[x][y][z][1])
        else:
            for x in range(len(self.mean)):
                mean.append([])
                var.append([])
                for z in range(len(self.mean[x])):
                    mean[x].append(self.mean[x][z][1])
                    var[x].append(self.var[x][z][1])
        return mean, var

    def calc_sorted(self):
        '''
        Generates sorted versions of self.mean and self.var.
        '''
        self.__m_mean = []
        self.__m_var = []
        if self.d3:
            for x in range(len(self.mean)):
                for y in range(len(self.mean[x])):
                    for z in range(len(self.mean[x][y])):
                        self.__m_mean.append(self.mean[x][y][z])
                        self.__m_var.append(self.var[x][y][z])
        else:
            for x in range(len(self.mean)):
                for z in range(len(self.mean[x])):
                    self.__m_mean.append(self.mean[x][z])
                    self.__m_var.append(self.var[x][z])
        self.__m_mean.sort(key=lambda p: p[1])
        self.__m_var.sort(key=lambda p: p[1], reverse=True)

    def __str__(self):
        return f"3D: {self.d3}, Mean: {self.clean_mean}\nVar: {self.clean_var}"


class Model(object):
    '''
    A wrapper for the GPy model.
    '''
    def __init__(self, d3=False):
        '''
        Creates a new model.

        Args:
        * d3: Whether this is a 3D model.
        '''
        self.input = []
        self.output = []
        # Cached versions of the GP model as well as posterior mean & variance,
        # so we don't have to recalculate them multiple times per iteration.
        self.__regression = None
        self.__predictions = None
        self.d3 = d3
        self.rmse_log = []

    def sample(self, pos, val):
        '''
        Adds a sample to the model.
        '''
        if self.d3:
            self.input.append([pos.x, pos.y, pos.z])
        else:
            self.input.append([pos.x, pos.z])
        self.output.append([val])
        self.__regression = None
        self.__predictions = None

    def rmse(self, grid, rgn=None):
        '''
        Calculates RMSE between the model and a grid.

        Args:
        * grid: The grid to which to compare the model.
        * rgn: The region in which to compare values. If none, it uses [(0, 0, 0), grid.size]
        '''
        if rgn is None:
            rgn = Region((0, 0, 0), grid.size)
        pred = self.predict(rgn)
        acc = 0
        num = 0
        if self.d3:
            for x in range(rgn.a.x, rgn.b.x):
                for y in range(rgn.a.y, rgn.b.y):
                    for z in range(rgn.a.z, rgn.b.z):
                        p = pred.mean[x][y][z][1]
                        o = grid[Vector(x, y, z)]
                        acc += (p - o)**2
                        num += 1
        else:
            for x in range(rgn.a.x, rgn.b.x):
                xi = x - rgn.a.x
                for z in range(rgn.a.z, rgn.b.z):
                    p = pred.mean[xi][z - rgn.a.z][1]
                    o = grid[Vector(x, 0, z)]
                    acc += (p - o)**2
                    num += 1
        return math.sqrt(acc / num)

    def log_rmse(self, grid, rgn=None):
        '''
        Gets the current RMSE and adds it to the RMSE log.
        '''
        self.rmse_log.append(self.rmse(grid, rgn))
        print(f"RMSE {len(self.rmse_log)}: {self.rmse_log[-1]}")

    @property
    def dims(self):
        '''
        Integer version of self.d3
        '''
        if self.d3:
            return 3
        else:
            return 2

    @property
    def regression(self):
        '''
        Gets the GPy regression for the current sample set.
        '''
        if self.__regression is None:
            self.__regression = gp.models.GPRegression(np.array(self.input), np.array(self.output),
                                                       gp.kern.Exponential(self.dims))
            # Optimization seems to give better results.
            self.__regression.optimize()
        return self.__regression

    def predict(self, rgn):
        '''
        Generates a Prediction for points in rgn.
        '''

        if self.__predictions is None or rgn not in self.__predictions:
            if self.__predictions is None:
                self.__predictions = {}
            # I couldn't find a method in GPy that gives the derivative function,
            # so I'm just getting the posterior mean & variance at every point,
            # because it's fast enough to be usable and it seems like it's more
            # prudent to spend my time on other parts of the program.
            p_mean = []
            p_var = []

            # Transforming the data into 2D arrays, so they can be displayed by matplotlib
            if self.d3:
                for x in range(rgn.a.x, rgn.b.x):
                    p_mean.append([])
                    p_var.append([])
                    for y in range(rgn.a.y, max(rgn.b.y, 1)):
                        p_mean[x - rgn.a.x].append([])
                        p_var[x - rgn.a.x].append([])
                        for z in range(rgn.a.z, rgn.b.z):
                            mean, var = self.regression.predict_noiseless(np.array([[x, y, z]]))
                            mean = mean[0][0]
                            var = var[0][0]
                            pos = Vector(x, y, z)
                            p_mean[x - rgn.a.x][y - rgn.a.y].append([pos, mean])
                            p_var[x - rgn.a.x][y - rgn.a.y].append([pos, var])
            else:
                for x in range(rgn.a.x, rgn.b.x):
                    p_mean.append([])
                    p_var.append([])
                    xi = x - rgn.a.x
                    for z in range(rgn.a.z, rgn.b.z):
                        mean, var = self.regression.predict_noiseless(np.array([[x, z]]))
                        mean = mean[0][0]
                        var = var[0][0]
                        pos = Vector(x, 0, z)
                        p_mean[xi].append([pos, mean])
                        p_var[xi].append([pos, var])
            self.__predictions[rgn] = Prediction(p_mean, p_var, self.d3)
        return self.__predictions[rgn]