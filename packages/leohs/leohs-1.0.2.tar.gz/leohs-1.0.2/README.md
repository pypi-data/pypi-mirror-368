# 🌍 LEOHS: Landsat ETM+ OLI Harmonization Script

**LEOHS** is a Python package for harmonizing Landsat 7 and 8 imagery using Google Earth Engine (GEE).
The harmonization functions generated from this tool can be used for long term landsat time series analysis.
LEOHS is designed specifically to create harmonization functions optimized for **user-defined study areas, time periods, and sampling parameters**.
The publication explaining the LEOHS tool can be found here: **[A tool for global and regional Landsat 7 and Landsat 8 cross-sensor harmonization](https://doi.org/10.1080/10106049.2025.2538108)**.
---

## 🔧 Requirements

- **Python 3.10** — LEOHS must be run in its own environment
- an active **Google Earth Engine** account
- an area of interest shapefile

---

## 📦 Installation

### 1. Create a clean Python 3.10 environment (recommended name: `leohs_env`)
```bash
conda create -n leohs_env python=3.10 -y
conda activate leohs_env
```
### 2. Install LEOHS
```bash
pip install leohs
```

## 🚀 Example Usage
Before using LEOHS, you must import both `ee` and `leohs`, then **authenticate and initialize** your Google Earth Engine (GEE) session. Only after that should you call `leohs.run_leohs(...)`.
```python
import ee
import leohs
ee.Authenticate() #need to authenticate GEE
ee.Initialize(project="your-earth-engine-project-id") #need to initialize GEE
leohs.run_leohs(
    Aoi_shp_path=r"E:\Canada.shp",
    Save_folder_path=r"E:\Canada_output",
    SR_or_TOA="SR",
    months=[6,7,8],
    years=[2018],
    sample_points_n=100000,
    project_ID="your-earth-engine-project-id")
```
## 🔧 `run_leohs` Parameters

- `Aoi_shp_path` *(str)*:  
  Path to your input AOI shapefile.
  
- `Save_folder_path` *(str)*:  
  Path to the output folder where results will be saved.
  
- `SR_or_TOA` *(str)*:  
  Type of Landsat imagery to process. Choose `"SR"` or `"TOA"`.

- `months` *(list of int)*:  
  List of months to include in image filtering (e.g., `[1,2,3,4,5,6,7,8,9,10,11,12]`).

- `years` *(list of int)*:  
  List of years to include in filtering (e.g., `[2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]`).

- `sample_points_n` *(int)*:  
  Number of sample points to generate (e.g., `100000`). Max: **1,000,000**.

- `shp` *(bool, optional, default=False)*:  
  if True, this parameter will create a shapefile of all the sampled pixels with Landsat values.

- `Deep` *(bool, optional, default=True)*:  
  This setting forces LEOHS to sample more image overlaps by breaking the sample points into ten groups and randomly shuffling the overlap image pair sampling order for each group
. The outcome is a more robust model training dataset while slightly increasing processing time.

- `maxCloudCover` *(int, optional, default=50)*:  
  Maximum cloud cover (%) for image filtering.

- `Regression_types` *(list of str, optional, default=["OLS"])*:  
  List of regression models to run. Valid values: `"OLS"`, `"RMA"`, `"TS"`.

- `CFMask_filtering` *(bool, optional, default=True)*:  
  Whether to apply CFMask filtering (cloud, water, snow masking).

- `Water` *(bool, optional, default=True)*:  
  Allow water pixels (only effective if `CFMask_filtering=True`).

- `Snow` *(bool, optional, default=True)*:  
  Allow snow pixels (only effective if `CFMask_filtering=True`).

- `project_ID` *(str, optional, default=None)*:  
  Your Google Earth Engine Project ID for GEE initialization. 



## 🛰️ Outputs

The following files are exported to the specified `Save_folder_path`:

- **Text log** (`TOA_LEOHS_harmonization.txt`):  
  Contains regression equations for each band, processing time, and diagnostic logs.

- **Heatmaps** (`.png` files):  
  Visualizations of pixel distributions between Landsat 7 and 8 for each band.

- **Pixel and pair data** (`.csv`) and (`.shp`):  
  Sampled pixel values and image names for all matched images. If shp==True, a shapefile will also be saved. 


## 🐛 Known Issues

- **Google Earth Engine computation timeout**  
  Occasionally, you may encounter an `ee.EEException: Computation timed out` error. This can happen when GEE servers are under heavy load.  
  🛠️ **Recommended fix**: Simply wait a bit of time, and re-run `leohs.run_leohs(...)`. The issue usually resolves itself on retry.

- **Performance and speed**  
  The runtime of LEOHS depends on Google Earth Engine load, the number of available CPU cores, and the number of sample points.  
  ⚠️ Using **one million sample points** may take **over 10 hours** to fully process.

- **AOI must intersect a WRS-2 Overlap**  
  The tool will fail if your Area of Interest (AOI) does **not intersect with any WRS-2 Overlap zones**.  
  📍 You can find a shapefile of valid WRS-2 Overlaps in the [LEOHS GitHub repository](https://github.com/galenrichardson/LEOHS).

- **No available images**  
  LEOHS will fail if there are **no valid Landsat image pairs** available that match your AOI, time range or cloud cover threshold.
- **Google Collab**  
  Presently LEOHS does not work in Google Collab due to dependency issues. This functionality might be added at a later date. 

## 📂 Additional Resources

Additional scripts for applying LEOHS, as well as global harmonization equations, can be found in the companion repository:  
🔗 [https://github.com/galenrichardson/LEOHS](https://github.com/galenrichardson/LEOHS)

## 📑 License

This project is licensed under the  
**GNU General Public License v3.0 or later (GPL-3.0-or-later)**  
© 2025 Galen Richardson

---

## 📬 Contact

**Author**: Galen Richardson  
**Email**: [galenrichardsonam@gmail.com](mailto:galenrichardsonam@gmail.com)

> Feel free to reach out for questions, bug reports, suggestions, or collaboration ideas.

