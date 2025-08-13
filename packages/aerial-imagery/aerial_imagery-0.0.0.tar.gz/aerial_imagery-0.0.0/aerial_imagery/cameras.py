import numpy as np

ccd_properties = {
    'ZED2_C2022': {
        'sensor_width': 3.6, # mm
        'sensor_height': 2.7, # mm
        'npix_x': 1920, # pixels
        'npix_y': 1080, # pixels
    },
    'DJI_P4RTK': {
        'sensor_width': 13.1, # mm
        'sensor_height': 8.8, # mm
        'npix_x': 5472, # pixels
        'npix_y': 3648, # pixels
    },
    'Leica_M10_Monochrom': {
        'sensor_width': 36, # mm
        'sensor_height': 24, # mm
        'npix_x': 7864, # pixels
        'npix_y': 5200, # pixels
    },
    'Sentinel2Granule': {
        'sensor_width': 10, # m
        'sensor_height': 10, # m
        'npix_x': 256, # pixels
        'npix_y': 256, # pixels
    },
    'Rascle2017': {
        'sensor_width': 8.8, # mm
        'sensor_height': 6.6, # mm
        'npix_x': 2536, # pixels
        'npix_y': 2068, # pixels
    },
    'workswell_wirspro': {
        'sensor_width': 10.88, # mm
        'sensor_height': 8.705, # mm
        'npix_x': 640, # pixels
        'npix_y': 512, # pixels
    },
    'Normalised': {
        'sensor_width': 1, # mm
        'sensor_height': 1, # mm
        'npix_x': 1, # pixels
        'npix_y': 1, # pixels
    },
}

def known_cameras():
    """
    Return a list of known cameras.
    """
    
    kc = list(ccd_properties.keys()) + ['custom']
    return kc

def get_ccd_properties(camera, kappa_rotation=0):
    """
    Return the CCD properties of a camera. You can also specify a rotation of the camera 
    around the z-axis for use with pre-rotated images.
    
    Parameters
    ----------
        camera: string
            Name of the camera
        kappa_rotation: float
            Rotation of the camera around the z-axis. Must be one of {0, 90, 180 or -90}. 
            Default is 0. If 90 or -90, the npix_x and npix_y are swapped as are the 
            sensor_width and sensor_height. 

    Returns
    -------
        dict
            Dictionary with the camera properties.
    """

    

    if not kappa_rotation in [0, 90, 180, -90]:
        raise(Exception("kappa_rotation must be 0, 90, 180 or -90"))
    
    ccd = ccd_properties[camera].copy()
    if kappa_rotation in [90, -90]:
        ccd['npix_x']       = ccd_properties[camera]['npix_y']
        ccd['npix_y']       = ccd_properties[camera]['npix_x']
        ccd['sensor_width'] = ccd_properties[camera]['sensor_height']
        ccd['sensor_height'] = ccd_properties[camera]['sensor_width']    

    ccd['kappa_rotation'] = kappa_rotation

    return ccd

