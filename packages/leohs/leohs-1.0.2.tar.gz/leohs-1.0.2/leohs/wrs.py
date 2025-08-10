# LEOHS: Landsat ETM+ OLI Harmonization Script
# Copyright (C) 2025 Galen Richardson
# This file is licensed under GPL-3.0-or-later
# Related Publication: https://doi.org/10.1080/10106049.2025.2538108
import geopandas as gpd
from shapely.geometry import shape, mapping, box
import pandas as pd
import numpy as np
import ee,geemap
from joblib import Parallel, delayed
from datetime import datetime
from .io import create_save_path,time_tracker

def create_WRS_gdf(input_shp, WRS_shapefile,Save_folder_path,logs):
    create_save_path(Save_folder_path,logs)
    #this creates a gdf of only WRS tiles found in the shapefile
    full_AOI=gpd.read_file(input_shp)
    full_AOI["geometry"] = full_AOI["geometry"].apply(lambda g: shape(mapping(g)))
    full_AOI=full_AOI.to_crs('EPSG:4326')  # Ensure CRS is set to EPSG:4326
    full_AOI['geometry']=full_AOI.geometry.buffer(0)
    wrsgdf=gpd.read_file(WRS_shapefile)
    wrsgdf=wrsgdf.to_crs('EPSG:4326')
    wrsgdf['geometry']=wrsgdf.geometry.buffer(0)
    overlap_wrs=gpd.sjoin(wrsgdf,full_AOI,how="inner",predicate='intersects')
    df_subset=overlap_wrs[['row1','path1','path2','geometry']].reset_index(drop=True)
    return df_subset,full_AOI
def split_aoi_into_strips(gdf, max_area=1e13):
    projected_gdf=gdf.to_crs('EPSG:8857')  # Project to equal area for calculation
    total_area=projected_gdf.geometry.area.sum()  # Calculate area
    if total_area<max_area:
        print('No need for splitting AOI -- Proceeding.')
        return gdf, None
    minx,miny,maxx,maxy=gdf.total_bounds
    midy=(miny+maxy)/2  # Calculate the midpoint y-coordinate, make upper and lower strips
    upper_strip,lower_strip=box(minx,midy,maxx,maxy),box(minx,miny,maxx,midy)
    upper_gdf=gpd.overlay(gdf,gpd.GeoDataFrame(geometry=[upper_strip],crs='EPSG:4326'),how='intersection')
    lower_gdf=gpd.overlay(gdf,gpd.GeoDataFrame(geometry=[lower_strip],crs='EPSG:4326'),how='intersection')
    num_strips=int(np.ceil(total_area/max_area))# Determine the number of strips needed based on the area
    strips=[]
    strip_width=(maxx-minx)/num_strips
    for i in range(num_strips):
        strip_minx=minx+i*strip_width
        strip_maxx=minx+(i+ 1)*strip_width
        upper_vertical_strip=box(strip_minx, midy, strip_maxx, maxy)# Process upper strip
        upper_strip_gdf=gpd.overlay(upper_gdf, gpd.GeoDataFrame(geometry=[upper_vertical_strip], crs='EPSG:4326'), how='intersection')
        strips.append(upper_strip_gdf)
        lower_vertical_strip=box(strip_minx, miny, strip_maxx, midy)# Process lower strip
        lower_strip_gdf=gpd.overlay(lower_gdf, gpd.GeoDataFrame(geometry=[lower_vertical_strip], crs='EPSG:4326'), how='intersection')
        strips.append(lower_strip_gdf)
    strips=[df for df in strips if not df.empty]
    print(f'{len(strips)} Strips created due to input AOI size -- Proceeding.')
    return gdf, strips
def date_cloud_aoi_filter(Landsatcollection,month,year,maxCloudCover,aoi):
    return Landsatcollection\
    .filter(ee.Filter.calendarRange(month, month, 'month')).filter(ee.Filter.calendarRange(year, year, 'year')) \
    .filter(ee.Filter.lte('CLOUD_COVER',maxCloudCover))\
    .filterBounds(aoi)
def get_image_names(image_collection):
    image_ids=image_collection.aggregate_array('system:id').getInfo()
    return image_ids
def extract_date_path_row(image_id):
    date_str=image_id.split('_')[-1]#used to extract date,path,row from landsat image name
    row,path=int(image_id.split('_')[-2][3:6]),int(image_id.split('_')[-2][:3])
    return datetime.strptime(date_str,'%Y%m%d'),row,path
def process_names(image_names):
    name_list=[]
    df=None #process the names and make a df from list of image names
    for name in image_names:
        date, row, path=extract_date_path_row(name)
        detailed_name=[name,date, row, path]
        name_list.append(detailed_name)
        df=pd.DataFrame(name_list)
        df.columns=['id', 'date', 'row','path']
        df[['row', 'path']]=df[['row', 'path']].astype(int)
    if df is not None:
        return df
