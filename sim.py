#! /usr/bin/env python3

# https://github.com/SheffieldML/GPy
# I'm using GPy instead of PyGP because GPy is better documented, and it's being actively maintained.
import matplotlib.pyplot as plt
import argparse

from util import *
from region import *
from robot import *
from model import *
import time

def main():
    import tests
    parser = argparse.ArgumentParser(description='WiFi Mapper')
    parser.add_argument("-s", type=int, nargs=3, default=[12, 12, 12], dest="size")
    parser.add_argument("-a", type=int, default=1, dest="src_amt")
    parser.add_argument("-m", type=int, default=12, dest="samples")
    parser.add_argument("-v", type=int, default=4, dest="uav_rows")
    parser.add_argument("-r", type=int, default=4, dest="radius")
    parser.add_argument("--rmse", action="store_true", dest="rmse")
    parser.add_argument("--display", action="store_true", dest="display")
    args = parser.parse_args()
    start = time.time()
    v_err, g_err, r_err = tests.compare(args.size, args.src_amt, args.samples, args.uav_rows, args.radius, args.rmse, args.display)
    if args.rmse:
        print(f"Error: V: {v_err}, G: {g_err}, R: {r_err}")
    print(f"Time: {time.time() - start}")

if __name__ == "__main__":
    main()