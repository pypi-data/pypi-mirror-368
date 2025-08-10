# LEOHS: Landsat ETM+ OLI Harmonization Script
# Copyright (C) 2025 Galen Richardson
# This file is licensed under GPL-3.0-or-later
# Related Publication: https://doi.org/10.1080/10106049.2025.2538108
import ee,re,time,random
import geopandas as gpd
import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from .io import apply_correction_factors
from ee.ee_exception import EEException

def create_img_df (overlap_df,Max_img_samples):
    df_shuffled=overlap_df.sample(frac=1).reset_index(drop=True)# Shuffle the DataFrame
    grouped=df_shuffled.groupby(['LS7_row','LS7_path','LS8_path'])# Group by the unique combination of LS7_row, LS7_path, and LS8_path
    return grouped.apply(lambda x: x.head(Max_img_samples)).reset_index(drop=True)
def get_unique_combinations_as_dicts(df):
    unique_combinations=df[['LS7_row','LS7_path','LS8_path']].drop_duplicates()# Extract unique combinations of LS7_row, LS7_path, LS8_path
    unique_combinations_list=unique_combinations.apply(lambda row: {'LS7_row': row['LS7_row'], 'LS7_path': row['LS7_path'],
                                                                    'LS8_path': row['LS8_path']}, axis=1).tolist()
    return unique_combinations_list #return list of unique combination dics
def filter_gdf_by_values(input_gdf, filter_values):
    input_gdf=input_gdf.replace([np.inf, -np.inf], np.nan).dropna()#used to return a gdf of points that are with a specified row1, path1, path2
    columns_to_convert=[col for col in input_gdf.columns if col != 'geometry']
    input_gdf[columns_to_convert]=input_gdf[columns_to_convert].astype(int)
    filtered_gdf=input_gdf[(input_gdf['LS7_row']==filter_values['LS7_row']) & (input_gdf['LS7_path']==filter_values['LS7_path'])
                           & (input_gdf['LS8_path']==filter_values['LS8_path'])] # Apply the filter to select the rows
    return filtered_gdf
def filter_imgs_by_row_paths(df, filter_values):
    query_str=' & '.join([f"{key}=={value}" for key, value in filter_values.items()])
    filtered_df=df.query(query_str)# Used to query img ids by row1, path1, path 2 to return lists of ids
    id_pairs=filtered_df[['LS7_id', 'LS8_id']].values.tolist()
    return id_pairs
def find_nearest_geometry(point, gdf):
    gdf['distance']=gdf['geometry'].apply(lambda x: point.distance(x))#used to make gee points the same geom as the input sample points
    nearest_index=gdf['distance'].idxmin()
    return gdf.loc[nearest_index,'geometry']
def sample_image_points(L_points, image_id, max_retries=5):
    attempt = 0
    while attempt <= max_retries:
        try:
            features = [ee.Feature(ee.Geometry.Point(geom.x, geom.y)) for geom in L_points.geometry]
            ee_points = ee.FeatureCollection(features)
            image = ee.Image(image_id)
            reducer = ee.Reducer.mean()
            sampled_dict = image.reduceRegions(collection=ee_points, reducer=reducer, scale=30).getInfo()
            break  # Exit loop if successful
        except EEException as e:
            if "Too Many Requests" in str(e):
                print(f"[Attempt {attempt + 1}/{max_retries}] Rate limit hit. Waiting...")
                time.sleep(random.uniform(60, 120))
                attempt += 1
            else:
                raise  # Propagate other Earth Engine errors
        except Exception as e:
            print(f"[Attempt {attempt + 1}/{max_retries}] Unexpected error: {e}")
            time.sleep(random.uniform(60, 120))
            attempt += 1
    else:
        raise RuntimeError(f"Failed after {max_retries} retries due to rate limits.")
    # Convert results to GeoDataFrame
    if 'features' in sampled_dict and sampled_dict['features']:
        sampled_gdf = gpd.GeoDataFrame.from_features(sampled_dict['features'])
        sampled_gdf['image_id'] = image_id
        # Snap each point back to its nearest original geometry
        sampled_gdf['nearest_geometry'] = sampled_gdf['geometry'].apply(lambda x: find_nearest_geometry(x, L_points))
        sampled_gdf['geometry'] = sampled_gdf['nearest_geometry']
        # Keep only valid bands + metadata
        columns_to_keep = [col for col in sampled_gdf.columns if ('B' in col and col.split('B')[1].isdigit()) or col in ['QA_PIXEL', 'QA_RADSAT']]
        columns_to_keep.extend(['image_id', 'geometry'])
        sampled_gdf = sampled_gdf[columns_to_keep]
        return sampled_gdf
    return None
