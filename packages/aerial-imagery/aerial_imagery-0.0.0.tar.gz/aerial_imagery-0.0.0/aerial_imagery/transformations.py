import numpy as np
# import navpy
import matplotlib.pyplot as plt

gscale = 1
cos, sin = np.cos, np.sin

def plot_ax_simple(O, COORDS, name, col, ha='left', bbox_alt=0, ax=None):
    """Code for plotting a 3D coordinate system.

    There is a more detailed code in plotutils

    Parameters
    ----------
    O: array
        Origin
    COORDS: 3x3 array
        The unit vectors
    
    """

    if ax is None:
        noax = True
        ax = plt.figure(figsize=(10, 10)).add_subplot(projection='3d')

    COORDS *= gscale
    lead_space = ' '*5

    xo, yo, zo = O
    xo, yo, zo = float(xo), float(yo), float(zo)
    label = name + f' [{xo:0.2f}, {yo:0.2f}, {zo:0.2f}]'
    ax.plot(xo, yo, zo, col+'.', label=label)
    ax.plot(xo, yo, bbox_alt, col+'.', alpha=0.2)
    
    if False:
        ax.text(xo, yo, zo,  lead_space + label + lead_space, \
                color=col, ha=ha)

    qa = 0.3
    x, y, z = COORDS
    ax.quiver(xo, yo, zo, x[0], x[1], x[2], colors=col, alpha=qa)
    ax.text(float(xo+x[0]), float(yo+x[1]), float(zo+x[2]), 'X', color=col)
    
    ax.quiver(xo, yo, zo, y[0], y[1], y[2], colors=col, alpha=qa)
    ax.text(float(xo+y[0]), float(yo+y[1]), float(zo+y[2]), 'Y', color=col)

    ax.quiver(xo, yo, zo, z[0], z[1], z[2], colors=col, alpha=qa)
    ax.text(float(xo+z[0]), float(yo+z[1]), float(zo+z[2]), 'Z', color=col)
    ax.plot(float(xo+z[0]), float(yo+z[1]), float(zo+z[2]), '.', color=col)
    print(f'z = [{float(xo+z[0]):0.3f}, {float(yo+z[1]):0.3f}, {float(zo+z[2]):0.3f}]')

    ax.plot(xo+x[0], yo+x[1], bbox_alt, 'x', ms=1, color=col)


def R_x(ang):
    """
    Rotation matrix for rotation around the current x axis.  

    Note that this is not consistent with navpy.
    """

    R_x = np.array([[1, 0,        0],
                    [0, cos(ang), -sin(ang)],
                    [0, sin(ang), cos(ang)]])
    
    return R_x

def R_y(ang):
    """
    Rotation matrix for rotation around the current y axis.  

    Note that this is not consistent with navpy.
    """

    ang = - ang 
    R_y = np.array([[cos(ang), 0, -sin(ang)],
                    [0,        1, 0],
                    [sin(ang), 0, cos(ang)]])
    
    return R_y

def R_z(ang):
    """
    Rotation matrix for rotation around the current z axis.  

    Note that this is not consistent with navpy.
    """

    R_z = np.array([[cos(ang), -sin(ang), 0],
                    [sin(ang), cos(ang),  0],
                    [0,        0,         1]])
    
    return R_z


def rotate_x(COORDS, ang):
    return R_x(ang)@COORDS

def rotate_y(COORDS, ang):
    return R_y(ang)@COORDS

def rotate_z(COORDS, ang):
    return R_z(ang)@COORDS




def is_orthogonal(R):
    """Simple method to test whether a matrix is orthogonal.

    Orthogonal matrices have the property R.T = inv(R), thus R@R.T == I
    """ 

    I = np.eye(R.shape[0])

    assert(np.all(np.isclose(R.T @ R, I)))

def R_yaw_pitch_roll(yaw, pitch, roll):
    """Allowed for back compatibility, will remove one day. 
    """

    raise Exception('THIS SHOULD NEVER HAVE BEEN CODED THIS WAY, USE R_ypr(yaw, pitch, roll).T INSTEAD OF R_yaw_pitch_roll(yaw, pitch, roll).')

    return R_ypr(yaw, pitch, roll).T

def R_ypr(yaw, pitch, roll, intrinsic=True):
    """3D rotation matrix for intrinsic Tait-Bryan angles with Z-Y'-X" sequencing.

    Some useful notes on the site https://danceswithcode.net/engineeringnotes/rotations_in_3d/
    rotations_in_3d_part1.html#:~:text=Executing%20the%20rotations%20in%20the,the%20order%20of%20elemental%20rotations.

    Parameters
    ----------
    Yaw: numeric
        The rotation around Z. This is the first rotation, putting us in the (X', Y', Z') reference frame
    Pitch: numeric
        The rotation around Y'. This is the second rotation, putting us in the (X", Y", Z") reference frame
    Roll: numeric
        The rotation around X". This is the third rotation, putting us in the (X'", Y'", Z'") reference frame

    Returns
    -------
    R: 3x3 np.array
        The rotation matrix for intrinsic Tait-Bryan angles with Z-Y'-X" sequencing
        
    """

    # Note that this is the transpose (and inverse) of the matrix in Equation 19. of Corriea et al. (2022) - i.e. it's the reverse rotation.
    # Note that this IS the matrix in Equation 9 of the dances with code site - i.e. 
    #               it is the intrinsic rotation matrix for y-p-r
    #               it is the extrinsic rotation matrix for r-p-y

    R_ypr_T = np.array(
               [[cos(yaw)*cos(pitch),    -sin(yaw)*cos(roll)+cos(yaw)*sin(pitch)*sin(roll),     sin(yaw)*sin(roll)+cos(yaw)*cos(roll)*sin(pitch)]
                ,
                [sin(yaw)*cos(pitch),     cos(yaw)*cos(roll)+sin(roll)*sin(pitch)*sin(yaw),    -cos(yaw)*sin(roll)+sin(pitch)*sin(yaw)*cos(roll)]
                ,
                [-sin(pitch),             cos(pitch)*sin(roll),                                 cos(pitch)*cos(roll)]])
    
    # We shall now invert(transpose) this
    R_ypr = R_ypr_T.T
    
    # Confirm that the intrinsic rotation matrix for y-p-r == R_z*R_y*R_x
    rotation_0 = R_z(yaw)@R_y(pitch)@R_x(roll) # X then Y then Z
    assert(np.all(np.isclose(R_ypr_T, rotation_0)))

    # Assert this is the same as calculating it ourselves
    rotation_1 = R_x(-roll)@R_y(-pitch)@R_z(-yaw) # Z then Y then X
    assert(np.all(np.isclose(R_ypr, rotation_1))) 
    
    # Assert this is the same as navpy - navpy is then the Extrinsic rotation. That really surprises me. 
    assert(np.all(np.isclose(R_ypr, navpy.angle2dcm(yaw, pitch, roll))))

    if intrinsic:

        return R_ypr_T
    
    else:

        return R_ypr_T
