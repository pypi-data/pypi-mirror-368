# ==============================================================================
# pyvale: the python validation engine
# License: MIT
# Copyright (C) 2025 The Computer Aided Validation Team
# ==============================================================================

import time
import numpy as np
from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt

# Pyvale imports
import pyvale.sensorsim as sens
import pyvale.mooseherder as mh


def main() -> None:
    print()
    print(80*"=")
    print("RASTER CYTHON FILE (should be *.so on Linux):")
    print(sens.rastercyth.__file__)
    print(80*"=")
    print()

    # This a path to an exodus *.e output file from MOOSE, this can be
    # replaced with a path to your own simulation file
    sim_path = sens.DataSet.render_mechanical_3d_path()
    #sim_path = sens.DataSet.render_simple_block_path()
    #sim_path = Path.home()/"pyvale"/"src"/"pyvale"/"simcases"/"case26_out.e"
    sim_data = mh.ExodusReader(sim_path).read_all_sim_data()

    disp_comps = ("disp_x","disp_y","disp_z")

    # Scale m -> mm
    sim_data = sens.scale_length_units(1000.0,sim_data,disp_comps)

    print()
    print(f"{np.max(np.abs(sim_data.node_vars['disp_x']))=}")
    print(f"{np.max(np.abs(sim_data.node_vars['disp_y']))=}")
    print(f"{np.max(np.abs(sim_data.node_vars['disp_z']))=}")
    print()

    # Extracts the surface mesh from a full 3d simulation for rendering
    render_mesh = sens.create_render_mesh(sim_data,
                                        ("disp_y","disp_x"),
                                        sim_spat_dim=3,
                                        field_disp_keys=disp_comps)

    print()
    print(80*"-")
    print("MESH DATA:")
    print(80*"-")
    print("connectivity.shape=(num_elems,num_nodes_per_elem)")
    print(f"{render_mesh.connectivity.shape=}")
    print()
    print("coords.shape=(num_nodes,coord[x,y,z])")
    print(f"{render_mesh.coords.shape=}")
    print()
    print("fields.shape=(num_coords,num_time_steps,num_components)")
    print(f"{render_mesh.fields_render.shape=}")
    if render_mesh.fields_disp is not None:
        print(f"{render_mesh.fields_disp.shape=}")
    print(80*"-")
    print()

    pixel_num = np.array((960,1280),dtype=np.int32)
    pixel_size = np.array((5.3e-3,5.3e-3),dtype=np.float64)
    focal_leng: float = 50.0
    cam_rot = Rotation.from_euler("zyx",(0.0,-30.0,-10.0),degrees=True)
    fov_scale_factor: float = 1.1

    (roi_pos_world,
     cam_pos_world) = sens.CameraTools.pos_fill_frame(
         coords_world=render_mesh.coords,
         pixel_num=pixel_num,
         pixel_size=pixel_size,
         focal_leng=focal_leng,
         cam_rot=cam_rot,
         frame_fill=fov_scale_factor,
     )

    cam_data = sens.CameraData(
        pixels_num=pixel_num,
        pixels_size=pixel_size,
        pos_world=cam_pos_world,
        rot_world=cam_rot,
        roi_cent_world=roi_pos_world,
        focal_length=focal_leng,
        sub_samp=2,
        back_face_removal=True,
    )

    print(80*"-")
    print("CAMERA DATA:")
    print(80*"-")
    print(f"{cam_data.image_dist=}")
    print(f"{cam_data.roi_cent_world=}")
    print(f"{cam_data.pos_world=}")
    print()
    print("World to camera matrix:")
    print(cam_data.world_to_cam_mat)
    print(80*"-")
    print()

    print(80*"-")
    total_frames = render_mesh.fields_render.shape[1]*render_mesh.fields_render.shape[2]
    print(f"Time steps to render: {render_mesh.fields_render.shape[1]}")
    print(f"Fields to render: {render_mesh.fields_render.shape[2]}")
    print(f"Total frames to render: {total_frames}")
    print(80*"-")

    print(80*"=")
    print("RASTER ELEMENT LOOP START")
    print(80*"=")

    num_loops = 1
    loop_times = np.zeros((num_loops,),dtype=np.float64)

    print()
    print("Running raster loop.")
    for nn in range(num_loops):
        print(f"Running loop {nn}")
        loop_start = time.perf_counter()

        (image_buffer,
         depth_buffer,
         elems_in_images) = sens.RasterCY.raster_static_mesh(cam_data,
                                                            render_mesh,
                                                            16)

        loop_times[nn] = time.perf_counter() - loop_start

    print()
    print(80*"=")
    print("PERFORMANCE TIMERS")
    print(f"Elements in image = {elems_in_images}")
    print(f"Image buffer shape = {image_buffer.shape}")
    print(f"Avg. total render time = {np.mean(loop_times):.4f} seconds")
    print(f"Avg. render time per frame = {(np.mean(loop_times)/total_frames):.4f} seconds")
    print(80*"=")


    #===========================================================================
    # PLOTTING
    plot_on = False
    plot_frames = (-1,)#range(3)
    plot_field = 0

    # depth_to_plot = np.copy(np.asarray(depth_buffer[:,:,plot_frame]))
    # depth_to_plot[depth_buffer[:,:,plot_frame] > 10*cam_data.image_dist] = np.nan
    # image_to_plot = np.copy(np.asarray(image_buffer[:,:,plot_frame,plot_field]))
    # image_to_plot[depth_buffer[:,:,plot_frame] > 10*cam_data.image_dist] = np.nan

    if plot_on:
        plot_opts = sens.PlotOptsGeneral()

        for ff in plot_frames:
            (fig, ax) = plt.subplots(figsize=plot_opts.single_fig_size_square,
                                    layout='constrained')
            fig.set_dpi(plot_opts.resolution)
            cset = plt.imshow(depth_buffer[:,:,ff],
                            cmap=plt.get_cmap(plot_opts.cmap_seq))
                            #origin='lower')
            ax.set_aspect('equal','box')
            fig.colorbar(cset)
            ax.set_title(f"Depth buffer: {ff}",fontsize=plot_opts.font_head_size)
            ax.set_xlabel(r"x ($px$)",
                        fontsize=plot_opts.font_ax_size, fontname=plot_opts.font_name)
            ax.set_ylabel(r"y ($px$)",
                        fontsize=plot_opts.font_ax_size, fontname=plot_opts.font_name)

            (fig, ax) = plt.subplots(figsize=plot_opts.single_fig_size_square,
                                    layout='constrained')
            fig.set_dpi(plot_opts.resolution)
            cset = plt.imshow(image_buffer[:,:,ff,plot_field],
                            cmap=plt.get_cmap(plot_opts.cmap_seq))
                            #origin='lower')
            ax.set_aspect('equal','box')
            fig.colorbar(cset)
            ax.set_title(f"Field Image: {ff}",fontsize=plot_opts.font_head_size)
            ax.set_xlabel(r"x ($px$)",
                        fontsize=plot_opts.font_ax_size, fontname=plot_opts.font_name)
            ax.set_ylabel(r"y ($px$)",
                        fontsize=plot_opts.font_ax_size, fontname=plot_opts.font_name)

        plt.show()


if __name__ == "__main__":
    main()