def filter_sat_by_bits(df):
    # Ensure QA_RADSAT is of integer type, handle NaN values
    df['QA_RADSAT']=pd.to_numeric(df['QA_RADSAT'],errors='coerce').fillna(0).astype(int)
    bitmask=0b01111111 #Define the bitmask for bits 0, 1, 2, 3, 4, 5, and 6 (0b01111111)
    return (df['QA_RADSAT'] & bitmask)==0 # Return a Boolean Series where True means bits 0-6 are all 0
def remove_invalid_pixels(df,CFMask_filtering,Water,Snow):
    numeric_columns=[col for col in df.columns if re.search(r'B\d+$', col)]
    df[numeric_columns]=df[numeric_columns].apply(pd.to_numeric,errors='coerce')
    condition_numeric=(df[numeric_columns]<=65455).all(axis=1) #no invalid numbers in numeric columns
    condition_sat=filter_sat_by_bits(df) #filter saturated pixels out
    if CFMask_filtering==False:
        condition_all=condition_numeric & condition_sat
        return df[condition_all]
    allowed_values=[5440,21824]# Define the allowed values for QA_PIXEL, Clear with lows set or mild cloud conf
    if Water==True:
        allowed_values.extend([5504,21952])#adding Water with lows set in LS7 and LS8
    if Snow==True:
        allowed_values.extend([13600,30048])#adding High conf snow/ice in LS7 and LS8
    condition_qa_pixel=df['QA_PIXEL'].isin(allowed_values)# Check conditions for QA_PIXEL column (values in allowed_values)
    condition_all= condition_numeric & condition_qa_pixel & condition_sat # Combine conditions
    return df[condition_all]# Filter the DataFrame
def filter_by_percentage_difference(df,Pixel_difference):
    columns=['B'] #only look at blue column
    for col in columns:
        df[f'{col}_diff']=abs((df[f'LS7_{col}']-df[f'LS8_{col}'])/abs(df[f'LS7_{col}']+df[f'LS8_{col}']*.5))
    filtered_df=df[df[[f'{col}_diff' for col in columns]].lt(Pixel_difference).all(axis=1)]
    filtered_df=filtered_df.drop(columns=[f'{col}_diff' for col in columns])
    return filtered_df
def filter_out_of_range_sr(df):
    bands = ['B','G','R','NIR','SWIR1','SWIR2']
    prefixes = ['LS7_', 'LS8_']
    columns_to_check = [prefix + band for prefix in prefixes for band in bands]
    return df[(df[columns_to_check] <= 1).all(axis=1) & (df[columns_to_check] >= 0).all(axis=1)] # Filter out rows where any column has a value > 1 or < 0
def update_df(df, newvalues):
    if newvalues is None:
        return df #Return the original DataFrame if newvalues is None
    if df.empty:
        return newvalues #make new values the df if it is empty
    else:
        return pd.concat([df, newvalues], ignore_index=True) #otherwise, concat newvalues
def append_prefix(df, prefix):
    new_columns=[prefix+col if col!='geometry' else col for col in df.columns]
    df.columns=new_columns
    return df
def make_join_gdf(LS7_pix_df,LS8_pix_df):
    LS7_pix_df,LS8_pix_df= append_prefix(LS7_pix_df,'LS7_'),append_prefix(LS8_pix_df,'LS8_') #add prefix to make it easy to tell
    joined_gdf=pd.merge(LS7_pix_df, LS8_pix_df,on='geometry',how='inner') #make singular gdf
    joined_gdf=gpd.GeoDataFrame(joined_gdf,geometry='geometry')
    columns=list(joined_gdf.columns)
    columns.remove('geometry')
    columns.append('geometry') #doing this to make the order correct
    joined_gdf=joined_gdf[columns] #reorder columns
    return joined_gdf.set_crs(epsg=4326, inplace=True)
