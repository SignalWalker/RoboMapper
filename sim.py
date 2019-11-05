#! /usr/bin/env python3

import numpy as np
# https://github.com/SheffieldML/GPy
# I'm using GPy instead of PyGP because GPy is better documented, and it's being actively maintained.
import GPy as gp
import math
import random
import matplotlib.pyplot as plt
import argparse

from util import *
from region import *
from robot import *
from model import *

def main():
    import tests
    tests.compare((12, 12, 12), 1, 12, 4, 8, 3, False, False)

if __name__ == "__main__":
    main()