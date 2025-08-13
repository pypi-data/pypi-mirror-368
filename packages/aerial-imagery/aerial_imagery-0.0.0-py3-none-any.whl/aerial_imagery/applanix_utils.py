import pandas as pd
import numpy as np
import warnings


# def parse_applanix_export(file_path, skiprows=34):
#     """
#     Parses the Applanix export file and returns a DataFrame.
    
#     Confirmed to work for the "ASCII" format in PosPac MMS v9.0

#     Args:
#         file_path (str): Path to the exterior orientation file.
        
#     Returns:
#         pd.DataFrame: DataFrame containing the parsed data.
#     """
#     col_names = pd.read_csv(file_path, skiprows=skiprows, nrows=1, header=None).iloc[0].tolist()
#     print(col_names)

#     col_names = [col.strip() for col in col_names][0::]
#     # col_names = [col.strip() for col in col_names][1::]
#     print(col_names)

#     # Check for duplicate column names and rename them
#     unique_names = []
#     for i, name in enumerate(col_names):
#         if name not in unique_names:
#             unique_names.append(name)
#         else:
#             n = np.sum(np.array(unique_names)==name)
#             col_names[i] = f"{name}_{n+1}"

#             print(f"Duplicate column name found: {name}")
        
#     unit_skip = 3  # Skip the nex few rows for units
#     df = pd.read_csv(file_path, skiprows=skiprows+unit_skip, delim_whitespace=True, names=col_names)
#     # df = pd.read_csv(file_path, skiprows=skiprows+10, delim_whitespace=True)
    
#     return df, col_names

# def parse_applanix_eo(file_path, skiprows=34):
#     """
#     Parses the Applanix exterior orientation and returns a DataFrame.
    
#     Confirmed to work for the "ASCII" format in PosPac MMS v9.0

#     Args:
#         file_path (str): Path to the exterior orientation file.
        
#     Returns:
#         pd.DataFrame: DataFrame containing the parsed data.
#     """
#     col_names = pd.read_csv(file_path, skiprows=skiprows, nrows=1, header=None).iloc[0].tolist()
#     print(col_names)

#     col_names = [col.strip() for col in col_names][0::]
#     # col_names = [col.strip() for col in col_names][1::]
#     print(col_names)

#     col_names = [c for c in col_names if c not in ['# EVENT']]
#     print(col_names)

#     col_names = np.array(col_names)
#     col_names[col_names=='TIME (s)'] = 'TIME'

#     # Check for duplicate column names and rename them
#     unique_names = []
#     for i, name in enumerate(col_names):
#         if name not in unique_names:
#             unique_names.append(name)
#         else:
#             n = np.sum(np.array(unique_names)==name)
#             col_names[i] = f"{name}_{n+1}"

#             print(f"Duplicate column name found: {name}")
        
#     unit_skip = 3  # Skip the nex few rows for units
#     df = pd.read_csv(file_path, skiprows=skiprows+unit_skip, delim_whitespace=True, names=col_names)
#     # df = pd.read_csv(file_path, skiprows=skiprows+10, delim_whitespace=True)
    
#     return df, col_names

