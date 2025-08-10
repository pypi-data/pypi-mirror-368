import os
from io import BytesIO
from typing import Dict, Union, Literal, List, Optional, Tuple

import mercantile
import numpy as np
import pyproj
import rasterio
import shapely
from PIL import Image

from geopandas import GeoDataFrame
from pydantic import BaseModel
from rasterio.session import AWSSession
from rio_tiler.io import COGReader
from rio_tiler.colormap import cmap
from rio_tiler.models import ImageData

from digitalarzengine.io.file_io import FileIO
from digitalarzengine.io.rio_raster import RioRaster
from digitalarzengine.processing.operations.transformation_ops import TransformationOperations
from digitalarzengine.processing.raster.rio_process import RioProcess
from digitalarzengine.utils.singletons import da_logger


class ContinuousStyle(BaseModel):
    """
     🎨 Example 1: Continuous Style
    {
        "type": "continuous",
        "min": 0,
        "max": 100,
        "palette": ["#0000FF", "#00FF00", "#FF0000"]
    }
    """

    type: Literal["continuous"]
    min: float
    max: float
    palette: List[str]


class DiscreteStyle(BaseModel):
    """
        🎨 Example 2: Discrete Style
        {
            "type": "discrete",
            "values": [0, 25, 50, 75, 100],
            "palette": {
                0: "#0000FF",
                1: "#00FFFF",
                2: "#00FF00",
                3: "#FFFF00",
                4: "#FF0000"
            },
            "min_val": 0,
            "max_val": 100
        }

    """
    type: Literal["discrete"]
    values: List[float]
    palette: Dict[int, str]
    min_val: Optional[float] = None
    max_val: Optional[float] = None


RasterStyleTypes = Union[ContinuousStyle, DiscreteStyle]


