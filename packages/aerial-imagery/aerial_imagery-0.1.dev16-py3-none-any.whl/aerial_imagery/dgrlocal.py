import navpy, numpy as np
import math
import matplotlib.pyplot as plt

import aerial_imagery.utils as utils
import aerial_imagery.distortion as distortion

from aerial_imagery.cameras import set_camera
import cv2 as cv

# Module for direct georeferencing alla Correia et al. 2002

R_NED_to_ENU = np.array([[0, 1, 0],[1, 0, 0],[0, 0, -1]])

def yaw_pitch_roll_from_R(R):

    yaw   =  math.atan2(R[1,0], R[0,0])
    pitch = -math.asin(R[2,0])
    roll  =  math.atan2(R[2,1], R[2,2])

    return yaw, pitch, roll

def R_yaw_pitch_roll(yaw, pitch, roll):
    "2 ways to do this"
    
    R_yaw_pitch_roll = np.array([[math.cos(yaw)*math.cos(pitch),-math.sin(yaw)*math.cos(roll)+math.cos(yaw)*math.sin(pitch)*math.sin(roll),math.sin(yaw)*math.sin(roll)+math.cos(yaw)*math.cos(roll)*math.sin(pitch)]
                ,
                [math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(roll)+math.sin(roll)*math.sin(pitch)*math.sin(yaw),-math.cos(yaw)*math.sin(roll)+math.sin(pitch)*math.sin(yaw)*math.cos(roll)]
                ,
                [-math.sin(pitch),math.cos(pitch)*math.sin(roll),math.cos(pitch)*math.cos(roll)]])

    assert(np.all(np.isclose(R_yaw_pitch_roll, navpy.angle2dcm(yaw, pitch, roll).T)))
    
    return R_yaw_pitch_roll


