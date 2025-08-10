# LEOHS: Landsat ETM+ OLI Harmonization Script
# Copyright (C) 2025 Galen Richardson
# This file is licensed under GPL-3.0-or-later
# Related Publication: https://doi.org/10.1080/10106049.2025.2538108
import numpy as np
import matplotlib.pyplot as plt
import os,sys
from sklearn.linear_model import LinearRegression, TheilSenRegressor
from datetime import datetime
from .io import time_tracker

def regression_calc(df, band, Regression_type,harmonization_order,num_cores):
    cols7, col8 = f'L7_{band}', f'L8_{band}'
    ho = harmonization_order
    if ho == ['LS8', 'LS7']:
        X, Y = df[col8].values.reshape(-1, 1), df[cols7].values
    elif ho == ['LS7', 'LS8']:
        X, Y = df[cols7].values.reshape(-1, 1), df[col8].values
    else:
        raise ValueError(f"Unexpected harmonization order: {ho}")
    if Regression_type == "OLS":
        model = LinearRegression(n_jobs=num_cores)
        model.fit(X, Y)
        r_value = model.score(X, Y)
        coefficients = model.coef_
        intercept =  model.intercept_
    elif Regression_type == "TS":
        model = TheilSenRegressor(n_jobs=num_cores, random_state=71)
        model.fit(X, Y)
        r_value = model.score(X, Y)
        coefficients = model.coef_
        intercept = model.intercept_
    elif Regression_type=="RMA":
        slope_y_on_x=np.polyfit(X.flatten(),Y.flatten(),1)[0]
        slope_x_on_y=np.polyfit(Y.flatten(),X.flatten(),1)[0]
        slope_rma=np.sqrt(slope_y_on_x*slope_x_on_y)# Calculate the RMA slope as the geometric mean of these slopes
        intercept=np.mean(Y)-slope_rma*np.mean(X)# Calculate the intercept
        coefficients=np.array([slope_rma])
        Y_pred=slope_rma * X + intercept
        TSS=np.sum(np.round(Y-np.mean(Y),5)**2)
        Y = Y.ravel()
        Y_pred = Y_pred.ravel()
        RSS = np.sum((np.round(Y - Y_pred,5)) ** 2)
        r_value=1-(RSS/TSS)
    else:
        raise ValueError(f"Unsupported Regression_type: {Regression_type}")
    return X, Y, r_value, coefficients, intercept
def make_equation(coefficients, intercept, harmonization_order, band):
    col_names = harmonization_order
    coef,intercept_rounded = round(coefficients[0], 4),round(intercept, 4)
    if intercept_rounded < 0:
        equation = f'{band}: {col_names[1]} = {coef}{col_names[0]} - {abs(intercept_rounded)}'
    else:
        equation = f'{band}: {col_names[1]} = {coef}{col_names[0]} + {intercept_rounded}'
    return equation
def make_heatmap(harmonization_order,X,Y,band,ax,row,col,SR_or_TOA):
    col_names=harmonization_order  # Getting the sensor order
    dtype=SR_or_TOA.upper()  # Finding the dtype
    x_line=np.linspace(X.min(), X.max(), 100)
    ax.hist2d(X.flatten(),Y,bins=100,cmap='viridis')# Create a 2D histogram (box heatmap)
    ax.plot(x_line,x_line,color='white',label='1:1',linewidth=1)
    min_val=max(X.min(),Y.min()) # Set x and y axis limits to be the same
    max_val=min(X.max(),Y.max())
    ax.set_xlim(min_val,max_val)
    ax.set_ylim(min_val,max_val)
    ticks=np.arange(np.floor(min_val),np.ceil(max_val)+0.1,0.1)# Set ticks only going up by 0.1
    ticks=ticks[(ticks >= min_val) & (ticks <= max_val)]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    if row==1: # Set axis labels only for outer plots
        ax.set_xlabel(f'{col_names[0]}',fontsize=24)
    if col==0:  # First column
        ax.set_ylabel(f'{col_names[1]}',fontsize=24)
    ax.set_title(f'{dtype} {band} Band',fontsize=18)
    ax.tick_params(axis='both', which='major',labelsize=18)
