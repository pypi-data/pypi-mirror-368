from __future__ import annotations

import math
from time import time

from scipy.spatial import KDTree
import numpy as np
import geopandas as gpd
from shapely.geometry import shape
from rasterio.features import shapes
from affine import Affine

from digitalarzengine.utils.singletons import da_logger


class BandProcess:

    @staticmethod
    def reclassify_band(img_arr: np.array, thresholds: dict, nodata=0) -> np.array:
        """
        img_arr: must be as row, col
        :param thresholds:
            example:  {
                    "water": (('lt', 0.015), 4),
                    "built-up": ((0.015, 0.02), 1),
                    "barren": ((0.07, 0.27), 2),
                    "vegetation": (('gt', 0.27), 3)
                }

        """
        if img_arr.ndim > 2:
            img_arr = np.squeeze(img_arr)
        res = np.empty(img_arr.shape)
        res[:] = nodata
        for key in thresholds:
            if thresholds[key][0][0] == 'lt':
                res = np.where(img_arr <= thresholds[key][0][1], thresholds[key][1], res)
            elif thresholds[key][0][0] == 'gt':
                res = np.where(img_arr >= thresholds[key][0][1], thresholds[key][1], res)
            else:
                con = np.logical_and(img_arr >= thresholds[key][0][0], img_arr <= thresholds[key][0][1])
                res = np.where(con, thresholds[key][1], res)
        return res.astype(np.uint8)

    @staticmethod
    def create_binary_mask(band_data: np.ndarray, class_value, tol: float = 1e-6) -> np.ndarray:
        """
        Binary mask: 1 where band_data equals class_value, else 0.
        Works for ints and floats; ignores NaNs.
        """
        arr = band_data
        if np.issubdtype(arr.dtype, np.floating):
            mask = np.isclose(arr, class_value, atol=tol, equal_nan=False)
        else:
            mask = (arr == class_value)
        # Ensure NaNs never match
        if np.issubdtype(arr.dtype, np.floating):
            mask &= ~np.isnan(arr)
        return mask.astype(np.uint8)

    @staticmethod
    def raster_2_polygon(
            band_data: np.ndarray,
            classes: list | None = None,
            transform: Affine | None = None,
            crs=None,
            simplify_tol: float = 0.0,
            float_match_tol: float = 1e-6,
    ) -> gpd.GeoDataFrame:
        """
        Vectorize class regions to polygons using rasterio.features.shapes (keeps georeference).

        :param band_data: 2D array of raster values.
        :param classes: Optional list of class values to extract. If None, inferred from data (excludes NaN).
        :param transform: Affine transform mapping pixel -> CRS coordinates. REQUIRED for proper georeferencing.
        :param crs: CRS for the output GeoDataFrame (e.g., dataset.crs or EPSG int).
        :param simplify_tol: Optional simplification tolerance (units of CRS). 0 disables.
        :param float_match_tol: Tolerance for float equality when building masks.
        :return: GeoDataFrame with columns ['class', 'geometry'].
        """
        if band_data.ndim != 2:
            raise ValueError("band_data must be a 2D array (single band).")

        if transform is None:
            # Without a transform, polygons will be in pixel coordinates. Usually not desired.
            # You can pass Affine.identity() if you explicitly want pixel space.
            transform = Affine.identity()

        # Auto-detect classes if not provided
        if classes is None:
            if np.issubdtype(band_data.dtype, np.floating):
                unique_vals = np.unique(band_data[~np.isnan(band_data)])
            else:
                unique_vals = np.unique(band_data)
            classes = unique_vals.tolist()

        records = []
        for class_value in classes:
            # Build a binary mask for this class
            binary_mask = BandProcess.create_binary_mask(band_data, class_value, tol=float_match_tol)

            # Vectorize: shapes() yields (geom, value) for connected regions with identical values
            # We pass the binary mask so value==1 means the target class
            for geom, val in shapes(binary_mask, mask=None, transform=transform):
                if val != 1:
                    continue
                poly = shape(geom)
                if not poly.is_empty:
                    if simplify_tol > 0.0:
                        poly = poly.simplify(simplify_tol, preserve_topology=True)
                        if poly.is_empty:
                            continue
                    records.append({"class": class_value, "geometry": poly})

        gdf = gpd.GeoDataFrame(records, crs=crs)
        return gdf

    @staticmethod
    def get_summary_data(
            data: np.ndarray,
            nodata=None,
            ignore_negative_values=True,
            ignore_values: list = (),
    ):
        """
        Returns dict with keys: mean, median, std, min, q25, q75, max, sum
        All NaN-safe. nodata and ignore_values are masked with float-safe comparisons.
        """
        data = data.astype(np.float64)  # for NaN ops

        # Float-safe nodata masking
        if nodata is not None:
            if np.issubdtype(data.dtype, np.floating):
                data[np.isclose(data, nodata, rtol=0.0, atol=1e-9)] = np.nan
            else:
                data[data == nodata] = np.nan

        # Mask explicit ignore values
        for value in ignore_values:
            if np.issubdtype(data.dtype, np.floating):
                data[np.isclose(data, value, rtol=0.0, atol=1e-9)] = np.nan
            else:
                data[data == value] = np.nan

        if ignore_negative_values:
            data[data <= 0] = np.nan

        if np.isnan(data).all():
            return {
                "mean": np.nan, "median": np.nan, "std": np.nan,
                "min": np.nan, "q25": np.nan, "q75": np.nan, "max": np.nan, "sum": np.nan
            }

        return {
            "mean": np.nanmean(data),
            "median": np.nanquantile(data, 0.5),
            "std": np.nanstd(data),
            "min": np.nanmin(data),
            "q25": np.nanquantile(data, 0.25),
            "q75": np.nanquantile(data, 0.75),
            "max": np.nanmax(data),
            "sum": np.nansum(data),
        }

    @classmethod
    def get_value_area_data(
            cls, data: np.ndarray, no_data,
            spatial_res, values=None,
            value_labels=None,  # dict|list|tuple|callable -> label per value (optional)
            unit: str = None,  # text label for the output unit
    ) -> list:
        """
        Compute area per pixel value.

        Parameters
        ----------
        data : np.ndarray
            Raster array.
        no_data : any
            No-data value.
        spatial_res : tuple|number
            (res_x, res_y) or a single area-per-pixel value (already in squared units).
            If tuple/list of length 2 -> area_per_pixel = res_x * res_y
            Else -> area_per_pixel = spatial_res (assumed already an area or a side length if you intend so).
        values : list, optional
            Subset of pixel values to include (passed through to get_value_count_data).
        value_labels : dict|list|tuple|callable, optional
            - dict: {value: "label"}
            - list/tuple: aligned with `values` (same order)
            - callable: f(value) -> "label"
        unit : str
            Output unit label (e.g., "sq. m", "sq. km", "sq. units").

        Returns
        -------
        list[dict]
            Each item: {"value": <val>, "area": <float>, "unit": <str>, "label": <str?>}
        """
        value_count = cls.get_value_count_data(data, no_data, values)
        out = []

        # Determine area per pixel in the SAME units as spatial_res
        if isinstance(spatial_res, (list, tuple)) and len(spatial_res) == 2:
            area_per_pixel = spatial_res[0] * spatial_res[1]
        else:
            area_per_pixel = spatial_res

        # Helper to resolve label
        def resolve_label(val):
            da_logger.debug(f"value {val}")
            if value_labels is None:
                return None
            if callable(value_labels):
                return value_labels(val)
            if isinstance(value_labels, dict):
                return value_labels.get(val)
            if isinstance(value_labels, (list, tuple)) and values is not None:
                try:
                    v = int(val)
                    return value_labels[v] if v < len(value_labels) else None
                except ValueError:
                    return None
            return None

        for v in value_count:
            val = v["value"]
            item = {
                "value": val,
                "area": v["count"] * area_per_pixel,
            }
            if unit is not None: item["unit"] = unit
            lbl = resolve_label(val)
            if lbl is not None:
                item["label"] = lbl
            out.append(item)

        return out

    @staticmethod
    def get_value_count_data(
            data: np.ndarray,
            no_data,
            values=None,
            value_labels=None  # optional label mapping
    ) -> list:
        """
        :param data: np.ndarray, e.g., data = raster.get_data_array(band_no)
        :param no_data: No-data value from raster
        :param values: list of pixel values or ranges; if None, values are auto-detected
        :param value_labels: dict|list|tuple|callable
            - dict: {value: "label"}
            - list/tuple: aligned with `values` order
            - callable: f(value) -> "label"
        :return: list of dicts like {"value": <val/range>, "count": <int>, "label": <label?>}
        """
        if no_data is not None and 'float' in str(data.dtype):
            data[data == no_data] = np.nan

        if values is None:
            if "float" in str(data.dtype):
                min_value = math.ceil(np.nanquantile(data, 0.25))
                max_value = math.ceil(np.nanquantile(data, 0.75))
                values = []
                prev_val = None
                for v in range(min_value, max_value):
                    if v in [min_value, max_value]:
                        values.append((v,))
                    else:
                        values.append((prev_val, v))
                    prev_val = v
            else:
                values = np.unique(data)
                values = values[values != no_data]
        else:
            if "float" in str(data.dtype) and not isinstance(values[0], tuple):
                val = [float(v) for v in values]
                values = []
                for i in range(len(val)):
                    if i == 0 or i == len(val) - 1:
                        values.append((val[i],))
                    else:
                        values.append((val[i - 1], val[i]))

        # Helper to resolve label
        def resolve_label(val, idx):
            if value_labels is None:
                return None
            if callable(value_labels):
                return value_labels(val)
            if isinstance(value_labels, dict):
                return value_labels.get(val)
            if isinstance(value_labels, (list, tuple)):
                return value_labels[idx] if idx < len(value_labels) else None
            return None

        output = []
        for idx, v in enumerate(values):
            if isinstance(v, tuple):
                if len(v) == 1 and idx == 0:
                    count = np.count_nonzero(data <= v[0])
                    key = f"<= {v[0]}"
                elif len(v) == 1 and idx != 0:
                    count = np.count_nonzero(data >= v[0])
                    key = f">= {v[0]}"
                else:
                    count = np.count_nonzero((data > v[0]) & (data <= v[1]))
                    key = " - ".join(map(str, v))
            else:
                v = float(v) if isinstance(v, str) else v
                count = np.count_nonzero(data == v)
                key = str(v)

            item = {"value": key, "count": count}
            lbl = resolve_label(key, idx)
            if lbl is not None:
                item["label"] = lbl
            output.append(item)

        return output

    @staticmethod
    def get_boolean_raster(data: np.ndarray, pixel_value: list):
        con = None
        for v in pixel_value:
            con = data == v if con is None else np.logical_or(con, data == v)
        res = np.where(con, 1, 0)
        res = res.astype(np.uint8)
        return res

    @staticmethod
    def create_distance_raster(data: np.ndarray, pixel_value, pixel_size_in_km=1):
        boolean_data = BandProcess.get_boolean_raster(data, pixel_value)
        dist_array = np.empty(boolean_data.shape, dtype=float)
        try:
            print("calculating distance raster")
            tree = KDTree(data=np.array(np.where(boolean_data == 1)).T, leafsize=64)
            t_start = time()
            for cur_index, val in np.ndenumerate(boolean_data):
                min_dist, min_index = tree.query([cur_index])
                if len(min_dist) > 0 and len(min_index) > 0:
                    min_dist = min_dist[0]
                    min_index = tree.data[min_index[0]]
                    # dist = math.sqrt(math.pow((cur_index[0] - min_index[0]),2)+math.pow((cur_index[1] - min_index[1]),2))
                    # print(min_dist, dist)
                    # if self.affine is not None:
                    #     if cur_index[1] == min_index[1]:
                    #         # columns are same meaning nearest is either vertical or self.
                    #         # no correction needed, just convert to km
                    #         dd_min_dist = min_dist * self.pixel_size
                    #         km_min_dist = dd_min_dist * 111.321
                    #
                    #     else:
                    #         km_min_dist = calc_haversine_distance(
                    #             convert_index_to_coords(cur_index, self.affine),
                    #             convert_index_to_coords(min_index, self.affine),
                    #         )
                    #
                    #     val = km_min_dist * 1000
                    #
                    # else:
                    # val = min_dist
                    dist_array[cur_index[0]][cur_index[1]] = min_dist * pixel_size_in_km
            e_time = time()
            print("Distance calc run time: {0} seconds".format(round(time() - t_start, 4)))
        except Exception as e:
            print(str(e))
        return dist_array
