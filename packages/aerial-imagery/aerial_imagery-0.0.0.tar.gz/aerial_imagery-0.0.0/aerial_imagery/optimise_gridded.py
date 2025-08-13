
from aerial_imagery.optimise_subroutines import get_params
from aerial_imagery.contours import normalise_img
import numpy as np
import aerial_imagery.geotiff as geotiff

"""
Functions for optimising shifts between 2 images by gridding the data.

This will need to be adapted to be a module. It needs to take dxdy, bounds and ocean as inputs.


"""

raise(Exception("Never completed this as a module"))

def objective_function(vector, myDGR, df_E, ds_exif, ind, blank, var_scales, other_params):

    XI, YI, ZI, ZI_sub = eval_func(vector, myDGR, df_E, ds_exif, ind, var_scales, other_params)

    # ZI_norm = ZI - np.nanmin(ZI)
    # ZI_norm = ZI_norm / np.nanmax(ZI_norm)

    # ZI_sub_norm = ZI_sub - np.nanmin(ZI_sub)
    # ZI_sub_norm = ZI_sub_norm / np.nanmax(ZI_sub_norm)
    ZI_norm = normalise_img(ZI)
    ZI_sub_norm = normalise_img(ZI_sub)

    d = ZI_sub_norm - ZI_norm
    rms = np.sqrt(np.nanmean(d**2))

    if False:
        print(f"RMS: {rms}")
        print(f"Vector: {vector}")

    return rms


def eval_func(vector, myDGR, df_E, ds_exif, ind, var_scales, other_params=None):

    dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs = get_params(vector, other_params, var_scales)

    # NOTE, THIS ASSUMES LITTLE DIFFSCALE DIFFERENCE BETWEEN THE FIRST AND SECOND IMAGE. I THINK THIS IS REASONABLE. 
    

    ro = df_E.iloc[ind]  # Use the first row for now, this is just a test
    img = ds_exif.isel(time=ind).temperature.values

    X, Y, Z = ro['EASTING'], ro['NORTHING'], ro['ELLIPSOID HEIGHT']
    HEADING, PITCH, ROLL = ro['HEADING'], ro['PITCH'], ro['ROLL']
    # KAPPA, PHI, OMEGA = ro['KAPPA'], ro['PHI'], ro['OMEGA']

    # Apply the perturbations
    X += dx 
    Y += dy 
    Z += dz 
    print(HEADING, PITCH, ROLL, dh, dp, dr, )
    HEADING += dh 
    PITCH   += dp 
    ROLL    += dr 

    myDGR.update_POS_NED(X, Y, Z)
    myDGR.update_HPR_Ref(HEADING, PITCH, ROLL, units='deg')

    meshx, meshy, meshz = myDGR.make_georef_grid(grid_n=None, alt=ocean)
    XI, YI, ZI = geotiff.make(meshx, meshy, img, bounds=bounds, dxdy=dxdy)

    ind_sub = ind + 1
    ro_sub = df_E.iloc[ind_sub]  # Use the first row for now, this is just a test
    img_sub = ds_exif.isel(time=ind_sub).temperature.values

    X_sub, Y_sub, Z_sub = ro_sub['EASTING'], ro_sub['NORTHING'], ro_sub['ELLIPSOID HEIGHT']
    HEADING_sub, PITCH_sub, ROLL_sub = ro_sub['HEADING'], ro_sub['PITCH'], ro_sub['ROLL']
    # KAPPA_sub, PHI_sub, OMEGA_sub = ro['KAPPA'], ro['PHI'], ro['OMEGA']

    # Apply the perturbations
    X_sub += dxs 
    Y_sub += dys 
    Z_sub += dzs 
    HEADING_sub += dhs 
    PITCH_sub   += dps 
    ROLL_sub    += drs 

    myDGR.update_POS_NED(X_sub, Y_sub, Z_sub)
    myDGR.update_HPR_Ref(HEADING_sub, PITCH_sub, ROLL_sub, units='deg')

    meshx_sub, meshy_sub, meshz_sub = myDGR.make_georef_grid(grid_n=None, alt=ocean)
    XI, YI, ZI_sub = geotiff.make(meshx_sub, meshy_sub, img_sub, bounds=bounds, dxdy=dxdy)

    return XI, YI, ZI, ZI_sub
