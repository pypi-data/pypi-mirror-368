# ==============================================================================
# pyvale: the python validation engine
# License: MIT
# Copyright (C) 2025 The Computer Aided Validation Team
# ==============================================================================

"""
Basics: Overview of the basic error library
================================================================================

Building on what we learned in examples 1.1-1.3 we now have a look at the basic
error library for pyvale. The sensor error models in pyvale are grouped into the
types of random (`ErrRand*`) and systematic (`ErrSys*`). In this example we will
consider probability distribution based sampled errors, constant offsets and
basic systematic errors such as digitisation / saturation.

In the next examples we will consider more advanced error sources including:
field errors that perturb the sensor parameters (e.g. location, sampling time
and orientation) requiring re-interpolation of the underlying field data; and
calibration errors.

Test case: Scalar field point sensors (thermocouples) on a 3D thermal simulation

Advanced users: It is also possible to write custom errors by writing your own
class that implements the `IErrCalculator` abstract base class and then add them
to your error chain.
"""

import numpy as np
import matplotlib.pyplot as plt

# Pyvale imports
import pyvale.mooseherder as mh
import pyvale.sensorsim as sens
import pyvale.dataset as dataset


#%%
# First we use everything we learned from the first three examples to build
# a thermocouple sensor array for the same 3D thermal simulation we have
# analysed in the previous example.
data_path = dataset.thermal_3d_path()
sim_data = mh.ExodusReader(data_path).read_all_sim_data()
sim_data = sens.scale_length_units(scale=1000.0,
                                    sim_data=sim_data,
                                    disp_comps=None)
n_sens = (1,4,1)
x_lims = (12.5,12.5)
y_lims = (0.0,33.0)
z_lims = (0.0,12.0)
sens_pos = sens.create_sensor_pos_array(n_sens,x_lims,y_lims,z_lims)

sample_times = np.linspace(0.0,np.max(sim_data.time),50) # | None

sensor_data = sens.SensorData(positions=sens_pos,
                            sample_times=sample_times)

field_key: str = "temperature"
tc_array = sens.SensorArrayFactory \
    .thermocouples_no_errs(sim_data,
                            sensor_data,
                            elem_dims=3,
                            field_name=field_key)

#%%
# Now we have our thermocouple array applied to our simulation without any
# errors we can build a custom chain of basic errors. Here we will start by
# adding a series of systematic errors that are independent:
err_chain = []

#%%
# For probability sampling systematic errors the distribution is sampled to
# provide an offset which is assumed to be constant over all sensor sampling
# times. This is different to random errors which are sampled to provide a
# different error for each sensor and time step.
#
# These systematic errors provide a constant offset to all measurements in
# simulation units or as a percentage.
err_chain.append(sens.ErrSysOffset(offset=-10.0))
err_chain.append(sens.ErrSysOffsetPercent(offset_percent=-1.0))

#%%
# These systematic errors are sampled from a uniform or normal probability
# distribution either in simulation units or as a percentage.
err_chain.append(sens.ErrSysUnif(low=-1.0,
                                high=1.0))
err_chain.append(sens.ErrSysUnifPercent(low_percent=-1.0,
                                        high_percent=1.0))
err_chain.append(sens.ErrSysNorm(std=1.0))
err_chain.append(sens.ErrSysNormPercent(std_percent=1.0))

#%%
# pyvale includes a series of random number generator objects that wrap the
# random number generators from numpy. These are named `Gen*` and can be
# used with an `ErrSysGen` or an `ErrSysGenPercent` object to create custom
# probability distribution sampling errors:
sys_gen = sens.GenTriangular(left=-1.0,
                            mode=0.0,
                            right=1.0)
err_chain.append(sens.ErrSysGen(sys_gen))

#%%
# We can also build the equivalent of `ErrSysUnifPercent` above using a
# `Gen` object inserted into an `ErrSysGenPercent` object:
unif_gen = sens.GenUniform(low=-1.0,
                            high=1.0)
err_chain.append(sens.ErrSysGenPercent(unif_gen))

#%%
# We can also add a series of random errors in a similar manner to the
# systematic errors above noting that these will generate a new error for
# each sensor and each time step whereas the systematic error sampling
# provides a constant shift over all sampling times for each sensor.
err_chain.append(sens.ErrRandNorm(std = 2.0))
err_chain.append(sens.ErrRandNormPercent(std_percent=2.0))
err_chain.append(sens.ErrRandUnif(low=-2.0,high=2.0))
err_chain.append(sens.ErrRandUnifPercent(low_percent=-2.0,
                                        high_percent=2.0))
rand_gen = sens.GenTriangular(left=-5.0,
                                mode=0.0,
                                right=5.0)
err_chain.append(sens.ErrRandGen(rand_gen))

#%%
# Finally we add some dependent systematic errors including rounding errors,
# digitisation and saturation. Note that the saturation error must be placed
# last in the error chain. Try changing some of these values to see how the
# sensor traces change - particularly the saturation error.
err_chain.append(sens.ErrSysRoundOff(sens.ERoundMethod.ROUND,0.1))
err_chain.append(sens.ErrSysDigitisation(bits_per_unit=2**16/100))
err_chain.append(sens.ErrSysSaturation(meas_min=0.0,meas_max=400.0))

err_int = sens.ErrIntegrator(err_chain,
                            sensor_data,
                            tc_array.get_measurement_shape())
tc_array.set_error_integrator(err_int)

#%%
# Now we can run the sensor simulation and display the results to see the
# different error sources as we have done in previous examples.
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

