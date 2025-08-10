# LEOHS: Landsat ETM+ OLI Harmonization Script
# Copyright (C) 2025 Galen Richardson
# This file is licensed under GPL-3.0-or-later
# Related Publication: https://doi.org/10.1080/10106049.2025.2538108
import os
import shutil
from datetime import datetime
import numpy as np

def SR_TOA_geeNames(SR_or_TOA):
    if SR_or_TOA.upper() == "SR":
        return "LANDSAT/LE07/C02/T1_L2","LANDSAT/LC08/C02/T1_L2"
    if SR_or_TOA.upper() == "TOA":
        return "LANDSAT/LE07/C02/T1_TOA","LANDSAT/LC08/C02/T1_TOA"
    else:
        print("Invalid entry")
def time_tracker(start_time):
    elapsed = int((datetime.now() - start_time).total_seconds())
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h: parts.append(f"{h}h")
    if m or h: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return ' '.join(parts)
def apply_correction_factors (LS7,LS8,gdf):
    if "TOA" in LS8 and "TOA" in LS7:
        return gdf
    elif "TOA" not in LS8 and "TOA" not in LS7:
        columns_to_transform=[col for col in gdf.columns if col not in ['LS7_image_id','LS8_image_id','geometry']]
        gdf[columns_to_transform]=gdf[columns_to_transform]*0.0000275 - 0.2
        return gdf
    else:
        print('ERROR!!! TOA and SR datasets selected')
def create_save_path(Save_folder_path,logs):
    if os.path.exists(Save_folder_path):
        i = 1
        old_path = f"{Save_folder_path}_old"
        while os.path.exists(old_path):
            old_path = f"{Save_folder_path}_old_{i}"
            i += 1
        shutil.move(Save_folder_path, old_path)
        logs.append(f"Renamed existing folder to: {old_path}")
        print(f"Renamed existing folder to: {old_path}")
    os.makedirs(Save_folder_path)
    return Save_folder_path
def split_gdf_into_equal_parts(Sample_points_gdf, num_parts=10):
    # Shuffle the GeoDataFrame
    shuffled_gdf = Sample_points_gdf.sample(frac=1).reset_index(drop=True)
    gdf_list = np.array_split(shuffled_gdf, num_parts)
    return gdf_list