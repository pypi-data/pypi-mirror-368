# LEOHS: Landsat ETM+ OLI Harmonization Script
# Copyright (C) 2025 Galen Richardson
# This file is licensed under GPL-3.0-or-later
# Related Publication: https://doi.org/10.1080/10106049.2025.2538108
import warnings,joblib
import geopandas as gpd
import pandas as pd
from importlib.resources import files
from datetime import datetime
from .io import SR_TOA_geeNames, time_tracker,split_gdf_into_equal_parts
from .wrs import create_overlap_df
from .points import create_sampling_points
from .sampling import create_big_gdf
from .regression import process_all_regressions
def get_internal_wrs_path():
    wrs_file = files('leohs.data').joinpath('WRS_overlaps.shp')
    return str(wrs_file)  # or: wrs_file.as_posix()
def run_leohs(Aoi_shp_path, Save_folder_path, SR_or_TOA, months, years, sample_points_n, shp=False, Deep=True,
              maxCloudCover=50,Regression_types=["OLS"], CFMask_filtering=True, Water=True, Snow=True,project_ID=None):
    import ee,os
    from importlib.metadata import version
    pkg_version = version("leohs")
    if project_ID != None:
        ee.Initialize(project=project_ID)
    else:
        ee.Initialize()
    warnings.filterwarnings("ignore")
    wrs_shp_path = get_internal_wrs_path() #get the wrs path from internal
    logs=[]
    logs.append(f"LEOHS version {pkg_version}")
    print(f'Running leohs {pkg_version}')
    total_start=datetime.now()
    logs.append(f"LEOHS start time: {total_start.strftime('%Y-%m-%d %H:%M:%S')}")
    num_cores=min(joblib.cpu_count(), 16) - 2
    core_print_statement=f'Number of cores: {joblib.cpu_count()}, running on {num_cores} cores (max 14)'
    print(core_print_statement)
    logs.append(core_print_statement)
    LS7, LS8=SR_TOA_geeNames(SR_or_TOA)
    Max_img_samples,Pixel_difference=10,1
    # Step 1: Create WRS grid
    overlap_df, frequency_gdf, full_AOI, logs = create_overlap_df(Aoi_shp_path, wrs_shp_path, Save_folder_path,SR_or_TOA, LS7, LS8,
                                                                  months,years,maxCloudCover,num_cores,logs,project_ID)
    # Step 2: Create sampling points
    Sample_points_gdf, overlap_points_gdf, logs = create_sampling_points(full_AOI, sample_points_n, frequency_gdf, num_cores, logs)
    # Step 3: Sample pixel values
    print('Sampling points in GEE imagery')
    t_sampling = datetime.now()
    if Deep == False:
        big_gdf, logs = create_big_gdf(overlap_points_gdf, overlap_df, Max_img_samples, LS7, LS8, num_cores,
                                 CFMask_filtering, Water, Snow, Pixel_difference, logs,project_ID)
        if big_gdf is not None or not big_gdf.empty:
            print('No valid pixels were sampled, consider changing LEOHS parameters')
    if Deep == True:
        big_gdf,n = gpd.GeoDataFrame(),1
        gdfs = split_gdf_into_equal_parts(overlap_points_gdf, num_parts=10)
        for overlap_points_gdf in gdfs:
            big_gdf_part, logs = create_big_gdf(overlap_points_gdf, overlap_df, Max_img_samples, LS7, LS8,
                                           num_cores,CFMask_filtering, Water, Snow, Pixel_difference, logs,project_ID)
            if big_gdf_part is not None or not big_gdf_part.empty:
                big_gdf = pd.concat([big_gdf, big_gdf_part], ignore_index=True)
        if big_gdf is not None or not big_gdf.empty:
            print('No valid pixels were in a chunk, consider changing LEOHS parameters')
    logs.append(f"Number of unique image pairs used: {big_gdf['L7_image_id'].nunique()}")
    logs.append(f"Number of sampled pixels in GEE for models: {len(big_gdf)}")
    logs.append(f"Pixel sampling and filtering completed in {time_tracker(t_sampling)}")
    print(f"GEE pixel sampling completed")
    dtype = SR_or_TOA.upper()
    big_gdf.to_csv(os.path.join(Save_folder_path, f"{dtype}_Landsatsamples.csv"),index=False)
    if shp == True:
        big_gdf.to_file(os.path.join(Save_folder_path, f"{dtype}_Landsatsamples.shp"), driver='ESRI Shapefile')
        logs.append(f"Shapefile of sampled pixels created")
    # Step 4: Run regressions
    logs = process_all_regressions(big_gdf, Regression_types, num_cores, Save_folder_path,SR_or_TOA, logs)
    #Finishing up
    total_time = time_tracker(total_start)# Logging
    logs.append(f"Total run time: {total_time}")
    with open(os.path.join(Save_folder_path,f'{SR_or_TOA.upper()}_LEOHS_harmonization.txt'), 'a') as file:
        file.write("\n=== LEOHS Processing Log ===")
        for line in logs:
            file.write("\n"+line)
    print(f"Logs have been saved to {Save_folder_path}, Total run time: {total_time} ")