class DGR(object):
    # This is the reference point
    _yaw_Ref   = np.nan #rad
    _pitch_Ref = np.nan #rad
    _roll_Ref  = np.nan #rad

    _solar_azim = np.nan #rad
    _solar_zenith  = np.nan #rad

    def __init__(self, camera='ZED2_C2022', camera_options={}, **kwargs):
        
        self.verbose = kwargs.pop('verbose', True,)

        self.name = kwargs.pop('name', 'Unnamed AF')
        offsets = kwargs.pop('offsets', {},)
        self.kappa_rotation = kwargs.pop('kappa_rotation', 0,) # This is how the camera is intended to be mounted in the gimbal, usuallo 0, pi/2 or -pi/2

        set_camera(self, camera, camera_options)

        if self.verbose:
            print('Creating airframe with:')
            print(f'    Camera = "{camera}"')
            print(f'         f_mm = "{self._f_mm}"')
            print(f'         c_x  = "{self._c_x}"')
            print(f'         c_y  = "{self._c_y}"')
            print(f'    Offsets = {offsets}')

        # Camera frame to Reference frame 
        ## First for C0 - i.e. no kappa rotation
        R_C0_to_Ref = np.array([[0, 0, 1],[-1, 0, 0],[0, 1, 0]])  # Corriea et al (2022)
        R_C0_to_Ref = np.array([[1, 0, 0],[0, 1, 0],[0, 0, 1]])   # Leave unchanged
        R_C0_to_Ref = np.array([[0, -1, 0],[-1, 0, 0],[0, 0, 1]]) # Swap X and Y and reverse

        R_C0_to_Ref = np.array([[0, -1, 0],[1, 0, 0],[0, 0, 1]])  # Swap X and -Y 

        ## Next the kappa rotation
        kappa_rot_mat = R_yaw_pitch_roll(self.kappa_rotation, 0, 0)
        
        ## Now the total rotation
        self.R_C_to_Ref_deterministic = kappa_rot_mat@R_C0_to_Ref

        # This will not be the case anymore, this is a key calibration parameter
        ## self.T_C_to_Ref set in self.update_translations(offsets)

        # UAS frame to END frame. This was NED in C2022.
        ## Need the translation only, rotation set by UAS IMU
        # self.T_UAS_to_END = np.array([[0],[0],[0]]) # Define NED origin - default to same as the UAS
        self.T_Ref_to_NED = np.array([[0],[0],[0]]) # Define NED origin - default to same as the UAS

        # END frame to ENU frame. This was NED in C2022.
        ## Need the rotation only, translation set by UAS XYZ position
        self.R_NED_to_ENU = R_NED_to_ENU # np.array([[0, 1, 0],[1, 0, 0],[0, 0, -1]])

        self.dist_coeffs=None

        self.update_translations(offsets)

    def update_translations(self, offsets):

        # offsets = self.offsets
        # Offsets - camera gimbal
        CRx = offsets.pop('CRx', 0)
        CRy = offsets.pop('CRy', 0)
        CRz = offsets.pop('CRz', 0)
        CRtheta = offsets.pop('CRtheta', 0)
        CRphi   = offsets.pop('CRphi', 0)
        CRpsi   = offsets.pop('CRpsi', 0)

        # Offsets - Gimbal to UAS
        ## Not needed for Applanix

        # Camera frame to Reference frame
        self.T_C_to_Ref = np.array([[CRx], [CRy], [CRz]])

        R_C_to_Ref_mounting = R_yaw_pitch_roll(CRtheta, CRphi, CRpsi)
        self.R_C_to_Ref = R_C_to_Ref_mounting@self.R_C_to_Ref_deterministic
 
        # Gimbal frame to UAS frame
        ## We don't need this for the Applanix method

        if self.verbose:
            print(f'Camera to reference linear offsets')
            print(f'  CRx = {CRx}')
            print(f'  CRy = {CRy}')
            print(f'  CRz = {CRz}')
            print(f'Camera to reference angular offsets')
            print(f'  CRtheta = {CRtheta}')
            print(f'  CRphi   = {CRphi}')
            print(f'  CRpsi   = {CRpsi}')

    def build_K(self):
        
        self.K = np.array([[self._fx_pix, 0,            self._c_x],
                           [0,            self._fy_pix, self._c_y],
                           [0,            0,            1]])
    
    def update_IMU_UAS(self, yaw, pitch, roll):
        """
        Function removed, Applanix doesn't care about the airframe reference
        """
        pass
        # self._yaw_UAS   = yaw
        # self._pitch_UAS = pitch
        # self._roll_UAS  = roll

        # self.R_UAS_to_END = R_yaw_pitch_roll(self._yaw_UAS, self._pitch_UAS, self._roll_UAS)
        
    def update_IMU_Ref(self, yaw, pitch, roll, frame='NED'):
        """
        Experimenting with 2 ways to specify, the first more an gimbal encoder approach, the second
        more a 2 IMU. The second one is not yet working.  
        """
        self._yaw_Ref   = yaw
        self._pitch_Ref = pitch
        self._roll_Ref  = roll

        self._frame_Ref = frame
        inv = np.linalg.inv

        if frame.upper() == 'ENU':
            raise('Exception')
            self.R_Ref_to_ENU   = R_yaw_pitch_roll(yaw, pitch, roll)
            self.R_Ref_to_NED = inv(self.R_NED_to_ENU) @ self.R_Ref_to_ENU
        if frame.upper() == 'NED':

            """
            This gives you your frame straight into NED as we believe the P4RTK does. 
            """
                
            self.R_Ref_to_NED   = R_yaw_pitch_roll(yaw, pitch, roll)
            self.R_Ref_to_ENU   = self.R_NED_to_ENU @ self.R_Ref_to_NED
            # self.R_G_to_UAS = inv(self.R_UAS_to_END) @ inv(self.R_END_to_ENU) @ R_G_to_ENU

        else:
            raise(Exception('oi'))

        
    def update_POS_Ref(self, x, y, z):
        
        self._UTM_x = x
        self._UTM_y = y
        self._UTM_z = z
    
    @property
    def Ref_UTM_xyz(self):
    
        return np.array([[self._UTM_x], [self._UTM_y], [self._UTM_z]])
    
    @property
    def T_NED_to_ENU(self):
        
        return self.UAS_UTM_xyz

    @property
    def FOV(self):
        # Field of view in degrees

        fovx = 2*np.arctan(self._npix_x/(2*self._fx_pix)) * (180/np.pi)
        fovy = 2*np.arctan(self._npix_y/(2*self._fy_pix)) * (180/np.pi)

        return fovx, fovy
        
    def print_FOV_metres(self, altitude):
    
        fovx, fovy = self.FOV
        fovx *= np.pi/180
        fovy *= np.pi/180

        # print(round(fovx), round(fovy))

        viewx = 2*np.tan(fovx/2)*altitude
        viewy = 2*np.tan(fovy/2)*altitude

        print("FOV {:.0f}  by {:.0f} m at altitide of {} m [if looking straight down].".format(abs(viewx), abs(viewy), altitude))

    def __call__(self, P_u, P_v, target_z = 0, fulloutput=False, halfoutput=False,
                 reverse=False):
        """
        Convert between ENU coordinates and pixel coordinates [use the reverse flag to toggle 
        between the two]. Note this assumes a rectified image. 

        Parameters
        ----------
            P_u, P_v: floats or 1D or 2D np.array of floats
                X and Y position of the input data to be geo rectified. By default, these are 
                pixel coordinates, but if using reverse=True these are geographic positions.  
            target_z: float
                Height of the photographed object in metres 

        Optional
        --------
            reverse: bool
                Toggle the direction of georectification. 
        """


        # def distort(P_C, dist_coeffs, reverse=False):

        #     if dist_coeffs is None:

        #         if self.verbose:
        #             print('No distortion')
        #         return P_C

        #     else:

        #         # Note, I'm going for the absolute simplest distortion model here. Simpler than: 
        #         # https://learnopencv.com/understanding-lens-distortion/
        #         if self.verbose:
        #             print('I got that distortion')

                
            
        #         if reverse:
        #             if self.verbose:
        #                 print('This is undistortion, which has to be done iteratively.')

        #             # Iterative approach needed?
        #             # https://math.stackexchange.com/questions/692762/how-to-calculate-the-inverse-of-a-known-optical-distortion-function

        #             P_C_prime_prime = P_C
        #             P_X_prime_prime = P_C_prime_prime[0, :]
        #             P_Y_prime_prime = P_C_prime_prime[1, :]

        #             # This is r', not r!!
        #             R_prime = np.sqrt(P_X_prime_prime**2 + P_Y_prime_prime**2)
                    
        #             # Initial guess for small distortion
        #             R_N = R_prime
        #             if self.verbose:
        #                 print('Iterating now!')
        #             max_it = 20
        #             for i in np.arange(0, max_it) :
        #                 if False: # One parameter radial
        #                     R_Nplus1 = R_prime / (1 + dist_coeffs[0]*R_N**2)
        #                 else:
        #                     R_Nplus1 = R_prime / (1 + dist_coeffs[0]*R_N**2 + dist_coeffs[1]*R_N**4 + dist_coeffs[2]*R_N**6)

        #                 diff = np.sum(np.abs(R_Nplus1-R_N))
                        
        #                 R_N = R_Nplus1
        #                 if self.verbose:
        #                     print(f'The difference after N iterations is {diff}')
        #                 pass

        #             R = R_N
        #             gamma = 1 + dist_coeffs[0]*R**2

        #             P_C_prime = np.ones_like(P_C_prime_prime)
        #             P_C_prime[0, :] = P_X_prime_prime/gamma
        #             P_C_prime[1, :] = P_Y_prime_prime/gamma

        #             raise Exception('I have moved this to the distortion module.')
        #             return P_C_prime

        #         else:
        #             raise Exception
        #             P_C_prime = P_C
        #             P_X_prime = P_C_prime[0, :]
        #             P_Y_prime = P_C_prime[1, :]

        #             # R = np.sqrt(P_X_prime**2 + P_Y_prime**2)

        #             # if False: # One parameter radial
        #             #     gamma = 1 + dist_coeffs[0]*R**2
        #             # else: # 3 Parameter radial
        #             #     gamma = 1 + dist_coeffs[0]*R**2 + dist_coeffs[1]*R**4 + dist_coeffs[2]*R**6

        #             # P_C_prime_prime = np.ones_like(P_C_prime)

        #             # P_C_prime_prime[0, :] = P_X_prime*gamma
        #             # P_C_prime_prime[1, :] = P_Y_prime*gamma
                    
        #             # raise Exception('I have moved this to the distortion module.')

        #             print('Marker')
        #             print(min(P_X_prime), max(P_X_prime))
        #             print(min(P_Y_prime), max(P_Y_prime))
        #             P_X_prime_prime, P_Y_prime_prime = distortion.distort_radial(P_X_prime, P_Y_prime, dist_coeffs, self.K)

        #             P_C_prime_prime = np.ones_like(P_C_prime)
        #             P_C_prime_prime[0, :] = P_X_prime_prime
        #             P_C_prime_prime[1, :] = P_Y_prime_prime

        #             print(P_C_prime_prime.dtype)

        #             return P_C_prime_prime
                

        if type(P_u) in [int, float, list]: # Scalar
            pass
        
        elif len(P_u.shape) > 2:
            raise(Exception('More than 2D arrays of points are not supported'))
        
        elif len(P_u.shape) == 2: # 2D array

            if False:
                print("2D mode")

            P_u_ = P_u.ravel()
            P_v_ = P_v.ravel()

            if type(target_z) == type(P_u):
                # print("TYPE MATCH")
                if np.all(target_z.shape == P_u.shape):
                    target_z = target_z.ravel()

            # mesh = self(P_u_, P_v_, target_z, reverse=reverse)
            mesh = self(P_u_, P_v_, target_z, reverse=reverse)
            # print(mesh)
            # print(mesh.shape)
            meshx = mesh[0, :].reshape(P_u.shape)
            meshy = mesh[1, :].reshape(P_u.shape)
            meshz = mesh[2, :].reshape(P_u.shape)

            P_ENU = np.hstack([meshx, meshy, meshz])

            # return P_ENU
            return meshx, meshy, meshz # Return like this for 2D mode
        

        P_u, P_v   = np.array(P_u), np.array(P_v)

        if not reverse: 
            # For forwards mode the distortion should be straight away on these pixel coords
            # What we actually require though is undistortion... I'm pretty sure
            niter = 4 # Speed mode 1! 
            P_u, P_v = distortion.undistort_radial(P_u, P_v, self.dist_coeffs, self.K, niter=niter)

        P_z        = np.ones_like(P_u)                  # Normalised z
        
        P_xyz = np.vstack([P_u, P_v, P_z])
        z_ENU = target_z                                # Height of the object(s) in ENU coords

        ########################################################################################
        ##### This is the reverse optoin, doesn't need to be here, will find a new home. #######
        ########################################################################################
        if reverse:
            # R_C_to_Ref   = self.R_C_to_Ref
            # R_C_to_NED   = self.R_Ref_to_NED@self.R_C_to_Ref
            R_C_to_ENU   = self.R_NED_to_ENU@self.R_Ref_to_NED@self.R_C_to_Ref

            # R_NED_to_ENU = self.R_NED_to_ENU
            # R_Ref_to_ENU = self.R_NED_to_ENU@self.R_Ref_to_NED 

            T_NED_to_ENU =  self.Ref_UTM_xyz
            T_Ref_to_ENU =  T_NED_to_ENU + self.R_NED_to_ENU@self.T_Ref_to_NED 
            T_C_to_ENU   =  T_Ref_to_ENU + self.R_NED_to_ENU@self.R_Ref_to_NED@self.T_C_to_Ref

            if True:
                target = P_xyz                # We're reversing, so our Pixel Positions are actually target positions.  
                target[2, :] = target_z       # Get rid of the normalised z, we have a real target here. 

                R_ENU_to_C = np.linalg.inv(R_C_to_ENU)       # Invert the rotation martrix
                P_C =  R_ENU_to_C @ (target - T_C_to_ENU)    # Translate, then rotate
                
                if False:
                    # This is old code and gives the right answer but less formally correct (also has no distortion)
                    P_i =  self.K @ P_C 
                    P_i /= P_i[2]
                else:
                    P_C_prime_prime = P_C / P_C[2]
                    
                    if False:
                        # P_C_prime = distort(P_C_prime_prime, self.dist_coeffs, reverse=True)
                        raise Exception('This is the wrong place to run the distortion.')
                    else:
                        P_C_prime = P_C_prime_prime
                    
                    P_i =  self.K @ P_C_prime 

            P_u, P_v, P_z = P_i
            P_u, P_v = distortion.distort_radial(P_u, P_v, self.dist_coeffs, self.K)
            P_i = np.array([P_u, P_v, P_z])

            return P_i
            
        else:
            ###########
            P_i = P_xyz     # Pixel coordinates

            R_C_to_Ref   = self.R_C_to_Ref
            R_C_to_NED   = self.R_Ref_to_NED@self.R_C_to_Ref
            R_C_to_ENU   = self.R_NED_to_ENU@self.R_Ref_to_NED@self.R_C_to_Ref

            R_NED_to_ENU = self.R_NED_to_ENU
            R_Ref_to_ENU = self.R_NED_to_ENU@self.R_Ref_to_NED 

            T_NED_to_ENU =  self.Ref_UTM_xyz
            T_Ref_to_ENU =  T_NED_to_ENU + self.R_NED_to_ENU@self.T_Ref_to_NED 
            T_C_to_ENU   =  T_Ref_to_ENU + self.R_NED_to_ENU@self.R_Ref_to_NED@self.T_C_to_Ref

            # Map from the image frame (pixels) to camera frame (distance)
                #    Calculate Camera frame vector prime. 
                #    The prime here indicates that the target distance (z_c) is unknown, and so too then are x_c and y_c.
            P_C_prime = np.linalg.inv(self.K) @ P_i

            if False:
                P_C_prime_prime = distort(P_C_prime, self.dist_coeffs)
                raise Exception('This is the wrong place to run the distortion.')
            else:
                P_C_prime_prime = P_C_prime
            
            if fulloutput:
                print("\n P_C_prime_prime:")
                print(P_C_prime_prime)

            if fulloutput:
                print("\n P_C_prime:")
                print(P_C_prime)

            # Map from the camera frame (distance) to the reference frame (distance)
                #    This is solely about camera mounting, and not anything about gimbal rotation
            # P_G_prime = self.R_C_to_G @ P_C_prime + self.T_C_to_G
            P_Ref_prime = self.R_C_to_Ref @ P_C_prime_prime + self.T_C_to_Ref

            if fulloutput:
                print("\n P_Ref_prime:")
                print(P_Ref_prime)

            # Map from the Reference frame (distance) to the North-East-Down frame (distance)
                # This can be done without translation, i.e. having the same origin

            P_NED_prime = self.R_Ref_to_NED @ P_Ref_prime + self.T_Ref_to_NED

            if fulloutput:
                print("\n P_NED_prime:")
                print(P_NED_prime)

            P_ENU_prime = self.R_NED_to_ENU @ P_NED_prime + T_NED_to_ENU

            if fulloutput:
                print("\n P_ENU_prime:")
                print(P_ENU_prime)

            ################################################################
            ### NOW WE NEED TO GO FROM THE 2D PRIME FRAME TO A FULL 3D FRAME
            ################################################################
            
            # T =  T_END_to_ENU 
            # T += self.R_END_to_ENU@self.T_UAS_to_END
            # T += self.R_END_to_ENU@self.R_UAS_to_END@self.T_G_to_UAS 
            # T += self.R_END_to_ENU@self.R_UAS_to_END@self.R_G_to_UAS@self.T_C_to_Gd
            T =  T_NED_to_ENU 
            T += self.R_NED_to_ENU@self.T_Ref_to_NED
            T += self.R_NED_to_ENU@self.R_Ref_to_NED@self.T_C_to_Ref
            
            if fulloutput:
                print("T = ", T)

            z_T = T[2]
            if fulloutput:
                print("z_T = ",z_T)

            z_ENU_prime = P_ENU_prime[2]
            if fulloutput  or halfoutput:
                print("z_ENU_prime = ",z_ENU_prime)

            #print("z_T = ",z_T)
            z_C = (z_ENU - z_T)/(z_ENU_prime - z_T)
            self.z_C = z_C
            if fulloutput or halfoutput:
                print("z_C = ",z_C)

            # Calculating P_ENU
            P_ENU = z_C*P_ENU_prime - z_C*T + T
        #     P_ENU = list(map(lambda P_ENU :str(P_ENU),P_ENU.round(4)))
            # P_ENU = np.array(list(map(lambda P_ENU : P_ENU, P_ENU.round(3))))

            if fulloutput or halfoutput:
                print("\n RESULT:")
                print("\n Input point:")
                print(P_i)
                print("\n Maps to:")
                print(P_ENU)

            return P_ENU

    def reverse(self, P_ENU):

        pass
    
    def get_component_positions(self):
        """
        Get the positions of the UAS, Gimbal and Camera
        """
        R_C_to_Ref   = self.R_C_to_Ref
        R_C_to_NED   = self.R_Ref_to_NED@self.R_C_to_Ref
        R_C_to_ENU   = self.R_NED_to_ENU@self.R_Ref_to_NED@self.R_C_to_Ref

        R_NED_to_ENU = self.R_NED_to_ENU
        R_Ref_to_ENU = self.R_NED_to_ENU@self.R_Ref_to_NED 

        T_NED_to_ENU =  self.Ref_UTM_xyz
        T_Ref_to_ENU =  T_NED_to_ENU + self.R_NED_to_ENU@self.T_Ref_to_NED 
        T_C_to_ENU   =  T_Ref_to_ENU + self.R_NED_to_ENU@self.R_Ref_to_NED@self.T_C_to_Ref

        T_C_to_ENU

        OENU = np.array([0., 0., 0.])[:, None]
        ##########
        ## NED NOW
        ##########
        ONED = T_NED_to_ENU

        #############
        ## Ref NOW
        #############
        ORef   = T_Ref_to_ENU

        #############
        ## CAMERA NOW
        #############
        OC   = T_C_to_ENU

        print(f'Camera position is {OC.T}')
        print(f'Ref position is {ORef.T}')
        print(f'NED position is {ONED.T}')

        return OC, ORef, ONED

    def plot_scene(self, bbox_alt=0, targets=[], 
               ax=None,
               al=15,
               gridcol='b',
               plot_corners=True,
               plot_ground=False):
    
        OC, ORef, ONED = self.get_component_positions()
        
        if ax is None:
            ax = plt.figure(figsize=(10, 10)).add_subplot(projection='3d')
        
        x, y, z = self.Ref_UTM_xyz
        xco, yco, zco = OC

        ax.scatter(xco, yco, zco, zdir='z', label=self.name, color=gridcol)

        if plot_ground:
            ax.scatter(xco, yco, bbox_alt, zdir='z', label=self.name + ' "X,Y"', color=gridcol, alpha=0.5)
    
        meshx, meshy, meshz = self.make_georef_grid(grid_n=11, alt=bbox_alt)

        ul = np.array([meshx[0, 0], meshy[0, 0], meshz[0, 0]])[:, None]
        ur = np.array([meshx[0, -1], meshy[0, -1], meshz[0, -1]])[:, None]
        lr = np.array([meshx[-1, -1], meshy[-1, -1], meshz[-1, -1]])[:, None]
        ll = np.array([meshx[-1, 0], meshy[-1, 0], meshz[-1, 0]])[:, None]
        # ul = self(0, 0, bbox_alt)
        # ur = self(self._npix_x, 0, bbox_alt)
        # lr = self(self._npix_x, self._npix_y, bbox_alt)
        # ll = self(0, self._npix_y, bbox_alt)    
        
        ####### THIS SHOULD PLOT FROM CAMERA POV, NOT UAS
        for c in (ul, ur, lr, ll):
            xc, yc, zc = c
            ax.plot([xco, xc], [yco, yc], [zco, zc], color=gridcol, ls=':', lw=1, alpha=1)

        if plot_corners:

            ax.plot(ul[0], ul[1], ul[2], 'ro', zdir='z', label='Image U.L.')
            ax.text(float(ul[0]), float(ul[1]), float(ul[2]), '[{},{}]'.format(ul[0], ul[1]), 
                    fontsize='x-small',
                    ha='right')
            
            # ax.plot(ur[0], ur[1], ur[2], 'r+', zdir='z')
            ax.text(float(ur[0]), float(ur[1]), float(ur[2]), '[{},{}]'.format(ur[0], ur[1]), 
                    fontsize='x-small',
                    ha='left')
            
            # ax.plot(lr[0], lr[1], lr[2], 'ko', zdir='z', label='Image L.R.')
            ax.text(float(lr[0]), float(lr[1]), float(lr[2]), '[{},{}]'.format(lr[0], lr[1]), 
                    fontsize='x-small',
                    ha='left')
            
            # ax.plot(ll[0], ll[1], ll[2], 'r+', zdir='z')
            ax.text(float(ll[0]), float(ll[1]), float(ll[2]), '[{},{}]'.format(ll[0], ll[1]), 
                    fontsize='x-small',
                    ha='right')
        
        bx = [ll[0], lr[0], ur[0], ul[0], ll[0]]
        by = [ll[1], lr[1], ur[1], ul[1], ll[1]]
        bz = [ll[2], lr[2], ur[2], ul[2], ll[2]]

        # plt.plot(bx, by, bz, 'r')
        
        l = self(np.linspace(0, 0), np.linspace(0, self._npix_y), bbox_alt)
        ax.plot(l[0], l[1], l[2], gridcol, zdir='z')
        
        r = self(np.linspace(self._npix_x, self._npix_x), np.linspace(0, self._npix_y), bbox_alt)
        ax.plot(r[0], r[1], r[2], gridcol, zdir='z')
        
        u = self(np.linspace(0, self._npix_x), np.linspace(self._npix_y, self._npix_y), bbox_alt)
        ax.plot(u[0], u[1], u[2], gridcol, zdir='z')
        
        b = self(np.linspace(0, self._npix_x), np.linspace(0, 0), bbox_alt)
        ax.plot(b[0], b[1], b[2], gridcol, zdir='z')
        
        c = self(self._c_x, self._c_y, bbox_alt)
        if plot_ground:
            ax.plot(c[0], c[1], c[2], 'k+', zdir='z', label='P.P.')

        
        if True: # Plot mesh
            
            # xpixg, ypixg = self.make_grid()

            # plt.plot(mesh[0, :], mesh[1, :], mesh[2, :], 'c.')
            for rx, ry, rz in zip(meshx, meshy, meshz):
                plt.plot(rx, ry, rz, gridcol, alpha=0.25)
            for rx, ry, rz in zip(meshx.T, meshy.T, meshz.T):
                plt.plot(rx, ry, rz, gridcol, alpha=0.25)
        
        
        for target in targets:
            targ = self(target[0], target[1], target[2])
            x = np.array(targ[0])
            y = np.array(targ[1])
            z = np.array(targ[2])
            if len(x)==1:
                ax.plot(x, y, z, 'k.', zdir='z')
            else:
                ax.plot(x, y, z, 'k', zdir='z')
            
            ax.text(x[0], y[0], z[0], target[3], fontsize='small', **target[4])
            
        ax.legend()
        
        if not al is None:
            ax.set_xlabel('x')
            ax.set_ylabel('y')

            zm = 10
            
            ax.set_xlim(-al, al)
            ax.set_ylim(-al, al)
            
            ax.set_xlim(c[0]-al, c[0]+al)
            ax.set_ylim(c[1]-al, c[1]+al)
            
            ax.set_zlim(0, zm)
            ax.set_aspect('equal')
        
        return ll
    
    def make_grid(self, grid_n=10):
        """
        Make a uniform (n+2)x(n+2) grid in the FOV 
        i.e. n is the number of internal points.  

        Parameters
        ----------
        grid_n: int
            Number of points in the grid to be returned. 
            If None, return full camera resolution. 

        Returns
        -------
        xpixg: np.array of ints
            The col indices of the return grid
        ypixg: np.array of ints
            The row indices of the return grid
        """
        
        if grid_n is None: # Return full camera res
            xpix = np.arange(0, self._npix_x)
            ypix = np.arange(0, self._npix_y)
        else:
            xpix = np.linspace(0, self._npix_x, grid_n)
            ypix = np.linspace(0, self._npix_y, grid_n)

        xpixg, ypixg = np.meshgrid(xpix, ypix)

        return xpixg, ypixg
    
    def make_georef_grid(self, grid_n=None, alt=0):
        """
        Make a uniform georeferenced (n+2)x(n+2) grid 
        in the FOV i.e. n is the number of internal points. 

        The grid is returned at ground level, i.e. z=0.

        Parameters
        ----------
        grid_n: int
            Number of points in the grid to be returned. 
            If None, return full camera resolution. 

        Returns
        -------
        xpixg: np.array of floats
            The x positions  of the return grid
        ypixg: np.array of floats
            The y positions  of the return grid
        zpixg: np.array of floats
            The z positions of the return grid
        """

        xpixg, ypixg = self.make_grid(grid_n=grid_n)
        meshx, meshy, meshz = self(xpixg, ypixg, alt)

        return meshx, meshy, meshz
    

    ##############################################
    ### BONUS CAMERA PROPERTIES ##################
    ##############################################
    @property
    def pixel_size_mm(self):
        """
        Return the pixel size in mm [x, y]
        """
        size = self._sensor_width_mm/self._npix_x, self._sensor_height_mm/self._npix_y
        return np.array(size)
    @property
    def principal_point_offset_pix(self):
        """
        Return the pixel coordinate of the principal point relative to the true CCD centre.
        """
        offset = self._c_x-self._npix_x/2, self._c_y-self._npix_y/2
        return np.array(offset)
    @property
    def principal_point_offset_mm(self):
        """
        Return the distance in mm between the principal pixel and the true CCD centre.
        """
        size = self.pixel_size_mm
        offset = self.principal_point_offset_pix

        return offset*size
    
    ##############################################
    ### SOLAR FUNCTIONS ##########################
    ##############################################
    def set_solar(self, solar_azim, solar_zenith):
        """
        Function to set the solar zenith and azimuth. 
        Definitions follow Rascle et al. (2017) GRL 
        paper. 

        Parameters
        ----------
        solar_zenith: floats
            The zenith angle of the sun relative to a 
            vertical line above the ground point. Zenith 
            is measured radians downward from vertical, 
            and defined over [0-pi/2). Assumed constant 
            for domain. 
        solar_azimuth: floats
            The azimuth angle of the sun relative to 
            the site. Azimuth is measured radians 
            clockwise from North. Assumed constant for 
            domain. 
            

        """

        self._solar_zenith = solar_zenith
        self._solar_azim   = solar_azim

    def get_specular_point(self):
        """
        From Rascle et al 2017 GRL

        Parameters
        ----------
        None

        Returns
        -------
        spx: float
            x location of the specular point
        spy: float
            y location of the specular point
        """

        solar_zenith = self._solar_zenith
        solar_azim   = self._solar_azim

        solar_dh = np.tan(solar_zenith)*self._UTM_z
        solar_dy = solar_dh*np.sin(np.pi/2-solar_azim)
        solar_dx = solar_dh*np.cos(np.pi/2-solar_azim)

        spx, spy = self._UTM_x+solar_dx, self._UTM_y+solar_dy

        return spx, spy

    def get_camera_angles(self, grid=None, grid_n=50):
        """
        From Rascle et al 2017 GRL

        Parameters
        ----------
        grid: list
            Length 3 list consisting of [meshx, meshy, meshz] 
            (see make_georef_grid). If None, the grid will be 
            calculated. 
        grid_n: int
            Used only if grid=None. 
            Number of points in the grid to be returned. 
            If None, return at full camera resolution.

        Returns
        -------
        meshx: np.array of floats
            The x positions of the retun grid
        meshy: np.array of floats
            The y positions of the retun grid
        meshz: np.array of floats
            The z positions of the retun grid
        camera_zenith: np.array of floats
            The zenith angle of the camera relative to a 
            vertical line above the grid point. Zenith 
            is measured radians downward from vertical, 
            and defined over [0-pi/2)
        camera_azimuth: np.array of floats
            The azimuth angle of the camera relative to 
            the grid point. Azimuth is measured radians 
            clockwise from North. 
                - For a point North of the camera, the 
                  camera is South, and the camera azimuth 
                  is thus pi radians (180 deg)
                - For a point East of the camera, the 
                  camera is West, and the camera azimuth 
                  is thus 3*pi/2 radians (270 deg)
        """
        if grid is None:
            meshx, meshy, meshz = self.make_georef_grid(grid_n=grid_n)
            grid = [meshx, meshy, meshz]
        meshx, meshy, meshz = grid
        
        # 1 - calculate offsets
        meshdx, meshdy, meshdz = meshx-self._UTM_x, meshy-self._UTM_y, meshz-self._UTM_z
        meshdh = np.abs(meshdx + 1.j*meshdy)

        # 2 - calculate angles
        camera_azim = np.arctan2(meshdy, meshdx) # Math
        camera_azim = np.pi/2-camera_azim        # Geo

        camera_zenith = np.arctan2(meshdh, self._UTM_z)

        if False:
            # camera_zenith = camera_zenith # Don't do this one, was just a fudge 
            pass
        else:
            # Reverse the azimuth perspective
            camera_azim = camera_azim + np.pi

        camera_azim = np.mod(camera_azim+2*np.pi, 2*np.pi)

        return meshx, meshy, meshz, camera_zenith, camera_azim

    def get_specular_facets(self, grid=None, grid_n=50):
        """
        Calculate the cartesian slopes (Z_xf and Z_yf) zenith angle (theta_f) 
        and azimuth angle (psi_f) of spectlar facets. Terminology and 
        conventions follow Rascle et al. (2017) GRL paper. 

        Parameters
        ----------
        grid: list
            Length 3 list consisting of [meshx, meshy, meshz] 
            (see make_georef_grid). If None, the grid will be 
            calculated. 
        grid_n: int
            Used only if grid=None. 
            Number of points in the grid to be returned. 
            If None, return at full camera resolution.

        Returns
        -------
        meshx: np.array of floats
            The x positions of the retun grid
        meshy: np.array of floats
            The y positions of the retun grid
        meshz: np.array of floats
            The z positions of the retun grid
        Z_xf: np.array of floats
            The eastward slope of facets satisfying 
            specular reflection. 
        Z_yf: np.array of floats
            The northward slope of facets satisfying 
            specular reflection. 
        theta_f: np.array of floats
            The zenith angle of the facets satisfying 
            specular reflection. Zenith is measured 
            radians downward from vertical, and defined 
            over [0-pi/2)
        psi_f: np.array of floats
            The azimuth angle of the facets satisfying  
            specular reflection. Azimuth is measured 
            radians clockwise from North. 
            
        """
        solar_zenith = self._solar_zenith
        solar_azim   = self._solar_azim

        if grid is None:
            meshx, meshy, meshz = self.make_georef_grid(grid_n=grid_n)
            grid = [meshx, meshy, meshz]

        meshx, meshy, meshz, camera_zenith, camera_azim = self.get_camera_angles(grid=grid)

        # meshx, meshy, meshz, camera_zenith, camera_azim = self.get_camera_angles(grid_n=grid_n)

        # 3 - calculate zenith and azimuth of secular facet 
        Z_xf = - (np.sin(solar_zenith)*np.sin(solar_azim) + np.sin(camera_zenith)*np.sin(camera_azim))/(np.cos(solar_zenith) + np.cos(camera_zenith))
        Z_yf = - (np.sin(solar_zenith)*np.cos(solar_azim) + np.sin(camera_zenith)*np.cos(camera_azim))/(np.cos(solar_zenith) + np.cos(camera_zenith))

        theta_f = np.arctan(np.sqrt(Z_xf**2+Z_yf**2))
        psi_f = np.arctan2(Z_yf, Z_xf)

        return meshx, meshy, meshz, Z_xf, Z_yf, theta_f, psi_f

    def get_fresnel(self, grid=None, grid_n=50):    
        """
        Get Fresnel reflection coefficient (\rho) for the specular 
        facet in every pixel, or for a regular grid inside the 
        footprint. 

        ISSUE: Papers aren't clear on whether this is the appropriate 
        way to calculate \rho, but it makes sense to me. 

        Parameters
        ----------
        grid: list
            Length 3 list consisting of [meshx, meshy, meshz] 
            (see make_georef_grid). If None, the grid will be 
            calculated. 
        grid_n: int
            Used only if grid=None. 
            Number of points in the grid to be returned. 
            If None, return at full camera resolution.

        Returns
        -------
        rho_fres: np.array of floats
            The Fresnel reflection coefficient for each grid point or pixel
        otherout:
            Dictionary containing a bunch of other interim calcs [for 
            debugging/education only]. These include:
                - theta_Fres:   Solar zenith relative to the facet
                                ssatisfying specular reflection
                - theta_Fres_x: theta_Fres component in y-z plane
                - theta_Fres_y: theta_Fres component in x-z plane
                - theta_c_y:    theta_c component in y-z plane
                - theta_c_y:    theta_c component in x-z plane
                - theta_f_x:    theta_f component in y-z plane
                - theta_f_y:    theta_f component in x-z plane
                - theta_f2:     reconstruction fo theta_f

        """

        solar_zenith = self._solar_zenith
        solar_azim   = self._solar_azim

        if grid is None:
            meshx, meshy, meshz = self.make_georef_grid(grid_n=grid_n)
            grid = [meshx, meshy, meshz]

        spx, spy = self.get_specular_point()
        meshx, meshy, meshz, camera_zenith, camera_azim = self.get_camera_angles(grid=grid)
        meshx, meshy, meshz, Z_xf, Z_yf, theta_f, psi_f = self.get_specular_facets(grid=grid)

        # camera_slope = np.tan(camera_zenith)
        # camera_slope_x = camera_slope*np.sin(camera_azim)
        # camera_slope_y = camera_slope*np.cos(camera_azim)

        # camera_azim = np.arctan2(meshdy, meshdx) # Math
        # camera_azim = np.pi/2-camera_azim        # Geo

        # AZ absolutely making this up
        theta_c_x = camera_zenith * np.sin(camera_azim)
        theta_c_y = camera_zenith * np.cos(camera_azim)

        # Azimuth relative to specular point
        spec_point_azim = np.arctan2(meshy-spy, meshx-spx) # Math
        spec_point_azim = np.pi/2-spec_point_azim          # Geo

        # theta_f_x = theta_f * np.sin(spec_point_azim)
        # theta_f_y = theta_f * np.cos(spec_point_azim)

        theta_f_x = np.arctan(np.tan(theta_f) * np.sin(spec_point_azim)) # Decomposition of theta_f - portion of theta_f in the z-y plane
        theta_f_y = np.arctan(np.tan(theta_f) * np.cos(spec_point_azim)) # Decomposition of theta_f - portion of theta_f in the z-x plane

        theta_f2 = np.arctan(np.sqrt( np.tan(theta_f_x)**2 + np.tan(theta_f_y)**2 )) # Reconstruction of theta_f, should match

        theta_Fres_x = theta_c_x + theta_f_x
        theta_Fres_y = theta_c_y + theta_f_y
        theta_Fres = np.arctan(np.sqrt( np.tan(theta_Fres_x)**2 + np.tan(theta_Fres_y)**2 ))

        rho_fres = utils.fresnel_rho(np.pi/2-theta_Fres)

        otherout = {}
        otherout['theta_Fres']   = theta_Fres
        otherout['theta_Fres_y'] = theta_Fres_y
        otherout['theta_Fres_x'] = theta_Fres_x
        otherout['theta_c_x']    = theta_c_x
        otherout['theta_c_y']    = theta_c_y
        otherout['theta_f_x']    = theta_f_x
        otherout['theta_f_y']    = theta_f_y
        otherout['theta_f2']     = theta_f2
        otherout['theta_Fres_x'] = theta_Fres_x
        otherout['theta_Fres_y'] = theta_Fres_y
        otherout['theta_Fres']   = theta_Fres

        return rho_fres, otherout

    def plot_specular(self):
        """
        From Rascle et al 2017 GRL
        """

        spx, spy = self.get_specular_point()
        
        # Solar position for the plot
        sx = self._UTM_x - (self._UTM_x - spx) *2 
        sy = self._UTM_y - (self._UTM_y - spy) *2 
        sz = self._UTM_z

        plt.plot(self._UTM_x, self._UTM_y, 'ko')

        plt.plot(spx, spy, 'rx', markerfacecolor=None, label='Specular sun spot')

        plt.plot([self._UTM_x, spx, sx], [self._UTM_y, spy, sy], [self._UTM_z, 0, sz], 'r--')
        plt.gca().text(sx, sy, sz, 'Sun', color='r')

        meshx, meshy, meshz, Z_xf, Z_yf, theta_f, psi_f   =  self.get_specular_facets(grid_n=50)

        theta_f = np.arctan(np.sqrt(Z_xf**2+Z_yf**2))

        scale_down = 10000
        cz = meshz+(theta_f*180/np.pi)/scale_down
        levels = np.array([0, 10, 20, 30, 40])/scale_down
        
        mb = plt.gca().contour(meshx, meshy, cz, zdir='z', colors='m', levels=levels)

        plt.legend()




