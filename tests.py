'''
Methods for testing the robot simulations.
'''

from region import *
from model import *
from util import *
from robot import *


def test(grid, samples, uav_rows, radius, rand, rmse_log_interval, display):
    '''
    Runs a robot simulation and returns the best guess for WiFi source position, the RMSE log (if desired),
    and the total number of samples taken.

    Args:
    * samples: Amount of samples for the UGV to take.
    * uav_rows: Amount of rows for the UAV to travel through.
    * radius: Movement radius for the UGV.
    * rand: Whether to test the random destination selection method or the variance method.
    * rmse_log_interval: How many samples to take before logging RMSE. If 0, RMSE is not logged.
    * display: Interval between display of matplotlib graphs.
    '''
    model = Model(grid.size[1] > 0)
    sample_total = 0

    if not rand:
        rgn = Region((0, 0, 0), grid.size)
        if rgn.b.y == 0:
            y_pos = 0
        else:
            y_pos = None
        uav = UAV(grid, rgn, model, y_pos, uav_rows, rmse_log_interval)
        uav_disp = display
        if uav_disp is not False:
            uav_disp = True
        sample_total += uav.find_source(display=uav_disp)
        rgn = uav.suggest()
    else:
        rgn = Region((0, 0, 0), (grid.size[0], 0, grid.size[2]))

    ugv = UGV(grid, model, rgn.a, radius, rgn, samples, rand, rmse_log_interval)
    sample_total += ugv.find_source(display=display)

    guess = ugv.guess()[0]

    model.log_rmse(grid)
    return guess, model.rmse_log, sample_total,


def compare(size, src_amt, samples, uav_rows, radius, rmse_log_interval, display):
    '''
    Runs test() for a random robot and a variance robot, then returns the rmse logs for both.

    Args: the same as test()
    '''
    grid = Map(size=size, src_amt=src_amt)
    print(f"Real: {grid.srcs}")
    v_guess, v_rmse, v_samples = test(grid, samples, uav_rows, radius, False, rmse_log_interval, display)
    # print(f"    VGuess: {v_guess}")
    r_guess, r_rmse, r_samples = test(grid, v_samples, uav_rows, radius, True, rmse_log_interval, display)
    # print(f"    RGuess: {r_guess}")
    return v_rmse, r_rmse


def rmse_csv(size, src_amt, samples, uav_rows, radius):
    '''
    Generates a CSV formatted string of the RMSE at each sample, for both the random robot
    and the variance robot.

    Args: the same as compare()
    '''
    v_rmse, r_rmse = compare(size, src_amt, samples, uav_rows, radius, 1, False)

    res = "Sample,Variance RMSE,Random RMSE\n"

    for i in range(len(v_rmse)):
        res += f"{i + 1},{v_rmse[i]},{r_rmse[i]}\n"

    return res