def plot_heatmap(df, harmonization_order,SR_or_TOA,Save_folder_path):
    bands=['B','G','R','NIR','SWIR1','SWIR2']
    fig, axs=plt.subplots(2, 3, figsize=(18,12))
    for i, band in enumerate(bands):
        row,col=divmod(i,3)
        cols7,col8=f'L7_{band}',f'L8_{band}'
        if harmonization_order==['LS8','LS7']:
            X,Y=df[col8].values.reshape(-1,1), df[cols7].values
        if harmonization_order==['LS7','LS8']:
            X,Y=df[cols7].values.reshape(-1,1), df[col8].values
        make_heatmap(harmonization_order,X,Y,band,axs[row,col],row,col,SR_or_TOA)
    plt.tight_layout()
    plt.savefig(os.path.join(Save_folder_path,f'{harmonization_order[0]}{harmonization_order[1]}_heatmaps.png'),dpi=500)
def process_all_regressions(df, Regression_types,num_cores,Save_folder_path,SR_or_TOA,logs):
    t0 = datetime.now()
    dtype = SR_or_TOA.upper()
    bands = ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2']
    orders = [['LS7', 'LS8'], ['LS8', 'LS7']]
    combined_file = os.path.join(Save_folder_path, f'{dtype}_LEOHS_harmonization.txt')
    if os.path.exists(combined_file):
        os.remove(combined_file)
    with open(combined_file, 'w') as file:
        file.write("LEOHS\n")
        file.write("https://doi.org/10.1080/10106049.2025.2538108\n")
    for R_type in Regression_types:
        t_reg = datetime.now()
        print(f"\n=== {R_type} Regression ===")
        # Write regression type header
        with open(combined_file, 'a') as file:
            file.write(f"\n=== {R_type} Regression ===\n")
        if R_type=='RMA': #only need to do harmonization in one direction due to regression type
            with open(combined_file, 'a') as file:
                header_line = f"-- {harmonization_order[1]} to {harmonization_order[0]} --"
                file.write(f"{header_line}\n")
            rvalues = []
            for band in bands:
                X, Y, r_value, coefficients, intercept = regression_calc(df, band, R_type, harmonization_order, num_cores)
                equation = make_equation(coefficients, intercept, harmonization_order, band)
                rvalues.append(r_value)
                print(f"{equation}")
                with open(combined_file, 'a') as file:
                    file.write(f"{equation}\n")
            avg_r = round(np.mean(rvalues), 4)
            print(f"Average R for {R_type} {harmonization_order}: {avg_r}")
            with open(combined_file, 'a') as file:
                file.write(f"Average R² on {R_type}: {avg_r}\n")
        else:
            rvalues = []
            for harmonization_order in orders:
                header_line = f"-- {harmonization_order[0]} to {harmonization_order[1]} --"
                print(header_line)
                with open(combined_file, 'a') as file:
                    file.write(f"{header_line}\n")
                for band in bands:
                    X, Y, r_value, coefficients, intercept = regression_calc(df, band, R_type, harmonization_order, num_cores)
                    equation = make_equation(coefficients, intercept, harmonization_order, band)
                    rvalues.append(r_value)
                    print(f"{equation}")
                    with open(combined_file, 'a') as file:
                        file.write(f"{equation}\n")
            avg_r = round(np.mean(rvalues), 4)
            print(f"Average R² on {R_type}: {avg_r}")
            with open(combined_file, 'a') as file:
                file.write(f"Average R² on {R_type}: {avg_r}\n")
        logs.append(f"{R_type} completed in {time_tracker(t_reg)}")
        # Add spacing between regression types
        with open(combined_file, 'a') as file:
            file.write("\n")
    logs.append(f"Regression processing completed in {time_tracker(t0)}")
    # Plot heatmaps (one per harmonization order)
    for harmonization_order in orders:
        plot_heatmap(df, harmonization_order,SR_or_TOA,Save_folder_path)
    logs.append(f"Heatmaps made in {Save_folder_path}")
    logs.append(f"Regression processing completed in {time_tracker(t0)}")
    return logs