def dgr_from_opencv2(camera_matrix, dist_coeffs, image_size, rvec, tvec, objpoints=None, imgpoints=None, verbose=False):
    """
    This is a function to spin out a DGR object from standard OpenCV calibration data.
    """

    k1, k2, p1, p2, k3 = dist_coeffs[0]
    assert np.isclose(p1, 0) , 'This function does not support tangential distortion'
    assert np.isclose(p2, 0) , 'This function does not support tangential distortion'

    radial_dcs = [k1, k2, k3]

    offsets = {} # We currently haven't tested this for any offsets
    kappa_rotation=0 # We currently haven't tested this for any kappa rotation

    dgr = DGR(camera="custom", name='From OpenCV', kappa_rotation=kappa_rotation,  verbose=False, 
                    offsets=offsets, camera_options={'K': camera_matrix, 'image_sive_cv': image_size})

    # Standard approach would be to get a rotation matrix and translation vector
    R_ENU_to_C, _ = cv.Rodrigues(rvec)
    R_C_to_ENU    = R_ENU_to_C.T
    T_ENU_to_C    = tvec
    RT_ENU_to_C = np.eye((4))
    RT_ENU_to_C[0:3, 0:3] = R_ENU_to_C
    RT_ENU_to_C[0:3, 3]   = T_ENU_to_C[:, 0]

    if False:
        # THis is the no Kappa, no offset version. Shouldn't need to make this assumption. 
        R_C_to_Ref = R_C0_to_Ref = np.array([[0, -1, 0],[1, 0, 0],[0, 0, 1]])
    else:
        # Why not get it straight from the object?
        R_C_to_Ref = dgr.R_C_to_Ref

    R_C_to_NED = R_NED_to_ENU.T @ R_C_to_ENU
    R_Ref_to_NED = R_NED_to_ENU.T @ R_C_to_ENU @ R_C_to_Ref.T

    h, p, r = yaw_pitch_roll_from_R(R_Ref_to_NED)

    # This is where we reverse the order of rotation and translation
    RT_C_to_ENU = np.linalg.inv(RT_ENU_to_C)
    T_C_to_ENU = RT_C_to_ENU[0:3, 3]
    x, y, z = T_C_to_ENU

    dgr.dist_coeffs = radial_dcs
    dgr.update_POS_Ref(x, y, z)
    dgr.update_IMU_Ref(h, p, r, frame='NED')


    if objpoints is not None:
        if imgpoints is not None:
            print('Image and object points have been specified, can do verification')
            imgpoints2cv, _ = cv.projectPoints(objpoints, rvec, tvec, camera_matrix, dist_coeffs)
            error = cv.norm(imgpoints, imgpoints2cv, cv.NORM_L2)#/len(imgpoints2)
            print(f'     OpenCV reprojection error: {error} pixels')

            error = reproj_cv(dgr, objpoints, imgpoints)
            print(f'        DGR reprojection error: {error} pixels')


    return dgr

def reproj_cv(dgr, objpoints, imgpoints):
    """
    Estimate reprojection error using OpenCV functions
    """

    obs = objpoints.shape
    if len(obs) == 3:
        objpoints = objpoints[:, 0, :]
    obs = objpoints.shape
    obj_x, ob_y = objpoints[:,0], objpoints[:,1]
    if obs[1] == 2:
        obj_z = np.zeros_like(obj_x)
    elif obs[1] == 3:
        obj_z = objpoints[:,2]

    # Probably should do the same with impoints

    out = dgr(obj_x, ob_y, obj_z, reverse=True)
    imgpoints2dgr = out.T[:, None, :][:, :, :-1].astype(np.float32)
    
    imgpoints2dgr = imgpoints2dgr.astype(imgpoints.dtype)

    error = cv.norm(imgpoints, imgpoints2dgr, cv.NORM_L2)#/len(imgpoints2)

    return error     
    
