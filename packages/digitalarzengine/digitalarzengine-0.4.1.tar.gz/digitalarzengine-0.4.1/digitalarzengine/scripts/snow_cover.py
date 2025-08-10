import os
import traceback
import xarray as xr
import earthaccess
import ee
import pandas as pd
import geopandas as gpd
from tqdm import tqdm


from digitalarzengine.io.file_io import FileIO
from digitalarzengine.io.gee.gee_image import GEEImage
from digitalarzengine.io.gee.gee_image_collection import GEEImageCollection
from digitalarzengine.io.gee.gee_region import GEERegion
from digitalarzengine.io.gee.gpd_vector import GPDVector
from digitalarzengine.io.managers.data_manager import DataManager
from digitalarzengine.pipeline.gee_pipeline import GEEPipeline, GEETags
from digitalarzengine.pipeline.pak_data import PakData
from digitalarzengine.settings import DATA_DIR, local_data_dir
from digitalarzengine.utils.date_utils import DateUtils


def download_google_open_building():
    # name = "pak"
    gdv = PakData.get_district_boundary()
    for index, row in gdv.iterrows():
        name = row.adm2_en
        fp = os.path.join(local_data_dir, f"pak/building/google_res/{name}/{name}_gee_building.gpkg")
        dir = FileIO.mkdirs(fp)
        dist_gdv = GPDVector(gpd.GeoDataFrame(geometry=[row.geom], crs=gdv.crs))
        index_map = dist_gdv.create_index_map(1000)
        index_map.to_file(os.path.join(dir, "index_map.gpkg"), driver='GPKG')
        print("index map created")
        gee_pipeline = GEEPipeline(dist_gdv)
        # gee_pipeline.get_google_buildings(fp)
        open_buildings = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons')
        # gee_fc = GEEFeatureCollection(open_buildings, gee_pipeline.region)
        # gee_fc.download_feature_collection(fp)
        print("done")


def save_df_to_netcdf(df: pd.DataFrame, fp: str):
    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Ensure datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Drop rows with missing values in important columns
    df = df.dropna(subset=['latitude', 'longitude', 'datetime', 'NDSI_Snow_Cover'])

    # Safely round coordinates
    df.loc[:, 'latitude'] = df['latitude'].round(5)
    df.loc[:, 'longitude'] = df['longitude'].round(5)

    # Set index for NetCDF structure
    df = df.set_index(['datetime', 'latitude', 'longitude'])

    # Convert to xarray dataset
    ds = xr.Dataset.from_dataframe(df)

    # Ensure proper dimension order
    ds = ds.transpose('datetime', 'latitude', 'longitude')

    # Save to NetCDF
    ds.to_netcdf(fp)
    print(f"Saved NetCDF file: {fp}")


def snow_cover_data():
    gdf = PakData.get_snow_covered_basins()
    gdf.to_crs(epsg=4326)
    aoi_gdf = GPDVector.to_aoi_gdf(gdf)
    gee_pipeline = GEEPipeline(aoi=None, is_browser=False)
    tile_gdf = GPDVector.get_zxy_tiles(aoi_gdf, zoom=10)
    total = len(tile_gdf)
    daily_dir = os.path.join(DATA_DIR, 'pak/snow_cover/yearly')
    os.makedirs(daily_dir, exist_ok=True)
    for index, row in tile_gdf.iterrows():
        # print("working on {} out of {}".format(index + 1,total))
        region = GEERegion.from_shapely_polygon(row.geometry)
        fp_csv = os.path.join(daily_dir, f'{row["z"]}_{row["x"]}_{row["y"]}.csv')
        fp_nc = os.path.join(daily_dir, f'{row["z"]}_{row["x"]}_{row["y"]}.nc')

        # Skip if NetCDF already exists
        if os.path.exists(fp_nc):
            continue
        # If CSV exists (from past runs), read it instead of querying
        if os.path.exists(fp_csv):
            print(f"Reading from existing CSV: {fp_csv}")
            yearly_df = pd.read_csv(fp_csv)
        else:
            print(f"Processing tile {index + 1} of {total}")
            region = GEERegion.from_shapely_polygon(row.geometry)
            yearly_df = pd.DataFrame()
            for year in tqdm(range(2001, 2026), desc='Snow year', total=25):
                start_date = ee.Date(f"{year}-01-01")
                end_date = ee.Date(f"{year}-12-31")
                tag = GEETags.SnowCover.value['modis']
                img_coll = (
                    ee.ImageCollection(tag)
                    .filterBounds(region.aoi)
                    .filterDate(start_date, end_date)
                    .select('NDSI_Snow_Cover')
                )
                df = GEEImageCollection(img_coll).info_ee_array_to_df(
                    region, ['NDSI_Snow_Cover'], scale=1000
                )
                yearly_df = pd.concat([yearly_df, df], ignore_index=True)

        # Save directly to NetCDF
        save_df_to_netcdf(yearly_df, fp_nc)


