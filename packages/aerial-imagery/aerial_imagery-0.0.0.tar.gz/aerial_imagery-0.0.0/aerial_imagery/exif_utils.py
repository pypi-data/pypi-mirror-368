import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_exif_changes(ds_exif):
    """
    Plot the changes in EXIF data over time.
    """
    
    exposure_change = np.append(0, np.diff(ds_exif['EXIF:ExposureTime'].values)) != 0 
    fnumber_change  = np.append(0, np.diff(ds_exif['EXIF:FNumber'].values)) != 0 
    iso_change      = np.append(0, np.diff(ds_exif['EXIF:ISO'].values)) != 0

    any_change = exposure_change | fnumber_change | iso_change
    # any_change = exposure_change | fnumber_change #| iso_change
    # any_change = exposure_change #| fnumber_change #| iso_change


    exif_time = ds_exif['time'].values 
    exif_time = exif_time - exif_time[0]  # Make relative to first time
    exif_time /= 1e9

    any_change_lin = np.append(0, np.where(any_change)[0])
    any_change_lin = np.append(any_change_lin, len(exif_time)-1)

    ylim = plt.gca().get_ylim()

    for i in np.arange(0, len(any_change_lin)-1):
        start = any_change_lin[i]
        end = any_change_lin[i+1]

        xs = np.array([exif_time[start], exif_time[start], exif_time[end], exif_time[end], exif_time[start]] ).astype(int)
        ys = np.array([ylim[0], ylim[1], ylim[1], ylim[0], ylim[0]] )
        
        lab = f'{ds_exif['EXIF:ExposureTime'].values[start]} s, {ds_exif['EXIF:FNumber'].values[start]}, ISO {ds_exif['EXIF:ISO'].values[start]}'
        plt.fill(xs, ys, alpha=0.5, label=lab)

        plt.legend()