def fix_column_names(big_gdf):
    columns_to_drop=[col for col in big_gdf.columns if any(substring in col for substring in ["VCID_","B8","B9","B10","B11",'ST','QA_PIXEL','QA_RADSAT'])]
    big_gdf=big_gdf.drop(columns=columns_to_drop)
    LS7_columns,LS8_columns=[col for col in big_gdf.columns if 'LS7' in col],[col for col in big_gdf.columns if 'LS8' in col]
    columns=big_gdf.columns
    col_list=[LS7_columns,LS8_columns]
    cols_fixed=[]
    for cols in col_list:
        if len(cols)>7: #must be LS8
            fixed_cols=['CA','B','G','R','NIR','SWIR1','SWIR2','image_id']
        elif len(cols)==7: #must be LS7
            fixed_cols=['B','G','R','NIR','SWIR1','SWIR2','image_id']
        else:
            print('Error Sensor Band names!')
            continue # Skip to the next iteration if there is an error
        if cols and cols[0].startswith('LS7_'):
            fixed_cols=['LS7_'+col for col in fixed_cols]
        if cols and cols[0].startswith('LS8_'):
            fixed_cols=['LS8_'+col for col in fixed_cols]
        cols_fixed.extend(fixed_cols)
    rename_dict={old_col: new_col for old_col, new_col in zip(columns, cols_fixed) if old_col != 'geometry'}
    big_gdf=big_gdf.rename(columns=rename_dict)# Rename the columns in the GeoDataFrame
    columns_to_drop=[col for col in big_gdf.columns if 'CA' in col]
    big_gdf.drop(columns=columns_to_drop, inplace=True) # Dropping the columns_to_drop
    return big_gdf
def remove_outliers(gdf):
    numeric_cols=gdf.select_dtypes(include=[np.number])# Select only numeric columns
    means,stds=numeric_cols.mean(),numeric_cols.std() #calculate mean and std
    condition=((numeric_cols-means).abs()<= 4*stds).all(axis=1) #condition for removing pix greater than 4std
    gdf_filtered=gdf[condition]# Apply the condition to filter out the outliers
    return gdf_filtered
def process_chunk_for_pix_val(points_chunk,id_pairs,LS7,LS8,CFMask_filtering,Water,Snow,Pixel_difference):
    joined_pix_gdf=gpd.GeoDataFrame()
    L_points=points_chunk.copy()
    for L_id in id_pairs:
        if len(L_points)==0:#if there are no more points to sample, end loop
            break
        names7,names8=L_id[0],L_id[1]
        L7_pixel_values=sample_image_points(L_points,names7)#sample LS7 image
        if L7_pixel_values is not None and not L7_pixel_values.empty:
            L7_pixel_values=remove_invalid_pixels(L7_pixel_values,CFMask_filtering,Water,Snow)#remove invalid pixels
            L_points_temp=L_points.copy()
            L_points_temp=L_points_temp[L_points_temp['geometry'].isin(L7_pixel_values['geometry'])]
            L8_pixel_values=sample_image_points(L_points_temp, names8)#sample LS8 with only valid LS7 observations
            if L8_pixel_values is not None and not L8_pixel_values.empty:
                L8_pixel_values=remove_invalid_pixels(L8_pixel_values,CFMask_filtering,Water,Snow)#remove invalid pixels
                joined_pix_temp=make_join_gdf(L7_pixel_values, L8_pixel_values)#make a single gdf
                joined_pix_temp=fix_column_names(joined_pix_temp)#fix the column names
                joined_pix_temp=apply_correction_factors(LS7,LS8,joined_pix_temp)#apply correction factors if SR
                joined_pix_temp=filter_out_of_range_sr(joined_pix_temp)#remove any over 1 or below 0 SR
                joined_pix_temp=filter_by_percentage_difference(joined_pix_temp,Pixel_difference)#filter by %diff
                L_points=L_points[~L_points['geometry'].isin(joined_pix_temp['geometry'])]#remove points from L_points that have pix values
                joined_pix_gdf=update_df(joined_pix_gdf, joined_pix_temp)
    return joined_pix_gdf