class COGRaster(COGReader):
    """
    Extended COGReader class for handling Cloud Optimized GeoTIFFs (COGs) from both local and S3 sources,
    supporting tile rendering, AOI clipping, custom color maps, and more.
    """

    file_path: str

    def __init__(self, input, **kwargs):
        super().__init__(input, **kwargs)
        self.file_path = input
        self.global_minmax = self._compute_global_minmax()

    def _compute_global_minmax(self):
        try:
            stats = self.dataset.read(1, masked=True)
            return float(stats.min()), float(stats.max())
        except Exception as e:
            da_logger.warning(f"Failed to compute global min/max: {e}")
            return 0, 255  # Fallback

    @staticmethod
    def open_cog(fp: str, s3_session=None) -> 'COGRaster':
        """
        Open a COG from local or S3 path.
        :param fp: File path or S3 URI.
        :param s3_session: AWS session for accessing S3.
        """
        if "s3://" in fp:
            return COGRaster.open_from_s3(fp, s3_session)
        return COGRaster.open_from_local(fp)

    @classmethod
    def open_from_url(cls, url: str) -> 'COGRaster':
        cog_raster = cls(url)
        cog_raster.file_path = url
        return cog_raster

    @classmethod
    def open_from_local(cls, file_path: str) -> 'COGRaster':
        cog_raster = cls(file_path)
        cog_raster.file_path = file_path
        return cog_raster

    @classmethod
    def open_from_s3(cls, s3_uri: str, session) -> 'COGRaster':
        """
        Open a COG file hosted on S3.
        """
        try:
            with rasterio.Env(AWSSession(session)):
                cog_raster = cls(s3_uri)
                cog_raster.file_path = s3_uri
                return cog_raster
        except Exception as e:
            da_logger.error(f"Failed to open COG from S3: {e}")
            raise

    def get_file_path(self) -> str:
        """
        Returns the file path of the COG.
        """
        return self.file_path

    def get_rio_raster(
            self,
            mask_area: Union[GeoDataFrame, shapely.geometry.Polygon, shapely.geometry.MultiPolygon] = None,
            crs=0
    ) -> RioRaster:
        """
        Returns a RioRaster object clipped to a given area.
        :param mask_area: GeoDataFrame or Polygon geometry.
        :param crs: Coordinate reference system.
        """
        if isinstance(mask_area, GeoDataFrame) and crs == 0:
            crs = mask_area.crs
        raster = RioRaster(self.dataset)
        if mask_area is not None:
            raster.clip_raster(mask_area, crs=crs)
        return raster

    @classmethod
    def create_cog(cls, src: Union[str, RioRaster], des_path: str = None, profile: str = "deflate") -> str:
        """
        Create a Cloud Optimized GeoTIFF from a source raster or file path.
        """
        if isinstance(src, str):
            src_raster = RioRaster(src)
            file_path = src
        else:
            file_path = src.get_file_name()
            src_raster = src

        if des_path is None:
            filename, _ = FileIO.get_file_name_ext(file_path)
            dirname = os.path.dirname(file_path)
            des_path = os.path.join(dirname, f"{filename}.cog")
        else:
            os.makedirs(os.path.dirname(des_path), exist_ok=True)

        src_raster.save_to_file(des_path)
        da_logger.info(f"Saved COG to {des_path}")
        return des_path

    @staticmethod
    def create_color_map(style: Union[RasterStyleTypes, dict]):
        """
        Creates a color map based on the given style, handling both palette lists and dictionaries.

        :param style: A Pydantic model or dictionary containing 'min', 'max', 'palette', and optionally 'values'.
        :return: A list of ((range_start, range_end), (R, G, B, A)) tuples or a registered colormap.
        """

        # Helper to safely get attribute or dict key
        def get(attr):
            return style[attr] if isinstance(style, dict) else getattr(style, attr)

        palette = get('palette')
        custom_color = {}

        # Build RGBA tuples from palette
        if isinstance(palette, dict):
            for j_str, hex_color in palette.items():
                j = int(j_str)  # Convert key to integer
                h = f"{hex_color}FF".lstrip('#')  # Add alpha if missing
                custom_color[j] = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
        else:
            for j_str, hex_color in palette.items():
                j = int(j_str)  # Convert key to integer
                h = f"{hex_color}FF".lstrip('#')
                custom_color[j] = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))

        # Handle discrete style with 'values'
        if (isinstance(style, dict) and "values" in style) or (
                not isinstance(style, dict) and hasattr(style, "values") and style.values):
            values = sorted(get('values'), key=float)
            min_val = get('min_val')
            max_val = get('max_val')

            if min_val is not None and values[0] > min_val:
                values[0] = min_val
            if max_val is not None:
                values.append(max_val if values[-1] < max_val else values[-1] + 1)

            color_map = []
            for i in range(len(custom_color)):
                color_map.append(((values[i], values[i + 1]), custom_color[i]))
            return color_map

        # Handle continuous style with 'min' and 'max'
        elif (isinstance(style, dict) and "min" in style and "max" in style) or \
                (not isinstance(style, dict) and hasattr(style, "min") and hasattr(style, "max")):
            min_val = get("min")
            max_val = get("max")
            step = (max_val - min_val) / (len(custom_color) - 1)
            values = [min_val + i * step for i in range(len(custom_color))]

            color_map = []
            for i in range(len(custom_color) - 1):
                color_map.append(((values[i], values[i + 1]), custom_color[i]))
            color_map.append(((values[-1], float('inf')), custom_color[len(custom_color) - 1]))
            return color_map

        # Fallback to registered colormap (optional use case)
        else:
            cp = cmap.register({"cc": custom_color})
            return cp.get("cc")

    def read_tile_as_png(self, x: int, y: int, z: int, color_map: dict, tile_size=256):
        try:
            tile: ImageData = self.tile(x, y, z, tilesize=tile_size)
            return BytesIO(tile.render(True, colormap=color_map, img_format='PNG'))
        except Exception as e:
            da_logger.exception(f"An exception occurred reason: {e}")
            return self.create_empty_image(tile_size, tile_size)

    @staticmethod
    def create_alpha_band(size_x, size_y):
        return np.zeros([size_x, size_y], dtype=np.uint8)

    def create_empty_image(self, size_x, size_y, format="PNG"):
        """
        Create a blank image in RGBA format.
        """
        blank_image = np.zeros([size_x, size_y, 4], dtype=np.uint8)
        return self.create_image(blank_image, format=format)

    @staticmethod
    def create_image(np_array, format="PNG") -> BytesIO:
        """
        Convert NumPy array to image bytes in specified format.
        """
        img = Image.fromarray(np_array)

        if format.upper() == "JPEG" and img.mode == "RGBA":
            img = img.convert("RGB")  # Drop alpha channel

        buffer = BytesIO()
        img.save(buffer, format=format)
        return buffer

    def get_pixel_value_at_long_lat(self, long: float, lat: float):
        """
        Get pixel value at geographic coordinates.
        """
        try:
            return self.point(long, lat)
        except Exception as e:
            da_logger.error(f"Failed to get pixel value at ({long}, {lat}): {e}")
            return None

    def read_tile(self, tile_x: int, tile_y: int, tile_z: int, tile_size: int = 256):
        """
        Read a specific tile.
        """
        try:
            if self.tile_exists(tile_x, tile_y, tile_z):
                return self.tile(tile_x, tile_y, tile_z, tilesize=tile_size)
            return self.create_empty_image(tile_size, tile_size), None
        except Exception as e:
            da_logger.error(f"Failed to read tile ({tile_x}, {tile_y}, {tile_z}): {e}")
            return self.create_empty_image(tile_size, tile_size), None

    def read_data_under_aoi(self, gdf: GeoDataFrame) -> RioRaster:
        """
        Read all tiles covering the AOI geometry and return as a single mosaic.
        """
        try:
            max_zoom = self.maxzoom
            tiles = mercantile.tiles(*gdf.to_crs(epsg=4326).total_bounds, zooms=max_zoom)
            ds_files = []
            for tile in tiles:
                data, mask = self.read_tile(tile.x, tile.y, tile.z)
                if isinstance(data, BytesIO):
                    data = np.zeros((1, 256, 256))
                extent = mercantile.bounds(*tile)
                raster = self.raster_from_array(data, mask, list(extent))
                ds_files.append(raster.get_dataset())
            return RioProcess.mosaic_images(ds_files=ds_files)
        except Exception as e:
            da_logger.error(f"Failed to read data under AOI: {e}")
            return RioRaster(None)

    def raster_from_array(self, data, mask, extent: list, tile_size=256) -> RioRaster:
        """
        Create a RioRaster from NumPy array using extent.
        """
        meta = self.dataset.meta
        g_transform = TransformationOperations.get_affine_matrix(extent, (tile_size, tile_size))
        return RioRaster.raster_from_array(data, crs=meta['crs'], g_transform=g_transform,
                                           nodata_value=meta.get('nodata', 0))

    def save_tile_as_geotiff(self, tile_x: int, tile_y: int, tile_z: int, output_filename: str):
        """
        Save a tile as a GeoTIFF file.
        """
        if not self.tile_exists(tile_x, tile_y, tile_z):
            da_logger.error(f"Tile ({tile_x}, {tile_y}, {tile_z}) does not exist.")
            return

        try:
            tile_bounds = list(mercantile.xy_bounds(mercantile.Tile(tile_x, tile_y, tile_z)))
            tile_data, _ = self.tile(tile_x, tile_y, tile_z)
            tile_data = np.squeeze(tile_data)

            with rasterio.open(
                    output_filename,
                    'w',
                    driver='GTiff',
                    height=tile_data.shape[0],
                    width=tile_data.shape[1],
                    count=1 if tile_data.ndim == 2 else tile_data.shape[0],
                    dtype=str(tile_data.dtype),
                    crs=pyproj.CRS.from_string("EPSG:3857"),
                    transform=rasterio.transform.from_bounds(*tile_bounds, tile_data.shape[1], tile_data.shape[0]),
                    nodata=self.dataset.nodata
            ) as dst:
                if tile_data.ndim == 2:
                    dst.write(tile_data, 1)
                else:
                    dst.write(tile_data)
        except Exception as e:
            da_logger.error(f"Failed to save tile as GeoTIFF: {e}")


    def get_tile_coordinates_at_zoom(self, zoom: int) -> List[Tuple[int, int]]:
        """
        Returns a list of (tile_x, tile_y) tuples for all tiles that intersect the COG
        file's bounds at a specified zoom level.

        :param zoom: The desired zoom level (z).
        :return: A list of (tile_x, tile_y) tuples.
        """
        tile_coords = []
        try:
            # Get the bounding box of the COG from the dataset's profile.
            cog_bounds = self.dataset.bounds

            # Check if the dataset has a CRS
            if not self.dataset.crs:
                da_logger.error("Dataset has no CRS. Cannot determine tile coordinates.")
                return []

            # The `mercantile.tiles` function expects WGS84 (EPSG:4326) bounds.
            # We need to transform the COG's bounds if they are not already in EPSG:4326.
            if self.dataset.crs.to_string() != 'EPSG:4326':
                transformer = pyproj.Transformer.from_crs(self.dataset.crs, 'EPSG:4326', always_xy=True)
                min_lon, min_lat = transformer.transform(cog_bounds.left, cog_bounds.bottom)
                max_lon, max_lat = transformer.transform(cog_bounds.right, cog_bounds.top)
            else:
                min_lon, min_lat, max_lon, max_lat = cog_bounds

            # Use mercantile to get the tiles that intersect the transformed bounds at the specified zoom.
            # We iterate through the tile generator and extract the x and y coordinates.
            for tile in mercantile.tiles(min_lon, min_lat, max_lon, max_lat, zooms=zoom):
                tile_coords.append((tile.x, tile.y))
        except Exception as e:
            da_logger.error(f"Failed to get tile coordinates at zoom {zoom}: {e}")
            return []

        return tile_coords

    def get_tile_values_at_tile_coords(self, tile_x: int, tile_y: int, tile_z: int, band_number: int = 1) -> List[
        Tuple[float, float, float]]:
        """
        Returns a list of (x, y, z) tuples for a specific tile at a given zoom level.
        The 'x' and 'y' are geospatial coordinates, and 'z' is the pixel value.
        :param tile_x: The x-coordinate of the tile.
        :param tile_y: The y-coordinate of the tile.
        :param tile_z: The zoom level (z) of the tile.
        :param band_number: The band number to read data from. Defaults to 1.
        """
        try:
            # Read the data and transform for a specific tile.
            tile_data, _ = self.tile(tile_x, tile_y, tile_z, tilesize=256, indexes=band_number)

            # Squeeze the data to get a 2D array if it's 3D (e.g., shape (1, 256, 256))
            tile_data = np.squeeze(tile_data)

            # Get the bounds of the tile
            tile_bounds = mercantile.xy_bounds(mercantile.Tile(tile_x, tile_y, tile_z))

            # Create an affine transform for the tile
            tile_transform = rasterio.transform.from_bounds(*tile_bounds, tile_data.shape[1], tile_data.shape[0])

            xyz_values = []

            # Iterate through each pixel of the tile
            for row in range(tile_data.shape[0]):
                for col in range(tile_data.shape[1]):
                    z_value = float(tile_data[row, col])
                    x_coord, y_coord = tile_transform * (col, row)
                    xyz_values.append((x_coord, y_coord, z_value))

            return xyz_values

        except Exception as e:
            da_logger.error(f"Failed to get xyz for tile ({tile_x}, {tile_y}, {tile_z}): {e}")
            return []
