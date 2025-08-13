import navpy, math
import matplotlib.pyplot as plt

import numpy as np 
import aerial_imagery.utils as utils
from aerial_imagery.cameras import set_camera

# import wave_radar as wr


def get_B_rel(self, zeta_1, zeta_2, U_41=5, grid=None):
    """
    Get relative brightness for a dgr object.
    """

    mx, my, m = utils.get_mss_cox_munk(U_41, low_wind_iso=True)

    meshx, meshy, meshz, camera_zenith, camera_azim  = self.get_camera_angles(grid=grid)
    grid = [meshx, meshy, meshz]

    meshx, meshy, meshz, Z_xf, Z_yf, theta_f, psi_f  = self.get_specular_facets(grid=grid)
    rho_fres, other_out = self.get_fresnel(grid=grid)

    p = utils.P(Z_xf, Z_yf, mx, my, zeta_1, zeta_2)
    p = 100*p/np.max(p)

    theta_r = theta_f
    # meshdx, meshdy, meshdz = meshx-self._UTM_x, meshy-self._UTM_y, meshz-self._UTM_z
    # meshdh = np.abs(meshdx + 1.j*meshdy)
    # meshdh = np.abs(meshdx + 1.j*meshdy)
    # camera_zenith = np.arctan2(meshdh, self._UTM_z)

    B_SunG_rel = p/(np.cos(camera_zenith)*np.cos(theta_r)**4)
    B_SunG_rel *= rho_fres

    B_SunG_rel = 100*B_SunG_rel/np.max(B_SunG_rel)

    return B_SunG_rel