import navpy, numpy as np
import math
import matplotlib.pyplot as plt

import aerial_imagery.utils as utils
import aerial_imagery.distortion as distortion

from aerial_imagery.cameras import set_camera
import cv2 as cv

'''
# Module for direct georeferencing alla Correia et al. 2002 but using Applanix inputs /conventions

'''

R_NED_to_ENU = np.array([[0, 1, 0],[1, 0, 0],[0, 0, -1]])
R_ENU_to_NED = R_NED_to_ENU.T # Equals it's transpose but that's OK

if False: # Old way
    R_C0_to_Ref = np.array([[0, 0, 1],[-1, 0, 0],[0, 1, 0]])  # Corriea et al (2022)
    R_C0_to_Ref = np.array([[1, 0, 0],[0, 1, 0],[0, 0, 1]])   # Leave unchanged
    R_C0_to_Ref = np.array([[0, -1, 0],[-1, 0, 0],[0, 0, 1]]) # Swap X and Y and reverse
    R_C0_to_Ref = np.array([[0, -1, 0],[1, 0, 0],[0, 0, 1]])  # Swap X and -Y 
else:
    pass

def yaw_pitch_roll_from_R(R):


    yaw   =  math.atan2(R[1,0], R[0,0])
    pitch = -math.asin(R[2,0])
    roll  =  math.atan2(R[2,1], R[2,2])

    return yaw, pitch, roll

def R_yaw_pitch_roll(yaw, pitch, roll):
    """
    Build a rotation matrix from yaw, pitch and roll angles. Note that this function 
    function uses standard aerospace conventions, i.e. the rotation is applied in the order of
    yaw, pitch and roll. This is different from the navpy.angle2dcm function which uses the
    order of roll, pitch and yaw.

    Note also that this will provide rotation from the reference to ENU. It 
    provides the inverse, or transpose then of the rotation from ENU to the reference frame. 
    That is:
        - R_ref_to_enu = R_yaw_pitch_roll(yaw, pitch, roll)
        - R_enu_to_ref = R_yaw_pitch_roll(yaw, pitch, roll).T
        
    """
    
    "2 ways to do this"
    
    R_yaw_pitch_roll = np.array([[math.cos(yaw)*math.cos(pitch),-math.sin(yaw)*math.cos(roll)+math.cos(yaw)*math.sin(pitch)*math.sin(roll),math.sin(yaw)*math.sin(roll)+math.cos(yaw)*math.cos(roll)*math.sin(pitch)]
                ,
                [math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(roll)+math.sin(roll)*math.sin(pitch)*math.sin(yaw),-math.cos(yaw)*math.sin(roll)+math.sin(pitch)*math.sin(yaw)*math.cos(roll)]
                ,
                [-math.sin(pitch),math.cos(pitch)*math.sin(roll),math.cos(pitch)*math.cos(roll)]])

    assert(np.all(np.isclose(R_yaw_pitch_roll, navpy.angle2dcm(yaw, pitch, roll).T)))
    
    return R_yaw_pitch_roll

