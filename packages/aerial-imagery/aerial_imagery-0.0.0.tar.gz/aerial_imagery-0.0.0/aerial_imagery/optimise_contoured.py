

"""
Class structure to allow optimisation on contours.
"""
from aerial_imagery.optimise_subroutines import get_params
from aerial_imagery.contours import contour_loader, normalise_img, edge_loader


from scipy.spatial.distance import directed_hausdorff
import numpy as np
from scipy.spatial.distance import cdist
from skimage import measure
import matplotlib.pyplot as plt
from matplotlib import path
import scipy.stats
import cv2

def modified_hausdorff(A, B, MHD_percentile=60, filter_level=np.inf):
    """
    Compute the Modified Hausdorff Distance (MHD) between two 2D point sets A and B.

    Parameters:
    A : list of lists or 2D array
        First set of points.
    B : list of lists or 2D array
        Second set of points.
    MHD_percentile : int, optional
        Percentile to use for the MHD calculation (default is 60).
    filter_level : float, optional
        Maximum distance level to filter bad inputs (default is np.inf).

    Returns:
    float
        The Modified Hausdorff Distance between the two sets of points.
    """
    
      # This is a max distance level to filter bad inputs

    # print(filter_level)

    D = cdist(A, B)  # pairwise distances A[i] to B[j]

    # A to B: for each point in A, find its closest point in B
    min_dists_A_to_B = D.min(axis=1)
    min_dists_A_to_B = min_dists_A_to_B[min_dists_A_to_B < filter_level]  # Filter out large distances

    A_to_B = np.percentile(min_dists_A_to_B, MHD_percentile)

    # B to A: for each point in B, find its closest point in A
    min_dists_B_to_A = D.min(axis=0)
    min_dists_B_to_A = min_dists_B_to_A[min_dists_B_to_A < filter_level]  # Filter out large distances

    B_to_A = np.percentile(min_dists_B_to_A, MHD_percentile)
    
    return max(A_to_B, B_to_A)

