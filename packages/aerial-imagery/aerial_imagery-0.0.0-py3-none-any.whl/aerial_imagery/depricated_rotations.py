
import numpy as np
import math
import navpy

""""
Collections of functions to build rotation matrices from angles. Written before being explicit about rotaiton notation etc.
These functions are deprecated but here for reference and will be removed in a future version.
"""

def R_yaw_pitch_roll(yaw, pitch, roll):
    """
    Build a rotation matrix from yaw, pitch and roll angles. Note that this function 
    function uses standard aerospace conventions, i.e. the rotation is applied in the order of
    yaw, pitch and roll. This is different from the navpy.angle2dcm function which uses the
    order of roll, pitch and yaw.

    Note also that this will provide rotation from the reference to ENU. It 
    provides the inverse, or transpose then of the rotation from ENU to the reference frame. 
    That is:
        - R_ref_to_enu = R_yaw_pitch_roll(yaw, pitch, roll)
        - R_enu_to_ref = R_yaw_pitch_roll(yaw, pitch, roll).T
        
    """
    
    "2 ways to do this"
    
    R_yaw_pitch_roll = np.array([[math.cos(yaw)*math.cos(pitch),-math.sin(yaw)*math.cos(roll)+math.cos(yaw)*math.sin(pitch)*math.sin(roll),math.sin(yaw)*math.sin(roll)+math.cos(yaw)*math.cos(roll)*math.sin(pitch)]
                ,
                [math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(roll)+math.sin(roll)*math.sin(pitch)*math.sin(yaw),-math.cos(yaw)*math.sin(roll)+math.sin(pitch)*math.sin(yaw)*math.cos(roll)]
                ,
                [-math.sin(pitch),math.cos(pitch)*math.sin(roll),math.cos(pitch)*math.cos(roll)]])

    assert(np.all(np.isclose(R_yaw_pitch_roll, navpy.angle2dcm(yaw, pitch, roll).T)))
    
    return R_yaw_pitch_roll

def R_kappa_phi_omega(kappa, phi, omega, order='KPO'):

    raise DeprecationWarning('R_kappa_phi_omega is deprecated, use R_extrinsic_kappa_phi_omega instead. This will be removed in a future version.')

def R_extrinsic_kappa_phi_omega(kappa, phi, omega, order='KPO'):

    k, p, o = kappa, phi, omega

    # Rz = R_kappa = np.array([
    #     [np.cos(k),  np.sin(k), 0],
    #     [-np.sin(k), np.cos(k), 0],
    #     [0,          0,         1]
    # ])
    Rz = R_kappa = np.array([
            [np.cos(k), -np.sin(k), 0],
            [np.sin(k),  np.cos(k), 0],
            [0,          0,         1]
        ])

    # Ry = R_phi = np.array([
    #     [np.cos(p), 0, -np.sin(p)],
    #     [0,         1, 0],
    #     [np.sin(p), 0, np.cos(p)]
    # ])
    Ry = R_phi = np.array([
        [np.cos(p), 0, np.sin(p)],
        [0,         1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])

    # Rx = R_omega = np.array([
    #     [1, 0,          0],
    #     [0, np.cos(o),  np.sin(o)],
    #     [0, -np.sin(o), np.cos(o)]
    # ])
    Rx = R_omega = np.array([
            [1, 0,          0],
            [0, np.cos(o), -np.sin(o)],
            [0, np.sin(o), np.cos(o)]
        ])
    # Applanix want R_omega, then R_phi, then R_kappa for NED → Camera frame, thus  R_NED_to_C = R_kappa @ R_phi @ R_omega 
    # R_kappa @ R_phi @ R_omega is the rotation from NED to Camera frame.
    # NED → Camera frame

    if order.upper() == 'KPO':
        return R_omega @ R_phi @ R_kappa  
    elif order.upper() == 'OPK':
        return R_kappa @ R_phi @ R_omega
    elif order.upper() == 'KOP':
        return R_phi @ R_omega @ R_kappa
    else:
        raise ValueError(f'Order {order} not recognised. Use "KPO", "OPK" or "KOP".')
    
def R_omega_phi_kappa(kappa, phi, omega):

    raise DeprecationWarning('R_omega_phi_kappa is deprecated, use R_kappa_phi_omega instead. This will be removed in a future version.')

    k, p, o = kappa, phi, omega

    Rz = R_kappa = np.array([
        [np.cos(k),  np.sin(k), 0],
        [-np.sin(k), np.cos(k), 0],
        [0,          0,         1]
    ])

    # Ry = R_phi = np.array([
    #     [np.cos(p), 0, -np.sin(p)],
    #     [0,         1, 0],
    #     [np.sin(p), 0, np.cos(p)]
    # ])
    Ry = R_phi = np.array([
        [np.cos(p), 0, np.sin(p)],
        [0,         1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])
    
    Rx = R_omega = np.array([
        [1, 0,          0],
        [0, np.cos(o),  np.sin(o)],
        [0, -np.sin(o), np.cos(o)]
    ])
    
    return R_kappa @ R_phi @ R_omega  # NThe one on the right is the first 
