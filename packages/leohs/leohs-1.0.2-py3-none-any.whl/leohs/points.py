# LEOHS: Landsat ETM+ OLI Harmonization Script
# Copyright (C) 2025 Galen Richardson
# This file is licensed under GPL-3.0-or-later
# Related Publication: https://doi.org/10.1080/10106049.2025.2538108
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio,random
from shapely.geometry import Point
from datetime import datetime
from rasterio.features import geometry_mask
from joblib import Parallel, delayed
from .io import time_tracker

def generate_equalA_points (AOI,points_n):
    AOI=AOI.to_crs('EPSG:8857')#make into equal earth projection for even global sampling
    transform=rasterio.transform.from_bounds(*AOI.total_bounds,10000,10000)#creates a raster grid
    mask=geometry_mask([geom for geom in AOI.geometry], transform=transform, invert=True, out_shape=(10000,10000))#creates masked raster grid
    rows, cols=np.where(mask)#Sample points from the mask raster grid
    random_indices=np.random.choice(len(rows), size=points_n, replace=False)
    sampled_rows,sampled_cols=rows[random_indices],cols[random_indices]
    x_coords, y_coords=rasterio.transform.xy(transform, sampled_rows, sampled_cols)
    points=[Point(x, y) for x, y in zip(x_coords, y_coords)]#Create points from the sampled coordinates
    points_gdf=gpd.GeoDataFrame(geometry=points, crs='EPSG:8857')
    print('Initial points generated, ensuring they are in WRS overlaps')
    return points_gdf
def find_nearest_polygon_and_generate_point(WRS_gdf, point):
    point = gpd.GeoSeries([point], crs=WRS_gdf.crs)#Ensure the point is in the same CRS as the polygons and AOI
    WRS_gdf['distance']=WRS_gdf['geometry'].distance(point.iloc[0])#Calculate the distance from the point to each polygon in WRS_gdf
    nearest_polygon=WRS_gdf.loc[WRS_gdf['distance'].idxmin()]['geometry']#Find the polygon with the minimum distance
    minx, miny, maxx, maxy=nearest_polygon.bounds #Generate a random point within the intersection polygon
    while True:
        random_point=Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if nearest_polygon.contains(random_point):
            return random_point
def process_points(aoi_points,overlap_gdf):
    overlap_gdf=overlap_gdf.to_crs('EPSG:8857')#Project to equal earth
    new_points=[]
    AOI_array=np.array([(point.x, point.y) for point in aoi_points.geometry])#Make AOI array for distance calculations
    for point_array in AOI_array:
        point=Point(point_array[0], point_array[1])
        if overlap_gdf.contains(point).any():
            new_points.append(point)#Append point if it is inside a WRS tile
        else:
            alt_point=find_nearest_polygon_and_generate_point(overlap_gdf, point)#If not, find closest alternative
            new_points.append(alt_point)#Append the alt point to the list directly
    return gpd.GeoDataFrame(geometry=new_points, crs='EPSG:8857')
def parallel_process_points(aoi_points,frequency_gdf,full_AOI,num_cores):
    full_AOI=full_AOI.to_crs('EPSG:8857')
    frequency_gdf=frequency_gdf.to_crs('EPSG:8857')
    clip_gdf=gpd.clip(frequency_gdf, full_AOI) #clipping frequency_gdf to AOI
    clip_gdf=clip_gdf.to_crs('EPSG:8857') # making it equal area
    clip_gdf=clip_gdf.explode().reset_index(drop=True) #removing multipolygons
    point_count=len(aoi_points)
    subset_size=max(point_count // num_cores, 1)
    aoi_subsets=[aoi_points.iloc[i:i + subset_size] for i in range(0, point_count, subset_size)]
    results=Parallel(n_jobs=num_cores)(
        delayed(process_points)(aoi_subset, clip_gdf) for aoi_subset in aoi_subsets)
    combined_gdf=gpd.GeoDataFrame(pd.concat(results, ignore_index=True))
    combined_gdf=combined_gdf.to_crs('EPSG:4326')#Convert back to WGS 84
    return combined_gdf
def create_overlap_points_gdf(points_gdf,WRS_gdf):
    points_gdf=points_gdf.to_crs(WRS_gdf.crs) #appends path/row information to points
    joined_gdf=gpd.overlay(points_gdf, WRS_gdf[['geometry','LS7_row','LS7_path','LS8_path']], how='intersection')# Perform the spatial join using 'overlap'
    joined_gdf=joined_gdf[['LS7_row','LS7_path','LS8_path','geometry']].drop_duplicates(subset='geometry') # Clean up the resulting GeoDataFrame
    return joined_gdf.reset_index(drop=True).drop_duplicates()
def create_sampling_points(full_AOI,sample_points_n,frequency_gdf,num_cores,logs):
    t0 = datetime.now()
    AOI_points=generate_equalA_points(full_AOI,sample_points_n)#makes random points in equal earth prj
    Sample_points_gdf=parallel_process_points(AOI_points,frequency_gdf,full_AOI,num_cores)#moves points inside WRS tiles
    overlap_points_gdf=create_overlap_points_gdf(Sample_points_gdf,frequency_gdf)#appends path/row information to points
    logs.append(f"Number of sampling points created: {len(Sample_points_gdf)}")
    logs.append(f"Sampling points created in {time_tracker(t0)}")
    return Sample_points_gdf,overlap_points_gdf,logs