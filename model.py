import GPy as gp
import numpy as np
from region import *

class Prediction(object):
    def __init__(self, mean, var):
        self.mean = mean
        self.var = var
        self.__m_mean = None
        self.__m_var = None

    @property
    def sorted_mean(self):
        if self.__m_mean is None:
            self.calc_sorted()
        return self.__m_mean

    @property
    def sorted_var(self):
        if self.__m_var is None:
            self.calc_sorted()
        return self.__m_var

    def calc_sorted(self):
        self.__m_mean = []
        self.__m_var = []
        for x in range(len(self.mean)):
            for y in range(len(self.mean[x])):
                for z in range(len(self.mean[x][y])):
                    self.__m_mean.append(self.mean[x][y][z])
                    self.__m_var.append(self.var[x][y][z])
        self.__m_mean.sort(key=lambda p: p[1])
        self.__m_var.sort(key=lambda p: p[1])


class Model(object):
    def __init__(self):
        self.input = []
        self.output = []
        # Cached versions of the GP model as well as posterior mean & variance,
        # so we don't have to recalculate them multiple times per iteration.
        self.__regression = None
        self.__predictions = None

    def sample(self, pos, val):
        self.input.append([pos.x, pos.y, pos.z])
        self.output.append([val])
        self.__regression = None
        self.__predictions = None

    @property
    def regression(self):
        if self.__regression is None:
            self.__regression = gp.models.GPRegression(np.array(self.input), np.array(self.output),
                                                       gp.kern.Exponential(3))
            # Optimization seems to give better results.
            self.__regression.optimize()
        return self.__regression

    def predict(self, rgn):
        # print(f"Obj: {self.regression.objective_function()}, Grad: {self.regression.objective_function_gradients()}")
        # print(f"Log: {self.regression.log_likelihood()}")

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
            self.__predictions[rgn] = Prediction(p_mean, p_var)
        return self.__predictions[rgn]