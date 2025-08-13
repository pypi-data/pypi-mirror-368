# Various tools for aerial imagery in oceanography

## Distortion
Radial disrtortion is implemented identically to OpenCV. The main module is `aerial_imagery.distortion`.  There is also a notebook comparing this module to OpenCV [here](https://github.com/iosonobert/aerial_imagery/blob/main/notebooks/distortion_us_vs_opencv.ipynb). The image bellow is from this notebook. 

<img src="./images/distortion.png" width="800">

## Pose estimates
Pose is a bit of a nightmare when you start comparing OpenCV and aerospace conventions. Demonstrations of how to do this are in [this notebook](https://github.com/iosonobert/aerial_imagery/blob/main/notebooks/pose_estimate_us_vs_opencv.ipynb)

<center><img src="./images/00-23-59-881-radiometric.pose.png" width="400"></center>

## Calibration
Calibration is pretty straight forward in OpenCV, and if using radial distortion only the parameters are interchangeable, so why wouldn't you do that? 

You can, but as far as I'm aware the camera positions and orientations in OpenCV calibration are either fully free parameters or specified apriori. You can't provide other constraints e.g. constrain cameras to lie on a sphere and look outward at some tangent to the sphere. This would be useful if, say, you know your camera lies on a sphere. The aim here is to build such a flexible calibration tool. 

Any other reasons? Well open CV has it's own optimiser. If you wanted to use some other machine learning or Bayesian approach, you'd need acccess to the calibration machinery. 

I've had a go at implementing my own optimiser, but it's not much chop. 

# DGR modules

There are 2 main classes that do the DGR. 

- [dgrlocal](https://github.com/iosonobert/aerial_imagery/blob/main/aerial_imagery/dgrlocal.py) is the main development class designed to use Applanix outputs. It is missing some functionality of the older classes, I'll add these back when the code stabilises. 
- [direct_gr_c2002](https://github.com/iosonobert/aerial_imagery/blob/main/aerial_imagery/direct_gr_c2002.py) was the original module designed to use the full Corriea et al. (2002) reference frames

[direct_gr_uwa](https://github.com/iosonobert/aerial_imagery/blob/main/aerial_imagery/direct_gr_uwa.py) was the initial attempt to pivot to Applanix outputs before I trimmed it back. This can probably go. 

Other modules handle very specific pieces of the puzzle, e.g. image distortion, pre programmed camera models, interface with imagery etc. 
 
<center><img src="./images/Spinning_complex.gif" width="500"></center>
