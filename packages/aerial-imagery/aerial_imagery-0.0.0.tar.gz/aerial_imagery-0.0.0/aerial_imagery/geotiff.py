
import numpy as np
from scipy import sparse
from scipy.interpolate import griddata

import rasterio
from rasterio.transform import from_origin


"""
Stealing interpolate functions from SFODA.


"""

def make(meshx, meshy, img, bounds=None, dxdy=5.0):

    assert meshx.shape == meshy.shape, "meshx and meshy must have the same shape"
    assert meshx.ndim == 2, "meshx must be a 2D array"
    assert meshx.shape == img.shape, "mesh and img must have the same shape"

    X, Y = meshx, meshy
    Z = img  # Assuming img is the temperature data or similar, may fail for other data types

    # Example resolution (in projected units like meters, or degrees if using lat/lon)
    dx = dy = dxdy   

    # Get bounds from X/Y
    if bounds is None:
        xmin, xmax = np.nanmin(X), np.nanmax(X)
        ymin, ymax = np.nanmin(Y), np.nanmax(Y)
        # xmin += 400 
        # ymin += 350
        # xmax -= 400 
        # ymax -= 350
    else:
        # xmean = np.nanmean(X)
        # ymean = np.nanmean(Y)
        # xmin = xmean - 200
        # xmax = xmean + 200
        # ymin = ymean - 200
        # ymax = ymean + 200 
        xmin, xmax, ymin, ymax = bounds

    # Create target grid coordinates
    xi = np.arange(xmin, xmax, dx)
    yi = np.arange(ymin, ymax, dy)
    XI, YI = np.meshgrid(xi, yi)


    # Flatten the irregular grid points
    points = np.column_stack((X.ravel(), Y.ravel()))
    values = Z.ravel()

    if False:
        # Interpolate to regular grid
        print(f'Interpolating to regular grid {XI.shape}...')
        ZI = griddata(points, values, (XI, YI), method='linear')  # or 'nearest', 'cubic'
    else:
        myGrid = RegGrid([xmin, xmax], [ymin, ymax], dx, dy)

        ZI = myGrid.griddata(X, Y, Z)

    return XI, YI, ZI

def save(projectionstr, XI, YI, ZI, dxdy, filename):
    """
    Save the interpolated grid data to a file.

    Args:
        XI (np.ndarray): X coordinates of the grid.
        YI (np.ndarray): Y coordinates of the grid.
        ZI (np.ndarray): Interpolated values on the grid.
        dxdy (float): Grid spacing in the x and y directions.
        filename (str): Name of the file to save the data.
    """
    

    # Define affine transform: from upper-left corner
    # transform = from_origin(xi[0], yi[-1] + dy, dx, dy)
    transform = from_origin(XI[0, 0], YI[-1, -1] + dxdy, dxdy, dxdy)

    nodata_val = -9999
    ZI_filled = np.where(np.isnan(ZI), nodata_val, ZI)

    print(f'Saving to {filename}...')

    with rasterio.open(
        filename,
        'w',
        driver    = 'GTiff',
        height    = ZI.shape[0],
        width     = ZI.shape[1],
        count     = 1,
        dtype     = ZI_filled.dtype,
        crs       = projectionstr,
        transform =transform,
        nodata=nodata_val,  # <<< explicitly define nodata
    ) as dst:
        dst.write(np.flipud(ZI_filled), 1)
    

        
class RegGrid(object):
    """
    Class for a regularly spaced cartesian grid
    """
    meshgrid = True

    def __init__(self, xlims, ylims, dx, dy, **kwargs):
        self.__dict__.update(**kwargs)

        self.ox = xlims[0]
        self.oy = ylims[0]
        self.dx = dx
        self.dy = dy
        self.xlims = xlims
        self.ylims = ylims

        #  Construct a 2D mesh of particles
        self.x = np.arange(xlims[0], xlims[1], dx)
        self.y = np.arange(ylims[0], ylims[1], dy)

        if self.meshgrid:
            self.X, self.Y = np.meshgrid(self.x, self.y)

        # shp = self.X.shape
        self.ny = self.y.size
        self.nx = self.x.size

    def returnij(self, x, y):
        """
        Returns the i,j (cols,rows) of the points in i,j

        Returns NaNs for points that are out of bounds
        """

        i = np.floor((x - self.ox) / self.dx)
        j = np.floor((y - self.oy) / self.dy)

        # Check the bounds
        ind = x > self.xlims[1]
        ind = i >= self.nx
        i[ind] = np.nan
        j[ind] = np.nan

        ind = x < self.ox
        ind = i < 0
        i[ind] = np.nan
        j[ind] = np.nan

        ind = y > self.ylims[1]
        ind = j >= self.ny
        i[ind] = np.nan
        j[ind] = np.nan

        ind = y < self.oy
        ind = j < 0
        i[ind] = np.nan
        j[ind] = np.nan

        # return i.astype(int), j.astype(int)
        return i, j

    def griddata(self, x, y, z):
        """
        Grids data in the vectors x, y and z.

        Uses sparse matrices and therefore duplicate entries are averaged.

        """
        # Get the coordinates
        i, j = self.returnij(x, y)
        ind = np.isfinite(i)

        i, j = i.astype(int), j.astype(int)

        # Build two sparse matrices - one for the data and one to count 
        # the number of entries
        ctr = np.ones(z.shape)

        # return i, j, ind
        data  = sparse.coo_matrix((z[ind],   (j[ind], i[ind])), shape=(self.ny, self.nx))
        count = sparse.coo_matrix((ctr[ind], (j[ind], i[ind])), shape=(self.ny, self.nx))

        data = data / count

        # return np.array(data.todense())
        return np.array(data)
    