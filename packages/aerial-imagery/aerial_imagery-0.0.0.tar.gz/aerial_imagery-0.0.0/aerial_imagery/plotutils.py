import navpy
import numpy as np
import math
import matplotlib.pyplot as plt
import aerial_imagery
import pandas as pd
import os
# import cameratransform as ct
from matplotlib import colors

from aerial_imagery.direct_gr_c2002 import R_yaw_pitch_roll
from aerial_imagery.model3d import get_chopper, build_3Dmodel, plot_3Dmodel

def plot_ax(ax, O, COORDS, name, col, gscale, bbox_alt=0, alpha=0.5, ha=None, va=None, column_vectors=True, zorder=None,
            fa_head_length=None):
        """
        Plots the axes of a coordinate system in 3D space.

        The function plots the origin and the axes of a coordinate system in 3D space. 
        The axes are represented as quivers originating from the origin. The function also 
        prints the coordinates of the end point of the Z axis.

        Parameters
        ----------
        ax : matplotlib.axes._subplots.Axes3DSubplot
            The axes of the plot.
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
        va : str, optional
            The vertical alignment of the text. Default is 'center'.
        fa_head_length : float, optional
            The length of the arrow head if using fancy arrows. If None, quiver is used.

        Returns
        -------
        None
        """
        # O  = COORDS[:, 0]
        # AX = COORDS[:, 1]

        COORDS = COORDS.copy() # Prevent modifying the original data
        COORDS *= gscale
        lead_space = ' '*5

        if ha is None:
            ha = ['left', 'left', 'left'] 
        elif isinstance(ha, str):
            ha = [ha, ha, ha]

        if va is None:
            va = ['center', 'center', 'center']
        elif isinstance(va, str):
            va = [va, va, va]

        xo, yo, zo = O
        xo, yo, zo = float(xo), float(yo), float(zo)
        if name == 'ENU':
            label = name
        else:
            label = name + f' [{xo:0.2f}, {yo:0.2f}, {zo:0.2f}]'

        try:
            lab1, lab2, lab3 = name 
        except:
            lab1, lab2, lab3 = f' ${name}_X$ ', f' ${name}_Y$ ', f' ${name}_Z$ ' 

        ax.plot(xo, yo, zo, col+'.', label=label)
        ax.plot(xo, yo, bbox_alt, col+'.', alpha=alpha)
        if False:
            ax.text(xo, yo, zo,  lead_space + label + lead_space, \
                    color=col, ha=ha)

        qa = alpha
        if column_vectors: # This is the default
            x, y, z = COORDS.T
        else:
            # This line pulls the columns. Oh no!  
            error
            x, y, z = COORDS 

        if fa_head_length is None:
            ax.quiver(xo, yo, zo, x[0], x[1], x[2], colors=col, alpha=qa, zorder=zorder)
            ax.quiver(xo, yo, zo, y[0], y[1], y[2], colors=col, alpha=qa, zorder=zorder)
            ax.quiver(xo, yo, zo, z[0], z[1], z[2], colors=col, alpha=qa, zorder=zorder)
        else:
            plot_arrow(ax, [xo, yo, zo], x, head_length=fa_head_length, resolution=10, color=col, alpha=qa, zorder=zorder)
            plot_arrow(ax, [xo, yo, zo], y, head_length=fa_head_length, resolution=10, color=col, alpha=qa, zorder=zorder)
            plot_arrow(ax, [xo, yo, zo], z, head_length=fa_head_length, resolution=10, color=col, alpha=qa, zorder=zorder)

        ax.text(float(xo+x[0]), float(yo+x[1]), float(zo+x[2]), lab1, color=col, ha=ha[0], va=va[0], zorder=zorder)        
        ax.text(float(xo+y[0]), float(yo+y[1]), float(zo+y[2]), lab2, color=col, ha=ha[1], va=va[1], zorder=zorder)
        ax.text(float(xo+z[0]), float(yo+z[1]), float(zo+z[2]), lab3, color=col, ha=ha[2], va=va[2], zorder=zorder)
        
        ax.plot(float(xo+z[0]), float(yo+z[1]), float(zo+z[2]), '.', color=col)

        print(f'z = [{float(xo+z[0]):0.3f}, {float(yo+z[1]):0.3f}, {float(zo+z[2]):0.3f}]')

        ax.plot(xo+x[0], yo+x[1], bbox_alt, 'x', ms=1, color=col)

