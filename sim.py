#! /usr/bin/env python3

'''
Executable file that runs a comparison test or an RMSE log generator, depending on
command arguments.
'''

# https://github.com/SheffieldML/GPy
# I'm using GPy instead of PyGP because GPy is better documented, and it's being actively maintained.
import matplotlib.pyplot as plt
import argparse

from util import *
from region import *
from robot import *
from model import *
import tests
import time

def main():
    parser = argparse.ArgumentParser(description='WiFi Mapper')
    parser.add_argument("-s", type=int, nargs=3, default=[12, 12, 12], dest="size")
    parser.add_argument("-a", type=int, default=1, dest="src_amt")
    parser.add_argument("-m", type=int, default=12, dest="samples")
    parser.add_argument("-v", type=int, default=4, dest="uav_rows")
    parser.add_argument("-r", type=int, default=8, dest="radius")
    parser.add_argument("--rmse", type=int, default=0, dest="rmse")
    parser.add_argument("--csv", action="store_true", dest="csv")
    parser.add_argument("--display", action="store_true", dest="display")
    parser.add_argument("--profile", action="store_true", dest="profile")
    args = parser.parse_args()
    start = time.time()

    if args.profile:
        import cProfile, pstats, io
        profile = cProfile.Profile(builtins=False)
        profile.enable()

    if args.csv:
        print(tests.rmse_csv(args.size, args.src_amt, args.samples, args.uav_rows, args.radius))
    else:
        v_err, r_err = tests.compare(args.size, args.src_amt, args.samples, args.uav_rows, args.radius, args.rmse, args.display)
        if args.rmse > 0:
            print(f"Error: V: {v_err[-1]}, R: {r_err[-1]}")
        print(f"Time: {time.time() - start}")

    if args.profile:
        profile.disable()
        s_stream = io.StringIO()
        p_stats = pstats.Stats(profile, stream=s_stream).sort_stats("time")
        p_stats.print_stats()
        print(s_stream.getvalue())

    if args.display:
        input("Press enter to continue...")


if __name__ == "__main__":
    main()