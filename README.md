# PyMapper

This is a library for running a simulation of a UAV and UGV that use Gaussian processes to determine the location of WiFi signal sources.

## Dependencies

* Python 3
* [GPy](https://github.com/SheffieldML/GPy)
* MatPlotLib
* Numpy

## Testing

To run a simulation and view its results:

`./sim.py`

You can pass arguments to this, and they can be listed, along with descriptions, using:

`./sim.py -h`

For example, `./sim.py --csv` will print a CSV log of RMSE values logged during the simulation.

Warning: While 3D simulation was partially implemented, it wasn't completed. Unless you're testing the 3D simulation, please always set the Y value of -s to 0. Ex. `./sim.py -s 256 0 256`