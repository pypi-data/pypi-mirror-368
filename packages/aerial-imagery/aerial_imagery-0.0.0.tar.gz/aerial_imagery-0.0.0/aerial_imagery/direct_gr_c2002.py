import navpy, numpy as np
import math
import matplotlib.pyplot as plt

import aerial_imagery.utils as utils
from aerial_imagery.cameras import set_camera

# Module for direct georeferencing alla Correia et al. 2002

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
    # Gimbal frame to UAS - IMU - frame
    _yaw_G   = np.nan #rad
    _pitch_G = np.nan #rad
    _roll_G  = np.nan #rad

    # UAS frame - IMU - to NED frame. from imu/data then rotated to NED
    _yaw_UAS   = np.nan #rad
    _pitch_UAS = np.nan #rad
    _roll_UAS  = np.nan #rad

    _solar_azim = np.nan #rad
    _solar_zenith  = np.nan #rad

    def __init__(self, camera='ZED2_C2022', camera_options={}, **kwargs):
        
        self.name = kwargs.pop('name', 'Unnamed UAS')
        offsets = kwargs.pop('offsets', {},)

        set_camera(self, camera, camera_options)
        self.update_translations(offsets)

        # Camera frame to Gimbal frame
        self.R_C_to_G = np.array([[0, 0, 1],[1, 0, 0],[0, 1, 0]])
        self.T_C_to_G = np.array([[0],[0],[0]])

        # UAS frame to NED frame
        ## Need the translation only, rotation set by UAS IMU
        self.T_UAS_to_NED = np.array([[0],[0],[0]]) # Define NED origin - default to same as the UAS

        # NED frame to ENU frame
        ## Need the rotation only, translation set by UAS XYZ position
        self.R_NED_to_ENU = np.array([[0, 1, 0],[1, 0, 0],[0, 0, -1]])

    def update_translations(self, offsets):

        # offsets = self.offsets

        # Offsets - camera gimbal
        CGx = offsets.pop('CGx', 0)
        CGy = offsets.pop('CGy', 0)
        CGz = offsets.pop('CGz', 0)

        # Offsets - gimbal to UAS
        GUx = offsets.pop('GUx', -0.002)
        GUy = offsets.pop('GUy', 0.023)
        GUz = offsets.pop('GUz', 0.002)

        # Camera frame to Gimbal frame
        self.T_C_to_G = np.array([[CGx],[CGy],[CGz]])
 
        # Gimbal frame to UAS frame
        ## Need the translation only, rotation set by gimbal IMU
        # self.T_G_to_UAS = np.array([[-0.002],[0.023],[0.002]])
        self.T_G_to_UAS = np.array([[GUx],[GUy],[GUz]])

    def build_K(self):
        
        self.K = np.array([[self._fx_pix, 0,            self._c_x],
                           [0,            self._fy_pix, self._c_y],
                           [0,            0,            1]])
    
    def update_IMU_UAS(self, yaw, pitch, roll):
        
        self._yaw_UAS   = yaw
        self._pitch_UAS = pitch
        self._roll_UAS  = roll

        self.R_UAS_to_NED = R_yaw_pitch_roll(self._yaw_UAS, self._pitch_UAS, self._roll_UAS)
        
    def update_IMU_G(self, yaw, pitch, roll, frame='UAS'):
        """
        Experimenting with 2 ways to specify, the first more an gimbal encoder approach, the second
        more a 2 IMU. The second one is not yet working.  
        """

        if frame.upper() == 'UAS':
            """
            This is the way coded in corriea et al. it's also how encoders would work
            """
            self._yaw_G   = yaw
            self._pitch_G = pitch
            self._roll_G  = roll
            
            self.R_G_to_UAS   = R_yaw_pitch_roll(self._yaw_G, self._pitch_G, self._roll_G)
        
        elif frame.upper() == 'NED':
            """
            This gives you your frame straight into NED as we believe the P4RTK does. 
            """
            self._yaw_G   = np.nan
            self._pitch_G = np.nan
            self._roll_G  = np.nan

            # Need to find R_G_to_UAS
            # R_C_to_NED = R_C_to_G @ R_G_to_UAS @ R_UAS_to_NED   
            #   above        known     unknown       known
            # R_G_to_UAS = inv(R_C_to_G) @ R_C_to_NED @ inv(R_UAS_to_NED) 
            #  unknown       known           above          known
            #
            inv = np.linalg.inv

            R_C_to_NED = R_yaw_pitch_roll(yaw, pitch, roll)
            self.R_G_to_UAS = inv(self.R_C_to_G) @ R_C_to_NED @ inv(self.R_UAS_to_NED)

            R_G_to_NED = R_yaw_pitch_roll(yaw, pitch, roll)
            self.R_G_to_UAS = R_G_to_NED @ inv(self.R_UAS_to_NED)

        else:
            raise(Exception)

        
    def update_POS_UAS(self, x, y, z):
        
        self._UTM_x = x
        self._UTM_y = y
        self._UTM_z = z
    
    @property
    def UAS_UTM_xyz(self):
    
        return np.array([[self._UTM_x], [self._UTM_y], [self._UTM_z]])
    
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

    def __call__(self, P_ui, P_vi, target_z = 0, fulloutput=False, halfoutput=False,
                 reverse=False):
        """
        Note this assumes a rectified image

        Inputs 
        ------
            P_ui, P_vi = X and Y pixel of the target
            UAS_UTM_xyz - Position of the UAS in metres [same as T_NED_to_ENU]
            target_uv_pix - X and Y pixels of the target in the rectified image 
            target_z - Height of the object in metres 
        """

        if type(P_ui) in [int, float, list]: # Scalar
            pass
        elif len(P_ui.shape) > 2:
            raise(Exception('More than 2D arrays off points are not supported'))
        elif len(P_ui.shape) == 2: # 2D array
            print("2D mode")
            P_ui_ = P_ui.ravel()
            P_vi_ = P_vi.ravel()

            mesh = self(P_ui_, P_vi_, target_z, reverse=reverse)
            # print(mesh)
            # print(mesh.shape)
            meshx = mesh[0, :].reshape(P_ui.shape)
            meshy = mesh[1, :].reshape(P_ui.shape)
            meshz = mesh[2, :].reshape(P_ui.shape)

            P_ENU = np.hstack([meshx, meshy, meshz])

            # return P_ENU
            return meshx, meshy, meshz # Return like this for 2D mode
        

        P_ui, P_vi = np.array(P_ui), np.array(P_vi)
        P_zi = np.ones_like(P_ui)
        