def parse_and_check_applanix(eo_file, ex_file):
    """
    Parse the Applanix EO and Export files and check for consistency.
    """
    ds_eo, col_names_eo, metadata_eo = parse_applanix_eo(eo_file)
    ds_ex, col_names_ex, metadata_ex = parse_applanix_export(ex_file)

    needed = {}
    needed['first_rotation'] = "First rotation is about the 'x' axis by the 'omega' angle."
    needed['second_rotation'] = "Second rotation is about the 'y' axis by the 'phi' angle."
    needed['third_rotation'] = "Third rotation is about the 'z' axis by the 'kappa' angle."
    needed['kappa_cardinal_rotation'] = 0
    needed['boresight_tx'] = 0
    needed['boresight_ty'] = 0
    needed['boresight_tz'] = 0
    needed['lever_arm_lx'] = 0
    needed['lever_arm_ly'] = 0
    needed['lever_arm_lz'] = 0
    needed['output_shift_X'] = 0
    needed['output_shift_Y'] = 0
    needed['output_shift_Z'] = 0
    
    for key, value in needed.items():
        assert metadata_eo[key] == value, f"Metadata mismatch for {key}: {metadata_eo[key]} != {value}"

    needed = {}
    needed['boresight_tx'] = 0
    needed['boresight_ty'] = 0
    needed['boresight_tz'] = 0
    needed['lever_arm_lx'] = 0
    needed['lever_arm_ly'] = 0
    needed['lever_arm_lz'] = 0
    
    for key, value in needed.items():
        assert metadata_ex[key] == value, f"Metadata mismatch for {key}: {metadata_ex[key]} != {value}"

    # Check if various fields are close, noting files have different numbers of DPs. 
    match_fields = ['TIME', 'EASTING', 'NORTHING', 'ELLIPSOID HEIGHT']
    for field in match_fields:
        assert np.isclose(ds_eo[field].values, ds_ex[field].values).all(), f"Field {field} doesn't match between export and EO files"
        print(f"Field {field} matches between export and EO files, setting EXPORT data to match EO EXACTLY")
        ds_eo[field] = ds_ex[field]
    
    df = pd.merge(ds_eo.to_pandas(), ds_ex.to_pandas(), on=match_fields, how='inner')
    
    ds = df.to_xarray()
    for attr in ds_ex.attrs:
        ds.attrs['EXPORT_'+attr] = ds_ex.attrs[attr]
    for attr in ds_eo.attrs:
        ds.attrs['EO_'+attr] = ds_eo.attrs[attr]

    return ds


