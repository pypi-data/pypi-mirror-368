import scipy.ndimage
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
import cv2

"""
Various functions to get contours from images. These are used in, for example, cross correlating and rectifying images. 
Contours have the advantage over full cross correlation in that they don't require regridding of the dataset. 

1. Matplotlib contouring - very slow, but works.
2. Skimage contouring - fast
3. OpenCV edge detection 

"""

def get_contour(meshx, meshy, img_norm, levels=2):

    contour = plt.contour(meshx, meshy, img_norm, levels=levels, colors="r")
    plt.close()

    x_coords, y_coords = [], []
    for i, level in enumerate(contour.levels):
        paths = contour.collections[i].get_paths()
        for path in paths:
            vertices = path.vertices
            x_coords, y_coords = vertices[:, 0], vertices[:, 1]

    return x_coords, y_coords

def get_contour2(img, levels):

    contour = plt.contour(img, levels=levels, colors="r")
    plt.close()

    x_coords, y_coords = [], []
    for i, level in enumerate(contour.levels):
        paths = contour.collections[i].get_paths()
        for path in paths:
            vertices = path.vertices
            x_coords, y_coords = vertices[:, 0], vertices[:, 1]

    return x_coords, y_coords

def get_contour_skimage(img, levels=[0], shortest_allowable_contour=100):
    """
    Get contours from a normalized image with skimage.
    """

      # This is a filter to keep us to real contours and not noise

    all_x = []
    all_y = []
    for level in levels:
        contours = measure.find_contours(img, level=level)
        # x, y = contours[1].T
        # plt.plot(x, y)

        for contour in contours:
            # x, y = contour.T
            y, x = contour[:, 0], contour[:, 1]

            if len(x) > shortest_allowable_contour:
                all_x.append(x)
                all_y.append(y)

    if len(all_x) > 0:
        all_x = np.concatenate(all_x)
        all_y = np.concatenate(all_y)

    if False:
        plt.plot(all_x, all_y, 'r.')
        plt.gca().set_aspect('equal')
        plt.xlabel('X Pixel')
        plt.ylabel('Y Pixel')
        plt.gca().invert_yaxis()

    return all_x, all_y

def normalise_img(Z):
    """
    Normalise to mean of zero and standard deviation of one.
    """
    
    if False:
        Z_norm = Z - np.nanmin(Z)
        Z_norm = Z_norm / np.nanmax(Z_norm)
    else:
        Z_norm = Z - np.nanmean(Z)
        Z_norm = Z_norm / np.nanstd(Z_norm)

    return Z_norm

def split_line_by_distance_np_m(coords, max_dist):
    """
    coords: (N, 2) array-like of (x, y) in meters
    max_dist: maximum cumulative segment distance
    Returns: list of sub-arrays (each sub-line)
    """
    coords = np.array(coords)
    diffs = np.diff(coords, axis=0)
    dists = np.linalg.norm(diffs, axis=1)

    segments = []
    current = [coords[0]]
    total = 0.0

    for i in range(1, len(coords)):
        this = dists[i-1]
        # print(this)
        total += this

        if this >= max_dist:
            segments.append(np.array(current))
            current = [coords[i]]
            total = 0.0
        else:
            current.append(coords[i])


    if len(current) > 1:
        segments.append(np.array(current))

    return segments


def contour_loader(my_img, levels):

    contour_func = get_contour2
    contour_func = get_contour_skimage
        
    my_contourx, my_contoury = contour_func(my_img, levels=levels)

    return my_contourx, my_contoury

def edge_loader(my_img, threshold1=7, threshold2=10, plot=False):

    blur = cv2.GaussianBlur(my_img, (3, 3), 1.4)

    blur = blur.astype(np.uint8)

    # Apply Sobel operator
    sobelx = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=3)  # Horizontal edges
    sobely = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=3)  # Vertical edges

    # Compute gradient magnitude
    gradient_magnitude = cv2.magnitude(sobelx, sobely)

    # Apply Canny Edge Detector
    if False:
        blur2 = cv2.convertScaleAbs(blur)
    else:
        blur2 = blur
    edges = cv2.Canny(blur2, threshold1=threshold1, threshold2=threshold2)
    
    edgey, edgex = np.where(edges)

    if plot:
        plt.imshow(blur)
        plt.show()
        plt.imshow(blur2)
        plt.show()
        plt.imshow(gradient_magnitude)
        plt.colorbar()
        plt.show()
        plt.imshow(gradient_magnitude>6)
        plt.show()
        plt.imshow(edges)
        plt.plot(edgex, edgey, 'r.', ms=0.5)
        plt.show()

    return edgex, edgey