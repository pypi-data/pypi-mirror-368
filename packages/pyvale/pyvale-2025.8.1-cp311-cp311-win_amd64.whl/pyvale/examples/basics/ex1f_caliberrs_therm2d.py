# ==============================================================================
# pyvale: the python validation engine
# License: MIT
# Copyright (C) 2025 The Computer Aided Validation Team
# ==============================================================================

"""
Basics: Sensor calibration systematic errors
================================================================================

In this example we show how `pyvale` can simulate sensor calibration errors with
user defined calibration functions.

Test case: Scalar field point sensors (thermocouples) on a 2D thermal simulation
"""

import numpy as np
import matplotlib.pyplot as plt

# Pyvale imports
import pyvale.mooseherder as mh
import pyvale.sensorsim as sens
import pyvale.dataset as dataset


#%%
# First we need to define some calibration functions. These functions must take
# a numpy array and return a numpy array of the same shape. We start by
# defining what we think our calibration is called `assumed_calib()` and then
# we also need to define the ground truth calibration `truth_calib()` so that
# we can calculate the error between them. The calibration functions shown below
# are simplified versions of the typical calibration curves for a K-type
# thermocouple.
def calib_assumed(signal: np.ndarray) -> np.ndarray:
    return 24.3*signal + 0.616


def calib_truth(signal: np.ndarray) -> np.ndarray:
    return -0.01897 + 25.41881*signal - 0.42456*signal**2 + 0.04365*signal**3


#%%
# We are first going to do a quick analytical calculation for the minimum
# and maximum systematic error we expect between our assumed and true
# calibration. For our true calibration we know this holds between 0 and 6mV
# so we perform the calculation over this range and print the min/max
# expected error over this range.
n_cal_divs = 10000
signal_calib_range = np.array((0.0,6.0),dtype=np.float64)
milli_volts = np.linspace(signal_calib_range[0],
                            signal_calib_range[1],
                            n_cal_divs)
temp_truth = calib_truth(milli_volts)
temp_assumed = calib_assumed(milli_volts)
calib_error = temp_assumed - temp_truth

print()
print(80*"-")
print(f"Max calibrated temperature: {np.min(temp_truth)} degC")
print(f"Min calibrated temperature: {np.max(temp_truth)} degC")
print()
print(f"Calibration error over signal:"
        + f" {signal_calib_range[0]} to {signal_calib_range[1]} mV")
print(f"Max calib error: {np.max(calib_error)}")
print(f"Min calib error: {np.min(calib_error)}")
print(80*"-")
print()

#%%
# Now let's go back and build the 2D thermal plate with simulated
# thermocouples that we analysed in the first two examples. We use this
# simulation as the temperatures are within our calibrated range.
data_path = dataset.thermal_2d_path()
sim_data = mh.ExodusReader(data_path).read_all_sim_data()
sim_data = sens.scale_length_units(scale=1000.0,
                                    sim_data=sim_data,
                                    disp_comps=None)

n_sens = (4,1,1)
x_lims = (0.0,100.0)
y_lims = (0.0,50.0)
z_lims = (0.0,0.0)
sens_pos = sens.create_sensor_pos_array(n_sens,x_lims,y_lims,z_lims)

sample_times = np.linspace(0.0,np.max(sim_data.time),50) # | None

sensor_data = sens.SensorData(positions=sens_pos,
                                sample_times=sample_times)

field_key: str = "temperature"
tc_array = sens.SensorArrayFactory \
    .thermocouples_no_errs(sim_data,
                            sensor_data,
                            elem_dims=2,
                            field_name=field_key)

#%%
# With our assumed and true calibration functions we can build our
# calibration error object and add it to our error chain as normal. Note
# that the truth calibration function must be inverted numerically so to
# increase accuracy the number of divisions can be increased. However, 1e4
# divisions should be suitable for most applications.
cal_err = sens.ErrSysCalibration(calib_assumed,
                                calib_truth,
                                signal_calib_range,
                                n_cal_divs=10000)
sys_err_int = sens.ErrIntegrator([cal_err],
                                    sensor_data,
                                    tc_array.get_measurement_shape())
tc_array.set_error_integrator(sys_err_int)

#%%
# Now we run our sensor simulation to see what our calibration does.
measurements = tc_array.calc_measurements()

print(80*"-")

sens_print = 0
comp_print = 0
time_last = 5
time_print = slice(measurements.shape[2]-time_last,measurements.shape[2])

print(f"These are the last {time_last} virtual measurements of sensor "
        + f"{sens_print}:")

sens.print_measurements(tc_array,sens_print,comp_print,time_print)

print(80*"-")

sens.plot_time_traces(tc_array,field_key)
plt.show()

