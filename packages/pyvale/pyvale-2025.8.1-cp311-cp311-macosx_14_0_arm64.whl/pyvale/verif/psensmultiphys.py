#===============================================================================
# pyvale: the python validation engine
# License: MIT
# Copyright (C) 2025 The Computer Aided Validation Team
#===============================================================================
from pathlib import Path
import copy
import numpy as np
import pyvale.mooseherder as mh
import pyvale.sensorsim as sens
import pyvale.verif.psens as psens
import pyvale.verif.psensscalar as psensscalar
import pyvale.verif.psensvector as psensvector
import pyvale.verif.psenstensor as psenstensor
import pyvale.verif.psensmech as psensmech
import pyvale.dataset as dataset


def load_simdata_list(data_paths: list[Path],
                      disp_comps: tuple[str,...]) -> list[mh.SimData]:
    sim_list = []
    for pp in data_paths:
        sim_data = mh.ExodusReader(pp).read_all_sim_data()
        sim_data = sens.scale_length_units(scale=1000.0,
                                            sim_data=sim_data,
                                            disp_comps=disp_comps)
        sim_list.append(sim_data)

    return sim_list


def simdata_list_2d() -> list[mh.SimData]:
    data_paths = dataset.thermomechanical_2d_experiment_paths()
    disp_comps = ("disp_x","disp_y")
    return load_simdata_list(data_paths,disp_comps)


def simdata_list_3d() -> list[mh.SimData]:
    data_paths = [dataset.element_case_output_path(dataset.EElemTest.TET4),
                  dataset.element_case_output_path(dataset.EElemTest.TET10),
                  dataset.element_case_output_path(dataset.EElemTest.HEX8),
                  dataset.element_case_output_path(dataset.EElemTest.HEX20)]
    disp_comps = ("disp_x","disp_y","disp_z")
    return load_simdata_list(data_paths,disp_comps)


def sens_pos_2d() -> dict[str,np.ndarray]:
    # Geometry does not change
    sim_dims = sens.SimTools.get_sim_dims(simdata_list_2d()[0])
    sens_pos = {}

    x_lims = sim_dims["x"]
    y_lims = sim_dims["y"]
    z_lims = (0,0)

    n_sens = (2,2,1)
    sens_pos["grid-22"] = sens.create_sensor_pos_array(n_sens,x_lims,y_lims,z_lims)

    return sens_pos

def sens_pos_2d_lock(sens_pos: np.ndarray) -> dict[str,np.ndarray]:
    pos_lock = {}
    (xx,yy,zz) = (0,1,2)

    lock = np.full_like(sens_pos,False,dtype=bool)
    lock[:,zz] = True # lock z
    pos_lock["grid-22"] = None

    return pos_lock


def sens_pos_3d_lock(sens_pos: np.ndarray) -> dict[str,np.ndarray]:
    pos_lock = {}
    (xx,yy,zz) = (0,1,2)

    lock = np.full_like(sens_pos,False,dtype=bool)
    lock[0,yy] = True
    lock[1,yy] = True
    lock[2,zz] = True
    lock[3,zz] = True
    lock[4,xx] = True
    lock[5,xx] = True
    pos_lock["cent-cube"] = lock

    return pos_lock


def sens_pos_3d() -> dict[str,np.ndarray]:
    sens_pos = {}
    sens_pos["cent-cube"] = np.array(((5.0,0.0,5.0),    # xz
                                      (5.0,10.0,5.0),   # xz
                                      (5.0,5.0,0.0),    # xy
                                      (5.0,5.0,10.0),   # xy
                                      (0.0,5.0,5.0),    # yz
                                      (10.0,5.0,5.0),)) # yz
    return sens_pos

def sens_data_2d_dict() -> dict[str,sens.SensorData]:
    # Time steps don't change so can take first sim here
    return psens.sens_data_dict(simdata_list_2d()[0],sens_pos_2d())

def sens_data_3d_dict() -> dict[str,sens.SensorData]:
    # Time steps don't change so can take first sim here
    return psens.sens_data_dict(simdata_list_3d()[0],sens_pos_3d())

def exp_sim_2d() -> dict[str,sens.ExperimentSimulator]:
    sens_data_dict = sens_data_2d_dict()
    sim_list = simdata_list_2d()

    fields = ("scal","vect","tens")
    exp_sims = {}
    for ss in sens_data_dict:

        sens_noerrs = {}
        sens_noerrs["scal"] = psensscalar.sens_noerrs(sim_list[0],
                                                      sens_data_dict[ss],
                                                      elem_dims=2)
        sens_noerrs["vect"] = psensvector.sens_2d_noerrs(sim_list[0],
                                                         sens_data_dict[ss])
        sens_noerrs["tens"] = psenstensor.sens_2d_noerrs(sim_list[0],
                                                         sens_data_dict[ss])

        pos_lock = sens_pos_2d_lock(sens_data_dict[ss].positions)
        for kk in pos_lock:
            if kk in ss:
                pos_lock_key = kk
                break

        err_chain_dict={}
        err_chain_dict["scal"] = psensscalar.err_chain_2d_dict(
            sens_noerrs["scal"].get_field(),
            sens_data_dict[ss].positions,
            sens_data_dict[ss].sample_times,
            pos_lock[pos_lock_key]
        )

        err_chain_dict["vect"] = psensmech.err_chain_2d_dict(
            sens_noerrs["vect"].get_field(),
            sens_data_dict[ss].positions,
            sens_data_dict[ss].sample_times,
            pos_lock[pos_lock_key]
        )

        err_chain_dict["tens"] = psensmech.err_chain_2d_dict(
            sens_noerrs["tens"].get_field(),
            sens_data_dict[ss].positions,
            sens_data_dict[ss].sample_times,
            pos_lock[pos_lock_key]
        )

        common_keys = (err_chain_dict["scal"].keys() &
                       err_chain_dict["vect"].keys() &
                       err_chain_dict["tens"].keys())
        # print(80*"=")
        # print(common_keys)
        # print(80*"=")

        for ee in common_keys:
            tag = f"exp2d_{ss}_err-{ee}"

            sensor_arrays = []
            for ff in fields:
                this_sens = copy.deepcopy(sens_noerrs[ff])
                # print(80*"-")
                # print(f"{ff=}")
                # print(f"{ee=}")
                # print(80*"-")
                if err_chain_dict[ff][ee] is not None:
                    err_int_opts = sens.ErrIntOpts
                    err_int = sens.ErrIntegrator(err_chain_dict[ff][ee],
                                                sens_data_dict[ss],
                                                this_sens.get_measurement_shape(),
                                                err_int_opts=err_int_opts)
                    this_sens.set_error_integrator(err_int)

                sensor_arrays.append(this_sens)

            sim_list = simdata_list_2d()
            sensor_arrays = [sens_noerrs["scal"],sens_noerrs["vect"],sens_noerrs["tens"]]
            exp_sim = sens.ExperimentSimulator(sim_list,
                                             sensor_arrays,
                                             num_exp_per_sim=10)
            exp_sims[tag] = exp_sim

    return exp_sims