def get_pix_values(id_pairs,filtered_points,LS7,LS8,CFMask_filtering,Water,Snow,Pixel_difference):
    all_joined_pix_gdf = gpd.GeoDataFrame()
    chunk_size=2000# Process points in chunks of 2000 since that is a GEE limit
    num_chunks=len(filtered_points)//chunk_size+1
    for i in range(num_chunks):
        start_idx=i*chunk_size #process them one at a time in order
        end_idx=start_idx+chunk_size
        points_chunk=filtered_points.iloc[start_idx:end_idx]
        chunk_joined_pix_gdf=process_chunk_for_pix_val(points_chunk,id_pairs,LS8,LS7,CFMask_filtering,Water,Snow,Pixel_difference)
        all_joined_pix_gdf=update_df(all_joined_pix_gdf,chunk_joined_pix_gdf) #update final gdf
    return all_joined_pix_gdf
def process_chunk_big_gdf(chunk, overlap_points_gdf, overlap_imgs_df, LS7, LS8, CFMask_filtering, Water, Snow, Pixel_difference,project_ID):
    if project_ID != None:
        ee.Initialize(project=project_ID)
    else:
        ee.Initialize()
    chunk_gdf = gpd.GeoDataFrame()
    for unique_row_path in chunk:
        filtered_points = filter_gdf_by_values(overlap_points_gdf, unique_row_path)
        id_pairs = filter_imgs_by_row_paths(overlap_imgs_df, unique_row_path)
        joined_pix_gdf = get_pix_values(id_pairs, filtered_points, LS7,LS8,
                                        CFMask_filtering,Water,Snow,Pixel_difference)
        if joined_pix_gdf is not None and not joined_pix_gdf.empty:
            chunk_gdf = update_df(chunk_gdf, joined_pix_gdf)
        time.sleep(0.5)
    return chunk_gdf
def create_big_gdf(overlap_points_gdf,overlap_df,Max_img_samples,LS7, LS8, num_cores,
                   CFMask_filtering, Water, Snow, Pixel_difference,logs,project_ID):
    overlap_imgs_df = create_img_df(overlap_df, Max_img_samples)
    unique_row_path_list = get_unique_combinations_as_dicts(overlap_df)
    chunks = [unique_row_path_list[i::num_cores] for i in range(num_cores)]
    # Run parallel processing using joblib
    gdfs = Parallel(n_jobs=num_cores)(
        delayed(process_chunk_big_gdf)(chunk,overlap_points_gdf,overlap_imgs_df,LS7,LS8,
            CFMask_filtering,Water,Snow,Pixel_difference,project_ID) for chunk in chunks)
    if all(gdf.empty for gdf in gdfs):
        print("Job failed, need more images or sample points")
        return None
    gdfs = [gdf for gdf in gdfs if not gdf.empty]
    big_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    if big_gdf.empty:
        big_gdf=pd.DataFrame()
        print("Warning: gdf is empty for this set of overlaps. Consider increasing number of samples")
        logs.append("gdf is empty for this set of overlaps. Consider increasing number of samples")
        return big_gdf, logs
    big_gdf = remove_outliers(big_gdf)
    replacements = {"LE07": "L7", "LC08": "L8"}# Replace LE07, LC08 with L7, L8
    for key, value in replacements.items():
        if 'LS7_image_id' in big_gdf.columns and key in big_gdf['LS7_image_id'].iloc[0]:
            big_gdf.columns = [col.replace("LS7", value) for col in big_gdf.columns]
        if 'LS8_image_id' in big_gdf.columns and key in big_gdf['LS8_image_id'].iloc[0]:
            big_gdf.columns = [col.replace("LS8", value) for col in big_gdf.columns]
    return big_gdf,logs