#         P_i = np.array([[P_ui], [P_vi], [1]])
        P_i = np.vstack([P_ui, P_vi, P_zi])
        z_ENU = target_z # Height of the object

        ########################################################################################
        ##### This is the reverse optoin, doesn't need to be here, will find a new home. #######
        ########################################################################################
        if reverse:
            
            R_C_to_ENU   = self.R_NED_to_ENU@self.R_UAS_to_NED@self.R_G_to_UAS@self.R_C_to_G

            T_NED_to_ENU = self.UAS_UTM_xyz
            T =  T_NED_to_ENU 
            T += self.R_NED_to_ENU@self.T_UAS_to_NED 
            T += self.R_NED_to_ENU@self.R_UAS_to_NED@self.T_G_to_UAS 
            T += self.R_NED_to_ENU@self.R_UAS_to_NED@self.R_G_to_UAS@self.T_C_to_G

            if True:
                target = P_i
                target[2, :] = target_z

                R_ENU_to_C = np.linalg.inv(R_C_to_ENU)
                P_C =  R_ENU_to_C @ (target - T)
                P_i =  self.K @ P_C 
                P_i /= P_i[2]
            
            # K2 = np.hstack([self.K, np.zeros((3, 1))])
            # E = np.hstack([R, T])
            # E = np.vstack([E, np.array([0 , 0, 0, 1])])
            # M = K2@E
            
            # return M
            return P_i, self.K, R_C_to_ENU, T
        
        ###########
        

        T_NED_to_ENU = self.UAS_UTM_xyz

        # Map from the image frame (pixels) to camera frame (distance)
            #    Calculate Camera frame vector prime. 
            #    The prime here indicates that the target distance (z_c) is unknown, and so too then are x_c and y_c.
        P_C_prime = np.linalg.inv(self.K) @ P_i

        if fulloutput:
            print("\n P_C_prime:")
            print(P_C_prime)

        # Map from the camera frame (distance) to the gimbal frame (distance)
            #    This is solely about camera mounting, and not anything about gimbal rotation
        P_G_prime = self.R_C_to_G @ P_C_prime + self.T_C_to_G

        if fulloutput:
            print("\n P_G_prime:")
            print(P_G_prime)

        # Map from the gimbal frame (distance) to the UAS frame (distance)
            # This is about the relative angles of gimbal and UAS, as well as the offset of the IMUs (or other angle measurement technique)
        # R_G_to_UAS = R_yaw_pitch_roll(self._yaw_G, self._pitch_G, self._roll_G)

        P_UAS_prime = self.R_G_to_UAS @ P_G_prime + self.T_G_to_UAS

        # Map from the UAS frame (distance) to the North-East-Down frame (distance)
            # This can be done without translation, i.e. having the same origin
        # R_UAS_to_NED = R_yaw_pitch_roll(self._yaw_UAS, self._pitch_UAS, self._roll_UAS)

        P_NED_prime = self.R_UAS_to_NED @ P_UAS_prime + self.T_UAS_to_NED

        if fulloutput:
            print("\n P_NED_prime:")
            print(P_NED_prime)

        P_ENU_prime = self.R_NED_to_ENU @ P_NED_prime + T_NED_to_ENU

        if fulloutput:
            print("\n P_ENU_prime:")
            print(P_ENU_prime)

        # print(3*(R_NED_to_ENU @ P_NED_prime) + T_NED_to_ENU)

        ################################################################
        ### NOW WE NEED TO GO FROM THE 2D PRIME FRAME TO A FULL 3D FRAME
        ################################################################
        
        T =  T_NED_to_ENU 
        T += self.R_NED_to_ENU@self.T_UAS_to_NED 
        T += self.R_NED_to_ENU@self.R_UAS_to_NED@self.T_G_to_UAS 
        T += self.R_NED_to_ENU@self.R_UAS_to_NED@self.R_G_to_UAS@self.T_C_to_G
        
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
    
    def plot_scene(self, bbox_alt=0, targets=[], uas_view=False, 
               ax=None,
               al=15,
               gridcol='b',
               alpha=1,
               plot_corners=True,
               plot_img_axis=True,):
    
        FOV = self.FOV
        FOV = self.print_FOV_metres(self._UTM_z)
        
        if ax is None:
            ax = plt.figure(figsize=(10, 10)).add_subplot(projection='3d')
        
        x, y, z = self.UAS_UTM_xyz
        ax.scatter(x, y, z, zdir='z', label=self.name, color=gridcol)
    
        ul = self(0, 0, bbox_alt)
        ur = self(self._npix_x, 0, bbox_alt)
        lr = self(self._npix_x, self._npix_y, bbox_alt)
        ll = self(0, self._npix_y, bbox_alt)    

        for c in (ul, ur, lr, ll):
            xc, yc, zc = c
            ax.plot([x, xc], [y, yc], [z, zc], color=gridcol, ls=':', lw=1, alpha=1)


        
        if plot_corners:

            ax.plot(ul[0], ul[1], ul[2], 'ro', zdir='z', label='Image U.L.')
            ax.text(float(ul[0]), float(ul[1]), float(ul[2]), '[{},{}]'.format(ul[0], ul[1]), 
                    fontsize='x-small',
                    ha='right')
            
            ax.plot(ur[0], ur[1], ur[2], 'r+', zdir='z')
            ax.text(float(ur[0]), float(ur[1]), float(ur[2]), '[{},{}]'.format(ur[0], ur[1]), 
                    fontsize='x-small',
                    ha='left')
            
            ax.plot(lr[0], lr[1], lr[2], 'ko', zdir='z', label='Image L.R.')
            ax.text(float(lr[0]), float(lr[1]), float(lr[2]), '[{},{}]'.format(lr[0], lr[1]), 
                    fontsize='x-small',
                    ha='left')
            
            ax.plot(ll[0], ll[1], ll[2], 'r+', zdir='z')
            ax.text(float(ll[0]), float(ll[1]), float(ll[2]), '[{},{}]'.format(ll[0], ll[1]), 
                    fontsize='x-small',
                    ha='right')
        
        bx = [ll[0], lr[0], ur[0], ul[0], ll[0]]
        by = [ll[1], lr[1], ur[1], ul[1], ll[1]]
        bz = [ll[2], lr[2], ur[2], ul[2], ll[2]]

        if False:
            plt.plot(bx, by, bz, 'r')
        
        l = self(np.linspace(0, 0), np.linspace(0, self._npix_y), bbox_alt)
        ax.plot(l[0], l[1], l[2], gridcol, zdir='z', alpha=alpha)
        
        r = self(np.linspace(self._npix_x, self._npix_x), np.linspace(0, self._npix_y), bbox_alt)
        ax.plot(r[0], r[1], r[2], gridcol, zdir='z', alpha=alpha)
        
        u = self(np.linspace(0, self._npix_x), np.linspace(self._npix_y, self._npix_y), bbox_alt)
        ax.plot(u[0], u[1], u[2], gridcol, zdir='z', alpha=alpha)
        
        b = self(np.linspace(0, self._npix_x), np.linspace(0, 0), bbox_alt)
        ax.plot(b[0], b[1], b[2], gridcol, zdir='z', alpha=alpha)
        
        c = self(self._c_x, self._c_y, bbox_alt)
        ax.plot(c[0], c[1], c[2], 'k+', zdir='z', label='P.P.')

        if plot_img_axis:
            sz = np.min([self._npix_y, self._npix_x])
            img_x = self(sz/2, bbox_alt)
            img_y = self(0, sz/2, bbox_alt)
            print(ul[0])
            print(img_y[0])
            [ul[2]]*2
            [ul[0], img_y[0]], [ul[1], img_y[1]]

            ax.quiver(ul[0], ul[1], ul[2], img_y[0]-ul[0], img_y[1]-ul[1], 0, color='k', alpha=alpha)
            ax.quiver(ul[0], ul[1], ul[2], img_x[0]-ul[0], img_x[1]-ul[1], 0, color='k', alpha=alpha)
            
            ax.text(float(img_x[0]), float(img_x[1]), float(0), '$IMG_X$'.format(ll[0], ll[1]), 
                    ha='left')
        
            ax.text(float(img_y[0]), float(img_y[1]), float(0), '$IMG_Y$'.format(ll[0], ll[1]), 
                    ha='left')
            
        if True: # Plot mesh
            
            # xpixg, ypixg = self.make_grid()
            meshx, meshy, meshz = self.make_georef_grid(grid_n=10, alt=bbox_alt)

            # plt.plot(mesh[0, :], mesh[1, :], mesh[2, :], 'c.')
            for rx, ry, rz in zip(meshx, meshy, meshz):
                plt.plot(rx, ry, rz, gridcol, alpha=0.25*alpha)
            for rx, ry, rz in zip(meshx.T, meshy.T, meshz.T):
                plt.plot(rx, ry, rz, gridcol, alpha=0.25*alpha)
        
        
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
        ax.set_xlabel('x')
        ax.set_ylabel('y')

        zm = 10
        
        ax.set_xlim(-al, al)
        ax.set_ylim(-al, al)
        
        ax.set_xlim(c[0]-al, c[0]+al)
        ax.set_ylim(c[1]-al, c[1]+al)
        
        ax.set_zlim(0, zm)
        ax.set_aspect('equal')
        
        if uas_view:
            elev = (self._pitch_UAS - self._pitch_G)*180/np.pi 
            
            inexplicable_and_not_quite_right_offset = -90
            inexplicable_and_not_quite_right_offset = +123
            azim = (self._yaw_G + self._yaw_UAS)*180/np.pi + inexplicable_and_not_quite_right_offset
            
            ax.view_init(azim=azim, elev=elev)
            ax.dist = z[0]-zm/2
        
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

        # AZ absolutely making this up
        theta_c_x = camera_zenith * np.sin(camera_azim)
        theta_c_y = camera_zenith * np.cos(camera_azim)

        theta_f_x = np.arctan(Z_xf)
        theta_f_y = np.arctan(Z_yf)

        theta_f2 = np.arctan(np.sqrt( np.tan(theta_f_x)**2 + np.tan(theta_f_y)**2 )) # Reconstruction of theta_f, should match

        theta_Fres_AZ_x = theta_c_x + theta_f_x
        theta_Fres_AZ_y = theta_c_y + theta_f_y

        theta_Fres_AZ = np.arctan(np.sqrt( np.tan(theta_Fres_AZ_x)**2 + np.tan(theta_Fres_AZ_y)**2 ))


        print('Should compare to Jackson and Alpers equation 10 which uses the spherical law of cosines. Not equal for some reason, so use Jackson and Alpers. ')
        phi_rel = solar_azim - camera_azim
        cos_2omega = np.cos(camera_zenith)*np.cos(solar_zenith) + np.sin(camera_zenith)*np.sin(solar_zenith)*np.cos(phi_rel)
        theta_Fres_JA10 = np.arccos(cos_2omega)/2

        rho_fres = utils.fresnel_rho(np.pi/2-theta_Fres_JA10)

        otherout = {}
        otherout['theta_Fres_AZ_y'] = theta_Fres_AZ_y
        otherout['theta_Fres_AZ_x'] = theta_Fres_AZ_x
        otherout['theta_c_x']    = theta_c_x
        otherout['theta_c_y']    = theta_c_y
        otherout['theta_f_x']    = theta_f_x
        otherout['theta_f_y']    = theta_f_y
        otherout['theta_f2']     = theta_f2
        otherout['theta_Fres_AZ']     = theta_Fres_AZ
        otherout['theta_Fres_JA10']   = theta_Fres_JA10

        otherout['phi_rel']         = phi_rel
        otherout['camera_zenith']   = camera_zenith
        otherout['solar_zenith']    = solar_zenith
        otherout['cos_2omega']      = cos_2omega

        return rho_fres, otherout


    def get_fresnel_OLD(self, grid=None, grid_n=50):    
        """

        OLD VERSION OF THIS I MADE UP IN WILL'S KITCHEN WHILE REALLY STRUGGLING WITH THE GEOMETRY

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

        print('Should compare to Jackson and Alpers equation 10 which uses the spherical law of cosines. ')

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
    
    def plot_specular(self, alpha=1):
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
        plt.gca().text(sx, sy, sz, 'Incoming Solar Rariation', color='r', ha='center')

        meshx, meshy, meshz, Z_xf, Z_yf, theta_f, psi_f   =  self.get_specular_facets(grid_n=50)

        theta_f = np.arctan(np.sqrt(Z_xf**2+Z_yf**2))

        # This is a hack to make them plot flat
        if False:
            scale_down = 10000
            cz = meshz+(theta_f*180/np.pi)/scale_down
            levels = np.array([0, 10, 20, 30, 40])/scale_down

            C = plt.gca().contour(meshx, meshy, cz, zdir='z', colors='m', levels=levels, alpha=alpha)

        else:
            cz = (theta_f*180/np.pi)
            levels = np.array([0, 10, 20, 30, 40])
            
            C = plt.gca().contour(meshx, meshy, cz, zdir='z', offset=0, colors='m', levels=levels, alpha=alpha)

        plt.gca().clabel(C)
        print('Should be adding labels')

        plt.legend()

        return C
