from region import *
from model import *
from util import *
from robot import *

# Generates a WiFi grid with given size & source position, then runs
# two robots (one directed by variance and the other random), then
# returns the distances from the real position each robots' final guesses
# were.
#
# Parameters:
#   size: The size of the WiFi map.
#   src_pos: The position of the WiFi emitter.
#   uav_rows: Number of sample rows for each UAV
#   radius: UGV move radius
#   stops: Number of samples to take for each chosen point.
#   display: Whether to display graphs and output guesses.
def test(grid, samples, uav_rows, radius, rand, armse_log, grmse_log, display):
    model = Model()
    sample_total = 0

    if not rand:
        rgn = Region((0, 0, 0), grid.size)
        uav = UAV(grid, rgn, model, 8, uav_rows)
        uav_disp = display
        if uav_disp is not False:
            uav_disp = True
        sample_total += uav.find_source(rmse_log=armse_log, display=uav_disp)
        rgn = uav.suggest()
    else:
        rgn = Region((0, 0, 0), (grid.size[0], 0, grid.size[2]))

    ugv = UGV(grid, model, rgn.a, radius, rgn, samples, rand=rand)
    sample_total += ugv.find_source(rmse_log=grmse_log, display=display)

    guess = ugv.guess()[0]

    error = rmse(grid, model)
    return guess, error, sample_total


def compare(size, src_amt, samples, uav_rows, radius, use_rmse, display):
    if use_rmse:
        varmse, vgrmse, rgrmse = [], [], []
    else:
        varmse, vgrmse, rgrmse = None, None, None
    grid = Map(size=size, src_amt=src_amt)
    print(f"Real: {grid.srcs}")
    v_guess, v_rmse, v_samples = test(grid, samples, uav_rows, radius, False, varmse, vgrmse, display)
    print(f"    VGuess: {v_guess}")
    r_guess, r_rmse, r_samples = test(grid, v_samples, uav_rows, radius, True, None, rgrmse, False)
    print(f"    RGuess: {r_guess}")
    return varmse, vgrmse, rgrmse


def v_test(size, src_amt, samples, uav_rows, radius, stops, use_rmse, display):
    if use_rmse:
        varmse, vgrmse = [], []
    else:
        varmse, vgrmse = None, None
    grid = Map(src_amt=src_amt)
    print(f"Real: {grid.pos}")
    v_guess, v_rmse = test(grid, samples, uav_rows, radius, stops, False, varmse, vgrmse, display)
    print(f"    VGuess: {v_guess}, ARMSE: {varmse[len(varmse) - 1]:.2f}, GRMSE: {vgrmse[len(vgrmse) - 1]:.2f}")


def rmse_csv(size, samples, uav_rows, radius, stops, display=False):
    varmse, vgrmse, rarmse, rgrmse = compare(size, 1, samples, uav_rows, radius, stops, True, display)

    res = "Grid Size,UAV Rows,UGV Move Radius,UAV Sample," \
          "UAV RMSE,UGV Sample,UGV RMSE,Random Sample,Random RMSE\n"

    for (i, a) in enumerate(varmse):
        if i == 0:
            res += f"{size[0]},{uav_rows},{radius},{i + 1},{a},,,,\n"
        else:
            res += f",,,{i + 1},{a},,,,\n"

    for (i, (a, r)) in enumerate(zip(vgrmse, rgrmse)):
        res += f",,,,,{i + 1},{a},{i + 1},{r}\n"

    return res


# Runs test() multiple times and displays the average distance for each
# type of robot.
def multitest(trials, size, sample_range, uav_rows, radius, stops):
    res = "Size,Samples,Destinations,Trial,UAV RMSE,UGV RMSE,Random RMSE\n"
    for samples in sample_range:
        print(f"Samples: {samples}")
        for i in range(trials):
            varmse, vgrmse, rarmse, rgrmse = compare(size, 1, samples, uav_rows, radius, stops, True, False)
            line = f"{size[0]}x{size[1]},{samples},{samples * stops},{i},{varmse[0]},{vgrmse[0]},{rgrmse[0]}\n"
            print(line)
            res += line
    return res