def set_camera(self, camera, camera_options):
    """
    Attach a camera to a DGR object and build the K transformation matrix. 

    Parameters
    ----------
        self: dgr object
            The object chasing a camera
        camera: string
            Name of the camera to attach
        camera_options: dict
            Additional camera options taken by some cameras [e.g. the
            leica_m10_monochrom allows interchangeable lenses]
                """

    camera_options = camera_options.copy()
    
    if camera.upper() == 'ZED2_C2022':
        """
        Use the ZED2 matrix from Corriea et al. (2022). Note that every ZED2 has a
        unique K which is a part of a camera validation. Corriea et al. (2022) 
        determined theirs using the Robot Operating System. 
        
        Looking at their c_x and c_y however, I think they are using the HD1080 
        version of the Z2 (see https://support.stereolabs.com/hc/en-us/articles/
        360007395634-What-is-the-camera-focal-length-and-field-of-view-#:~:text=
        The%20ZED%20and%20ZED%202,have%20a%206.3cm%20baseline.)
        
        """
        print('SHOULD READING CCD PARAMETERS FROM MODULE')
        print('SHOULD READING CCD PARAMETERS FROM MODULE')

        focalLength_pix   = 1000 # Pixels, ZED2 HD2K/HD1080
        
        self._fx_pix = 1055.334228515625
        self._fy_pix = 1055.334228515625
        self._c_x = 990.0682373046875
        self._c_y = 544.24639892578125
        
        self._npix_x = 1920 # Not in the paper
        self._npix_y = 1080 # Not in the paper
        
        sizepix_mm = 0.002 # Not in the paper

        self._sensor_width_mm  = sizepix_mm*self._npix_x # Not in the paper
        self._sensor_height_mm = sizepix_mm*self._npix_y # Not in the paper

        self._f_mm = self._fx_pix*self._sensor_width_mm/self._npix_x
        
        self.build_K()

    elif camera.upper() == 'DJIP4RTK':
        """
        From Branson
        """
        print('SHOULD READING CCD PARAMETERS FROM MODULE')
        print('SHOULD READING CCD PARAMETERS FROM MODULE')
        focalLength_pix   = 1000 # 
        
        self._fx_pix = 3666.666504
        self._fy_pix = 3666.666504

        self._npix_x = 5472 
        self._npix_y = 3648 

        self._c_x = self._npix_x/2
        self._c_y = self._npix_y/2
                
        self._sensor_width_mm  = 13.1
        self._sensor_height_mm = 8.8

        self._f_mm = self._fx_pix*self._sensor_width_mm/self._npix_x
        
        self.build_K()
    
    elif camera.lower() == 'leica_m10_monochrom':
        """
        Example is a LEICA 40.89 Mpx M10 monochrome. 

        10x10 m
        256x256 pixels
        """
        print('SHOULD READING CCD PARAMETERS FROM MODULE')
        print('SHOULD READING CCD PARAMETERS FROM MODULE')

        f_mm = camera_options.pop('f_mm', 50)
        self._f_mm = f_mm

        # 40.89 Mpx 
        self._npix_x = 7864 # 
        self._npix_y = 5200 # 

        self._c_x = self._npix_x/2 # Middle it!
        self._c_y = self._npix_y/2 # Middle it!
        
        # Full frame sensor
        self._sensor_width_mm  = 36 
        self._sensor_height_mm = 24 

        self._fx_pix = self._f_mm/(self._sensor_width_mm/self._npix_x)
        self._fy_pix = self._f_mm/(self._sensor_height_mm/self._npix_y)
        
        self.build_K()
    
    elif camera.lower() == 'sentinel2granule':

        """
        Trying to make a camera that would represent an interpolated 10x10 Sentinel granule. 

        10x10 m
        256x256 pixels
        """
        print('SHOULD READING CCD PARAMETERS FROM MODULE')
        print('SHOULD READING CCD PARAMETERS FROM MODULE')

        s2_altitude = 786*1000 # m
        my_delta    = 10 # m

        self._npix_x = 256 # Arbirtary
        self._npix_y = 256 # Arbirtary

        self._c_x = self._npix_x/2 # Middle it!
        self._c_y = self._npix_y/2 # Middle it!
        
        self._fx_pix = s2_altitude/my_delta
        self._fy_pix = s2_altitude/my_delta
        
        self.build_K()

    elif camera.lower() == 'rascle2017':

        """
        Camera was a JAI BM-500GE panchromatic. This has a 2/3 sensor (8.8 x 6.6 mm) and a 5 mm focal length.

        """
        print('SHOULD READING CCD PARAMETERS FROM MODULE')
        print('SHOULD READING CCD PARAMETERS FROM MODULE')

        f_mm = camera_options.pop('f_mm', 5)
        self._f_mm = f_mm

        # 40.89 Mpx 
        self._npix_x = 2536 # 
        self._npix_y = 2068 # 

        self._c_x = self._npix_x/2 # Middle it!
        self._c_y = self._npix_y/2 # Middle it!
        
        # 2/3 sensor
        self._sensor_width_mm  = 8.8 
        self._sensor_height_mm = 6.6

        self._fx_pix = self._f_mm/(self._sensor_width_mm/self._npix_x)
        self._fy_pix = self._f_mm/(self._sensor_height_mm/self._npix_y)
        
        self.build_K()

    elif camera.lower() == 'workswell_wirspro':

        '''Workswell CCD parameters:
            - CCD size: 1.088 x 0.8705 cm
            - CCD resolution: 640 x 512 px
            - Pixel size: 17 x 17 um
            - Focal length: 19 mm
            EXIF:ImageWidth                                                                   640
            EXIF:ImageHeight                                                                  512
            EXIF:FocalLength                                                                   19
            EXIF:FocalPlaneXResolution                                                 588.235294
            EXIF:FocalPlaneYResolution                                                 588.505747
        '''

        kappa_pre_rotation = camera_options.pop('kappa_pre_rotation', 0) 
        ccd_params = get_ccd_properties(camera, kappa_pre_rotation)

        print(ccd_params)

        self._npix_x = ccd_params['npix_x'] 
        self._npix_y = ccd_params['npix_y'] 
        self._sensor_width_mm  = ccd_params['sensor_width']
        self._sensor_height_mm = ccd_params['sensor_height']

        # self._f_mm = 19
        self._f_mm = camera_options.pop('f_mm', 19) # I believe we have 9 and 19 mm focal lengths
        # self._f_mm = camera_options.pop('f_mm', 9) # I believe we have 9 and 19 mm focal lengths
        self._c_x = camera_options.pop('c_x', self._npix_x/2) # If no input, middle it!
        self._c_y = camera_options.pop('c_y', self._npix_y/2) # If no input, middle it!

        self._fx_pix = self._f_mm/(self._sensor_width_mm/self._npix_x)
        self._fy_pix = self._f_mm/(self._sensor_height_mm/self._npix_y)
        
        # print(f'Using c_x = {self._c_x}')
        # print(f'Using c_y = {self._c_y}')
        self.build_K()

    elif camera.lower() == 'normalised':
        """ For the normalised camera we only need the numbers of pixels.
        """
        
        print('SHOULD READING CCD PARAMETERS FROM MODULE')
        print('SHOULD READING CCD PARAMETERS FROM MODULE')

        self._npix_x = camera_options['npix_x'] 
        self._npix_y = camera_options['npix_y'] 

        self._f_mm = camera_options.pop('f_mm', 1)

        self._c_x = camera_options.pop('c_x', self._npix_x/2) # If no input, middle it!
        self._c_y = camera_options.pop('c_y', self._npix_y/2) # If no input, middle it!

        self._sensor_width_mm = camera_options.pop('_sensor_width_mm', self._npix_x) # If no input, middle it!
        self._sensor_height_mm = camera_options.pop('_sensor_width_mm', self._npix_y) # If no input, middle it!

        self._fx_pix = self._f_mm/(self._sensor_width_mm/self._npix_x)
        self._fy_pix = self._f_mm/(self._sensor_height_mm/self._npix_y)
        
        self.build_K()

    elif camera.lower() == 'custom':
        """ HERE WE SPECIFY K, and image size

        This is silly I should just allow post setting of K but whatever
        """

        self._f_mm = np.nan 

        self._sensor_width_mm = np.nan 
        self._sensor_height_mm = np.nan 
        
        self._npix_x = camera_options['image_sive_cv'][0] # This is the open cv convention of (nx, ny)
        self._npix_y = camera_options['image_sive_cv'][1] # This is the open cv convention of (nx, ny)
        
        K = camera_options['K'] 
        self.K       = K 
        self._c_x    = K[0,2]
        self._c_y    = K[1,2] 
        self._fx_pix = K[0,0] 
        self._fy_pix = K[1,1] 

    else:
        
        raise(Exception(f"Camera '{camera}' not recognised"))
        