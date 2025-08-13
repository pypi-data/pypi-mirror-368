import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import aerial_imagery.utils as utils


"""
Distortion functions for aerial imagery. OpenCV uses the following model for distortion:

x_distorted = x * (1 + k1 * r^2 + k2 * r^4 + k3 * r^6) + 2 * p1 * x * y + p2 * (r^2 + 2 * x^2)
y_distorted = y * (1 + k1 * r^2 + k2 * r^4 + k3 * r^6) + p1 * (r^2 + 2 * y^2) + 2 * p2 * x * y

where r^2 = x^2 + y^2, and (x, y) are the coordinates of the point in the undistorted image. The distortion 
coefficients k1, k2, k3, p1, and p2 are used to model the radial and tangential distortion of the lens. The 
distortion coefficients are usually obtained by calibrating the camera using a set of images of a checkerboard 
pattern. The distortion coefficients are then used to undistort the images, and to correct for the distortion 
in the images.

The inverse of the distortion model is nonlinear, and is usually solved using an iterative method. Here is a bit 
of a primer for radial only distortion:

https://math.stackexchange.com/questions/692762/how-to-calculate-the-inverse-of-a-known-optical-distortion-function

Here is another paper that discusses numerical derivation of inverse distortion coefficients:

https://www.researchgate.net/publication/315824536_Calculating_the_Inverse_Radial_Distortion_Model_Based_on_Zhang_method

The roots moduel in numpy (https://numpy.org/doc/stable/reference/generated/numpy.roots.html) may be beneficial for this. 


"""

def distort_radial(x, y, dist_coeffs, camera_mtx):
    """
    Distorts X and Y points using a 3 parameter model for radial distortion.

    Currently, only the iterative method is implemented for undistortion.

    Parameters
    ----------
    x, y : numpy.ndarray
        Arrays containing the x and y coordinates of the undistorted points.
    dist_coeffs : numpy.ndarray (3,)
        The 3 radial distortion coefficients.
    camera_mtx : numpy.ndarray (3,3)
        The 3x3 camera matrix.

    Returns
    -------
    x_distorted, y_distorted : numpy.ndarray
        Arrays containing the x and y coordinates of the distorted points.
    """

    assert camera_mtx.shape == (3,3), "The camera matrix must be a 3x3 matrix."

    k1, k2, k3 =  dist_coeffs
    f_x_mm, f_y_mm, c_x, c_y = camera_mtx[0,0], camera_mtx[1,1], camera_mtx[0,2], camera_mtx[1,2]

    x_norm = (x - c_x) / f_x_mm
    y_norm = (y - c_y) / f_y_mm
    
    r2 = x_norm**2 + y_norm**2
    r4 = r2**2
    r6 = r2**3

    gamma = 1 + k1*r2 + k2*r4 + k3*r6

    x_distorted_norm = x_norm * gamma
    y_distorted_norm = y_norm * gamma

    x_distorted = x_distorted_norm * f_x_mm + c_x
    y_distorted = y_distorted_norm * f_y_mm + c_y
    
    return x_distorted, y_distorted

def distort_full(x, y, k1, k2, k3, p1, p2):
    """
    Distort X and Y points using 5 parameter model for both radial and tangential distortion. 
    """

    r2 = x**2 + y**2
    r4 = r2**2
    r6 = r2**3

    x_distorted = x * (1 + k1 * r2 + k2 * r4 + k3 * r6) + 2 * p1 * x * y + p2 * (r2 + 2 * x**2)
    y_distorted = y * (1 + k1 * r2 + k2 * r4 + k3 * r6) + p1 * (r2 + 2 * y**2) + 2 * p2 * x * y

    raise NotImplementedError("Have not properly implemented this for normalised coordinates.")

    return x_distorted, y_distorted

def undistort_radial(x_distorted, y_distorted, dist_coeffs, camera_mtx, method='iterative', verbose=False, niter=20):
    """
    Undistorts X and Y points using a 3 parameter model for radial distortion.

    Currently, only the iterative method is implemented for undistortion.

    Parameters
    ----------
    x_distorted, y_distorted : numpy.ndarray
        Arrays containing the x and y coordinates of the distorted points.
    dist_coeffs : numpy.ndarray (3,)
        The 3 radial distortion coefficients.
    camera_mtx : numpy.ndarray (3,3)
        The 3x3 camera matrix.
    method : str, optional
        The method to use for undistortion. Default is 'iterative'.
    verbose : bool, optional
        If True, prints out additional information during the undistortion process. Default is False.
    niter : int, optional
        The number of iterations to perform if using the iterative method. Default is 20.

    Returns
    -------
    x, y : numpy.ndarray
        Arrays containing the x and y coordinates of the undistorted points.
    """

    k1, k2, k3 =  dist_coeffs
    f_x_mm, f_y_mm, c_x, c_y = camera_mtx[0,0], camera_mtx[1,1], camera_mtx[0,2], camera_mtx[1,2]

    x_distorted_norm = (x_distorted - c_x) / f_x_mm
    y_distorted_norm = (y_distorted - c_y) / f_y_mm

    if method.lower() == 'iterative': 

        # This is r', not r which we need!!
        r_distorted = np.sqrt(x_distorted_norm**2 + y_distorted_norm**2)
        
        # Initial guess for small distortion
        r_N = r_distorted
        if verbose:
            print('Iterating to find the distorted radius now!')

        for i in np.arange(0, niter) :
            
            r_Nplus1 = r_distorted / (1 + dist_coeffs[0]*r_N**2 + dist_coeffs[1]*r_N**4 + dist_coeffs[2]*r_N**6)

            diff = np.sum(np.abs(r_Nplus1-r_N))
            
            r_N = r_Nplus1
            if verbose:
                print(f'The difference after N iterations is {diff}')
            pass

        r = r_N
        r2 = r**2
        r4 = r2**2
        r6 = r2**3
        
        gamma = 1 + k1*r2 + k2*r4 + k3*r6

        x_norm = x_distorted_norm/gamma
        y_norm = y_distorted_norm/gamma

        x = x_norm * f_x_mm + c_x
        y = y_norm * f_y_mm + c_y


    else:
        raise NotImplementedError("Haven't implemented the other methods yet.")

    return x, y