def cycle_through_image_names(LS7, LS8,months,years,maxCloudCover, aoi):
    aoi=geemap.geopandas_to_ee(aoi)
    matching_pairs=[]
    for year in years:
        for month in months:
            LS7_SR=date_cloud_aoi_filter(ee.ImageCollection(LS7),month,year,maxCloudCover,aoi)  # filter date, cloud, aoi
            LS8_SR=date_cloud_aoi_filter(ee.ImageCollection(LS8),month,year,maxCloudCover,aoi)
            LS7_names,LS8_names=get_image_names(LS7_SR),get_image_names(LS8_SR)  # get names of all the images that are within the filter
            LS7_df,LS8_df=process_names(LS7_names), process_names(LS8_names)  # process the names using string manipulation and make into a df
            if LS7_df is not None and not LS7_df.empty and LS8_df is not None and not LS8_df.empty:  # not empty dfs or ones that do not exist
                for index_LS7, row_LS7 in LS7_df.iterrows():
                    # Find rows in LS8_df with the same 'row' and 'path' within +1 or -1, and date within 1 day
                    possible_1row_matches=LS8_df[(LS8_df['row']==row_LS7['row']) &
                        ((LS8_df['path']==row_LS7['path'] + 1) | (LS8_df['path']==row_LS7['path'] - 1)) &
                        (abs(LS8_df['date']-row_LS7['date']).dt.days<= 1)]  # this is the formula for finding matches
                    for index_LS8, row_LS8 in possible_1row_matches.iterrows():
                        matching_pairs.append({'LS7_id': row_LS7['id'], 'LS7_date': row_LS7['date'], 'LS7_row': row_LS7['row'], 'LS7_path': row_LS7['path'],
                                               'LS8_id': row_LS8['id'], 'LS8_date': row_LS8['date'], 'LS7_row': row_LS8['row'], 'LS8_path': row_LS8['path']})
                    # Find rows in LS8_df with same 'row' and edge paths within +1 or -1 date
                    possible_edge_matches=LS8_df[(LS8_df['row']==row_LS7['row']) &
                        ((LS8_df['path']==row_LS7['path'] + 232) | (LS8_df['path']==row_LS7['path'] - 232)) &
                        (abs(LS8_df['date']-row_LS7['date']).dt.days<= 1)]  # this is the formula for finding matches
                    for index_LS8, row_LS8 in possible_edge_matches.iterrows():
                        matching_pairs.append({'LS7_id': row_LS7['id'], 'LS7_date': row_LS7['date'], 'LS7_row': row_LS7['row'], 'LS7_path': row_LS7['path'],
                                               'LS8_id': row_LS8['id'], 'LS8_date': row_LS8['date'], 'LS8_row': row_LS8['row'], 'LS8_path': row_LS8['path']})
    return matching_pairs
def chunk_list(lst,n):
    avg, out, last=len(lst) / float(n),[],0.0 #Divide a list into `n` chunks.
    while last<len(lst):
        out.append(lst[int(last):int(last + avg)])
        last+=avg
    return out
def process_strip_chunk(LS7,LS8,months,years,maxCloudCover,strips_chunk,chunk_index,project_ID):
    all_matching_pairs=[]
    if project_ID != None:
        ee.Initialize(project=project_ID)
    else:
        ee.Initialize()
    for strip_n,strip in enumerate(strips_chunk):
        matching_pairs=cycle_through_image_names(LS7,LS8,months,years,maxCloudCover,strip)
        all_matching_pairs.extend(matching_pairs)
    return all_matching_pairs
def create_overlap_df(Aoi_shp_path, wrs_shp_path, Save_folder_path,SR_or_TOA,LS7,LS8,
                      months,years,maxCloudCover,num_cores,logs,project_ID):
    t0 = datetime.now()
    logs.append(f"Processing {SR_or_TOA.upper()} imagery")
    WRS_gdf, full_AOI = create_WRS_gdf(Aoi_shp_path, wrs_shp_path, Save_folder_path,logs)
    full_AOI, strips = split_aoi_into_strips(full_AOI)
    LS7, LS8=ee.ImageCollection(LS7),ee.ImageCollection(LS8)
    if strips is None:
        logs.append(f"Processing overlap search without using strips")
        matching_pairs=cycle_through_image_names(LS7, LS8,months,years,maxCloudCover,full_AOI)
        overlap_df=pd.DataFrame(matching_pairs)
    else:
        logs.append(f"Processing overlap search using {len(strips)} strips")
        chunks=chunk_list(strips, num_cores)# Split the strips list into smaller chunks for parallel processing
        results=Parallel(n_jobs=num_cores)(
            delayed(process_strip_chunk)(LS7,LS8,months,years,maxCloudCover, chunk, idx, project_ID) for idx, chunk in enumerate(chunks))
        all_matching_pairs=[pair for result in results for pair in result]# Combine results from all chunks
        overlap_df=pd.DataFrame(all_matching_pairs)
        overlap_df.drop_duplicates(inplace=True)
    print(f"GEE Image filtering completed")
    if overlap_df.empty:
        print("No matches available.\nTry either a larger AOI, different date, or a different maximum cloud cover.")
        return None, None
    grouped_df=overlap_df.groupby(['LS7_row','LS7_path','LS8_path']).size().reset_index(name='count_gee')#create frequency_GDF
    frequency_gdf=pd.merge(grouped_df, WRS_gdf, left_on=['LS7_row','LS7_path','LS8_path'], right_on=['row1','path1','path2'], how='inner')
    if frequency_gdf.empty:
        print("No matches available. \n Failed to join images to WRS index")
        return None, None
    frequency_gdf=gpd.GeoDataFrame(frequency_gdf,geometry='geometry')
    frequency_gdf.crs='EPSG:4326'
    frequency_gdf = frequency_gdf.drop_duplicates(subset='geometry')#get rid of duplicates
    logs.append(f"Number of image pairs available: {len(overlap_df)}")
    logs.append(f"Image overlap dataframe created in {time_tracker(t0)}")
    return overlap_df,frequency_gdf,full_AOI,logs