def snow_cover_normal_data():
    gdf = PakData.get_snow_covered_basins()
    aoi_gdf = GPDVector.to_aoi_gdf(gdf)
    gee_pipeline = GEEPipeline(aoi=aoi_gdf, is_browser=False)
    start_year = 2001
    end_year = 2024
    output_dir = os.path.join(DATA_DIR, 'pak', 'snow_cover/stats')
    data_manager = DataManager(output_dir, base_name="snow_cover_normal_data",
                               purpose="snow cover normal data from 2001 to 2024")
    for doy in range(1, 366):
        try:
            key = f'snow_cover_normal_{doy}_{start_year}-{end_year}'
            fp = os.path.join(output_dir, f'{key}.tif')
            dates = DateUtils.get_date_list_by_doy(doy, start_year, end_year)
            tag = GEETags.SnowCover.value['modis']
            img_collection = GEEImageCollection.customize_collection(tag, dates)
            img_collection.filterBounds(gee_pipeline.region.bounds).select('NDSI_Snow_Cover')
            # res = GEEImageCollection.get_ymd_list(img_collection)

            if not os.path.exists(fp):
                # print(res)
                mean_img = img_collection.mean()
                mean_img = mean_img.select('NDSI_Snow_Cover')
                GEEImage(mean_img).download_image(fp, gee_pipeline.region, scale=1000, within_aoi_only=False,
                                                  no_of_bands=1, save_metadata=False)
            # record = {
            #     "doy": doy,
            #     "ymd_list": res,
            #     "file_name": fp
            # }
            # data_manager.add_record(key, record)
        except Exception as e:
            traceback.print_exc()


def download_snow_cover_modis():
    gdf = PakData.get_snow_covered_basins()
    aoi_gdf = GPDVector.to_aoi_gdf(gdf)
    bounds = aoi_gdf.total_bounds.tolist()  # [minx, miny, maxx, maxy]
    west, south, east, north = bounds
    print(f"Using bounding box: {west}, {south}, {east}, {north}")

    earthaccess.login()

    # Search for MOD10A1 granules
    results = earthaccess.search_data(
        short_name="MOD10A2",
        version="061",
        temporal=("2021-01-01", "2021-01-03"),
        cloud_hosted=False,
        bounding_box=(west, south, east, north),
    )

    if not results:
        print("❌ No MODIS snow cover data found for the given parameters.")
        return

    # Download the files
    local_path = os.path.join(local_data_dir, 'pak', 'earth_data/snow_cover')
    os.makedirs(local_path, exist_ok=True)
    earthaccess.download(results, local_path)


def precipitation_normal_data():
    gdf = PakData.get_pak_basins()
    aoi_gdf = GPDVector.to_aoi_gdf(gdf)
    gee_pipeline = GEEPipeline(aoi=aoi_gdf, is_browser=False)
    start_year = 2001
    end_year = 2024
    output_dir = os.path.join(DATA_DIR, 'pak', 'precipitation/stats')
    data_manager = DataManager(output_dir, base_name="precipitation_normal_data",
                               purpose="precipitation normal data from 2001 to 2024")
    for doy in range(1, 366):
        print("Processing doy " + str(doy))
        try:
            key = f'precipitation_normal_{doy}_{start_year}-{end_year}'
            fp = os.path.join(output_dir, f'{key}.tif')
            if not os.path.exists(fp):
                dates = DateUtils.get_date_list_by_doy(doy, start_year, end_year)
                # tag = GEETags.SnowCover.value['modis']
                tag = 'UCSB-CHG/CHIRPS/DAILY'
                band_name = 'precipitation'
                img_collection = GEEImageCollection.customize_collection(tag, dates)
                img_collection.filterBounds(gee_pipeline.region.bounds).select(band_name)
                res = GEEImageCollection.get_ymd_list(img_collection)

                # print(res)
                mean_img = img_collection.mean()
                mean_img = mean_img.select(band_name)
                GEEImage(mean_img).download_image(fp, gee_pipeline.region, scale=5000, within_aoi_only=False,
                                                  no_of_bands=1, save_metadata=False)
                record = {
                    "doy": doy,
                    "ymd_list": res,
                    "file_name": fp
                }
                data_manager.add_record(key, record)
            else:
                new_key = f'precipitation_normal_{doy}_{start_year}-{end_year}'
                old_key = f'snow_cover_normal_{doy}_{start_year}-{end_year}'

                # new_fp = os.path.join(output_dir, f'{new_key}.tif')
                # os.rename(fp, new_fp)
                data_manager.change_key(old_key, new_key)
        except Exception as e:
            traceback.print_exc()
