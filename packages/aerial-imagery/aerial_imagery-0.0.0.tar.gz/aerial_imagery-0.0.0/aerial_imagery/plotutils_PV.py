import navpy
import pyvista as pv
import numpy as np
import math
import aerial_imagery
import pandas as pd
import os
# import cameratransform as ct

from aerial_imagery.direct_gr_c2002 import R_yaw_pitch_roll
from aerial_imagery.model3d import get_chopper, build_3Dmodel, plot_3Dmodel


def set_camera_azimuth_pv(plotter, new_azim=0):
    # Get current camera params
    cam = plotter.camera
    pos = np.array(cam.position)
    focal = np.array(cam.focal_point)

    # Vector from focal point to camera
    vec = pos - focal

    # Convert Cartesian to spherical coords (radius, azimuth, elevation)
    radius = np.linalg.norm(vec)
    elev = np.degrees(np.arcsin(vec[2] / radius))
    azim = np.degrees(np.arctan2(vec[1], vec[0]))

    # Southeast azimuth = 135 degrees (x=+y-)

    # Convert back to Cartesian with new azimuth, same radius and elevation
    elev_rad = np.radians(elev)
    azim_rad = np.radians(new_azim)

    x = radius * np.cos(elev_rad) * np.cos(azim_rad)
    y = radius * np.cos(elev_rad) * np.sin(azim_rad)
    z = radius * np.sin(elev_rad)

    new_pos = focal + np.array([x, y, z])

    # Set new camera position, keep same focal and up
    cam.position = new_pos.tolist()
    plotter.camera = cam

def plot_ax_pv(plotter, 
               O, 
               COORDS, 
               name, 
               col, 
               gscale, 
               bbox_alt=0, 
               alpha=0.5, 
               text_offset_xyz=np.array([0., 0., 0.]), 
               column_vectors=True):
        """
        Plots publication ready the axes of a coordinate system in 3D space using PYVISTA.

        The function plots the origin and the axes of a coordinate system in 3D space. 
        The axes are represented as quivers originating from the origin. The function also 
        prints the coordinates of the end point of the Z axis.

        Parameters
        ----------
        plotter : pyvista.Plotter
            The PyVista plotter object to which the axes will be added.
        O : array_like
            The coordinates of the origin of the coordinate system.
        COORDS : array_like
            The coordinates of the axes of the coordinate system. The axes are scaled by `gscale`.
        name : str
            The name of the coordinate system. If the name is 'ENU', the label of the plot is the name itself. 
            Otherwise, the label is the name followed by the coordinates of the origin.
        col : str
            The color of the plot.
        gscale : float
            The scale factor for the axes.
        bbox_alt : float
            Altitude of the ground - origin and x are shadowed / projected here.
        ha : str, optional
            The horizontal alignment of the text. Default is 'left'.

        Returns
        -------
        None
        """


        COORDS = COORDS.copy() # Prevent modifying the original data
        COORDS *= gscale
        lead_space = ' '*5

        xo, yo, zo = O
        xo, yo, zo = float(xo), float(yo), float(zo)

        points = np.vstack([O.T]*3)
        points

        if column_vectors: # This is the default
            vectors = COORDS.T
        else:
            # This line pulls the columns. Oh no!  
            error
            vectors = COORDS 

        # Create PyVista plotter
        
        # Add cones (glyphs) at each point
        if False:
            cloud = pv.PolyData(points)
            cloud["vectors"] = vectors

            cones = cloud.glyph(orient="vectors", scale=True, factor=1 )
        
            plotter.add_mesh(cones, color=col, smooth_shading=False)
        else:
            for point, vector in zip(points, vectors):

                arrow = pv.Arrow(
                start=[0, 0, 0],
                direction=vector,
                tip_length  =0.3/gscale,
                tip_radius  =0.05/gscale,
                shaft_radius=0.02/gscale,
                )

                arrow.points *= gscale
                arrow.translate(point, inplace=True)

                plotter.add_mesh(arrow, color=col, opacity=alpha)
        
        if True:
            print(name)
            # Create labels
            labels = [f"{v[0]:.1f}, {v[1]:.1f}, {v[2]:.1f}" for v in vectors]
            labels = name
            tips = points + vectors

            # print("tips", tips)
            tips = tips + text_offset_xyz
            # print("tips", tips)
            # Add labels at the vector tips
            plotter.add_point_labels(tips, 
                                     labels, 
                                     font_size=10, 
                                     text_color="black",
                                     always_visible=True,
                                     shape_color=col, 
                                     point_size=0)

        plotter.show_grid(
            color='gray',
            # line_width=1.0,
            show_xaxis=True,
            show_yaxis=True,
            show_zaxis=True,
            bold=False,
            font_size=0
        )

        plotter.set_background('white')    
        
        return plotter

def plot_chopper_pv(plotter=None, origin=np.array([0, 0, 0]), R=np.eye(3), color="lightblue", opacity=0.5, show_edges=True, scale=1):

    if plotter is None:
        plotter = pv.Plotter()

    x, y, z, i, j, k, fc = get_chopper()
    x_ENU = x - np.mean(x)
    y_ENU = y - np.mean(y)
    z_ENU = z - np.mean(z)

    nom_dir = 'east'
    if nom_dir=='east':
        xyz_ENU = np.vstack([x_ENU, y_ENU, -z_ENU]) * scale
    else:
        raise ValueError(f"Unknown nominal direction: {nom_dir}")

    xyz_ENU = R @ xyz_ENU 
    x_ENU, y_ENU, z_ENU = xyz_ENU
    
    points = np.vstack([x_ENU+origin[0], y_ENU+origin[1], z_ENU+origin[2]]).T

    three = np.ones_like(i)*3
    faces = np.vstack([three, i, j, k]).T

    mesh = pv.PolyData(points, faces)
    edges = mesh.extract_all_edges()
    # Add opaque black edges separately
    plotter.add_mesh(
        edges,
        color=color,
        line_width=0.1,
        opacity=0.8

    )

    # Plot

    plotter.add_mesh(mesh, color=color, opacity=opacity, show_edges=show_edges)

    if True:
        points = np.vstack([x_ENU+origin[0], y_ENU+origin[1], 0*z_ENU]).T
        mesh = pv.PolyData(points, faces)
        plotter.add_mesh(mesh, color='gray', opacity=opacity, show_edges=False)



