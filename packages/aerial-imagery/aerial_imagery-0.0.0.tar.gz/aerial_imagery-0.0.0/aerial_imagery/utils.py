import numpy as np

def reflec(w: np.ndarray, n_sw: float) -> float:
    """
    Parameters
    ----------
    w : numpy.ndarray
        Angle of incidence of a light ray at the water surface (radians)

    n_sw : float
        Index of refraction of seawater [default = 1.34]

    Returns
    -------
    rho : ndarray
        fresnel reflectance

    Equations
    ---------
    n_air sin(w) = n_sw sin(w_pr)

                 tan(w - w_pr)**2
    Refl(par)  = ----------------
                 tan(w + w_pr)**2

                 sin(w - w_pr)**2
    Refl(perp) = ----------------
                 sin(w + w_pr)**2

    Where:
         w      Incident angle
         n_air  Index refraction of Air
         w_pr   Refracted angle
         n_sw   Index refraction of sea water
    """

    assert np.all(w<=np.pi/2), "Imposssible angle"
    # w_pr = ne.evaluate("arcsin(sin(w) / n_sw)")  # noqa: F841
    # rho = ne.evaluate(
    #     "0.5*((sin(w-w_pr)/sin(w+w_pr))**2 + (tan(w-w_pr)/tan(w+w_pr))**2)"
    # )

    w_pr = np.arcsin(np.sin(w) / n_sw)  # noqa: F841
    rho = 0.5*((np.sin(w-w_pr)/np.sin(w+w_pr))**2 + (np.tan(w-w_pr)/np.tan(w+w_pr))**2)
    
    
    rho[w < 0.00001] = 0.0204078  # Unclear why NASA sets this value?

    return rho

def fresnel_rho(w: np.ndarray, n_sw=1.34) -> float:
    """
    Wrapper for .utils.reflec 
    """
    return reflec(w, n_sw)



def P_univ(z_x, sigma2_x):
    """
    Univariate Gaussian PDF of surface slope z_x for MSS sigma_x.
    """
    P = (1/(np.sqrt(2*np.pi*sigma2_x)))* \
        np.exp(-(1/2)*(z_x**2/sigma2_x))

    return P

def P(z_x, z_y, sigma2_x, sigma2_y, mean_x=0, mean_y=0):
    """
    Bivariate anisotropic Gaussian PDF of surface slopes z_x and z_x 
    with for MSS sigma2_x and sigma2_x.
    """

    P = (1/(np.sqrt(2*np.pi*sigma2_x*sigma2_y)))* \
    np.exp( -(1/2)*((z_x-mean_x)**2/sigma2_x + (z_y-mean_y)**2/sigma2_y) )

    return P


def get_mss_cox_munk(U_41, slick=False, low_wind_iso=False):
    """
    This is the MSS from section 6.3 of Cox and Munk (1954). 
    
    I note that there is anomalous behaviour in the absence of slicks that 
    sigma_c_2 is greater than sigma_u_2 for low wind. sigma_c_2 also never 
    vanishes - likely due to the range of the fit used. 

    Parameters
    ----------
    U_41: numeric
        Wind speed at 41 ft. 
    slick: bool
        A flag for whether there is a surface slick, as defined in Cox and Munk (1954)
    low_wind_iso: bool
        A flag to retern a modified version for low wind, where u_c is set to u_u

    Returns
    -------
    sigma_u_2: numeric
        The MSS slope for the principal axis - upwind
    sigma_c_2: numeric
        The MSS slope for the secondary axis - downwind
    sigma_2: numerc
        The total MSS slope (sigma_u_2 + sigma_c_2)

    References
    ----------
    Cox, C., & Munk, W. (1954). Measurement of the roughness of the sea surface 
    from photographs of the sun’s glitter. Josa, 44(11), 838-850.

    """


    U_41 = np.array(U_41)
    
    if np.array(U_41).shape == ():
        U_41 = U_41[None] 

    if not slick:
        mx = 0.000 + 0.00316*U_41 
        my = 0.003 + 0.00192*U_41 
        m  = 0.003 + 0.00512*U_41 

    else:
        mx = 0.005 + 0.00078*U_41 
        my = 0.003 + 0.00084*U_41 
        m  = 0.008 + 0.00156*U_41 

    # m = mx + my # Not actually how Cox and Munk (1954) did this

    if low_wind_iso: # This is a little condition I made to return isotropic conditions in low wind
        i = mx<my
        mx[i] = m[i]/2
        my[i] = m[i]/2

    sigma_u_2 = mx
    sigma_c_2 = my
    sigma_2   = m

    return sigma_u_2, sigma_c_2, sigma_2

# def get_mss_cheaply_iso(U_10):
#     """
#     This should use cox and munk, but I can't find it so I'm just 
#     digitising Rascle et al 2018's Fig 1c. 

#     To start, I know at 9 m/s sigma2_x = 0.028, sigma2_y = 0.020

#     I don't understand why MSSy never vanishes (has a y intercept).

#     """

#     print('WARNING: MADE THESE UP!!')

#     U_10 = np.array(U_10)
    
#     if np.array(U_10).shape == ():
#         U_10 = U_10[None] 

#     sx, sy =  [0.04964 * (U_10**0.5)]*2
#     mx, my = sx**2, sy**2 

#     m = np.sqrt(mx**2+my**2)
#     m = mx + my

#     if low_wind_iso: # This is a little condition I made to return isotropic conditions in low wind
#         i = mx<my
#         mx[i] = m[i]/2
#         my[i] = m[i]/2

#     return mx, my, m

# def get_mss_cheaply(U_10, low_wind_iso=False):
#     """
#     This should use cox and munk, but I can't find it so I'm just 
#     digitising Rascle et al 2018's Fig 1c. 

#     To start, I know at 9 m/s sigma2_x = 0.028, sigma2_y = 0.020

#     I don't understand why MSSy never vanishes (has a y intercept).

#     """

#     print('WARNING: MADE THESE UP!!')

#     U_10 = np.array(U_10)
    
#     if np.array(U_10).shape == ():
#         U_10 = U_10[None] 

#     # mx, my = U_10/321, U_10/450+0.0032
#     mx, my = U_10/321, U_10/535+0.0032

#     m = np.sqrt(mx**2+my**2)
#     m = mx + my

#     if low_wind_iso: # This is a little condition I made to return isotropic conditions in low wind
#         i = mx<my
#         mx[i] = m[i]/2
#         my[i] = m[i]/2

#     return mx, my, m

