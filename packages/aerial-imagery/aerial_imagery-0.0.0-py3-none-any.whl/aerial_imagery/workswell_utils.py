import glob
import pandas as pd
import geopandas as gpd
import exiftool
import intake
import os

from pathlib import Path


# Conditionally add exiftool to path
# EXIF_TOOL = '/group/pawsey0106/exiftool'
EXIF_TOOL = r'/home/andrew/Image-ExifTool-12.69'
# EXIF_TOOL = '/home/bra467/Image-ExifTool-12.63'

EXIF_TOOL_full = r'/home/andrew/Image-ExifTool-12.69/exiftool'

if not os.path.exists(EXIF_TOOL):
    raise FileNotFoundError(f'ExifTool not found at {EXIF_TOOL}. Must reset this hard code in the script.')

current_path = os.environ["PATH"]
if EXIF_TOOL not in current_path:
    os.environ["PATH"] += os.pathsep + EXIF_TOOL

try:
    exiftool.ExifTool(EXIF_TOOL_full)
except(PermissionError):
    raise PermissionError(f'ExifTool executable at {EXIF_TOOL_full} does not have appropriate permissions. Update this to continue [i.e. chmod 777 {EXIF_TOOL_full}]')
except:
    raise Exception(f'Unknown error running ExifTool')

def load_metadata(image_root,
                  image_extension='tiff',
                  longitude='Composite:GPSLongitude',
                  latitude='Composite:GPSLatitude',
                  altitude='Composite:GPSAltitude',
                  time='Composite:SubSecDateTimeOriginal',
                  time_fmt='%Y:%m:%d %H:%M:%S.%f',
                  timezone_offset=8,
                  SOURCE_EPSG='EPSG:4979',
                  TARGET_EPSG='EPSG:7850+9458',
                  original_root=None):
    
    if isinstance(image_root, str):
        print("The image_root path is a string, converting to pathlib.Path.")
        image_root = Path(image_root)

    elif isinstance(image_root, Path):
        print("The path is a Path object, all good.")
    else:
        raise(Exception('Unrecognised input type '))

    exif_data = image_root / 'ExifData.csv'
    
    if os.path.exists(exif_data):
        print('Found pre-existing exif data (ExifData.csv) so we are just goint to load this')
        df_meta = pd.read_csv(exif_data)
        print(f'Loaded {exif_data}')
    else:
        image_paths = sorted(glob.glob(f"{image_root}/**/*.{image_extension}",recursive=True))
        print(f'Found {len(image_paths)} images')
        with exiftool.ExifTool(EXIF_TOOL_full) as et:
            print('Parsing exif data')
            metadata = et.execute_json(*image_paths)
            df_meta  = pd.DataFrame(metadata)
            df_meta.to_csv(exif_data)
            print(f'Exif data saved to {exif_data}')
            
    print(df_meta[time][0])
    df_meta['photo_time'] = pd.to_datetime(df_meta[time],format=time_fmt)
    df_meta['photo_time'] = df_meta['photo_time']-pd.to_timedelta(timezone_offset,'h')
    df_meta=df_meta.set_index('photo_time')
    
    import pyproj
    from pyproj.transformer import Transformer, TransformerGroup
    from pyproj.crs import CRS

    pyproj.network.set_network_enabled(active=True)
    print(f'PYPROJ Network Enabled?: {pyproj.network.is_network_enabled()}')
    
    t = Transformer.from_crs(CRS(SOURCE_EPSG).to_3d(),
                              CRS(TARGET_EPSG).to_3d(),
                              always_xy=True)
    
    if longitude in df_meta:
        df_meta['CAMERA:Easting(m)'], df_meta['CAMERA:Northing(m)'], df_meta['CAMERA:Height(m)'] = t.transform(df_meta[longitude],df_meta[latitude],df_meta[altitude])
        
        gdf = gpd.GeoDataFrame(df_meta, geometry=gpd.points_from_xy(x=df_meta['CAMERA:Easting(m)'], 
                                                                    y=df_meta['CAMERA:Northing(m)'], 
                                                                    z=df_meta['CAMERA:Height(m)'],
                                                                    crs = TARGET_EPSG))
        
        if original_root is not None:
            # Patch in new image_root paths, replacing original_root
            gdf = gdf.replace(to_replace=f'\b{original_root}\b', value=image_root, regex=True)
    else:
        print('This data is not geotagged')
        gdf = gpd.GeoDataFrame(df_meta)

    return gdf