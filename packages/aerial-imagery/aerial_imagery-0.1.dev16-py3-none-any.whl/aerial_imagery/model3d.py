import aerial_imagery, os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch
from mpl_toolkits.mplot3d import Axes3D 
import mpl_toolkits.mplot3d.art3d as art3d
import mpl_toolkits.mplot3d as a3

import matplotlib.colors as colors
import pylab as pl

import numpy as np
import matplotlib.pyplot as plt
# import navpy

from aerial_imagery.transformations import plot_ax_simple, R_x, R_y, R_z


def get_chopper():
    """Function to return 3D model of a helicopter. The data are from plotly (https://plotly.com/chart-studio-help/make-a-3d-mesh-plot/).

    Parameters
    ----------
    None

    Returns:
    x, y, z: array
        x, y and z coordinates of the chopper. 
    vtx: list of arrays
        List of arrays describing the faces. Each list entry is a vertex, and the rows are xf, yf, zf
    fc: list if hex color strings
        facecolors from the original plotly data

    """
    # module_dir = os.path.split(wave_radar.__file__)[0]
    module_dir = aerial_imagery.__path__[0]
    data_dir = os.path.join(module_dir, '../data')

    chopper_file = os.path.join(data_dir, '3d-mesh-helicopter.csv')

    heli = pd.read_csv(chopper_file)

    x  = heli.x.values
    y  = heli.y.values
    z  = heli.z.values
    i  = heli.i.values
    j  = heli.j.values
    k  = heli.k.values
    fc = heli.facecolor.values

    ind = np.isnan(x)

    x = x[~ind]
    y = y[~ind]
    z = z[~ind]

    x -= np.mean(x)
    y -= np.min(y)
    z -= np.min(z)

    x /= 20 
    y /= 20
    z /= 20 

    y -= 3
    z -= 1.5

    xyz = np.vstack([x, y, z])
    xyz = R_z(np.pi/2)@xyz

    x, y, z = xyz

    return x, y, z, i, j, k, fc

def build_3Dmodel(x, y, z, i, j, k):

    vtx = []
    for I, J, K in zip(i, j, k):

        tri = [I, J, K]
        myx = x[tri]
        myy = y[tri]
        myz = z[tri]
        vtx += [np.vstack((myx, myy, myz)).T]

    return vtx

def plot_3Dmodel(vtx, fc, ax=None, edgecolors='k', facecolors='w', alpha=0.5, linewidths=None):
    'Edgecolors only used if FC is none'

    if linewidths is None:
        linewidths = alpha/2

    if ax is None:
        noax = True
        ax = plt.figure(figsize=(10, 10)).add_subplot(projection='3d')

    for i, v in enumerate(vtx):

        if fc is None :
            tri = a3.art3d.Poly3DCollection([v], edgecolors=edgecolors, facecolors=facecolors, linewidths=linewidths, alpha=alpha)
        else:
            tri = a3.art3d.Poly3DCollection([v])
            
            if type(fc) == str :
                tri.set_color(fc)
            else:
                tri.set_color(fc[i])

        ax.add_collection3d(tri)

    ax.set_aspect('equal')
    plt.xlabel('x')
    plt.ylabel('y')
    ax.set_zlabel('z')

    if False:
        myx = xl[[0, 1, 1, 0]]
        myy = yl[[1, 1, 0, 0]]
        myz = 0*myx
        vtx = np.vstack((myx, myy, myz)).T

        tri = a3.art3d.Poly3DCollection([vtx])
        tri.set_alpha(0.2)
        ax.add_collection3d(tri)

        myx = 0*xl[[0, 1, 1, 0]]
        myy = yl[[1, 1, 0, 0]]
        myz = zl[[0, 1, 1, 0]]

        vtx = np.vstack((myx, myy, myz)).T

        tri = a3.art3d.Poly3DCollection([vtx])
        tri.set_alpha(0.2)
        ax.add_collection3d(tri)

        myx = xl[[0, 1, 1, 0]]
        myy = 0*yl[[1, 1, 0, 0]]
        myz = zl[[1, 1, 0, 0]]

        vtx = np.vstack((myx, myy, myz)).T

        tri = a3.art3d.Poly3DCollection([vtx])
        tri.set_alpha(0.2)
        ax.add_collection3d(tri)

    print('3D model rendered')

    return ax