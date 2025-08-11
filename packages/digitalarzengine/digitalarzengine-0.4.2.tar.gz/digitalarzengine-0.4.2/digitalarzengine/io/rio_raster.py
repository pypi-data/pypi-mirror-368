import math
import os

import pandas as pd
import rasterio
from osgeo import gdal
import geopandas as gpd

import numpy as np
import rasterio as rio
from typing import Union, List, Optional, Tuple

import shapely
from affine import Affine
from rasterio import CRS, windows

from rasterio.mask import mask
from rasterio.transform import from_bounds

from shapely import box

from digitalarzengine.io.file_io import FileIO
from digitalarzengine.processing.raster.band_process import BandProcess
from digitalarzengine.utils.singletons import da_logger


class RioRaster:
    dataset: rio.DatasetReader = None

    def __init__(self, src: Union[str, rio.DatasetReader, None], prj_path: str = None):
        if src is not None:
            self.set_dataset(src)
            if prj_path is not None and os.path.exists(prj_path):
                self.add_crs_from_prj(prj_path)

    def __repr__(self):
        if self.empty:
            return "<RioRaster: Empty>"
        return f"<RioRaster: {self.dataset.name}, {self.get_image_resolution()}, {self.get_crs()}>"

    def set_dataset(self, src: Union[str, rio.DatasetReader]):
        """
        Set the raster dataset from a source.

        :param src: The source path or DatasetReader object.
        """
        try:
            if isinstance(src, rio.DatasetReader):
                if '/vsipythonfilelike/' in src.name:
                    self.dataset = self.rio_dataset_from_array(src.read(), src.meta)
                else:
                    self.dataset = src
            elif isinstance(src, str):
                if "/vsimem/" in src:
                    with rio.MemoryFile(src) as memfile:
                        self.dataset = memfile.open()
                else:
                    if os.path.exists(src):
                        self.dataset = rio.open(src, mode='r', ignore_cog_layout_break='YES')
                    else:
                        raise FileNotFoundError(f"Raster file not available at {src}")

            if self.dataset is None:
                raise ValueError("Dataset could not be set. It is None.")
        except Exception as e:
            da_logger.exception(f"Error setting dataset: {e}")

    def get_dataset(self) -> rio.DatasetReader:
        """Get the current dataset."""
        return self.dataset

    @staticmethod
    def rio_dataset_from_array(data: np.ndarray, meta, descriptions: list = None) -> rio.DatasetReader:
        """
        Create a RioDataset from an array.

        :param data: The data array.
        :param meta: The metadata.
        :param descriptions: The band descriptions.
        :return: The resulting DatasetReader object.
        """
        bands = 1 if len(data.shape) == 2 else data.shape[0]
        memfile = rio.MemoryFile()
        dst = memfile.open(**meta,
                           compress='lzw',
                           BIGTIFF='YES')
        for i in range(bands):
            d = data if len(data.shape) == 2 else data[i, :, :]
            dst.write(d, i + 1)
        if descriptions is not None:
            for i, desc in enumerate(descriptions):
                if desc:
                    dst.set_band_description(i + 1, desc)
        dst.close()
        return memfile.open()

    def add_crs_from_prj(self, prj_file):
        """
        Add CRS from a .prj file.

        :param prj_file: The path to the .prj file.
        """
        ame, ext = os.path.splitext(prj_file)
        if ext.lower() == ".prj":
            with open(prj_file) as f:
                wkt = f.read()
                self.dataset.crs = CRS.from_wkt(wkt)

    def get_meta(self):
        """Get the metadata of the current dataset."""
        return self.dataset.meta

    def get_spectral_resolution(self) -> int:
        """
        Get the number of bands (spectral resolution) in the raster.

        :return: Number of bands.
        """
        if self.dataset is not None:
            return self.dataset.count
        else:
            raise ValueError("Dataset is not set.")

    def get_spatial_resolution(self, in_meter=True) -> tuple:
        """
        Return the spatial resolution (pixel size) as (x_resolution, y_resolution).

        If `in_meter` is True and the CRS is geographic (degrees),
        it will approximate the resolution in meters using a degree-to-meter conversion
        at the dataset's center latitude.
        """
        if self.dataset is None:
            raise ValueError("Dataset is not set.")

        a, _, _, _, e, _ = self.dataset.transform[:6]
        x_res, y_res = abs(a), abs(e)

        if in_meter:
            crs = CRS.from_user_input(self.dataset.crs)
            if crs.is_geographic:
                # Get dataset center latitude for conversion
                bounds = self.dataset.bounds
                center_lat = (bounds.top + bounds.bottom) / 2

                # Convert degrees to meters at center latitude
                meters_per_degree_lon = 111320 * math.cos(math.radians(center_lat))
                meters_per_degree_lat = 110540  # average

                x_res *= meters_per_degree_lon
                y_res *= meters_per_degree_lat

        return x_res, y_res

    def get_radiometric_resolution(self) -> str:
        """
        Return the radiometric resolution (bit depth) based on the data type.

        :return: String representing the data type (e.g., 'uint8', 'int16')
        """
        if self.dataset is not None:
            return self.dataset.dtypes[0]  # Assume all bands have the same dtype
        else:
            raise ValueError("Dataset is not set.")

    def get_image_resolution(self) -> tuple:
        """
        Return the image resolution in pixels as (width, height).

        :return: Tuple (width, height)
        """
        if self.dataset is not None:
            return self.dataset.width, self.dataset.height
        else:
            raise ValueError("Dataset is not set.")

    @property
    def empty(self):
        return self.dataset is None

    @staticmethod
    def write_to_file(img_des: str, data: np.ndarray, crs: CRS, affine_transform: Affine, nodata_value,
                      band_names: List[str] = ()):
        """Write raster data to a file (GeoTIFF or COG) with optional S3 support.

        Args:
            img_des (str): The destination file path (local or S3 URI).
            data (np.ndarray): The raster data array.
            crs (CRS): The Coordinate Reference System.
            affine_transform (Affine): The affine transformation.
            nodata_value: The no-data value.
            band_names: list of band names to write with file as description
        """
        try:

            dir_name = FileIO.mkdirs(img_des)
            da_logger.debug(f"directory name {dir_name}")
            # Determine driver and BigTIFF
            driver = 'COG' if img_des.lower().endswith('.cog') else 'GTiff'
            bigtiff = 'YES' if data.nbytes > 4 * 1024 * 1024 * 1024 else 'NO'

            # Get dimensions and bands
            if len(data.shape) == 2:
                # bands, rows, cols = 1, *data.shape
                bands = 1
                rows, cols = data.shape
            else:
                bands, rows, cols = data.shape

            # Write raster data with optional S3 environment

            with rio.open(img_des, 'w', driver=driver, height=rows, width=cols,
                          count=bands, dtype=str(data.dtype), crs=crs,
                          transform=affine_transform, compress='deflate',
                          predictor=1, zlevel=7,  # Predictor and compression level for Deflate
                          nodata=nodata_value, BIGTIFF=bigtiff) as dst:

                for i in range(bands):
                    d = data if bands == 1 else data[i, :, :]
                    dst.write(d, indexes=i + 1) if bands > 1 else dst.write(d)
                    # Assign band names (Check if band names list is correct)
                    if i < len(band_names):
                        dst.set_band_description(i + 1, band_names[i])

                # Add overviews for COGs (if applicable)
                if driver == 'COG':
                    dst.build_overviews([2, 4, 8, 16, 32])

        except rio.RasterioIOError as e:
            da_logger.exception(f"Error writing raster to file {img_des}: {e}")

    def save_to_file(self, img_des: str, data: np.ndarray = None, crs: CRS = None,
                     affine_transform: Affine = None, nodata_value=None, band_names: List[str] = ()):
        """
        Save the dataset to a file.

        :param img_des: The destination file path.
        :param data: The data array to save.
        :param crs: The CRS to use.
        :param affine_transform: The affine transform to use.
        :param nodata_value: The no-data value to use.
        :param band_names: The list of band name to write in the file as description
        """
        data = self.get_data_array() if data is None else data
        crs = crs if crs else self.dataset.crs
        affine_transform = affine_transform if affine_transform else self.dataset.transform
        nodata_value = nodata_value if nodata_value else self.get_nodata_value()
        self.write_to_file(img_des, data, crs, affine_transform, nodata_value, band_names=band_names)

    def get_data_array(self, band: int = None, convert_no_data_2_nan: bool = False, envelop_gdf=None) -> np.ndarray:
        """
        Get the data array from the dataset, optionally within an envelope.

        :param band: The band number to read (1-based index). Reads all bands if None.
        :param convert_no_data_2_nan: Whether to convert no-data values to NaN.
        :param envelop_gdf: Optional GeoDataFrame containing the envelope geometry to crop data.
        :return: NumPy array of raster values.
        """
        if self.dataset is None:
            raise ValueError("Raster dataset is empty.")

        dataset = self.dataset

        if envelop_gdf is not None:
            # Ensure CRS match
            if envelop_gdf.crs != dataset.crs:
                envelop_gdf = envelop_gdf.to_crs(dataset.crs)

            # Mask raster with given envelope geometry
            geom = [envelop_gdf.unary_union]
            data_arr, _ = mask(dataset, geom, crop=True, indexes=band)
        else:
            data_arr = dataset.read(band) if band else dataset.read()

        if convert_no_data_2_nan:
            nodata_val = dataset.nodata
            if nodata_val is not None:
                if not np.issubdtype(data_arr.dtype, np.floating):
                    data_arr = data_arr.astype(np.float32)
                data_arr[data_arr == nodata_val] = np.nan

        return data_arr

    def get_data_shape(self):
        """
        Get the shape of the data array.

        :return: Tuple of (band, row, column).
        """
        data = self.get_data_array()
        bands, rows, cols = 0, 0, 0
        if len(data.shape) == 2:
            bands = 1
            rows, cols = data.shape
        elif len(data.shape) == 3:
            bands, rows, cols = data.shape
        return bands, rows, cols

    def get_crs(self) -> CRS:
        """Get the CRS of the dataset."""
        return self.dataset.crs

    def get_extent_after_skip_rows_cols(self, n_rows_skip, n_cols_skip):
        """
        Get the extent of the dataset after skipping rows and columns.

        :param n_rows_skip: Number of rows to skip.
        :param n_cols_skip: Number of columns to skip.
        :return: The new extent.
        """
        y_size, x_size = self.get_image_resolution()
        geo_t = self.get_geo_transform()
        min_x = geo_t[2] + n_cols_skip * geo_t[0]
        max_y = geo_t[5] + n_rows_skip * geo_t[4]
        max_x = geo_t[2] + geo_t[0] * (x_size - n_cols_skip)
        min_y = geo_t[5] + geo_t[4] * (y_size - n_rows_skip)
        return min_x, min_y, max_x, max_y

    def get_envelop(self, n_rows_skip: int = 0, n_cols_skip: int = 0, srid: int = 0) -> gpd.GeoDataFrame:
        """
        Build the raster envelope as a single-row GeoDataFrame.

        :param n_rows_skip: Number of rows to skip (top/bottom handling should be in your extent fn).
        :param n_cols_skip: Number of columns to skip (left/right handling should be in your extent fn).
        :param srid: Optional EPSG code to reproject the envelope to.
        :return: GeoDataFrame with one polygon row representing the envelope.
        """
        if self.dataset is None:
            raise ValueError("Dataset is not set.")

        # Get extent with or without skipping
        if n_rows_skip or n_cols_skip:
            minx, miny, maxx, maxy = self.get_extent_after_skip_rows_cols(n_rows_skip, n_cols_skip)
        else:
            minx, miny, maxx, maxy = self.get_raster_extent()

        # Build polygon in the dataset's native CRS
        gdf = gpd.GeoDataFrame(
            {"id": [1]},
            geometry=[box(minx, miny, maxx, maxy)],
            crs=self.get_crs()  # should return a pyproj CRS or EPSG int
        )

        # Reproject if requested (to_crs returns a new GeoDataFrame)
        if srid:
            gdf = gdf.to_crs(epsg=srid)

        return gdf

    def get_raster_extent(self) -> list:
        """Get the extent of the raster."""
        bounds = self.dataset.bounds
        return [bounds.left, bounds.bottom, bounds.right, bounds.top]

    def get_raster_srid(self) -> int:
        """
        Get the spatial reference ID (SRID) of the raster.

        :return: The SRID or 0 if unavailable.
        """
        if self.dataset is None:
            raise ValueError("Dataset is not set.")

        try:
            crs = self.dataset.crs
            if crs is None:
                return 0

            # Try EPSG directly
            epsg_code = crs.to_epsg()
            if epsg_code:
                return epsg_code

            # If not EPSG, try parsing from WKT
            crs_obj = CRS.from_wkt(str(crs))
            return crs_obj.to_epsg() or 0

        except Exception as e:
            da_logger.exception(f"Error getting SRID: {e}")
            return 0

    def get_geo_transform(self) -> Affine:
        """
        Get the affine transform of the dataset.

        :return: The affine transform.
            the sequence is [a,b,c,d,e,f]
        """
        return self.dataset.transform

    def get_nodata_value(self):
        """Get the no-data value of the dataset."""
        return self.dataset.nodata

    def set_nodata(self, nodata_value=None):
        """Set NoData value for the raster (requires writable dataset, e.g. mode='r+')."""
        if self.dataset is None:
            raise ValueError("Raster dataset is empty.")

        # Must be writable
        if self.dataset.mode not in ("r+", "w", "w+"):
            raise RuntimeError(
                f"Dataset is read-only (mode='{self.dataset.mode}'). "
                "Reopen with mode='r+' (or write to a new file) to set NoData."
            )

        # Choose a sensible default if not provided
        dtype = np.dtype(self.dataset.dtypes[0])
        if nodata_value is None:
            if dtype.kind in ("f",):  # float
                nodata_value = np.finfo(dtype).max  # or use np.nan if your workflow/driver supports it
            else:  # int/uint
                nodata_value = np.iinfo(dtype).min

        # Set NoData (no update_tags on DatasetReader; writable dataset will persist on close)
        self.dataset.nodata = nodata_value
        return nodata_value

    def rio_raster_from_array(self, img_arr: np.ndarray) -> 'RioRaster':
        """
        Create a RioRaster object from an array.

        :param img_arr: The image array.
        :return: A new RioRaster object.
        """
        # meta_data = self.get_meta().copy()
        raster = self.raster_from_array(img_arr, crs=self.get_crs(),
                                        g_transform=self.get_geo_transform(),
                                        nodata_value=self.get_nodata_value())
        return raster

    @staticmethod
    def raster_from_array(img_arr: np.ndarray, crs: Union[str, CRS],
                          g_transform: Affine, nodata_value=None) -> 'RioRaster':
        """
        Create a RioRaster object from an array.

        :param img_arr: The image array.
        :param crs: The CRS to use.
        :param g_transform: The affine transform to use.
        :param nodata_value: The no-data value to use.
        :return: A new RioRaster object.
        """
        try:
            memfile = rio.MemoryFile()
            if len(img_arr.shape) == 2:
                bands = 1
                rows, cols = img_arr.shape
            else:
                bands, rows, cols = img_arr.shape

            with memfile.open(driver='GTiff',
                              height=rows,
                              width=cols,
                              count=bands,
                              dtype=str(img_arr.dtype),
                              crs=crs,
                              transform=g_transform,
                              nodata=nodata_value,
                              compress='lzw',
                              BIGTIFF='YES') as dataset:
                for i in range(bands):
                    d = img_arr if len(img_arr.shape) == 2 else img_arr[i, :, :]
                    dataset.write(d, i + 1)
                dataset.close()

            dataset = memfile.open()  # Reopen as DatasetReader
            new_raster = RioRaster(dataset)
            return new_raster

        except Exception as e:
            da_logger.exception(f"Error creating raster from array: {e}")
            return None

    def get_bounds(self) -> tuple:
        """
        Get the bounding box of the raster in the format (minx, miny, maxx, maxy).

        :return: Tuple of (minx, miny, maxx, maxy).
        """
        if self.dataset is not None:
            # return self.dataset.bounds  # returns BoundingBox(minx, miny, maxx, maxy)
            return tuple(self.dataset.bounds)
        else:
            raise ValueError("Dataset is not set.")

    def clip_raster(
            self,
            aoi: Union[gpd.GeoDataFrame, shapely.geometry.Polygon, shapely.geometry.MultiPolygon],
            in_place: bool = True,
            crs: Union[int, str, CRS] = None,
            clip_within_aoi: bool = False
    ) -> 'RioRaster':
        """
        Clip the raster to an area of interest (AOI), setting nodata to the raster's nodata value (or default 0).

        :param aoi: The area of interest.
        :param in_place: Whether to modify the current object or return a new one.
        :param crs: CRS of the AOI if not already set (optional).
        :param clip_within_aoi: True to clip raster strictly inside AOI shape, False to clip by AOI bounding box.
        :return: Clipped RioRaster object (self or new).
        """
        if self.dataset is None:
            raise RuntimeError("Dataset is not set. Use set_dataset() first.")

        if isinstance(aoi, (shapely.geometry.Polygon, shapely.geometry.MultiPolygon)):
            aoi = gpd.GeoDataFrame(geometry=[aoi], crs=crs)

        if aoi.crs is None:
            if crs is None:
                raise ValueError("AOI CRS is not set and no 'crs' argument was provided.")
            aoi.set_crs(crs, inplace=True)

        if not aoi.crs.equals(self.get_crs()):
            aoi = aoi.to_crs(self.get_crs())

        raster_bounds = self.get_bounds()
        raster_box = box(*raster_bounds)

        try:
            intersecting_idx = aoi.sindex.query(raster_box, predicate="intersects")
        except Exception as e:
            da_logger.exception(f"Spatial index failed. Falling back to manual intersection. {e}")
            intersecting_idx = [i for i, geom in enumerate(aoi.geometry) if raster_box.intersects(geom)]

        if len(intersecting_idx) == 0:
            da_logger.error("❌ Raster does not intersect with AOI. Returning empty result.")
            return self if in_place else None

        aoi = aoi.iloc[intersecting_idx]

        # Extract geometry or extent
        if clip_within_aoi:
            geometries = [geom for geom in aoi.geometry if geom.is_valid and not geom.is_empty]
        else:
            bbox = aoi.total_bounds
            geometries = [box(*bbox)]

        if not geometries:
            raise ValueError("AOI contains no valid geometries.")

        # Get nodata value
        nodata_value = self.get_nodata_value()
        if nodata_value is None:
            dtype = np.dtype(self.dataset.dtypes[0])
            nodata_value = 0 if np.issubdtype(dtype, np.integer) else np.nan

        out_img, out_transform = mask(self.dataset, geometries, crop=True, nodata=nodata_value)
        out_meta = self.dataset.meta.copy()
        out_meta.update({
            "height": out_img.shape[1],
            "width": out_img.shape[2],
            "transform": out_transform,
            "nodata": nodata_value,
            "crs": self.dataset.crs,
        })

        descriptions = self.dataset.descriptions
        descriptions = descriptions if any(descriptions) else ()

        clipped = self.rio_dataset_from_array(out_img, out_meta, descriptions)

        if in_place:
            self.dataset = clipped
            return self
        else:
            return RioRaster(clipped)

    def reproject_to(self, target_crs: Union[str, CRS], in_place=False) -> 'RioRaster':
        """
        Reproject the current raster to the specified CRS.

        :param target_crs: CRS to reproject to (e.g., 'EPSG:4326' or rasterio.CRS object)
        :param in_place: If True, modifies self. Otherwise returns a new RioRaster.
        :return: Reprojected RioRaster object or self (if in_place=True)
        """
        from rasterio.warp import calculate_default_transform, reproject, Resampling

        target_crs = CRS.from_user_input(target_crs)

        transform, width, height = calculate_default_transform(
            self.dataset.crs, target_crs,
            self.dataset.width, self.dataset.height,
            *self.dataset.bounds
        )

        kwargs = self.dataset.meta.copy()
        kwargs.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        if self.dataset.nodata is not None:
            kwargs['nodata'] = self.dataset.nodata

        memfile = rio.MemoryFile()
        with memfile.open(**kwargs) as dst:
            for i in range(1, self.dataset.count + 1):
                reproject(
                    source=rio.band(self.dataset, i),
                    destination=rio.band(dst, i),
                    src_transform=self.dataset.transform,
                    src_crs=self.dataset.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest
                )

            # Set band descriptions if available
            descriptions = self.dataset.descriptions
            if descriptions:
                for i, desc in enumerate(descriptions):
                    if desc:
                        dst.set_band_description(i + 1, desc)

        new_raster = RioRaster(memfile.open())
        if in_place:
            self.dataset = new_raster.dataset
            return self
        else:
            return new_raster

    def pad_raster(self, des_raster: 'RioRaster', in_place: bool = True) -> Union[None, 'RioRaster']:
        src_crs = self.get_crs()
        des_crs = des_raster.get_crs()

        # Check CRS compatibility
        if src_crs != des_crs:
            da_logger.debug("🔄 CRS mismatch. Reprojecting source raster to match destination raster CRS...")
            self.reproject_to(des_crs, in_place=True)

        aff: Affine = self.get_geo_transform()
        des_bounds = des_raster.get_bounds()

        rows, cols = rio.transform.rowcol(
            aff,
            xs=[des_bounds[0], des_bounds[2]],
            ys=[des_bounds[3], des_bounds[1]],
        )

        height = rows[1] - rows[0]
        width = cols[1] - cols[0]

        window = windows.Window(col_off=cols[0], row_off=rows[0], width=width, height=height)
        window_transform = windows.transform(window, aff)

        kwargs = self.dataset.meta.copy()
        kwargs.update({
            'crs': self.get_crs(),
            'transform': window_transform,
            'width': width,
            'height': height
        })

        memfile = rio.MemoryFile()
        dst = memfile.open(**kwargs)

        fill = self.dataset.nodata
        if fill is None:
            fill = 0  # or any other suitable default like np.nan for float types

        data = self.dataset.read(window=window, boundless=True, fill_value=fill)
        dst.write(data)
        dst.close()
        result = RioRaster(memfile.open())

        if in_place:
            self.dataset = result.dataset
            return None
        else:
            return result

    def reclassify_raster(
            self,
            thresholds: Union[dict, List[tuple]],
            band: int = None,
            nodata: int = 0
    ) -> 'RioRaster':
        """
        Reclassify a single-band raster using defined threshold rules.

        :param thresholds: Reclassification rules in dict or list format.
            Dict example:
                {
                    "water": (('lt', 0.015), 4),
                    "built-up": ((0.015, 0.02), 1),
                    "barren": ((0.07, 0.27), 2),
                    "vegetation": (('gt', 0.27), 3)
                }
            List example:
                [
                    (('lt', 0.015), 4),
                    ((0.015, 0.02), 1),
                    ((0.07, 0.27), 2),
                    (('gt', 0.27), 3)
                ]

        :param band: 1-based band number. If not specified and multiple bands exist, raises error.
        :param nodata: Optional fallback NoData value.
        :return: A new reclassified single-band RioRaster.
        """
        if self.dataset is None:
            raise ValueError("Raster dataset is empty.")

        band_count = self.get_spectral_resolution()
        if band_count > 1 and band is None:
            raise ValueError("Multiple bands detected. Specify 'band' explicitly for reclassification.")

        band = band or 1
        img_arr = self.get_data_array(band)
        img_arr = np.squeeze(img_arr)

        # Support both dict and list threshold formats
        if isinstance(thresholds, dict):
            threshold_rules = list(thresholds.values())
        elif isinstance(thresholds, list):
            threshold_rules = thresholds
        else:
            raise TypeError("Thresholds must be a dict or a list of tuples.")

        nodata_val = self.get_nodata_value()
        if nodata_val is None or nodata_val == nodata:
            nodata_val = nodata

        classified = BandProcess.reclassify_band(img_arr, threshold_rules, nodata_val)
        result_array = np.expand_dims(classified.astype(np.uint8), axis=0)

        return self.rio_raster_from_array(result_array)

    def get_masked_array(self, band=1) -> np.ma.MaskedArray:
        """
        Return a masked NumPy array with nodata values masked out.

        :param band: Band number to read (default 1).
        :return: Masked array.
        """
        data = self.get_data_array(band)
        nodata = self.get_nodata_value()
        return np.ma.masked_where(data == nodata, data)

    # def to_xarray(self):
    #     """
    #     Convert the raster to xarray.DataArray for advanced analysis.
    #
    #     :return: xarray.DataArray object.
    #     """
    #     import rioxarray  # extends xarray with rasterio support
    #
    #     if self.dataset is None:
    #         raise ValueError("Raster dataset is empty.")
    #
    #     # rioxarray.open_rasterio returns an xarray.DataArray
    #     return rioxarray.open_rasterio(self.dataset.name, masked=True)

    @staticmethod
    def create_dummy_geotiff(
            output_path: str = "tests/data/sample_geotiff.tif",
            width: Optional[int] = None,
            height: Optional[int] = None,
            spatial_resolution: Optional[float] = None,
            count: int = 3,
            crs: str = "EPSG:4326",
            extent: Optional[Tuple[float, float, float, float]] = None,
            dtype: Union[np.dtype, str] = np.uint8,
            value_range: Optional[Tuple[float, float]] = None
    ) -> str:
        """
        Create a dummy GeoTIFF with optional extent, spatial resolution, data type, and value range.
            create_dummy_geotiff(
                output_path="tests/data/ndvi_dummy.tif",
                spatial_resolution=0.001,
                count=1,
                dtype=np.float16,
                value_range=(0.0, 1.0)
            )
        :param output_path: Output file path.
        :param width: Width in pixels (optional if spatial_resolution is set).
        :param height: Height in pixels (optional if spatial_resolution is set).
        :param spatial_resolution: Pixel resolution in CRS units (assumes square pixels).
        :param count: Number of bands.
        :param crs: Coordinate Reference System.
        :param extent: (minx, miny, maxx, maxy) bounding box.
        :param dtype: Numpy dtype or string (e.g., np.float16, "uint8").
        :param value_range: Tuple (min, max) to define data range.
        :return: Output path.
        """
        if os.path.exists(output_path):
            return output_path

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if extent is None:
            minx, miny = 74.3, 31.45
            maxx, maxy = 74.35, 31.50
            extent = (minx, miny, maxx, maxy)

        minx, miny, maxx, maxy = extent
        x_res = maxx - minx
        y_res = maxy - miny

        if spatial_resolution is not None:
            width = int(np.ceil(x_res / spatial_resolution))
            height = int(np.ceil(y_res / spatial_resolution))
        elif width is None or height is None:
            raise ValueError("Either spatial_resolution or both width and height must be provided.")

        transform = from_bounds(minx, miny, maxx, maxy, width, height)

        # Handle value range for float or int types
        if value_range is not None:
            low, high = value_range
            if np.issubdtype(np.dtype(dtype), np.integer):
                data = np.random.randint(low, high + 1, (count, height, width), dtype=dtype)
            else:
                data = np.random.uniform(low, high, (count, height, width)).astype(dtype)
        else:
            # Default random integer 0–255
            data = np.random.randint(0, 255, (count, height, width), dtype=dtype)
        import rasterio
        with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=height,
                width=width,
                count=count,
                dtype=data.dtype,
                crs=crs,
                transform=transform,
        ) as dst:
            dst.write(data)

        return output_path

    def get_band_colormap(self, band_no: int = 1) -> dict:
        """
        Reads the colormap from the specified band of the raster dataset.

        Parameters:
            band_no (int): The band number to read the colormap from. Defaults to 1.

        Returns:
            dict: A dictionary mapping pixel values to RGB(A) tuples.
                  - Keys are integer pixel values (e.g., 0, 1, 2, ...)
                  - Values are tuples of (R, G, B) or (R, G, B, A) where each is in the range 0–255
        """
        with self.get_dataset() as src:
            try:
                colormap = src.colormap(band_no)
                return colormap if colormap else {}
            except ValueError as e:
                if "NULL color table" in str(e):
                    return {}
                else:
                    raise  # Re-raise other unexpected ValueErrors

    def save_with_colormap_and_lookup_table(
            self,
            output_fp: str,
            lookup_df: pd.DataFrame,
            band_no: int = 1,
            class_column: str = "class_name",
            value_column: str = "pixel_value",
            color_column: str = "color",
            nodata_value: int = 0,
            is_hex=True
    ):
        """
        Create a new raster (single-band) with a colormap and a Raster Attribute Table (RAT),
        writing entries only for pixel values actually present in the raster data.

        Parameters:
            output_fp (str): Output raster path.
            lookup_df (pd.DataFrame): DataFrame with pixel value, color, and class name.
            band_no (int): Band number to process (default: 1).
            class_column (str): Column with class descriptions.
            value_column (str): Column with pixel values.
            color_column (str): Column with color values (hex or RGB string/tuple).
            nodata_value (int): Value used as NoData in the raster.
            is_hex (bool): Whether the color is given in hex format (e.g. "#ffbb22"). If False, assumes RGB strings or tuples.
        """

        # Enable explicit error handling in GDAL
        gdal.UseExceptions()

        def parse_color(c):
            """Parses a color from hex or RGB string/tuple into an (R, G, B) tuple"""
            if is_hex and isinstance(c, str) and c.startswith("#"):
                c = c.lstrip("#")
                return tuple(int(c[idx:idx + 2], 16) for idx in (0, 2, 4))
            if isinstance(c, str):
                return tuple(map(int, c.strip("() ").split(",")))
            return tuple(int(x) for x in c)

        # ---- Read & prepare raster data and metadata ----
        raster_data = self.get_data_array(band_no).astype("uint8")
        meta = self.get_meta().copy()
        meta.update(dtype="uint8", count=1, nodata=nodata_value)

        # Get the set of allowed pixel values from the lookup table
        allowed_values = set(lookup_df[value_column].astype(int).unique())

        #
        # Replace all values not in lookup with nodata_value
        mask_invalid = ~np.isin(raster_data, list(allowed_values))
        raster_data[mask_invalid] = nodata_value

        # Determine which pixel values are actually present (excluding NoData)
        present_values = set(np.unique(raster_data)) - {nodata_value}

        # Filter lookup table to only include present values
        lut = lookup_df[lookup_df[value_column].isin(present_values)].copy()

        # Build colormap dictionary: pixel value → (R, G, B)
        colormap = {int(r[value_column]): parse_color(r[color_column]) for _, r in lut.iterrows()}
        if nodata_value not in colormap:
            colormap[nodata_value] = (0, 0, 0)  # Black for NoData

        # ---- Write new raster and colormap using rasterio ----
        with rasterio.open(output_fp, "w", **meta) as dst:
            dst.write(raster_data, 1)
            dst.write_colormap(1, colormap)

        # ---- Write Raster Attribute Table (RAT) with GDAL ----
        ds = gdal.Open(output_fp, gdal.GA_Update)
        if ds is None:
            raise RuntimeError(f"Failed to open {output_fp} with GDAL for RAT writing.")
        band = ds.GetRasterBand(1)

        # Prepare sorted lookup for consistent row ordering
        lut_sorted = lut.copy()
        lut_sorted[value_column] = lut_sorted[value_column].astype(int)
        lut_sorted = lut_sorted.sort_values(by=value_column).reset_index(drop=True)

        # Create and populate the Raster Attribute Table (RAT)
        rat = gdal.RasterAttributeTable()
        rat.CreateColumn("Value", gdal.GFT_Integer, gdal.GFU_Generic)
        rat.CreateColumn("Label", gdal.GFT_String, gdal.GFU_Name)
        rat.CreateColumn("Red", gdal.GFT_Integer, gdal.GFU_Red)
        rat.CreateColumn("Green", gdal.GFT_Integer, gdal.GFU_Green)
        rat.CreateColumn("Blue", gdal.GFT_Integer, gdal.GFU_Blue)
        rat.SetRowCount(len(lut_sorted))

        for i, (_, row) in enumerate(lut_sorted.iterrows()):
            val = int(row[value_column])
            r, g, b = parse_color(row[color_column])
            label = str(row[class_column]) if pd.notnull(row[class_column]) else f"Class {val}"
            rat.SetValueAsInt(i, 0, val)
            rat.SetValueAsString(i, 1, label)
            rat.SetValueAsInt(i, 2, r)
            rat.SetValueAsInt(i, 3, g)
            rat.SetValueAsInt(i, 4, b)

        band.SetDefaultRAT(rat)

        # ---- Set category names (for QGIS and similar viewers) ----
        max_val = max([nodata_value] + list(present_values)) if present_values else nodata_value
        size = max(max_val + 1, 256)
        cat_names = [""] * size
        if nodata_value < size:
            cat_names[nodata_value] = "NoData"

        for _, row in lut_sorted.iterrows():
            v = int(row[value_column])
            if v < size:
                cat_names[v] = str(row[class_column]) if pd.notnull(row[class_column]) else f"Class {v}"

        try:
            band.SetCategoryNames(cat_names)
        except Exception:
            # Some formats may not support category names; ignore safely
            pass

        ds.FlushCache()
        # ds = None

    def get_band_name(self, band_no: int):
        """
        Get the name of a band. Falls back to 'Band {band_no}' if no name is available.

        :param band_no: The band number (1-based index).
        :return: The band name as a string.
        """
        if self.dataset is None:
            raise ValueError("Dataset is not set.")

        if self.dataset.descriptions and len(self.dataset.descriptions) >= band_no:
            name = self.dataset.descriptions[
                band_no - 1]  # Rasterio is 1-based indexing for bands, but descriptions list is 0-based
            if name and name.strip():
                return name

        return f"Band {band_no}"

    def get_band_summaries(self) -> pd.DataFrame:
        """
        Get summaries of all bands in the dataset.

        :return: A DataFrame containing the summaries.
        """
        summaries = {}
        for i in range(self.get_spectral_resolution()):
            band_name = self.get_band_name(i)
            data = self.get_data_array(i)
            no_data = self.get_nodata_value()
            summary = BandProcess.get_summary_data(data, nodata=no_data)
            summaries[band_name] = summary
        return pd.DataFrame(summaries).T

    def close(self):
        if self.dataset:
            self.dataset.close()