def plot_chopper(R_UAS_to_ENU, UTM_xyz, bbox_alt, ax=None, plot_shadow=True, scale=1, edgecolors='g'):
    """
    Plots a 3D model of a chopper in a given coordinate system.

    The function plots a 3D model of a chopper in the UAS coordinate system. The chopper is 
    represented as a collection of polygons. The function also has the option to plot the shadow 
    of the chopper.

    Parameters
    ----------
    R_UAS_to_ENU : numpy.ndarray
        The rotation matrix from the UAS coordinate system to the ENU coordinate system.
    UTM_xyz : tuple
        The coordinates of the chopper in the UTM coordinate system.
    bbox_alt : float
        The altitude of the bounding box.
    ax : matplotlib.axes.Axes, optional
        The axes on which to plot the chopper. Default is the current axes.
    plot_shadow : bool, optional
        If True, the function also plots the shadow of the chopper. Default is True.
    scale : float, optional
        The scale factor for the chopper. Default is 1.

    Returns
    -------
    matplotlib.axes.Axes
        The axes on which the chopper is plotted.
    """

    if ax is None:
        ax = plt.gca()

    UTM_x, UTM_y, UTM_z = UTM_xyz

    x, y, z, i, j, k, fc = get_chopper()
    x_ENU = x - np.mean(x)
    y_ENU = y - np.mean(y)
    z_ENU = z - np.mean(z)
    z_ENU = -z_ENU
    xyz_ENU = np.vstack([x_ENU, y_ENU, z_ENU]) * scale

    if False:
        vtx_ENU = build_3Dmodel(x_ENU, y_ENU, z_ENU, i, j, k)

    # xyz_NED = R_NED_to_ENU.T@xyz_ENU

    # x_NED, y_NED, z_NED = xyz_NED

    # Plot my NED chopper
    # x, y, z = xyz_NED/2
    if False:
        vtx_NED = build_3Dmodel(x_NED+UTM_x, y_NED+UTM_y, z_NED+UTM_z, i, j, k)

    if False:
        # NEED A LITTLE X-Y SWAP TRICK HERE! 
        yxz_UAS = dgr.R_UAS_to_NED.T@np.vstack([y, x, z])
        y, x, z = yxz_UAS*2
        vtx_UAS = build_3Dmodel(x+UTM_x, y+UTM_y, z+UTM_z, i, j, k)
    else:
        xyz_UAS = R_UAS_to_ENU@xyz_ENU
        x, y, z = xyz_UAS/2
        vtx_UAS = build_3Dmodel(x+UTM_x, y+UTM_y, z+UTM_z, i, j, k)
        vtx_UAS_shadow = build_3Dmodel(x+UTM_x, y+UTM_y, z*bbox_alt, i, j, k)
    
    ax  = plot_3Dmodel(vtx_UAS, None, edgecolors=edgecolors, facecolors='w', alpha=0.5, linewidths=0.1, ax=ax)
    if plot_shadow:
        ax  = plot_3Dmodel(vtx_UAS_shadow, None, edgecolors='k', facecolors='k', alpha=0.5, linewidths=0.001, ax=ax)



def plot_arrow(ax, start, direction, head_length=0.2, resolution=10, color='blue', alpha=0.5, zorder=None):
    # Normalize the direction vector
    direction = np.array(direction)
    length = np.linalg.norm(direction)
    if length == 0:
        raise ValueError("Zero-length direction vector")
    direction_unit = direction / length

    # Define lengths
    shaft_length = length - head_length
    if shaft_length <= 0:
        raise ValueError("Head length is too long compared to the total length")
    
    head_radius = head_length/4
    shaft_radius = head_radius / 3

    # Create the cylinder (shaft) along z-axis
    if False: # Make a full length cylinder
        z_cyl = np.linspace(0, shaft_length, 2)
    else: 
        shaft_start = np.max([shaft_length-2*head_length, 0])
        z_cyl = np.linspace(shaft_start, shaft_length, 2)


    theta = np.linspace(0, 2 * np.pi, resolution)
    theta_grid, z_grid = np.meshgrid(theta, z_cyl)
    x_cyl = shaft_radius * np.cos(theta_grid).T
    y_cyl = shaft_radius * np.sin(theta_grid).T
    z_cyl = z_grid.T

    # Create the cone (head) along z-axis
    z_cone = np.linspace(shaft_length, length, 2)
    r_cone = np.linspace(head_radius, 0, 2)
    theta_grid_cone, z_grid_cone = np.meshgrid(theta, z_cone)
    r_grid_cone, _ = np.meshgrid(r_cone, theta)
    x_cone = r_grid_cone * np.cos(theta_grid_cone).T
    y_cone = r_grid_cone * np.sin(theta_grid_cone).T
    z_cone = z_grid_cone.T

    # Combine cylinder and cone coordinates
    x = np.concatenate((x_cyl, x_cone), axis=1)
    y = np.concatenate((y_cyl, y_cone), axis=1)
    z = np.concatenate((z_cyl, z_cone), axis=1)

    # Stack coordinates for rotation
    coords = np.stack((x, y, z), axis=-1)

    # Compute rotation matrix to align z-axis with the direction vector
    def rotation_matrix_from_vectors(vec1, vec2):
        a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
        v = np.cross(a, b)
        c = np.dot(a, b)
        if c == -1:
            return -np.eye(3)
        s = np.linalg.norm(v)
        kmat = np.array([[0, -v[2], v[1]],
                         [v[2], 0, -v[0]],
                         [-v[1], v[0], 0]])
        rotation_matrix = np.eye(3) + kmat + kmat @ kmat * ((1 - c) / (s ** 2))
        return rotation_matrix

    R = rotation_matrix_from_vectors(np.array([0, 0, 1]), direction_unit)

    # Apply rotation and translation
    coords_rotated = coords @ R.T
    coords_rotated += np.array(start)

    # Extract rotated coordinates
    x_rot, y_rot, z_rot = coords_rotated[..., 0], coords_rotated[..., 1], coords_rotated[..., 2]

    # Plot the arrow
    face_color = colors.to_rgba(color, alpha=alpha)  # Transparent face
    edge_color = colors.to_rgba(color, alpha=1.0)    # Opaque edge
    print(edge_color)
    print(edge_color, face_color)
    if False:
        ax.plot_surface(x_rot, y_rot, z_rot, color=color, linewidth=0, antialiased=False, zorder=zorder)
    else:
        ax.plot_surface(x_rot, y_rot, z_rot, color=face_color, edgecolors=edge_color, linewidth=0, antialiased=False, zorder=zorder)
        x = [start[0], start[0] + direction[0]]
        y = [start[1], start[1] + direction[1]]
        z = [start[2], start[2] + direction[2]]
        ax.plot(x, y, z, '--', color=color, linewidth=1, zorder=zorder)




