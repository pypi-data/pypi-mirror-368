import numpy as np

def set_params(N, dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs):
    #
    # vector, other_params = set_params(N, dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs)
    #
    
    if N==12:
        vector       = np.array([dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs])
        other_params = None
    elif N==9:
        vector       = np.array([dh, dp, dr, dxs, dys, dzs, dhs, dps, drs])
        other_params = np.array([dx, dy, dz])              # Fill the rest with zeros if not provided
    elif N==8: # Drop First Heading
        vector       = np.array([dp, dr, dxs, dys, dzs, dhs, dps, drs])
        other_params = np.array([dx, dy, dz, dh])          # Fill the rest with zeros if not provided
    elif N==6: # Drop First P and R
        vector       = np.array([dxs, dys, dzs, dhs, dps, drs])
        other_params = np.array([dx, dy, dz, dh, dp, dr])  # Fill the rest with zeros if not provided

    return vector, other_params

def get_params(vector, other_params, var_scales):

    if other_params is None:
        other_params = np.zeros(12-len(vector))  # Fill the rest with zeros if not provided


    assert len(vector) + len(other_params) == 12, f"The total length of vector [{len(vector)}] and other_params [{len(other_params)}] must be 12."

    x_scale, y_scale, z_scale, h_scale, p_scale, r_scale = var_scales

    if len(vector) == 12:  # I don't think we need the XYZ offsets of the first image
        dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs = vector

        # Scale the parameters
        dx *= x_scale
        dy *= y_scale
        dz *= z_scale
        dh *= h_scale
        dp *= p_scale
        dr *= r_scale

        dxs *= x_scale
        dys *= y_scale
        dzs *= z_scale
        dhs *= h_scale
        dps *= p_scale
        drs *= r_scale
    elif len(vector) == 9:
        dh, dp, dr, dxs, dys, dzs, dhs, dps, drs = vector

        # Scale the parameters
        dh *= h_scale
        dp *= p_scale
        dr *= r_scale
        
        dxs *= x_scale
        dys *= y_scale
        dzs *= z_scale
        dhs *= h_scale
        dps *= p_scale
        drs *= r_scale

        dx, dy, dz = other_params
    elif len(vector) == 8: # Drop First Heading 
        dp, dr, dxs, dys, dzs, dhs, dps, drs = vector

        # Scale the parameters
        dp *= p_scale
        dr *= r_scale
        
        dxs *= x_scale
        dys *= y_scale
        dzs *= z_scale
        dhs *= h_scale
        dps *= p_scale
        drs *= r_scale

        dx, dy, dz, dh = other_params
    elif len(vector) == 6: # Drop First P and R 
        dxs, dys, dzs, dhs, dps, drs = vector

        # Scale the parameters
        dxs *= x_scale
        dys *= y_scale
        dzs *= z_scale
        dhs *= h_scale
        dps *= p_scale
        drs *= r_scale

        dx, dy, dz, dh, dp, dr = other_params
        # print("dx, dy, dz, dh, dp, dr")
        # print( dx, dy, dz, dh, dp, dr )


    return dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs
