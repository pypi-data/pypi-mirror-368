import cv2 as cv
import numpy as np , pandas as pd
import matplotlib.pyplot as plt

# from dgrlocal import DGR 
import aerial_imagery.dgrlocal as dgrlocal
from aerial_imagery.dgrlocal import DGR 
from sklearn.neighbors import NearestNeighbors



def get_template(hole_size_pix, dark_core, plot=True):
    """
    Return a template for a hole of a given size. 

    User determines whether it has a dark core, or light core. 

    """

    hole_size_pix = int(hole_size_pix)
    template_pix = hole_size_pix*2 # Should be even number
    template_pix = np.ceil(hole_size_pix/2)*2 # Should be even number

    tx, ty = [np.arange(-template_pix/2, template_pix/2+1)]*2
    # tx, ty = [np.arange(0, np.ceil(template_pix/2)+1)]*2
    tx, ty = np.meshgrid(tx, ty)

    tt = (tx-hole_size_pix)**2 + (ty-hole_size_pix)**2 < (hole_size_pix/2)**2
    tt = (tx-0)**2 + (ty-0)**2 < (hole_size_pix/2)**2
    if dark_core:
        tt = ~ tt

    tt = tt.astype(np.uint8)
    # tt *= (2**7)
    tt *= 254#(2**7)

    if False: 
        template_file = 'template.tif' 
        cv.imwrite(template_file, tt.astype(np.uint8))
        template = cv.imread(template_file)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

        plt.pcolormesh(tx, ty, template)
        plt.colorbar()
        plt.show()

    else:
        template = tt

    if plot:
        plt.pcolormesh(tx, ty, tt, cmap='bone')
        plt.title(f'{hole_size_pix} pixel template')
        plt.colorbar()
        plt.show()

    return template

def get_template_old(hole_size_pix, dark_core, plot=True):
    """
    Return a template for a hole of a given size. 

    User determines whether it has a dark core, or light core. 

    """

    hole_size_pix = int(hole_size_pix)
    template_pix = hole_size_pix*2 # Should be even number

    tx, ty = [np.arange(0, template_pix+1)]*2
    tx, ty = np.meshgrid(tx, ty)

    tt = (tx-hole_size_pix)**2 + (ty-hole_size_pix)**2 < (hole_size_pix/2)**2
    if dark_core:
        tt = ~ tt

    tt = tt.astype(np.uint8)
    # tt *= (2**7)
    tt *= 254#(2**7)

    if False: 
        template_file = 'template.tif' 
        cv.imwrite(template_file, tt.astype(np.uint8))
        template = cv.imread(template_file)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

        plt.pcolormesh(tx, ty, template)
        plt.colorbar()
        plt.show()

    else:
        template = tt

    if plot:
        plt.pcolormesh(tx, ty, tt, cmap='bone')
        plt.title(f'{hole_size_pix} pixel template')
        plt.colorbar()
        plt.show()

    return template

def get_rec(topleft, bottomright):
    """Helper function to give a rectangle for plotting from 2 opposite points. 
    """
    tl = topleft
    br = bottomright

    x = [tl[0], tl[0], br[0], br[0], tl[0]]
    y = [tl[1], br[1], br[1], tl[1], tl[1]]

    return x, y

def match_template(gray, template, invert = False):
    """Main template matching code
    """
    w, h = template.shape[::-1]

    method = cv.TM_CCOEFF

    res = cv.matchTemplate(gray, template, cv.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

    if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
        want_the_min = True
        
    else:
        want_the_min = False
        
    if invert:
        want_the_min = not want_the_min
        
    if want_the_min:
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + w, top_left[1] + h)

    return res, min_val, max_val, min_loc, max_loc, top_left, bottom_right


import scipy.optimize as opt

def subpix_refinement(gray, template, local_maxima):

    def twoD_Gaussian(xy, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
        x, y = xy
        xo = float(xo)
        yo = float(yo)    
        a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
        b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
        c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
        g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) 
                                + c*((y-yo)**2)))
        return g.ravel()

    h, w = template.shape
    x = np.arange(0, w)
    y = np.arange(0, h)
    x, y = np.meshgrid(x, y)

    biggest_shift = 0

    local_maxima_subpix = local_maxima.copy()

    for i, pt in enumerate(local_maxima):
        my_window = gray[pt[1]-int(h/2):pt[1]+int(h/2)+1, pt[0]-int(w/2):pt[0]+int(w/2)+1]
        my_window = my_window-np.min(my_window)
        my_window = my_window/np.max(my_window)

        initial_guess = (1, w/2, h/2, w/4, h/8, 0, 0)
        try:
            popt, pcov = opt.curve_fit(twoD_Gaussian, (x, y), my_window.ravel(), p0=initial_guess)
        except:
            print(f'    ....subpix optimiser failed to fit point {i} at [{pt[1]}, {pt[0]}]')
        data_fitted = twoD_Gaussian((x, y), *popt).reshape(x.shape)

        amplitude, xo, yo, sigma_x, sigma_y, theta, offset = popt

        xd = xo - int(w/2)
        yd = yo - int(h/2)

        d = np.sqrt(xd**2+yd**2)
        biggest_shift = np.max([biggest_shift, d])

        myx, myy = pt
        local_maxima_subpix[i] = [myx+xd, myy+yd]

        if False:
            plt.imshow(my_window, cmap='bone')
            plt.contour(x, y, data_fitted, colors='r')
            plt.plot(xo, yo, 'b.')
            plt.plot(int(w/2), int(h/2), 'r.')
            print(xo, yo)
            print(xd, yd)
            print(pt)
        
    print(f'Subpixel correction complete, largest shift was {biggest_shift} pixels')

    return local_maxima_subpix

def locate_holes(gray, template, threshold, corner_max=None, window_upper=None):
    """
    Find pegboard holes based on template matching

    corner_max: all corners must be less than this value.
    """

    res, min_val, max_val, min_loc, max_loc, top_left, bottom_right = match_template(gray, template)

    threshold *= max_val

    w, h = template.shape[::-1]
        
    
    loc = np.where( res >= threshold)
    print(f'{len(loc[0])} points passed the initial threshold test')
            
    local_maxima = []
    # Now filter out points that are too close to others
    for pt in zip(*loc[::-1]):
        pass
        # x, y = get_rec(pt, (pt[0]+w, pt[1]+h)) 
        # plt.plot(x, y, 'r')

        my_res_window =  res[pt[1]-int(h/2):pt[1]+int(h/2), pt[0]-int(w/2):pt[0]+int(w/2)]
        my_window     =  gray[pt[1]-h:pt[1], pt[0]-w:pt[0]]
        my_window     =  gray[pt[1]:pt[1]+h, pt[0]:pt[0]+w]
        if 0 in my_res_window.shape:
            continue

    
        my_local_max = np.where(my_res_window==np.max(my_res_window))

        # my_local_max = [my_local_max[0][0]+int(h/2)+pt[1], my_local_max[1][0]+int(w/2)+pt[0]]
        my_local_max = [my_local_max[1][0]+pt[0], my_local_max[0][0]+pt[1]]

        add_point = False
        if my_local_max in local_maxima:
            # print('Already found this point')
            pass
        else:
            if corner_max is None:
                add_point = True
            else:

                list = [my_window[0, 0] <= corner_max , my_window[0, -1] <= corner_max , my_window[-1, 0] <= corner_max , my_window[-1, -1] <= corner_max ]
                bool = np.all(list)
                if bool:
                    add_point = True

                else:
                    pass
                    # print(my_window)
                    # print(list)
                    # print(bool)
                    # print(my_window[0, 0] <= corner_max)
                    # print(my_window[0, -1] <= corner_max)
                    # print(my_window[-1, 0] <= corner_max)
                    # print(my_window[-1, -1] <= corner_max)
                    
                    # print(pt)
                    # plt.figure()
                    # plt.pcolormesh(my_res_window)

                    # print(pt)
                    # plt.figure()
                    # plt.pcolormesh(my_window)
                    # plt.colorbar()
                    # error


        if add_point:
            local_maxima += [my_local_max]

    print(f'Result filtered to {len(local_maxima)} local peaks with the appropriate range.')
    

    return local_maxima, res

def find_keypoints(image, 
                   n_grid=144, 
                   board_size_px=140,
                   blob_params=dict(minArea=3.5,
                                    maxArea=200,
                                    filterByArea=True,
                                    filterByCircularity=False,
                                    filterByConvexity=False,
                                    filterByInertia=False,
                                    filterByColor=False,
                                    minDistBetweenBlobs=3,
                                    ),):
    
    
    # Set up the detector with user defined min and max thresholds
    params = cv.SimpleBlobDetector_Params()
    # Set the parameters, looping the dictionary
    for key, value in blob_params.items():
        setattr(params, key, value)
    params_repr = '\n'.join([f'\t{key}: {getattr(params, key)}' for key in dir(params) if not key.startswith('_')])
    # logger.debug(f'Blob Detector Parameters:\n{params_repr}')
    detector = cv.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(image)
    print(f'Found {len(keypoints)} keypoints')
    
    # Put keypoints into a dataframe
    keypoints_df = pd.DataFrame([[kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id] for kp in keypoints],
                                columns=['x_scaled', 'y_scaled', 'size', 'angle', 'response', 'octave', 'class_id'])

    # Filter outliers based on nearest neighbours


    # nn = NearestNeighbors(n_neighbors=min(n_grid,len(keypoints_df)),metric='euclidean')
    nn = NearestNeighbors(n_neighbors=np.min([n_grid, len(keypoints_df)]),metric='euclidean')
    nn.fit(keypoints_df[['x_scaled','y_scaled']])
    distances, indices = nn.kneighbors(keypoints_df[['x_scaled','y_scaled']])
    keypoints_df['mean_dist_scaled'] = distances[:,1:].mean(axis=1)
    keypoints_df['std_dist_scaled'] = distances[:,1:].std(axis=1)
    # Scale keypoints back to original image size
    
    # keypoints_df['x'] = keypoints_df.x_scaled/upsampling
    # keypoints_df['y'] = keypoints_df.y_scaled/upsampling
    keypoints_df['x'] = keypoints_df.x_scaled
    keypoints_df['y'] = keypoints_df.y_scaled

    origin = np.array([0,0])
    keypoints_df['origin_distance'] = np.linalg.norm(keypoints_df[['x','y']].values - origin, axis=1)

    # Need to think about this threshold more
    # keypoints_filtered = keypoints_df[keypoints_df.mean_dist_scaled<0.8*upsampling*board_size_px]
    keypoints_filtered = keypoints_df[keypoints_df.mean_dist_scaled<0.8*board_size_px]
    
    print(f'Filtered {len(keypoints_df)-len(keypoints_filtered)} outliers')
    print(f'Keypoints remaining: {len(keypoints_filtered)}')

    # keypoints_filtered_o = keypoints_filtered.copy()

    # If still more than n_grid, filter by the maximum mean distance
    if len(keypoints_filtered) > n_grid:
        keypoints_filtered = keypoints_filtered.sort_values('mean_dist_scaled', ascending=True).head(n_grid)
        print(f'Cropped to {n_grid} closest keypoints')

    local_maxima    = [[x, y] for x, y in zip(keypoints_filtered['x'], keypoints_filtered['y'])]

    local_maxima, ordered_points = sort_local_maxima_pb(local_maxima)

    # keypoints_filtered = keypoints_filtered.loc[ordered_points].copy()
    # local_maxima = np.array(local_maxima)[ordered_points]
    
    return local_maxima, keypoints_filtered, keypoints_df


def sort_local_maxima(local_maxima):
    """Sort the local maxima by distance from the origin."""

    if True: # This should be an input
        lm = np.array(local_maxima)
        ld = np.sum(lm**2, 1)
        li = np.argsort(ld)
        li
        local_maxima = [local_maxima[i] for i in li]

    return local_maxima

def sort_local_maxima_pb(local_maxima):
    """Paul's method for walking through nearest neighbours to sort a grid. 

    """

    xy = np.array(local_maxima) # This is an n x 2 np array

    origin_distance = np.sqrt(np.sum(xy**2, axis=1))
    points_to_visit = list(origin_distance.argsort())

    current_point = points_to_visit.pop(0)
    ordered_points = [current_point]

    while len(points_to_visit) > 1:
        # Find the closest point from the 3 nearest neighbours that has the minimum change in y
        # nn = NearestNeighbors(n_neighbors=min(3,len(points_to_visit)),metric='euclidean')
        nn = NearestNeighbors(n_neighbors=np.min([3,len(points_to_visit)]),metric='euclidean')

        xy_rem = xy[points_to_visit, :] # This is an n x 2 np array
        xy_cur = xy[current_point, :]  # This is an m x 2 np array
        
        nn.fit(xy_rem)
        distances, indices = nn.kneighbors(xy_cur.reshape(1,-1))
        # Find the point with the minimum change in y
        
        min_dy = np.inf
        cy = xy_cur[1]
        
        near_ys = [xy_rem[i, 1] for i in indices.flatten()]

        for d,(i, y) in enumerate(zip(indices.flatten(), near_ys)):
            dy = np.abs(y - cy)
            if dy < min_dy:
                min_dy = dy
                next_point = points_to_visit[i]
                next_dist = distances.flatten()[d]

        if next_dist > 1.3*np.min(distances):
            # If the next point is too far away (>~sqrt(2)), just take the closest point
            next_point = points_to_visit[indices.flatten()[np.argmin(distances)]]

        ordered_points.append(next_point)
        points_to_visit.remove(next_point)
        current_point = next_point

    # Add the last point
    ordered_points.append(points_to_visit.pop(0))
    local_maxima = [local_maxima[i] for i in ordered_points]

    return local_maxima, ordered_points


def local_maxima_plot(gray, local_maxima, local_maxima_raw, figsize=(15, 8), fontsize=16):

    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(1, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    x = np.array(local_maxima)[:, 0]
    y = np.array(local_maxima)[:, 1]

    mux = np.mean(x)
    muy = np.mean(y)

    dx = np.abs(x-mux)
    dy = np.abs(y-muy)

    d = np.max([dx, dy]) + 10
    
    ax1.imshow(gray, cmap = 'gray')
    ax2.imshow(gray, cmap = 'gray', alpha=0.5)

    ax2.plot(x, y, alpha=0.7, lw=4)

    ncols = 5
    cmap = plt.cm.get_cmap('Spectral', ncols)

    for i, (pt, pt_sp) in enumerate(zip(local_maxima_raw, local_maxima)):
        
        ax1.plot(pt[0], pt[1], 'r+', label='original' if i==0 else None)
        ax1.plot(pt_sp[0], pt_sp[1], 'b+', label='refined' if i==0 else None)
        ax1.text(pt_sp[0], pt_sp[1], i, color='b', fontsize=fontsize)

        ax2.plot(pt[0], pt[1], 'r+', label='original' if i==0 else None)
        ax2.plot(pt_sp[0], pt_sp[1], 'b+', label='refined' if i==0 else None)

        text_col = cmap(np.mod(i, ncols))
        ax2.text(pt_sp[0], pt_sp[1], i, color=text_col, fontsize=fontsize, fontweight='bold')

    ax2.legend()
    title = f'Hole locations filtered to {len(local_maxima)} unique points'
    

    plt.suptitle(title)

    ax2.set_xlim([mux-d, mux+d])
    ax2.set_ylim([muy+d, muy-d])
    ax2.set_aspect('equal')

    return fig


def find_grid(grid_size, local_maxima, square, plot=True, gray=None, buffer=80, plot_full=True, bad_detects=[], recalculate_rows=False, figsize=(15, 15)):
    """Define a grid based on the holes located in detect_pegboard.locate_holes

    """

    N, M = grid_size

    if gray is None:
        plot = False

    if plot and plot_full:
        plt.figure(figsize=figsize)
        plt.imshow(gray, cmap = 'gray')

        for i, pt in enumerate(local_maxima):
            if i in bad_detects:
                plt.plot(pt[0], pt[1], 'k.')
                plt.text(pt[0], pt[1], i, color='k', fontsize=16)
            else:
                plt.plot(pt[0], pt[1], 'b.')
                plt.text(pt[0], pt[1], i, color='b', fontsize=16)

        for i, pt in enumerate(square):
            my_pt = local_maxima[pt]
            plt.plot(my_pt[0], my_pt[1], 'r.')
            plt.text(my_pt[0], my_pt[1], pt, color='r', fontsize=16)

    # FOR NOW DO  VERY CRUDE BURRER MAY NEED IMPROVING LATER
    dp = buffer
    sx = [local_maxima[square[0]][0] - dp,
         local_maxima[square[1]][0] - dp,
         local_maxima[square[2]][0] + dp,
         local_maxima[square[3]][0] + dp]

    sy = [local_maxima[square[0]][1] + dp,
         local_maxima[square[1]][1] - dp,
         local_maxima[square[2]][1] - dp,
         local_maxima[square[3]][1] + dp]
    sx += [sx[0]]
    sy += [sy[0]]
    

    bottomx = np.linspace(local_maxima[square[0]][0], local_maxima[square[3]][0], M)
    bottomy = np.linspace(local_maxima[square[0]][1], local_maxima[square[3]][1], M)

    topx = np.linspace(local_maxima[square[1]][0], local_maxima[square[2]][0], M)
    topy = np.linspace(local_maxima[square[1]][1], local_maxima[square[2]][1], M)


    leftx = np.linspace(local_maxima[square[0]][0], local_maxima[square[1]][0], N)
    lefty = np.linspace(local_maxima[square[0]][1], local_maxima[square[1]][1], N)

    rightx = np.linspace(local_maxima[square[3]][0], local_maxima[square[2]][0], N)
    righty = np.linspace(local_maxima[square[3]][1], local_maxima[square[2]][1], N)

    if plot and plot_full:

        # plt.plot(sx, sy, 'r')
        plt.plot(bottomx, bottomy, 'r', marker='x', lw=2, ms=10)
        plt.plot(topx, topy, 'm', marker='x', lw=2, ms=10)
        plt.plot(leftx, lefty, 'b', marker='x', lw=2, ms=10)
        plt.plot(rightx, righty, 'c', marker='x', lw=2, ms=10)

    
    ## NOW ACTUALLY FIND THE GRID
    print(f'Bad detects are: {bad_detects}')
    bi = np.array([i not in bad_detects for i in np.arange(len(local_maxima))])
    local_maxima = np.array(local_maxima)
    local_maxima = local_maxima[bi, :]

    grid_ind = np.nan*np.zeros(grid_size)

    local_maxima_x = np.array([p[0] for p in local_maxima])
    local_maxima_y = np.array([p[1] for p in local_maxima])
    local_maxima_y

    for row in np.arange(0, N):
        if recalculate_rows: # This will recalculate the grid after each row. Helps for sloping grids
            i = 0
        else:
            i = row
        
        rowx = np.linspace(leftx[i], rightx[i], M)
        rowy = np.linspace(lefty[i], righty[i], M)

        if plot and plot_full:
            plt.plot(rowx, rowy, 'wx')
            plt.plot(rowx, rowy, 'k+')

        dx = local_maxima_x[:, None] - rowx
        dy = local_maxima_y[:, None] - rowy
        d2 = dx**2 + dy**2

        my_ind = np.argmin(d2, 0)
        
        grid_ind[row, :] = my_ind

        # plt.plot(leftx, lefty, marker='o')
        # plt.plot(rightx, righty, marker='o')
        
        if recalculate_rows:
            # Recalculate the left and right hand sides from the current located point. 
            xl, yl = local_maxima_x[my_ind[0].astype(int)],   local_maxima_y[my_ind[0].astype(int)]
            xr, yr = local_maxima_x[my_ind[M-1].astype(int)], local_maxima_y[my_ind[M-1].astype(int)]
            
            leftx = np.linspace(xl, leftx[-1], N-row)
            lefty = np.linspace(yl, lefty[-1], N-row)

            rightx = np.linspace(xr, rightx[-1], N-row)
            righty = np.linspace(yr, righty[-1], N-row)

            # Now drop the current row to give remaining rows ONLY. 
            leftx  = leftx[1::]
            lefty  = lefty[1::]
            rightx = rightx[1::]
            righty = righty[1::]


    if plot and plot_full:
        title = f'Square and initial edgepoint guesses from user inputs'
        plt.title(title)
        plt.show()

    
    if plot:
        plt.figure(figsize=figsize)
        plt.imshow(gray, cmap = 'gray')

    grid_ind
    grid_x = local_maxima_x[grid_ind.astype(int)]
    grid_y = local_maxima_y[grid_ind.astype(int)]
    grid_z = np.nan*grid_y

    

    if plot:
        mp1, mp2 = [], []
    
        gridcol = 'r'
        for rx, ry, rz in zip(grid_x, grid_y, grid_z):
            mp1.append(plt.plot(rx, ry, '--', color=gridcol, alpha=1))
        for rx, ry, rz in zip(grid_x.T, grid_y.T, grid_z.T):
            mp2.append(plt.plot(rx, ry, '--', color=gridcol, alpha=1))
            
        plt.text(grid_x[0, 0], grid_y[0, 0],          '   [1, 1]   ', color='r', ha='right', fontweight='bold')
        plt.text(grid_x[N-1, 0], grid_y[N-1, 0],     f'   [{N}, 1]   ', color='r', ha='right', fontweight='bold')
        plt.text(grid_x[N-1, M-1], grid_y[N-1, M-1], f'   [{N}, {M}]   ', color='r', ha='left', fontweight='bold')
        plt.text(grid_x[0, M-1], grid_y[0, M-1],     f'   [1, {M}]   ', color='r', ha='left', fontweight='bold')

        plt.grid('on')
        
    if False:
        plt.plot(bottomx, bottomy, 'r', marker='x', lw=2, ms=10)
        plt.plot(topx, topy, 'm', marker='x', lw=2, ms=10)
        plt.plot(leftx, lefty, 'b', marker='x', lw=2, ms=10)
        plt.plot(rightx, righty, 'c', marker='x', lw=2, ms=10)

    
    
    return grid_x, grid_y

template_match_defaults = {'hole_size_pix': 5,
                            'threshold': 0.8,
                            'dark_core': False,
                            'corner_max': 100}
blob_params_defaults = dict(minArea=3.5,
                    maxArea=1000,
                    filterByArea=True,
                    filterByCircularity=False,
                    filterByConvexity=False,
                    filterByInertia=False,
                    filterByColor=False,
                    minDistBetweenBlobs=3,
                    )

blob_detect_defaults = dict(blob_params=blob_params_defaults)

def full_whack(gray, 
               locate_method='template_match',
               locate_args=template_match_defaults, 
               grid_size=None, 
               square=None, 
               bad_detects=[], 
               nn_filter = True,
               n_grid  = 144,
               board_size_px = 150,
               recalculate_rows=False,
               figsize=(15, 15), 
               fontsize=16,
               plot=True,):
    
    """Run through the whole process

    locator_args: a dictionary of arguments for the function that finds the holes.

    """

    locate_method = locate_method.lower()
    if locate_method == 'template_match':
        args = template_match_defaults.copy()
        args.update(locate_args)

        hole_size_pix    = args['hole_size_pix']
        threshold        = args['threshold']
        dark_core        = args['dark_core']
        corner_max       = args['corner_max']
        refine_sub_pix   = args['refine_sub_pix']

        print(f'hole_size_pix = {hole_size_pix}')

        template = get_template(hole_size_pix, dark_core, plot=False)

        local_maxima, res = locate_holes(gray, template, threshold, corner_max=corner_max)

        prelim_outputs = [template, res] 


    elif locate_method == 'blob_detect':

        args = blob_detect_defaults.copy()
        args.update(locate_args)
        
        blob_params    = args['blob_params']

        local_maxima, keypoints_i, _ = find_keypoints(gray, blob_params=blob_params)

        local_maxima_raw = local_maxima # Not sure there is subpix in there

        prelim_outputs = [keypoints_i] 

    print(f'Detected {len(local_maxima)} holes')


    # Fileter based on nearest neighbours
    if nn_filter: 

        nn = NearestNeighbors(n_neighbors=np.min([n_grid, len(local_maxima)]), metric='euclidean')
        xy = np.array(local_maxima)

        nn.fit(xy)
        distances, indices = nn.kneighbors(xy)
        mean_dist_scaled = distances[:,1:].mean(axis=1)
        std_dist_scaled = distances[:,1:].std(axis=1)

        # # Need to think about this threshold more
        good_points = mean_dist_scaled<0.8*board_size_px

        local_maxima = [[x, y] for x, y, in xy[good_points]]

        print(f'     ....Filetered this to {len(local_maxima)} holes')


    # Refine subpixel
    if locate_method == 'template_match':
        if refine_sub_pix:
            print('    Running subpixel refinement...')
            local_maxima_raw = local_maxima
            local_maxima = subpix_refinement(gray, template, local_maxima_raw)
        else:
            print('    Not running subpixel refinement.')
            local_maxima_raw = local_maxima
    else:
        print(f'    There is no sub pixel refinement for method {locate_method}...')
        local_maxima_raw = local_maxima

    # Now we sort
    local_maxima, _ = sort_local_maxima_pb(local_maxima)

    if grid_size is None or square is None:
        print("We don't have a grid or a corner index, so we'll just plot the result located points.")
        preliminary = True
        local_maxima_plot(gray, local_maxima, local_maxima_raw, figsize=figsize, fontsize=fontsize)
        # plt.imshow(template, cmap = 'gray')

        
        return local_maxima, prelim_outputs
    
    else:
        preliminary = False
        grid_x, grid_y = find_grid(grid_size, local_maxima, square, gray=gray, plot=plot, plot_full=False, bad_detects=bad_detects, figsize=figsize, recalculate_rows=recalculate_rows)
        return grid_x, grid_y




def estimate_pose_calcfunc(input, DGR_KWARGS, markerCorners, tag_size, plot=True):
    """
    Run forward and backward reprojection for a square marker of size tag_size x tag_size.

    Requires the markerCorners variable which specifies the pixel coordinates of the tag.

    # MARKER CORNERS MATCHES THE CV2.ARUCO DEFINITION, SO TOP LEFT, TOP RIGHT, BOTTOM RIGHT, BOTTOM LEFT

    Bottom left is defined automatically as the world coordinate [0, 0, 0] point. Tag is assumed to be in the X-Y plane [Z=0 everywhere]
    """

    yaw, pitch, roll, tx, ty, tz = input
    
    x0, y0 = markerCorners[0][0][0]
    x1, y1 = markerCorners[0][0][1]
    x2, y2 = markerCorners[0][0][2]
    x3, y3 = markerCorners[0][0][3]
    xyz0 = np.array([x0, y0, 1])[:, None]
    xyz1 = np.array([x1, y1, 1])[:, None]
    xyz2 = np.array([x2, y2, 1])[:, None]
    xyz3 = np.array([x3, y3, 1])[:, None]

    xyz = np.hstack([xyz0, xyz1, xyz2, xyz3])
    # XYZ = np.array([[0, 1, 0, 1], [1, 1, 0, 1], [1, 0, 0, 1], [0, 0, 0, 1]]).T
    XYZ = np.array([[0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, 0]]).T * tag_size
    # XYZ = np.array([[0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, 0]]).T * tag_size

    deg2rad = np.pi/180

    lin_offsets = [0, 0, 0] 
    ang_offsets = [0, 0, 0] 

    offsets = {'CRx': lin_offsets[0], 
    'CRy':        lin_offsets[1], 
    'CRz':        lin_offsets[2], 
    'CRtheta':    ang_offsets[0], 
    'CRphi':      ang_offsets[1], 
    'CRpsi':      ang_offsets[2], }

    DGR_KWARGS.update(offsets=offsets)
    DGR_KWARGS.update(verbose=False)

    dgr = DGR(**DGR_KWARGS)
    dgr.update_POS_Ref(tx, ty, tz)
    dgr.update_IMU_Ref(yaw, pitch, roll, frame='NED')
    
    # meshxf, meshyf, meshzf = dgr.make_georef_grid(alt=0)
    if plot:
        dgr.plot_scene(plot_corners=True, al=3, bbox_alt=0)
        plt.gca().set_zlim(0, 6)


    X, Y, Z = XYZ
    xyz_calc = dgr(X, Y, Z, reverse=True)
    
    if plot:
        print(xyz[0:2, :])
        # [plt.text(x, y, z, i) for i, (x,y,z) in  enumerate(xyz.T)]
        [plt.plot(x, y, z, 'r+') for x,y,z in  xyz_calc.T]
                
        print('Printing Z')
        print(Z)
        plt.plot(X, Y, Z, 'r') 
        
        # plt.plot(, 'r.')

    return xyz, xyz_calc, XYZ, dgr

def estimate_pose_minfunc(input, DGR_KWARGS, markerCorners, tag_size):
    """
    Return the pixel reprojection error for a tag geometry and user defined pose. 

    Can be minimised to estimate the pose. 

    """

    xyz, xyz_calc, XYZ, dgr = estimate_pose_calcfunc(input, DGR_KWARGS, markerCorners, tag_size, plot=False)

    diff = xyz_calc - xyz
    # print('diff')
    # print(diff)
    # print()

    return  np.linalg.norm(diff)

import scipy.optimize

def estimate_pose(DGR_KWARGS, markerCorners, tag_size, x0=[0, 0, 0, 0, 0, 1], plot=True):
    """A Function for estimating the POSE of the scene once tag corners are found.

    Returns a DGR object with the pose loaded.
    """
    # res = scipy.optimize.minimize(minfunc, x0=[0, 0, 0, 0, 0, 2], method='Nelder-Mead')
    res = scipy.optimize.minimize(estimate_pose_minfunc, x0=[0, 0, 0, 0, 0, 3], args=(DGR_KWARGS, markerCorners, tag_size))

    yaw, pitch, roll, tx, ty, tz = res.x
    # input = [0., 0., 0., 0., 0., 5.]
    xyz, xyz_calc, XYZ, dgr = estimate_pose_calcfunc(res.x, DGR_KWARGS, markerCorners, tag_size, plot=plot)

    print(f'Total pixel error: {res.fun:0.1f}')
    print(f'Yaw: {yaw*180/np.pi:0.1f}')
    print(f'Pitch: {pitch*180/np.pi:0.1f}')
    print(f'Roll: {roll*180/np.pi:0.1f}')
    print(f'X: {tx:0.1f}')
    print(f'Y: {ty:0.1f}')
    print(f'Z: {tz:0.1f}')

    thresh = 3
    assert res.fun < thresh, f'Total pixel error remains above {thresh:0.1f}, pose estimation failed.'

    return dgr, res
 

def plotpose(dgr, n=6):
    """Plot out the reference frame using the output DGR object
    """
    x0, y0, z0 = dgr(0, 0, 0, reverse=True)
    plt.plot(x0, y0, 'w*')
    print(x0, y0)

    x_x, y_x, z_x = dgr([0, 1], [0, 0], [0, 0], reverse=True)
    plt.plot(x_x, y_x, 'r', label='+ve X')

    x_y, y_y, z_y = dgr([0, 0], [0, 1], [0, 0], reverse=True)
    plt.plot(x_y, y_y, 'b', label='+ve Y')

    x_z, y_z, z_z = dgr([0, 0], [0, 0], [0, 1], reverse=True)
    plt.plot(x_z, y_z, 'g', label='+ve Z')

    a1 = np.array([0, 0, 1, 1, 0])/2
    a2 = np.array([0, 1, 1, 0, 0])/2
    a3 = np.array([0, 0, 0, 0, 0])/2

    def fill_grid_image(x, y, c, n):
        """
        This is a dud actually, it should linspace in world coords. 
        """
        Xl = np.linspace(x[0], x[1], n)
        Yl = np.linspace(y[0], y[1], n)
        Xr = np.linspace(x[3], x[2], n)
        Yr = np.linspace(y[3], y[2], n)
        
        for x1, x2, y1, y2 in zip(Xl, Xr, Yl, Yr):
            plt.plot([x1, x2], [y1, y2], c, alpha=0.5, lw=0.8)

        Xl = np.linspace(x[1], x[2], n)
        Yl = np.linspace(y[1], y[2], n)
        Xr = np.linspace(x[0], x[3], n)
        Yr = np.linspace(y[0], y[3], n)
        
        for x1, x2, y1, y2 in zip(Xl, Xr, Yl, Yr):
            plt.plot([x1, x2], [y1, y2], c, alpha=0.5, lw=0.8)

    def fill_grid(x, y, z, c, n, OPT='xy'):
        """
        """
        
        OPT = OPT.lower()
        
        x = np.linspace(np.min(x), np.max(x), n)
        y = np.linspace(np.min(y), np.max(y), n)
        z = np.linspace(np.min(z), np.max(z), n)

        if OPT in ['xy', 'yx']:
            xg, yg = np.meshgrid(x, y)
            zg = 0*xg
        elif OPT in ['xz', 'zx']:
            xg, zg = np.meshgrid(x, z)
            yg = 0*xg
        elif OPT in ['yz', 'zy']:
            yg, zg = np.meshgrid(y, z)
            xg = 0*yg
        else:
            error

        X, Y, Z = dgr(xg, yg, zg, reverse=True)
    
        for x, y, z in zip(X, Y, Z):
            plt.plot(x, y, z, color=c, alpha=0.5, lw=0.8)
            # plt.plot(x, y, z, color=c, alpha=1, lw=2)

        for x, y, z in zip(X.T, Y.T, Z.T):
            plt.plot(x, y, z, color=c, alpha=0.5, lw=0.8)
            # plt.plot(x, y, z, color=c, alpha=1, lw=2)

    x_xy, y_xy, z_xy = dgr(a1, a2, a3, reverse=True)
    c = 'r'
    c = 'magenta'
    plt.fill(x_xy, y_xy, c, alpha=0.5, label='X-Y plane')
    plt.plot(x_xy, y_xy, c, alpha=1)
    # fill_grid(x_xy, y_xy, c, n=n)
    fill_grid(a1, a2, a3, c, n=n)

    x_yz, y_yz, z_yz = dgr(a3, a1, a2, reverse=True)
    c = 'b'
    c = 'cyan'
    plt.fill(x_yz, y_yz, c, alpha=0.5, label='Y-Z plane')
    plt.plot(x_yz, y_yz, c, alpha=1)
    # fill_grid(x_yz, y_yz, c, n=n)
    fill_grid(a3, a1, a2, c, n=n, OPT='YZ')

    x_xz, y_xz, z_xz = dgr(a1, a3, a2, reverse=True)
    c = 'limegreen'
    c = 'yellow'
    plt.fill(x_xz, y_xz, c, alpha=0.5, label='X-Z plane')
    plt.plot(x_xz, y_xz, c, alpha=1)
    # fill_grid(x_xz, y_xz, c, n=n)
    fill_grid(a1, a3, a2, c, n=n, OPT='XZ')

    plt.legend()



def validate(dgr, grid_x, grid_y):
    """
    Just calculate average spacing and std for offline validation
    """
    X, Y, Z = dgr(grid_x, grid_y, 0)

    dx = X[0:-1, :] - X[1::, :]
    dy = Y[0:-1, :] - Y[1::, :]
    dz = Z[0:-1, :] - Z[1::, :]
    d1 = np.sqrt(dx**2 + dy**2 + dz**2)

    dx = X[:, 0:-1] - X[:, 1::]
    dy = Y[:, 0:-1] - Y[:, 1::]
    dz = Z[:, 0:-1] - Z[:, 1::]
    d2 = np.sqrt(dx**2 + dy**2 + dz**2)

    d = np.hstack([np.ravel(d1), np.ravel(d2)])

    return d