import matplotlib.pyplot as plt
import numpy as np

def load(file, normalise=True,  kappa_rotation=0, reduce=True):
    """
    Function to load image. 

    Parameters
    ----------
    file : str
        File path to image
    normalise : bool
        Normalise image to 0-255 [default = True]
    reduce : bool
        Reduce image to uint8 [default = True]
    kappa_rotation : int
        Rotation of image [default = 0]. Options: 0, 90, 180, -90. 
        Positive rotation is counter clockwise. 
    
    """
    gray_ww = plt.imread(file)
    
    if normalise:
        gray_ww = gray_ww.astype(float)
        gray_ww = 255*gray_ww/np.max(gray_ww)

    if reduce:
        gray_ww = gray_ww.astype(np.uint8)

    if not kappa_rotation in [0, 90, 180, -90]:
        raise(Exception("kappa_rotation must be 0, 90, 180 or -90"))
    
    

    if len(gray_ww.shape) == 2:
        if kappa_rotation == 0:
            pass
        elif kappa_rotation == 90:
            gray_ww = gray_ww.T
            gray_ww = gray_ww[::-1, :]
        elif kappa_rotation == -90:
            gray_ww = gray_ww.T
        elif kappa_rotation == 180:
            gray_ww = gray_ww[::-1, :]
            print('YO')
    else:
        if kappa_rotation == 0:
            pass
        elif kappa_rotation == 90:
            gray_ww = gray_ww.transpose([1, 0, 2])
            gray_ww = gray_ww[::-1, :, :]
        elif kappa_rotation == -90:
            gray_ww = gray_ww.transpose([1, 0, 2])
        elif kappa_rotation == 180:
            gray_ww = gray_ww[::-1, :, :]
            print('YO')

    if False:
        new_max = 254

        gray_ww[gray_ww>new_max] = new_max
        gray_ww = gray_ww/np.uint8(new_max)
        gray_ww = gray_ww*254
        gray_ww = gray_ww.astype(np.uint8)

    return gray_ww