def parse_applanix_eo(file_path):
    """
    Parses the Applanix exterior orientation and returns a DataFrame.
    
    Confirmed to work for the "ASCII" format in PosPac MMS v9.0

    Args:
        file_path (str): Path to the exterior orientation file.
        
    Returns:
        pd.DataFrame: DataFrame containing the parsed data.
    """

    header_rows = 34
    metadata = {}
    print('Reading headers from file:', file_path) 
    ################################ 
    ##### THIS IS GROSS BUT IT WORKS.
    ################################ 
    with open(file_path, 'r') as file:
        for i in np.arange(header_rows):
            line = file.readline().strip()
            print(line)  # Use .strip() to remove newline characters
            if i == 1:
                ps = 'POS Exterior Orientation Computation Utility'
                assert line.startswith(ps), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                if not line.endswith('Version  9.0'):
                    v = line.split(' ')[-1]
                    warnings.warn(f"This appears to be from version {v}. This has only been tested for PosPac MMS V9.0", UserWarning)
            if i == 9:
                assert line.startswith('Event time shift:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                metadata['event_time_shift'] = float(line.split(':')[1].split(' ')[1].strip())
            
            # Skip the event file stuff as we don't use it. 
            # if i == 14:
            #     assert line.startswith('Mission Start Time:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
            # if i == 15:
            #     assert line.startswith('Date of Mission:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
            #     metadata['mission_start_date'] = line.split(':')[1].strip()
            # if i == 16:
            #     assert line.startswith('Start Time:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
            #     metadata['mission_start_time'] = line.split(':')[1].strip()

            # Mapping stuff now
            if i == 14:
                assert line.startswith('Mapping frame epoch:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                metadata['mapping_frame_epoch'] = line.split(':')[1].strip()      
            if i == 15:
                assert line.startswith('Mapping frame datum:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                left, right, _ = line.split(';')
                metadata['mapping_frame_datum']      = left.split(':')[1].strip()       
                assert right.strip().startswith('Mapping frame projection :'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                metadata['mapping_frame_projection'] = right.split(':')[1].strip()     
            if i == 16:
                assert line.startswith('central meridian'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                metadata['central_meridian'] = float(line.split('=')[1].split(' ')[1].strip())
            if i == 17:
                assert line.startswith('latitude of the grid origin'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                left, right,  = line.split(';')
                left = left.split('=')[1].strip()
                left = left.split(' ')
                metadata['grid_origin_latitude']       = float(left[0])
                metadata['grid_origin_latitude_units'] = left

                assert right.strip().startswith('grid scale factor'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                right = right.split('=')[1].strip()
                right = right.split(':')[0].strip()
                metadata['grid_scale_factor']       = float(right)
            if i == 18:
                assert line.startswith('false easting'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                left, right, _  = line.split(';')
                left = left.split('=')[1].strip()
                left = left.split(' ')
                metadata['false_easting']       = float(left[0])
                metadata['false_easting_units'] = left[1]
                
                assert right.strip().startswith('false northing'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                right = right.split('=')[1].strip()
                right = right.split(' ')
                metadata['false_northing']       = float(right[0])
                metadata['false_northing_units'] = right[1]
            
            # ROTATION SEQUENCE stuff now
            if i == 19:
                assert line.startswith('Sequence of the rotation from mapping to image frame:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
        
            if i == 20:
                assert line.startswith('First rotation is about the '), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                metadata['first_rotation'] = line
            if i == 21:
                assert line.startswith('Second rotation is about the '), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                metadata['second_rotation'] = line
            if i == 22:
                assert line.startswith('Third rotation is about the '), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                metadata['third_rotation'] = line
            if i == 23:
                assert line.startswith('Kappa cardinal rotation'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                line = line.split(':')[1].strip()
                metadata['kappa_cardinal_rotation'] = float(line[0])
                metadata['kappa_cardinal_rotation_units'] = line[1]

            # BORESIGHT stuff now
            if i == 24:
                assert line.startswith('Boresight values'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                line = line.split(':')[1].strip()
                line = line.split(',')
                for i, t in enumerate(['tx', 'ty', 'tz']):
                    part = line[i].split('=')
                    assert part[0].strip().startswith(t), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                    dataunit = part[1].strip().split(' ')
                    data = dataunit[0]
                    unit = "".join(dataunit[1::])
                    metadata[f'boresight_{t}'] = float(data.strip())
                    metadata[f'boresight_{t}_units'] = unit.strip()
            if i == 25:
                assert line.startswith('Lever arm values'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                line = line.split(':')[1].strip()
                line = line.split(',')
                for i, t in enumerate(['lx', 'ly', 'lz']):
                    part = line[i].split('=')
                    assert part[0].strip().startswith(t), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                    dataunit = part[1].strip().split(' ')
                    data = dataunit[0]
                    unit = "".join(dataunit[1::])
                    metadata[f'lever_arm_{t}'] = float(data.strip())
                    metadata[f'lever_arm_{t}_units'] = unit.strip()

            # OUTPUT SHIFT now
            if i == 26:
                assert line.startswith('Shift values'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                line = line.split(':')[1].strip()
                line = line.split(',')
                for i, t in enumerate(['X', 'Y', 'Z']):
                    part = line[i].split('=')
                    assert part[0].strip().startswith(t), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                    data, unit = part[1].strip().split(' ')
                    metadata[f'output_shift_{t}'] = float(data.strip())
                    metadata[f'output_shift_{t}_units'] = unit.strip()

            if i == 29:
                assert line.startswith('POS/AV Computed Data at Camera Perspective Centre'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
            if i == 30:
                assert line.startswith('Grid:'), "File does not appear to be a valid PosPac MMS v9.0 EO file."
                line = line.split(';')
                print(line)
                assert len(line)>=4, "File does not appear to be a valid PosPac MMS v9.0 EO file."
                line = line[0:4]
                for part in line:
                    desc, value = part.split(':')
                    desc = desc.strip()
                    value = value.strip()
                    metadata[f'grid_{desc}'] = value


    print('Reading columns from file:', file_path)

    col_names = pd.read_csv(file_path, skiprows=header_rows, nrows=1, header=None).iloc[0].tolist()
    print(col_names)

    col_names = [col.strip() for col in col_names][0::]
    # col_names = [col.strip() for col in col_names][1::]
    print(col_names)

    col_names = [c for c in col_names if c not in ['# EVENT']]
    print(col_names)

    col_names = np.array(col_names)
    col_names[col_names=='TIME (s)'] = 'TIME'

    # Check for duplicate column names and rename them
    unique_names = []
    for i, name in enumerate(col_names):
        if name not in unique_names:
            unique_names.append(name)
        else:
            n = np.sum(np.array(unique_names)==name)
            col_names[i] = f"{name}_{n+1}"

            print(f"Duplicate column name found: {name}")
        
    unit_skip = 3  # Skip the nex few rows for units
    df = pd.read_csv(file_path, skiprows=header_rows+unit_skip, delim_whitespace=True, names=col_names)
    # df = pd.read_csv(file_path, skiprows=skiprows+10, delim_whitespace=True)
    
    ds = df.to_xarray()
    for metadata_key, metadata_value in metadata.items():
        ds.attrs[metadata_key] = metadata_value

    return ds, col_names, metadata


def parse_applanix_export(file_path):
    """
    Parses the Applanix export file and returns a DataFrame.
    
    Confirmed to work for the "ASCII" format in PosPac MMS v9.0

    Args:
        file_path (str): Path to the exterior orientation file.
        
    Returns:
        pd.DataFrame: DataFrame containing the parsed data.
    """
    
    header_rows = 24

    metadata = {}
    print('Reading headers from file:', file_path) 
    ################################ 
    ##### THIS IS GROSS BUT IT WORKS.
    ################################ 
    with open(file_path, 'r') as file:
        for i in np.arange(header_rows):
            line = file.readline().strip()
            # print(line)  # Use .strip() to remove newline characters
            if i == 1:
                assert line.startswith('POS Export Utility'), "File does not appear to be a valid PosPac MMS v9.0 export file."
            if i == 9:
                assert line.startswith('Event time shift:'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                metadata['event_time_shift'] = float(line.split(':')[1].split(' ')[1].strip())
            
            # Skip the event file stuff as we don't use it. 
            if i == 14:
                assert line.startswith('Mission Start Time:'), "File does not appear to be a valid PosPac MMS v9.0 export file."
            if i == 15:
                assert line.startswith('Date of Mission:'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                metadata['mission_start_date'] = line.split(':')[1].strip()
            if i == 16:
                assert line.startswith('Start Time:'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                metadata['mission_start_time'] = line.split(':')[1].strip()

            # Mapping stuff now
            if i == 17:
                assert line.startswith('Mapping frame epoch:'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                metadata['mapping_frame_epoch'] = line.split(':')[1].strip()      
            if i == 18:
                assert line.startswith('Mapping frame datum:'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                left, right, _ = line.split(';')
                metadata['mapping_frame_datum']      = left.split(':')[1].strip()       
                assert right.strip().startswith('Mapping frame projection :'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                metadata['mapping_frame_projection'] = right.split(':')[1].strip()     
            if i == 19:
                assert line.startswith('central meridian'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                metadata['central_meridian'] = float(line.split('=')[1].split(' ')[1].strip())
            if i == 20:
                assert line.startswith('latitude of the grid origin'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                left, right,  = line.split(';')
                left = left.split('=')[1].strip()
                left = left.split(' ')
                metadata['grid_origin_latitude']       = float(left[0])
                metadata['grid_origin_latitude_units'] = left

                assert right.strip().startswith('grid scale factor'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                right = right.split('=')[1].strip()
                right = right.split(':')[0].strip()
                metadata['grid_scale_factor']       = float(right)
            if i == 21:
                assert line.startswith('false easting'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                left, right, _  = line.split(';')
                left = left.split('=')[1].strip()
                left = left.split(' ')
                metadata['false_easting']       = float(left[0])
                metadata['false_easting_units'] = left[1]
                
                assert right.strip().startswith('false northing'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                right = right.split('=')[1].strip()
                right = right.split(' ')
                metadata['false_northing']       = float(right[0])
                metadata['false_northing_units'] = right[1]

            # BORESIGHT stuff now
            if i == 22:
                assert line.startswith('Boresight values'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                line = line.split(':')[1].strip()
                line = line.split(', ')
                for i, t in enumerate(['tx', 'ty', 'tz']):
                    part = line[i].split('=')
                    assert part[0].strip().startswith(t), "File does not appear to be a valid PosPac MMS v9.0 export file."
                    data, unit = part[1].strip().split(' ')
                    metadata[f'boresight_{t}'] = float(data.strip())
                    metadata[f'boresight_{t}_units'] = unit.strip()
            if i == 23:
                assert line.startswith('Lever arm values'), "File does not appear to be a valid PosPac MMS v9.0 export file."
                line = line.split(':')[1].strip()
                line = line.split(', ')
                for i, t in enumerate(['lx', 'ly', 'lz']):
                    part = line[i].split('=')
                    assert part[0].strip().startswith(t), "File does not appear to be a valid PosPac MMS v9.0 export file."
                    data, unit = part[1].strip().split(' ')
                    metadata[f'lever_arm_{t}'] = float(data.strip())
                    metadata[f'lever_arm_{t}_units'] = unit.strip()

    print('Reading columns from file:', file_path)
    col_names = pd.read_csv(file_path, skiprows=header_rows, nrows=1, header=None).iloc[0].tolist()
    # print(col_names)

    col_names = [col.strip() for col in col_names][0::]
    # col_names = [col.strip() for col in col_names][1::]
    # print(col_names)

    # Check for duplicate column names and rename them
    unique_names = []
    for i, name in enumerate(col_names):
        if name not in unique_names:
            unique_names.append(name)
        else:
            n = np.sum(np.array(unique_names)==name)
            col_names[i] = f"{name}_{n+1}"

            print(f"Duplicate column name found: {name}")
    
    print('Reading data from file:', file_path)
    unit_skip = 3  # Skip the nex few rows for units
    df = pd.read_csv(file_path, skiprows=header_rows+unit_skip, delim_whitespace=True, names=col_names)
    # df = pd.read_csv(file_path, skiprows=skiprows+10, delim_whitespace=True)
    
    ds = df.to_xarray()
    for metadata_key, metadata_value in metadata.items():
        ds.attrs[metadata_key] = metadata_value

    return ds, col_names, metadata

def parseUF(uncertainty_file):
    """
    Parsing our own uncertainty file format.
    """
    with open(uncertainty_file, 'r') as file:
            line = file.readline().strip()

            assert line == 'TIME,EASTING,NORTHING,ORTH HEIGHT,std(E)[m],std(N)[m],std(U)[m],std(H)[deg],std(P)[deg],std(R)[deg],#SV[],PDOP[],Xaccel[],Yaccel[],Zaccel,Xangrate[],Yangrate[],Zangrate[],X prim-ref lever[m],Y prim-ref lever[m],Z prim-ref lever[m]'

            lines = file.readlines()

    col_names = ['TIME', 'EASTING', 'NORTHING', 'ORTH HEIGHT','std_E', 'std_N', 'std_U', 'std_H', 'std_P', 'std_R',
                    'num_SV', 'PDOP', 'X_accel', 'Y_accel', 'Z_accel',
                    'X_angrate', 'Y_angrate', 'Z_angrate',
                    'X_prim_ref_lever', 'Y_prim_ref_lever', 'Z_prim_ref_lever']
    df_uncert = pd.read_csv(uncertainty_file, skiprows=1, delim_whitespace=False, names=col_names)
    df_uncert.set_index('TIME', inplace=True)

    return df_uncert