def undistort_full(x, y, k1, k2, k3, p1, p2):
    """
    Undistort X and Y points using model for both radial and tangential distortion. 
    """

    # The distortion model is nonlinear, and is usually solved using an iterative method. 
    # Here is a bit of a primer for radial only distortion:
    # https://math.stackexchange.com/questions/692762/how-to-calculate-the-inverse-of-a-known-optical-distortion-function
    # Here is another paper that discusses numerical derivation of inverse distortion coefficients:
    # https://www.researchgate.net/publication/315824536_Calculating_the_Inverse_Radial_Distortion_Model_Based_on_Zhang_method
    # The roots moduel in numpy (https://numpy.org/doc/stable/reference/generated/numpy.roots.html) may be beneficial for this. 

    raise NotImplementedError("Haven't implemented the inverse of the 5 parameter distortion model yet.")


#### OpenCV parser functions, if one is so inclined
def undistort_radial_opencv(xd, yd, dist_coeffs, camera_matrix):
    """
    Undistorts points using OpenCV's undistortPoints function.

    Parameters
    ----------
    xd, yd : numpy.ndarray
        Arrays containing the x and y coordinates of the distorted points.
    dist_coeffs : numpy.ndarray (3,)
        The 3 radial distortion coefficients. This function will map these to the 5 
        parameter model used by OpenCV.
    camera_matrix : numpy.ndarray
        The camera matrix.

    Returns
    -------
    xu, yu : numpy.ndarray
        Arrays containing the x and y coordinates of the undistorted points.
    """

    
    dist_coeffs_cv            = np.array([0, 0, 0, 0, 0]).astype('float32')
    dist_coeffs_cv[[0, 1, 4]] = dist_coeffs
    dist_coeffs_cv = dist_coeffs_cv.reshape(1, 5).astype('float32')
    
    camera_matrix = camera_matrix.astype('float32')

    s = xd.shape
    xd, yd = xd.ravel(), yd.ravel()

    distorted_point = np.vstack([xd, yd]).T
    distorted_point = np.expand_dims(distorted_point, axis=1)

    undistorted_point      = cv.undistortPoints(distorted_point, camera_matrix, dist_coeffs_cv, None, camera_matrix)

    # undistorted_point_norm = cv.undistortPoints(distorted_point, camera_matrix, dist_coeffs, None)
    # undistorted_point_norm = cv.convertPointsToHomogeneous( undistorted_point_norm ) 

    # rtemp = ttemp = np.array([0. ,0. ,0. ], dtype='float32')
    # redistorted_point, hmmm = cv.projectPoints(undistorted_point_norm, rtemp, ttemp, camera_matrix, dist_coeffs)

    xu = undistorted_point[:, 0, 0]
    yu = undistorted_point[:, 0, 1]

    xu = xu.reshape(s)
    yu = yu.reshape(s)

    return xu, yu

def distort_radial_opencv(xu, yu, dist_coeffs, camera_matrix):
    """
    Distorts points using OpenCV's projectPoints function.

    Parameters
    ----------
    xu, yu : numpy.ndarray
        Arrays containing the x and y coordinates of the undistorted points.
    dist_coeffs : numpy.ndarray(3,)
        The 3 radial distortion coefficients. This function will map these to the 5 
        parameter model used by OpenCV.
    camera_matrix : numpy.ndarray
        The camera matrix.

    Returns
    -------
    xr, yr : numpy.ndarray
        Arrays containing the x and y coordinates of the distorted points.
    """

    dist_coeffs_cv            = np.array([0, 0, 0, 0, 0]).astype('float32')
    dist_coeffs_cv[[0, 1, 4]] = dist_coeffs
    dist_coeffs_cv = dist_coeffs_cv.reshape(1, 5).astype('float32')
    
    camera_matrix = camera_matrix.astype('float32')

    s = xu.shape
    xu, yu = xu.ravel(), yu.ravel()

    undistorted_point = np.vstack([xu, yu]).T
    undistorted_point = np.expand_dims(undistorted_point, axis=1)

    # undistorted_point_norm = cv.undistortPoints(distorted_point, camera_matrix, dist_coeffs, None)
    undistorted_point_norm = (undistorted_point - camera_matrix[:2,2]) / camera_matrix[[0,1],[0,1]]

    undistorted_point_norm = cv.convertPointsToHomogeneous( undistorted_point_norm ) 

    rtemp = ttemp = np.array([0. ,0. ,0. ], dtype='float32')
    redistorted_point, hmmm = cv.projectPoints(undistorted_point_norm, rtemp, ttemp, camera_matrix, dist_coeffs_cv)

    xr = redistorted_point[:, 0, 0]
    yr = redistorted_point[:, 0, 1]

    xr = xr.reshape(s)
    yr = yr.reshape(s)

    return xr, yr