class ContourOptimizer:
    """
    Class to optimize contours using the Modified Hausdorff Distance (MHD).
    """

    def __init__(self, myDGR, df_motion, ds_images, ocean, var_scales, bounds=None):
        """
        Initialize the ContourOptimizer with necessary parameters.

        Parameters:
        - myDGR: aerial_imagery direct georeferencing object.
        - df_motion: DataFrame containing motion data.
        - ds_images: Dataset containing images.
        - ocean: Reference altitude for ocean level.
        - var_scales: Scales for the variables.
        - bounds: Optional bounds for the grid.
        """

        self.verbose = False

        self.myDGR = myDGR
        self.df_motion = df_motion
        self.ds_images = ds_images
        self.ocean = ocean
        self.var_scales = var_scales
        self.bounds = bounds

        self.ind = 0  # Default index for optimization

        self.clip_contours = True  # Whether to clip the contours to the bounding box. Will be slower, but give better results.

        self.MHD_percentile = 60 # Default percentile for MHD calculation
        self.MHD_filter_level = np.inf  # Default filter level for MHD calculation

        self.su = 1  # Subsampling factor for contours, can be adjusted for performance
        self.Lambda = 1  # Regularization parameter, can be adjusted based on prior knowledge
        self.priors = None  # Placeholder for priors, can be set later

    def process_images(self, gb):

        ds_images = self.ds_images
        ind = self.ind

        raw_img = ds_images.isel(time=ind).temperature.values
        raw_img_sub = ds_images.isel(time=ind+1).temperature.values

        img = normalise_img(raw_img)
        img_sub = normalise_img(raw_img_sub)

        if gb is not None:
            img     = scipy.ndimage.gaussian_filter(img, sigma=gb)
            img_sub = scipy.ndimage.gaussian_filter(img_sub, sigma=gb)
        else:
            img     = img
            img_sub = img_sub

        self.raw_img = raw_img
        self.raw_img_sub = raw_img_sub

        self.img = img
        self.img_sub = img_sub


    def calculate_contours(self, levels):
        """
        Calculate contours for the given index.

        Parameters:
        - ind: Index of the image to process.
        - levels: Contour levels to use.
        - gb: Gaussian blur parameter.

        Returns:
        - Nothing, but sets contourx, contoury, contourx_sub, contoury_sub attributes.
        """

        ds_images = self.ds_images
        ind = self.ind

        contourx, contoury         = contour_loader(self.img, levels)
        contourx_sub, contoury_sub = contour_loader(self.img_sub, levels)

        self.contour = (contourx, contoury)
        self.contour_sub = (contourx_sub, contoury_sub)

    def calculate_edges(self, threshold1=7, threshold2=10, plot=False):
        
        contourx, contoury         = edge_loader(self.img,     threshold1=threshold1, threshold2=threshold2, plot=plot)
        contourx_sub, contoury_sub = edge_loader(self.img_sub, threshold1=threshold1, threshold2=threshold2, plot=plot)
        
        self.contour = (contourx, contoury)
        self.contour_sub = (contourx_sub, contoury_sub)

    def georef_contours(self, vector, other_params):

        # Save these for use by subfunctions
        self.__vector__ = vector
        self.__other_params__ = other_params
        
        myDGR      = self.myDGR
        # ds_images  = self.ds_images
        ocean      = self.ocean
        # bounds     = self.bounds
        var_scales = self.var_scales
        ind        = self.ind

        # These rely on calculating the contours first
        contours   = self.contour
        contours_sub = self.contour_sub

        contourx, contoury         = contours    
        contourx_sub, contoury_sub = contours_sub 

        contourx = contourx[::self.su]  # Subsample for speed
        contoury = contoury[::self.su]
        contourx_sub = contourx_sub[::self.su]
        contoury_sub = contoury_sub[::self.su]

        # NOTE, THIS ASSUMES LITTLE DIFFSCALE DIFFERENCE BETWEEN THE FIRST AND SECOND IMAGE. I THINK THIS IS REASONABLE. 
        myDGR, TIME1 = self.update_DGR(subframe=False)
        XI, YI, ZI = myDGR(contourx, contoury, target_z=ocean)
        
        myDGR, TIME2 = self.update_DGR(subframe=True)
        XI_sub, YI_sub, ZI_sub = myDGR(contourx_sub, contoury_sub, target_z=ocean)
        
        self.geo_contours = (XI, YI)
        self.geo_contours_sub = (XI_sub, YI_sub)
        self.times = (TIME1, TIME2)

    def plot_contours(self, ax=None, georef=False):
        """
        Plot the contours for the current index.

        Parameters:
        - ax: Optional matplotlib axis to plot on. If None, creates a new figure.
        """

        if ax is None:
            fig, ax = plt.subplots()

        if not georef:
            contourx, contoury         = self.contour    
            contourx_sub, contoury_sub = self.contour_sub 
        else:
            XI, YI = self.geo_contours
            XI_sub, YI_sub = self.geo_contours_sub

            contourx, contoury         = XI, YI
            contourx_sub, contoury_sub = XI_sub, YI_sub

        ax.plot(contourx, contoury, 'r.', label='Contour 1')
        ax.plot(contourx_sub, contoury_sub, 'b.', label='Contour 2')
        
        ax.legend()
        if georef:
            pass
            ax.set_title(f"Geroref contours for index {self.ind}")
            ax.set_xlabel('Easting (m)')
            ax.set_ylabel('Northing (m)')
        else:
            ax.invert_yaxis()
            ax.set_title(f"Pixel coordinate contours for index {self.ind}")

            ax.set_xlabel('X Pixel')
            ax.set_ylabel('Y Pixel')
            
        ax.set_aspect('equal')

    def _get_params(self):

        dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs = get_params(self.__vector__, self.__other_params__, self.var_scales)

        return dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs

    def update_DGR(self, subframe=False):
        """
        Update the Direct Georeferencing object with the current index.

        Parameters:
        - index: Index of the image to process.
        """

        myDGR      = self.myDGR
        df_motion  = self.df_motion
        var_scales = self.var_scales

        if subframe:
            ind = self.ind + 1
        else:
            ind = self.ind
        

        # dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs = get_params(vector, other_params, var_scales)
        dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs = self._get_params()
        ro = df_motion.iloc[ind]  # Use the first row for now, this is just a test
    
        X, Y, Z = ro['EASTING'], ro['NORTHING'], ro['ELLIPSOID HEIGHT']
        HEADING, PITCH, ROLL = ro['HEADING'], ro['PITCH'], ro['ROLL']
        # KAPPA, PHI, OMEGA = ro['KAPPA'], ro['PHI'], ro['OMEGA']

        # Apply the perturbations
        if subframe:
            X += dxs 
            Y += dys 
            Z += dzs 
            HEADING += dhs 
            PITCH   += dps 
            ROLL    += drs
        else:
            X += dx 
            Y += dy 
            Z += dz 
            HEADING += dh 
            PITCH   += dp 
            ROLL    += dr 

        if self.verbose:
            print(f"[X, Y, Z, H, R, P] for index {ind}: [{X:.2f}, {Y:.2f}, {Z:.2f}, {HEADING:.2f}, {PITCH:.2f}, {ROLL:.2f}]")

        myDGR.update_POS_NED(X, Y, Z)
        myDGR.update_HPR_Ref(HEADING, PITCH, ROLL, units='deg')

        return myDGR, ro.TIME
    
    def get_meshes(self, subframe=False):

        self.update_DGR(subframe=subframe)
        return self.myDGR.make_georef_grid(grid_n=None, alt=self.ocean)
    
    def get_bbox(self, subframe=False):
        """
        Get the bounding box for the georeferenced contours.
        """
        self.update_DGR(subframe=subframe)
        return self.myDGR.make_georef_bbox(grid_n=None, alt=self.ocean)

    def eval_func_hausdorff(self):

        XI, YI = self.geo_contours
        XI_sub, YI_sub = self.geo_contours_sub
        TIME1, TIME2 = self.times

        # Whether to clip the contours to the bounding box
        if self.clip_contours:
            boxx,  boxy,  boxz  = self.get_bbox()
            boxx_sub, boxy_sub, boxz_sub = self.get_bbox(subframe=True)

            q_points = np.column_stack((XI, YI))
            bounding_box_path_sub = path.Path(np.column_stack((boxx_sub, boxy_sub)))
            in_ind = bounding_box_path_sub.contains_points(q_points)
            XI = XI[in_ind]; YI = YI[in_ind]

            q_points_sub = np.column_stack((XI_sub, YI_sub))
            bounding_box_path = path.Path(np.column_stack((boxx, boxy)))
            in_ind_sub = bounding_box_path.contains_points(q_points_sub)
            XI_sub = XI_sub[in_ind_sub]; YI_sub = YI_sub[in_ind_sub]
        
        if False: # Normal Hausdorff distance
            projected_points_1 = np.column_stack((XI, YI))
            projected_points_2 = np.column_stack((XI_sub, YI_sub))

            hausdorff_distance = max(
                directed_hausdorff(projected_points_1, projected_points_2)[0],
                directed_hausdorff(projected_points_2, projected_points_1)[0]
            )
            total_cost = hausdorff_distance
        else: # Modified Hausdorff distance
            A = [[x, y] for x, y in zip(XI, YI)]
            B = [[x, y] for x, y in zip(XI_sub, YI_sub)]
            try:
                total_cost = modified_hausdorff(A, B, self.MHD_percentile, self.MHD_filter_level)
            except:
                total_cost = np.inf  # If it fails, return a large cost

        times = [TIME1, TIME2]

        return total_cost, XI, YI, XI_sub, YI_sub, times
    
    def get_params(self, vector, other_params=None, var_scales=None):
        """
        This is just a wrapper for the get_params function so that it doesn't need to be imported into any other code. 
        """

        var_scales = self.var_scales 
        return get_params(vector, other_params, var_scales)

    def objective_SUBfunction_hausdorf(self):
        """"
        This doesn't do anything anymore
        """

        total_cost, XI, YI, XI_sub, YI_sub, times = self.eval_func_hausdorff()
        
        return total_cost, XI, YI, XI_sub, YI_sub, times 
    
    def get_priors(self, df_uncertainty, subframe=True):
        """
        A function to get the SBET marginal uncertainties at a specific time.
        """

        if subframe:
            ind = self.ind + 1
        else:
            ind = self.ind

        ro = self.df_motion.iloc[ind]  

        df_time = df_uncertainty.index
        time = ro.TIME

        output = {}
        pairs = {}
        pairs['dx'] = 'std_E'
        pairs['dy'] = 'std_N'
        pairs['dz'] = 'std_U'
        pairs['dh'] = 'std_H'
        pairs['dp'] = 'std_P'
        pairs['dr'] = 'std_R'
        
        for pair in pairs:

            dt = np.abs(df_time - time)
            ti = np.where(dt == np.min(dt))[0][0]

            val = df_uncertainty[pairs[pair]].values[ti]
            output[pair] = val

            if False:
                print(f"SBET {pairs[pair]} at time {time} is {val:.3f}")

        output['time'] = time

        self.priors = output


    def objective_function_hausdorf(self, vector, other_params):


        self.georef_contours(vector, other_params)
        
        MHD, XI, YI, XI_sub, YI_sub, times = self.objective_SUBfunction_hausdorf()
        priors = self.priors

        if False:
            return total_cost # Not regularised and not a cost function
        
        C = scipy.stats.norm.logpdf(MHD, 0, 1)


        if not priors is None:

            dx, dy, dz, dh, dp, dr, dxs, dys, dzs, dhs, dps, drs = self._get_params()

            marg = priors

            P =  scipy.stats.norm.logpdf(dxs, 0, marg['dx'])
            P += scipy.stats.norm.logpdf(dys, 0, marg['dy'])
            P += scipy.stats.norm.logpdf(dzs, 0, marg['dz'])
            P += scipy.stats.norm.logpdf(dhs, 0, marg['dh'])
            P += scipy.stats.norm.logpdf(dps, 0, marg['dp'])
            P += scipy.stats.norm.logpdf(drs, 0, marg['dr'])

            log_prob = C + self.Lambda * P

        else:

            log_prob = C

        return -log_prob  


    def check_marginal_perts(self, vector, other_params, ext=0.005, m = 51):
        """
        A function to check the marginal perturbations. Essentially you're looking for the width of the "bowl" in the cost function. 
        Also any local minima or asymmetries.

        Note, this is pretty hokey, it only looks at the last 6 parameters - i.e. the second frame. 
        """

        assert len(vector) == 6, f"Vector must be of length 6, got {len(vector)}"

        var_scales = self.var_scales
        var_scales_dict = {}
        labels = ['dxs', 'dys', 'dzs', 'dhs', 'dps', 'drs']
        for i, label in enumerate(labels):
            var_scales_dict[label] = var_scales[i]
        
        func = self.objective_function_hausdorf

        mypertcosts = np.zeros([len(vector), m])
        myperts = np.zeros([len(vector), m])

        for n in np.arange(len(vector)):
            print(f"Parameter {n+1} {labels[n]}...")
            # if 

            mypert_lin = np.linspace(-ext, ext, m)
            if False:
                mypert = mypert_lin
            else: # Bias these towards zero for better resolution
                sign = np.sign(mypert_lin)
                mypert = np.abs(mypert_lin)**1.5 # Bias towards zero
                mypert = mypert * sign # Restore sign
                
                mypert = mypert / mypert[-1] * mypert_lin[-1] # Rescale
                
                pass
                
            scale = var_scales_dict[labels[n]]

            for i, pert in enumerate(mypert):
                # print(pert)
                vec_to_use = vector.copy()
                vec_to_use[n] += pert

                cost = func(vec_to_use, other_params=other_params)

                mypertcosts[n, i] = cost
                myperts[n, i] = pert*scale # This is the actual perturbation applied to the parameter inside the optimiser, and so this is what we want to plot
            
            # myperts.append(mypert)

            print(f"   done")

        # Last but not lweast output the unperturbed cost
        cost = func(vector, other_params)
        
        return cost, myperts, mypertcosts


    def compute_hessian_central(self, vector, other_params, epsilon=1e-5):
        """
        Compute the Hessian matrix of a scalar-valued function using centered finite differences.

        Parameters:

        vector : ndarray
            The point at which the Hessian is evaluated.
        other_params : ndarray
            Additional parameters for the objective function.
        epsilon : float, optional
            The step size for finite differences - this is scaled for each parameter, which is weird

        Returns:
        hessian : ndarray
            The Hessian matrix.
        """

        
        print(f"Calculating Hessian - V4")
        neg_log_prob = self.objective_function_hausdorf # This is the function we want to compute the Hessian of

        # func = lambda x, other_params: -neg_func(x, other_params)
        # func = neg_func
        
        x0 = np.asarray(vector)
        f_0  = neg_log_prob(x0,    other_params)

        n = x0.size
        hessian = np.zeros((n, n))

        for i in range(n):

            print(f"Starting row {i+1} of {n}")

            x_p = x0.copy()
            x_m = x0.copy()
            x_p[i] += epsilon
            x_m[i] -= epsilon
            f_p = neg_log_prob(x_p, other_params)
            f_m = neg_log_prob(x_m, other_params)
            hessian[i, i] = (f_p - 2 * f_0 + f_m) / epsilon**2
            
            for j in range(i+1, n):
                print(f"    Starting col {j+1} of {n}")

                x_pp = x0.copy(); x_pp[i] += epsilon; x_pp[j] += epsilon
                x_pm = x0.copy(); x_pm[i] += epsilon; x_pm[j] -= epsilon
                x_mp = x0.copy(); x_mp[i] -= epsilon; x_mp[j] += epsilon
                x_mm = x0.copy(); x_mm[i] -= epsilon; x_mm[j] -= epsilon

                f_pp = neg_log_prob(x_pp, other_params)
                f_pm = neg_log_prob(x_pm, other_params)
                f_mp = neg_log_prob(x_mp, other_params)
                f_mm = neg_log_prob(x_mm, other_params)

                value = (f_pp - f_pm - f_mp + f_mm) / (4 * epsilon**2)
                hessian[i, j] = value
                hessian[j, i] = value  # exploit symmetry
                    
        H = hessian
        K = np.linalg.inv(H)
        d = np.sqrt(np.diag(K))
        C = K/d[None, :]
        C = C/d[:, None]

        assert (np.linalg.eig(H)[0]>0).all(), f"Hessian around the central point {vector} with epsilon of {epsilon} is not positive definite"
        assert (np.diag(H)>0).all(), f"Hessian around the central point {vector} with epsilon of {epsilon} has non-positive diagonal elements"
        
        print(f"Hessian around the central point {vector} with epsilon of {epsilon} is positive definite")

        return H, K, C