def R_kappa_phi_omega(kappa, phi, omega):

    k, p, o = kappa, phi, omega

    # Rz = R_kappa = np.array([
    #     [np.cos(k),  np.sin(k), 0],
    #     [-np.sin(k), np.cos(k), 0],
    #     [0,          0,         1]
    # ])
    Rz = R_kappa = np.array([
            [np.cos(k), -np.sin(k), 0],
            [np.sin(k),  np.cos(k), 0],
            [0,          0,         1]
        ])

    # Ry = R_phi = np.array([
    #     [np.cos(p), 0, -np.sin(p)],
    #     [0,         1, 0],
    #     [np.sin(p), 0, np.cos(p)]
    # ])
    Ry = R_phi = np.array([
        [np.cos(p), 0, np.sin(p)],
        [0,         1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])

    # Rx = R_omega = np.array([
    #     [1, 0,          0],
    #     [0, np.cos(o),  np.sin(o)],
    #     [0, -np.sin(o), np.cos(o)]
    # ])
    Rx = R_omega = np.array([
            [1, 0,          0],
            [0, np.cos(o), -np.sin(o)],
            [0, np.sin(o), np.cos(o)]
        ])
    # Applanix want R_omega, then R_phi, then R_kappa for NED → Camera frame, thus  R_NED_to_C = R_kappa @ R_phi @ R_omega 
    # R_kappa @ R_phi @ R_omega is the rotation from NED to Camera frame.
    # NED → Camera frame

    return R_omega @ R_phi @ R_kappa  

def R_omega_phi_kappa(kappa, phi, omega):

    k, p, o = kappa, phi, omega

    Rz = R_kappa = np.array([
        [np.cos(k),  np.sin(k), 0],
        [-np.sin(k), np.cos(k), 0],
        [0,          0,         1]
    ])

    # Ry = R_phi = np.array([
    #     [np.cos(p), 0, -np.sin(p)],
    #     [0,         1, 0],
    #     [np.sin(p), 0, np.cos(p)]
    # ])
    Ry = R_phi = np.array([
        [np.cos(p), 0, np.sin(p)],
        [0,         1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])
    
    Rx = R_omega = np.array([
        [1, 0,          0],
        [0, np.cos(o),  np.sin(o)],
        [0, -np.sin(o), np.cos(o)]
    ])
    
    return R_kappa @ R_phi @ R_omega  # NThe one on the right is the first 

def compute_reprojection_error_angle(R_a_to_b, R_b_to_a):
    ''' 
    Compute the angle represented by a forward-backward rotation matrix, R, 
    as the largest angle between the 3 vectors and their representative unit normal
    '''

    R_a_to_a = R_a_to_b @ R_b_to_a  # Forward-backward rotation matrix

    max_angle = 0
    for i in range(3):
        # print(f"R[0, {i}]: {R[0, i]}")
        v = [0, 0, 0]
        v[i] = 1 # Unit normal
        v2 = R_a_to_a[i, :]

        if True: # Normalise the vector to unit length, this gives weird answers
            v2 = v2 / np.linalg.norm(v2)  # Normalize the vector
        else: # Normalise the vector in the expected unit normal direction, gives more intuitive answers
            v2 = v2 / v2[i]  # Normalize the vector
        dot = np.clip(np.dot(v2, v), -1.0, 1.0)
        dot = np.dot(v2, v)

        angle_rad = np.arccos(dot)
        angle_deg = np.degrees(angle_rad)

        print(v, v2)
        print(dot)
        print(angle_deg)

        max_angle = max(max_angle, np.abs(angle_deg))

    print(f"Angle error of forward and backward reprojection: {max_angle:.6f} degrees")

    return max_angle

class DGR(object):
    # This is the reference point
    _yaw_Ref   = np.nan #rad
    _pitch_Ref = np.nan #rad
    _roll_Ref  = np.nan #rad

    _solar_azim = np.nan #rad
    _solar_zenith  = np.nan #rad

    def __init__(self, ext_imu, ori_method, camera='ZED2_C2022', camera_options={}, **kwargs):
        """
        Direct georeferencing class for aerial imagery using the Applanix conventions and outputs.

        Parameters
        ----------
            ext_imu: bool
                Is external IMU in use or not?.
            ori_method:
                The method used to specify orientation of the system. This can be 'HPR' for heading, pitch and roll, or 'KPO' for kappa, phi and omega.
            camera: str
                The name of the camera to use. This is used to set the camera parameters.
            camera_options: dict
                A dictionary of options for the camera, such as focal length, pixel size, etc.
            **kwargs: dict
                Additional keyword arguments, such as verbose, name, offsets, kappa_rotation.

        """

        ori_method = ori_method.upper()
        if ori_method not in ['HPR', 'KPO']:
            raise ValueError(f'Orientation method {ori_method} not recognised. Use "HPR" or "KPO".')
        
        if ext_imu and ori_method=='HPR':
            raise ValueError('External IMU is not compatible with HPR orientation method. This requires encoder angles and consistency checking. Use KPO instead.')

        self.verbose = kwargs.pop('verbose', True,)

        self.ext_imu = ext_imu
        self.ori_method = ori_method

        self.name = kwargs.pop('name', 'Unnamed AF')
        boresight_pert = kwargs.pop('boresight_pert', {},)
        
        self._kappa_rotation = kwargs.pop('kappa_rotation', 0,) # This is how the camera is intended to be mounted in the gimbal, usuallo 0, pi/2 or -pi/2

        if len(kwargs.keys()) > 0:
            raise Exception(f'Unused keyword arguments in DGR constructor: {kwargs.keys()}')

        set_camera(self, camera, camera_options)

        if self.verbose:
            print('Creating airframe with:')
            print(f'    Camera = "{camera}"')
            print(f'         f_mm = "{self._f_mm}"')
            print(f'         c_x  = "{self._c_x}"')
            print(f'         c_y  = "{self._c_y}"')
            print(f'    boresight_pert = {boresight_pert}')

        self.dist_coeffs = np.array([0., 0., 0.])

        self.has_KappaPhiOmega = False
        self.has_HPR_Ref = False

        ########################################################
        ## Update boresight pert to get R_C_to_C0 and T_C_to_C0 
        ########################################################

        self.update_boresight_pert(boresight_pert)

        ########################################################
        ## Use kappa cardinal rotation pert to get R_C0_to_G ###
        ########################################################
        ## Default R_C0_to_G
        R_C0_to_G   = np.array([[0, -1, 0],[1, 0, 0],[0, 0, 1]])  # Swap X and -Y 
        ## Next the kappa rotation
        kappa_rot_mat = R_yaw_pitch_roll(self._kappa_rotation, 0, 0)
        ## Now the total rotation
        self.R_C0_to_G = kappa_rot_mat @ R_C0_to_G # This is actually C to Ref when "aligned". 

        ########################################################
        ## Use default sensor pos [0, 0, 0] to get T_C0_to_G ###
        ########################################################
        self.update_Camera_Pos(0, 0, 0)

        ########################################################
        ## Use kappa cardinal rotation pert to get R_C0_to_G ###
        ########################################################
        self.T_C0_to_G = np.array([[0],[0],[0]]) # Define NED origin - default to same as the UAS

        ########################################################
        ## Now a default Gimbal rotation to get R_G_to_Ref   ###
        ########################################################
        self.update_Gimbal(0, 0, 0)
        self.T_G_to_Ref = np.array([[0],[0],[0]]) # Define Gimbal origin - default to same as the Ref

            
        if self.ori_method.upper() == 'HPR':
            ########################################################
            ## Now a default HPR rotation to get R_Ref_to_NED   ###
            ########################################################
            self.update_HPR_Ref(0, 0, 0, units='rad')
        elif self.ori_method.upper() == 'HPR':
            error    
        else:
            error
        ########################################################
        ## Simply define T_Ref_to_NED as zero offset for now ###
        ########################################################
        self.T_Ref_to_NED = np.array([[0],[0],[0]]) # Define NED origin - default to same as the UAS

        ## Need the rotation only, translation set by UAS XYZ position
        self.R_NED_to_ENU = R_NED_to_ENU # np.array([[0, 1, 0],[1, 0, 0],[0, 0, -1]])
        R_ENU_to_NED      = R_NED_to_ENU.T



    def update_Camera_Pos(self, Gx, Gy, Gz):

        # Store these
        self._Gx = Gx
        self._Gy = Gy
        self._Gz = Gz

        self.T_C0_to_G = np.array([[Gx], [Gy], [Gz]])

    def update_Gimbal(self, Gtheta, Gphi, Gpsi, units='rad'):
        """
        Update the gimbal angles of the camera.
        This is used to set the rotation matrix from the camera to the gimbal.
        """
        if units.lower() in ['d', 'deg', 'degrees']:
            print('Converting angles from degrees to radians.')
            Gtheta = np.deg2rad(Gtheta)
            Gphi   = np.deg2rad(Gphi)
            Gpsi   = np.deg2rad(Gpsi)  
            print(f'Updating Gimbal angles to [Gtheta, Gphi, CRpsi]=[{Gtheta}, {Gphi}, {Gpsi}] in radians.')
        elif units.lower() in ['r', 'rad', 'radians']:
            pass
        else:
            raise ValueError(f'Units {units} not recognised. Use "rad" or "deg".')

        
        self.R_G_to_Ref = R_yaw_pitch_roll(Gtheta, Gphi, Gpsi) 


    def update_boresight_pert(self, offsets, units='rad'):
        """
        Update perturbations of boresight angles
        """
        if units.lower() in ['d', 'deg', 'degrees']:
            print('Converting boresight perturbations from degrees to radians.')
            offsets['CRtheta'] = np.deg2rad(offsets.get('CRtheta', 0))
            offsets['CRphi']   = np.deg2rad(offsets.get('CRphi', 0))
            offsets['CRpsi']   = np.deg2rad(offsets.get('CRpsi', 0))  
            print(f'Updating boresight perturbations to [CRtheta, CRphi, CRpsi]=[{offsets["CRtheta"]}, {offsets["CRphi"]}, {offsets["CRpsi"]}] in radians.')
        elif units.lower() in ['r', 'rad', 'radians']:
            pass
        else:
            raise ValueError(f'Units {units} not recognised. Use "rad" or "deg".')
        
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
        if False:

            self.T_C_to_Ref = np.array([[CRx], [CRy], [CRz]])

            R_C_to_Ref_mounting = R_yaw_pitch_roll(CRtheta, CRphi, CRpsi)
            self.R_C_to_Ref_mounting = R_C_to_Ref_mounting

            self.R_C_to_Ref = R_C_to_Ref_mounting@self.R_C_to_Ref_deterministic

        else:

            # self.T_G_to_Ref =    np.array([[0], [0], [0]])              # Gimbal to Reference frame are collocated
            # self.R_C_to_G = np.array([[1, 0, 0],[0, 1, 0],[0, 0, 1]]) # Gimbal and camera nominally are aligned

            self.T_C_to_C0  =    np.array([[CRx], [CRy], [CRz]])        # Gimbal and camera nominally are aligned

            R_C_to_C0       = R_yaw_pitch_roll(CRtheta, CRphi, CRpsi)  # This isn't really how I intended this but OK
            self.R_C_to_C0  = R_C_to_C0

        # Gimbal frame to UAS frame
        ## We don't need this for the Applanix method

        if self.verbose:
            print(f'UPDATING boresight perturbations')
            print(f'  Camera to reference linear offsets')
            print(f'    CRx = {CRx}')
            print(f'    CRy = {CRy}')
            print(f'    CRz = {CRz}')
            print(f'  Camera to reference angular offsets')
            print(f'    CRtheta = {CRtheta}')
            print(f'    CRphi   = {CRphi}')
            print(f'    CRpsi   = {CRpsi}')
            print(f'  R_C_to_C0')
            print(f'    {self.R_C_to_C0}')
            print(f'  T_C_to_C0')
            print(f'    {self.T_C_to_C0}')

    def build_K(self):
        
        self.K = np.array([[self._fx_pix, 0,            self._c_x],
                           [0,            self._fy_pix, self._c_y],
                           [0,            0,            1]])
    
    def update_IMU_UAS(self, yaw, pitch, roll):
        """
        Function removed, Applanix doesn't care about the airframe reference
        """
        raise(Exception('This function is not used anymore, it is here for reference only.'))
        
    def update_HPR_Ref(self, heading, pitch, roll, units='rad'):
        """
        Applanix export and EO will give you heading, pitch and roll of the Reference frame.

        What we need to do here is set the R_Ref_to_NED
        
        """

        print(f'Updating Reference frame angles to [H,P,R]=[{heading}, {pitch}, {roll}] in {units}.')
        self._frame_Ref = 'NED'

        if units.lower() in ['d', 'deg', 'degrees']:
            print('Converting HPR angles from degrees to radians.')
            heading = np.deg2rad(heading)
            pitch   = np.deg2rad(pitch)
            roll    = np.deg2rad(roll)  
            print(f'Updating Reference frame angles to [H,P,R]=[{heading}, {pitch}, {roll}] in radians.')
        elif units.lower() in ['r', 'rad', 'radians']:
            pass
        else:
            raise ValueError(f'Units {units} not recognised. Use "rad" or "deg".')
        
        self._heading_Ref = heading
        self._pitch_Ref   = pitch
        self._roll_Ref    = roll

        # inv = np.linalg.inv

        """
        This gives you your frame straight into NED as we believe the Applanix does. 
        """
            
        self.HPR_R_Ref_to_NED        = R_yaw_pitch_roll(heading, pitch, roll)
        self.HPR_R_NED_to_Ref        = self.HPR_R_Ref_to_NED.T
        
        print(f'HPR_R_NED_to_Ref = {self.HPR_R_NED_to_Ref}')

        self.HPR_R_Ref_to_ENU   = R_NED_to_ENU @ self.HPR_R_Ref_to_NED
        
        self.has_HPR_Ref = True

        if (not self.ext_imu) and self.has_KappaPhiOmega:
            self.check_IMU_consistency()

    def update_KappaPhiOmega(self, kappa, phi, omega, units='rad', order='KPO'):
        """
        Now applanix will also give you the kappa, phi and omega angles of the Sensor frame. 
        Note that this is not the camera body frame, but the camera / image frame. Here we 
        check for consistency between the kappa, phi and omega angles and the heading, pitch 
        and roll angles of the Reference frame. We assume the standard camera convention and 
        assume that there is no angle between the camera body frame and the image frame.

        NOTE, POSPAC DOES NOT DO BORESIGHT CAL SO WE ASSUME THIS IS UNCALIBRATED AND HENCE IT IS C0 

        """

        print(f'Updating Reference frame angles to [kappa,phi,omega]=[{kappa}, {phi}, {omega}] in {units}.')
        if units.lower() in ['d', 'deg', 'degrees']:
            print('Converting [kappa,phi,omega] angles from degrees to radians.')

            kappa = np.deg2rad(kappa)
            phi   = np.deg2rad(phi)
            omega = np.deg2rad(omega)  
            print(f'Updating Reference frame angles to [kappa,phi,omega]=[{kappa}, {phi}, {omega}] in radians.')
        elif units.lower() in ['r', 'rad', 'radians']:
            pass
        else:
            raise ValueError(f'Units {units} not recognised. Use "rad" or "deg".')

        self._kappa = kappa
        self._phi   = phi
        self._omega = omega

        # R_NED_to_C      = R_yaw_pitch_roll(kappa, phi, omega)
        # R_NED_to_C      = R_omega_phi_kappa(kappa, phi, omega)
        

        # self.R_C_to_NED = R_NED_to_C.T

        # R_C_to_NED      = R_yaw_pitch_roll(kappa, phi, omega)
        kappa_rot_mat        = R_yaw_pitch_roll(self._kappa_rotation, 0, 0)
        if order.upper()=='OPK': # Intrinsic vs extrinsic?
            KPO_R_C0_to_NED      = R_omega_phi_kappa(kappa, phi, omega)
            KPO_R_C0_to_NED      = KPO_R_C0_to_NED @ kappa_rot_mat  
            print('NEED TO TEST THIS FOR ALL ANGLES')
            error
            for i in np.arange(10):
                print('THIS SOMETIMES MIXES UP PITCH AND ROLL, DEPENDING ON KAPPA, I THINK')
        elif order.upper()=='KPO':
            KPO_R_C0_to_NED      = R_kappa_phi_omega(kappa, phi, omega)
            KPO_R_C0_to_NED      = KPO_R_C0_to_NED @ kappa_rot_mat  # I don't love this to be honest. 
            print('NEED TO TEST THIS FOR ALL ANGLES')

            for i in np.arange(10):
                print('THIS ALWAYS MIXES UP PITCH AND ROLL, I THINK'
                      )
        else:
            raise ValueError(f'Order {order} not recognised. Use "KPO" or "OPK".')
        KPO_R_NED_to_C0      = KPO_R_C0_to_NED.T

        self.KPO_R_C0_to_NED = KPO_R_C0_to_NED
        print(f'KPO_R_NED_to_C = {KPO_R_NED_to_C0}')
        print(f'KPO_R_C_to_NED = {self.KPO_R_C0_to_NED}')

        self.has_KappaPhiOmega = True
        if (not self.ext_imu) and self.has_HPR_Ref:
            self.check_IMU_consistency()

    def check_IMU_consistency(self, alt=0):
        """
        Check the consistency between the HPR and KPO angles. 
        """
       
        print('We have no external IMU so we can check for consistency between the HPR angles and the KPO angles.')
        print()

        if True:
            ori_method = self.ori_method
            # Overwriting a property in a test / check isn't ideal but it works for now
            self.ori_method = 'HPR'
            meshxHPR, meshyHPR, meshz = self.make_georef_grid(grid_n=None, alt=alt)
            self.ori_method = 'KPO'
            meshxKPO, meshyKPO, meshz = self.make_georef_grid(grid_n=None, alt=alt)

            self.ori_method = ori_method  # Restore the original method

            d = np.sqrt((meshxHPR - meshxKPO)**2 + (meshyHPR - meshyKPO)**2)
            d = np.sum(d) / np.prod(meshyKPO.shape)

            print(f"Total inconsistency between KPO and HPR at a height of {alt} m: {d:.2e} metres per pixel")
            # assert d < 1e-6, "KPO and HPR inconsistency"

            return d
        
        else:
            print('MORE WORK NEEEDED ON NEW BETA KPO METHOD')

    def calculate_reference_frames(self):
        """
        Calculate the reference frames based on the current HPR and KPO angles.
        This is used to update the R_C_to_NED and R_Ref_to_NED matrices.


        """
        
        if self.ori_method.upper() == 'HPR':
            if not self.has_HPR_Ref:
                raise ValueError('HPR angles of the Reference frame are not set. Use update_HPR_Ref() first.')
            """
            With HPR setting we Know the Reference frame angles Apriori, so this is the simplest method as long as 
            NED is at Ref.  
            """

            # NED to ENU - THESE ARE JUST CONSTANT
            HPR_T_NED_to_ENU      =  self.T_NED_to_ENU
            HPR_R_NED_to_ENU      =  self.R_NED_to_ENU



            # THIS IS WHAT IS SPECIFIED AND CALCULATED BY self.update_HPR_Ref()
            HPR_R_Ref_to_NED = self.HPR_R_Ref_to_NED



            # REF to ENU
            HPR_T_Ref_to_ENU      =  HPR_T_NED_to_ENU + HPR_R_NED_to_ENU @ self.T_Ref_to_NED 
            HPR_R_Ref_to_ENU      =  HPR_R_NED_to_ENU @ HPR_R_Ref_to_NED 

            # G to ENU
            HPR_T_G_to_ENU        =  HPR_T_Ref_to_ENU + HPR_R_Ref_to_ENU @ self.T_G_to_Ref 
            HPR_R_G_to_ENU        =  HPR_R_Ref_to_ENU @ self.R_G_to_Ref

            # C0 to ENU 
            HPR_T_C0_to_ENU       =  HPR_T_G_to_ENU + HPR_R_G_to_ENU @ self.T_C0_to_G
            HPR_R_C0_to_ENU       =  HPR_R_G_to_ENU @ self.R_C0_to_G

            # C to ENU
            HPR_T_C_to_ENU        =  HPR_T_C0_to_ENU + HPR_R_C0_to_ENU @ self.T_C_to_C0
            HPR_R_C_to_ENU        =  HPR_R_C0_to_ENU @ self.R_C_to_C0

            
            # HPR_R_C_to_NED        = R_ENU_to_NED @ HPR_R_C_to_ENU
            # self.HPR_R_C_to_NED   = HPR_R_C_to_NED
            # self.HPR_R_Ref_to_NED = HPR_R_Ref_to_NED
            
            self.HPR_T_C_to_ENU   = HPR_T_C_to_ENU
            self.HPR_T_C0_to_ENU  = HPR_T_C0_to_ENU
            self.HPR_T_G_to_ENU   = HPR_T_G_to_ENU
            self.HPR_T_Ref_to_ENU = HPR_T_Ref_to_ENU
            self.HPR_T_NED_to_ENU = HPR_T_NED_to_ENU

            self.HPR_R_C_to_ENU   = HPR_R_C_to_ENU
            self.HPR_R_C0_to_ENU  = HPR_R_C0_to_ENU
            self.HPR_R_G_to_ENU   = HPR_R_G_to_ENU
            self.HPR_R_Ref_to_ENU = HPR_R_Ref_to_ENU
            self.HPR_R_NED_to_ENU = HPR_R_NED_to_ENU

            HPR = {}
            HPR['R_C_to_ENU']   = HPR_R_C_to_ENU
            HPR['R_C0_to_ENU']  = HPR_R_C0_to_ENU
            HPR['R_G_to_ENU']   = HPR_R_G_to_ENU
            HPR['R_Ref_to_ENU'] = HPR_R_Ref_to_ENU
            HPR['R_NED_to_ENU'] = HPR_R_NED_to_ENU
            HPR['T_C_to_ENU']   = HPR_T_C_to_ENU
            HPR['T_C0_to_ENU']  = HPR_T_C0_to_ENU
            HPR['T_G_to_ENU']   = HPR_T_G_to_ENU
            HPR['T_Ref_to_ENU'] = HPR_T_Ref_to_ENU
            HPR['T_NED_to_ENU'] = HPR_T_NED_to_ENU


            HPR['R_Ref_to_NED'] = HPR_R_Ref_to_NED

            return HPR
            return HPR_R_C_to_ENU, HPR_R_G_to_ENU, HPR_R_Ref_to_ENU, HPR_R_Ref_to_NED, HPR_T_C_to_ENU

        elif self.ori_method.upper() == 'KPO':

            if not self.has_KappaPhiOmega:
                raise ValueError('KPO angles of the Sensor frame are not set. Use update_KappaPhiOmega() first.')


            # NED to ENU - THESE ARE JUST CONSTANT
            KPO_T_NED_to_ENU      =  self.T_NED_to_ENU
            KPO_R_NED_to_ENU      =  self.R_NED_to_ENU

            # THIS IS WHAT IS SPECIFIED AND CALCULATED BY self.update_KappaPhiOmega()
            KPO_R_C0_to_NED = self.KPO_R_C0_to_NED    
            # THIS IS WHAT IS SPECIFIED AND CALCULATED BY self.update_POS_Ref()
            KPO_T_NED_to_ENU = self.T_NED_to_ENU

            # REF to ENU - this is trivial due to collocation but OK
            KPO_T_Ref_to_ENU      =  KPO_T_NED_to_ENU + KPO_R_NED_to_ENU @ self.T_Ref_to_NED 
            KPO_T_G_to_ENU        =  KPO_T_Ref_to_ENU

            # C0 to ENU
            KPO_R_C0_to_ENU   = KPO_R_NED_to_ENU @ KPO_R_C0_to_NED
            KPO_R_ENU_to_C0   = KPO_R_C0_to_ENU.T

            

            ## NOW WE'RE GOIING BACKWARDS
            # G to ENU
            # R_C0_to_ENU       =  R_G_to_ENU @ self.R_C0_to_G
            KPO_R_G_to_ENU      = KPO_R_C0_to_ENU @ self.R_C0_to_G.T  # This is the rotation from Gimbal to ENU

            # REF to ENU
            # KPO_R_G_to_ENU        =  KPO_R_Ref_to_ENU @ self.R_G_to_Ref
            KPO_R_Ref_to_ENU        = KPO_R_G_to_ENU @ self.R_G_to_Ref.T  # This is the rotation from Reference to ENU
            # KPO_T_G_to_ENU        =  KPO_T_Ref_to_ENU + KPO_R_Ref_to_ENU @ self.T_G_to_Ref 
            KPO_T_Ref_to_ENU        = KPO_T_G_to_ENU - KPO_R_Ref_to_ENU @ self.T_G_to_Ref  # This is the translation from Reference to ENU

            ## NOW WE'RE GOIING FORWARDS AGAIN
            # C0 to ENU 
            KPO_T_C0_to_ENU       =  KPO_T_G_to_ENU + KPO_R_G_to_ENU @ self.T_C0_to_G

            # C to ENU
            KPO_T_C_to_ENU        =  KPO_T_C0_to_ENU + KPO_R_C0_to_ENU @ self.T_C_to_C0
            KPO_R_C_to_ENU        =  KPO_R_C0_to_ENU @ self.R_C_to_C0


            KPO = {}
            KPO['R_C_to_ENU']      = KPO_R_C_to_ENU
            KPO['R_C0_to_ENU']     = KPO_R_C0_to_ENU
            KPO['R_G_to_ENU']      = KPO_R_G_to_ENU
            KPO['R_Ref_to_ENU']    = KPO_R_Ref_to_ENU
            KPO['R_NED_to_ENU']    = KPO_R_NED_to_ENU
            KPO['T_C_to_ENU']      = KPO_T_C_to_ENU
            KPO['T_C0_to_ENU']     = KPO_T_C0_to_ENU
            KPO['T_G_to_ENU']      = KPO_T_G_to_ENU
            KPO['T_Ref_to_ENU']    = KPO_T_Ref_to_ENU
            KPO['T_NED_to_ENU']    = KPO_T_NED_to_ENU

            KPO_R_Ref_to_NED       = KPO_R_NED_to_ENU.T @ KPO_R_Ref_to_ENU
            KPO['R_Ref_to_NED']    = KPO_R_Ref_to_NED

            return KPO
        
        else:
            raise ValueError(f'Method {self.ori_method} not recognised. Use "HPR" or "KPO"')

    def calculate_AF_reference_frame(self):
        """
        Calculate the airframe reference frame.

        Note that we don't need this for georeferencing but it has some other uses. 
        """

        pass

    def update_POS_Ref(self, x, y, z):
        
        for i in np.arange(10):
            print('Hoooooley dooley I need to to confirm that both methods are giving me the Ref position, not the camera.')
            print('Really maybe this should be POS NED.')

        self._UTM_x = x
        self._UTM_y = y
        self._UTM_z = z
    
    @property
    def Ref_UTM_xyz(self):
    
        return np.array([[self._UTM_x], [self._UTM_y], [self._UTM_z]])
    
    @property
    def T_NED_to_ENU(self):
        
        return self.Ref_UTM_xyz
        # return self.UAS_UTM_xyz

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
        print(fulloutput)

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


        # R_C_to_ENU, R_Ref_to_ENU, R_Ref_to_NED, T_C_to_ENU = self.calculate_reference_frames(method='HPR') #
        # R_C_to_ENU, R_Ref_to_ENU, R_Ref_to_NED, T_C_to_ENU = self.calculate_reference_frames()
        REFFRAMES = self.calculate_reference_frames()

        if reverse:


            if True:
                target = P_xyz                # We're reversing, so our Pixel Positions are actually target positions.  
                target[2, :] = target_z       # Get rid of the normalised z, we have a real target here. 

                # R_ENU_to_C = np.linalg.inv(self.R_C_to_ENU)       # Invert the rotation martrix
                # P_C =  R_ENU_to_C @ (target - self.T_C_to_ENU)    # Translate, then rotate
                R_ENU_to_C = np.linalg.inv(REFFRAMES['R_C_to_ENU'])       # Invert the rotation martrix
                P_C =  R_ENU_to_C @ (target - REFFRAMES['T_C_to_ENU'])    # Translate, then rotate
                
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

            # if False: # Move this to standalone function
            #     R_C_to_Ref   = self.R_C_to_Ref
            #     R_C_to_NED   = self.R_Ref_to_NED@self.R_C_to_Ref
            #     R_C_to_ENU   = self.R_NED_to_ENU@self.R_Ref_to_NED@self.R_C_to_Ref

            #     R_NED_to_ENU = self.R_NED_to_ENU
            #     R_Ref_to_ENU = self.R_NED_to_ENU@self.R_Ref_to_NED 

            #     T_NED_to_ENU =  self.Ref_UTM_xyz
            #     T_Ref_to_ENU =  T_NED_to_ENU + self.R_NED_to_ENU@self.T_Ref_to_NED 
            #     T_C_to_ENU   =  T_Ref_to_ENU + self.R_NED_to_ENU@self.R_Ref_to_NED@self.T_C_to_Ref

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
            
            ## NOW I'VE ADDED AN EXPLICIT C0 FRAME!
            print('C to C0')
            print(P_C_prime)
            print(self.R_C_to_C0)
            print(self.T_C_to_C0)
            P_C0_prime = self.R_C_to_C0  @ P_C_prime_prime + self.T_C_to_C0 # C to C0
            print(P_C0_prime)

            ## NOW I'VE ADDED BACK THIS GIMBAL FRAME!
            P_G_prime   = self.R_C0_to_G @ P_C0_prime + self.T_C0_to_G   # C to G

            # And now Ref
            P_Ref_prime = self.R_G_to_Ref @ P_G_prime + self.T_G_to_Ref # G to Ref

            if fulloutput:
                print("\n P_Ref_prime:")
                print(P_Ref_prime)
            print("\n P_Ref_prime:")
            print(P_Ref_prime)
            
            print(fulloutput)
            # error

            # Map from the Reference frame (distance) to the North-East-Down frame (distance)
                # This can be done without translation, i.e. having the same origin

            P_NED_prime = REFFRAMES['R_Ref_to_NED'] @ P_Ref_prime + self.T_Ref_to_NED

            if fulloutput:
                print("\n P_NED_prime:")
                print(P_NED_prime)

            P_ENU_prime = self.R_NED_to_ENU @ P_NED_prime + self.T_NED_to_ENU

            if fulloutput:
                print("\n P_ENU_prime:")
                print(P_ENU_prime)

            ################################################################
            ### NOW WE NEED TO GO FROM THE 2D PRIME FRAME TO A FULL 3D FRAME
            ################################################################
            if z_ENU is None:
                P_ENU = P_ENU_prime
            else:
                # T =  T_END_to_ENU 
                # T += self.R_END_to_ENU@self.T_UAS_to_END
                # T += self.R_END_to_ENU@self.R_UAS_to_END@self.T_G_to_UAS 
                # T += self.R_END_to_ENU@self.R_UAS_to_END@self.R_G_to_UAS@self.T_C_to_Gd
                if False:
                    T =  self.T_NED_to_ENU 
                    T += self.R_NED_to_ENU @ self.T_Ref_to_NED
                    T += self.R_NED_to_ENU @ R_Ref_to_NED @ self.T_C_to_Ref # Ref to ENU * C to Ref
                else:
                    T =  self.T_NED_to_ENU                      # To NED
                    T += self.R_NED_to_ENU @       self.T_Ref_to_NED  # To Ref
                    T += self.R_NED_to_ENU @ REFFRAMES['R_Ref_to_NED'] @ self.T_G_to_Ref  # To G
                    T += self.R_NED_to_ENU @ REFFRAMES['R_Ref_to_NED'] @ self.R_G_to_Ref @ self.T_C0_to_G  # To C0
                    T += self.R_NED_to_ENU @ REFFRAMES['R_Ref_to_NED'] @ self.R_G_to_Ref @ self.R_C0_to_G @ self.T_C_to_C0   # To c<------- This is clearly wrong!!!

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

    def forward_backward_reprojection_error(self, alt = 0):
        """
        Calculate the forward and backward reprojection error.
        This is a sanity check to ensure that the forward and backward transformations are consistent.
        """
        # Forward transformation
        xpixg, ypixg = self.make_grid(grid_n=None)
        meshx, meshy, meshz = self(xpixg, ypixg, alt, fulloutput=False)

        # Backward transformation
        xpixg2, ypixg2, one = self(meshx, meshy, alt, fulloutput=False, reverse=True)

        # Calculate the distance between the original and transformed points
        d = np.sqrt((xpixg - xpixg2)**2 + (ypixg - ypixg2)**2)
        d = np.sum(d) / np.prod(xpixg.shape)

        print(f"Total forward backward reprojection error to a height of {alt} m: {d:.2e} pixels per pixel")
        assert d < 1e-6, "Forward backward reprojection error is too high"

        return d

    def reverse(self, P_ENU):

        pass

    def get_axes(self):

        """
        Return all of the Axes you need
        """

        REFFRAMES = self.calculate_reference_frames()

        ###############################
        # ENU - OUR STARTING POSITION #
        ###############################
        ENU = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # ENU axes

        ################################
        # NED - CALC NOT REALLY NEEDED #
        ################################
        NED = R_ENU_to_NED @ ENU   # Convert ENU to NED

        ################################
        # REF -                        #
        ################################
        R_ENU_to_Ref = REFFRAMES['R_Ref_to_ENU'].T  # Inverse of the rotation matrix
        Ref = R_ENU_to_Ref @ ENU     # Convert ENU to Reference frame

        ################################
        # GIMBAL -                     #
        ################################
        R_ENU_to_G = REFFRAMES['R_G_to_ENU'].T  # Inverse of the rotation matrix
        G = R_ENU_to_G @ ENU     # Convert ENU to Reference frame
        
        ################################
        # Camera_0 -                   #
        ################################
        R_ENU_to_C0 = REFFRAMES['R_C0_to_ENU'].T  # Inverse of the rotation matrix
        C0 = R_ENU_to_C0 @ ENU     # Convert ENU to Reference frame

        
        ################################
        # Camera -                     #
        ################################
        R_ENU_to_C = REFFRAMES['R_C_to_ENU'].T  # Inverse of the rotation matrix
        C = R_ENU_to_C @ ENU     # Convert ENU to Reference frame

        ################################
        # OUTPUTS -                    #
        ################################
        axes = {}
        axes['ENU'] = ENU
        axes['NED'] = NED
        axes['R']   = Ref
        axes['G']   = G
        axes['C0']  = C0
        axes['C']   = C

        return axes

    def get_component_positions(self):
        """
        Get the positions of the Reference and Camera. 

        At the moment the camera to reference translation is correct for KPR only. 

        It shouldn't be in the reference frame, rather it should be in this C0 frame, which is essentially the Gimbal frame. 

        So, I shouldn't have removed the Gimbal Frame. I'm going to call it the 

        """

        REFFRAMES = self.calculate_reference_frames()

        # raise(Exception('This function is needs fixing for the new applanix system.'))
        if self.ori_method.upper() in ['HPR', 'KPO']:
            
            T_NED_to_ENU =  self.Ref_UTM_xyz
            T_Ref_to_ENU =  T_NED_to_ENU + REFFRAMES['R_NED_to_ENU']@self.T_Ref_to_NED 
            T_G_to_ENU   =  T_Ref_to_ENU + REFFRAMES['R_Ref_to_ENU']@self.T_G_to_Ref
            T_C0_to_ENU  =  T_G_to_ENU   + REFFRAMES['R_G_to_ENU']  @self.T_C0_to_G
            T_C_to_ENU   =  T_C0_to_ENU  + REFFRAMES['R_C0_to_ENU'] @self.T_C_to_C0

            # R_Ref_to_G_mounting = self.R_G_to_Ref_mounting.T

            # T_C_to_ENU   =  T_NED_to_ENU + self.R_NED_to_ENU@R_Ref_to_NED@R_Ref_to_G_mounting@self.T_G_to_Ref


        else:
            raise ValueError(f'Method {self.method} not recognised. Use "HPR".')


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

        print(f'Camera position [T_ENU_to_C] is {OC.T}')
        print(f'Ref position [T_ENU_to_Ref] is {ORef.T}')
        print(f'NED position [T_ENU_to_NED] is {ONED.T}')

        origins = {}
        origins['ENU'] = OENU
        origins['NED'] = ONED
        origins['R'] = ORef
        origins['G']   = T_G_to_ENU
        origins['C0']  = T_C0_to_ENU
        origins['C']   = OC

        return origins

    def plot_scene(self, bbox_alt=0, targets=[], 
               ax=None,
               al=15,
               gridcol='b',
               plot_corners=True,
               plot_ground=False,
               method='HPR'):
    
        OC, ORef, ONED = self.get_component_positions()
        
        if ax is None:
            ax = plt.figure(figsize=(10, 10)).add_subplot(projection='3d')
        
        x, y, z = self.Ref_UTM_xyz
        xco, yco, zco = OC

        ax.scatter(xco, yco, zco, zdir='z', label=self.name, color=gridcol)

        if plot_ground:
            ax.scatter(xco, yco, bbox_alt, zdir='z', label=self.name + ' "X,Y"', color=gridcol, alpha=0.5)
    
        meshx, meshy, meshz = self.c(grid_n=11, alt=bbox_alt)

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
        
        l = self(np.linspace(0, 0), np.linspace(0, self._npix_y), bbox_alt, method=method)
        ax.plot(l[0], l[1], l[2], gridcol, zdir='z')
        
        r = self(np.linspace(self._npix_x, self._npix_x), np.linspace(0, self._npix_y), bbox_alt, method=method)
        ax.plot(r[0], r[1], r[2], gridcol, zdir='z')
        
        u = self(np.linspace(0, self._npix_x), np.linspace(self._npix_y, self._npix_y), bbox_alt, method=method)
        ax.plot(u[0], u[1], u[2], gridcol, zdir='z')
        
        b = self(np.linspace(0, self._npix_x), np.linspace(0, 0), bbox_alt, method=method)
        ax.plot(b[0], b[1], b[2], gridcol, zdir='z')
        
        c = self(self._c_x, self._c_y, bbox_alt, method=method)
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
            targ = self(target[0], target[1], target[2], method=method)
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
    
    def make_georef_grid(self, grid_n=None, alt=0, fulloutput=False):
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
        meshx, meshy, meshz = self(xpixg, ypixg, alt, fulloutput=False)

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

    R_C_to_NED   = R_NED_to_ENU.T @ R_C_to_ENU
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
    
