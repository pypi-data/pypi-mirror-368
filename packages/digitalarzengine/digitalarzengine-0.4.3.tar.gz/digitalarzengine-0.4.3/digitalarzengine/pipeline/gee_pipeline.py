import enum
import os

import geopandas as gpd
from typing import Union

from digitalarzengine.io.gee.gee_auth import GEEAuth
from digitalarzengine.io.gee.gee_region import GEERegion
from digitalarzengine.io.gee.gpd_vector import GPDVector
from digitalarzengine.settings import BASE_DIR


class GEETags(enum.Enum):
    Water = {"modis": 'MODIS/061/MOD09A1'}
    Temperature = {"modis": 'MODIS/061/MOD11A1'}
    SnowCover = {"modis": 'MODIS/061/MOD10A1'}  # MODIS/061/MOD10A1


class GEEPipeline:
    aoi_gdv: GPDVector = None
    region: GEERegion = None
    gee_auth: GEEAuth = None  # ✅ Class-level singleton authentication

    def __init__(self,aoi: Union[GPDVector, gpd.GeoDataFrame] = None, is_browser=False):
        """Initialize GEE Pipeline, ensuring authentication is initialized once."""
        self.ensure_gee_initialized(is_browser)
        if aoi is not None and not aoi.empty:
            self.set_region(aoi)

    @classmethod
    def ensure_gee_initialized(cls,is_browser=False):
        """Ensures Google Earth Engine is authenticated and re-initializes if necessary."""
        if cls.gee_auth is None or not cls.gee_auth.is_initialized:
            cls.set_gee_auth(is_browser)
        else:
            print("✅ Google Earth Engine already initialized")

    @classmethod
    def set_gee_auth(cls, is_browser=False):
        """Initializes GEE authentication only once per application run."""
        if is_browser:
            GEEAuth.gee_init_browser()
        else:
            gee_service_account_fp = os.path.join(BASE_DIR, 'config', 'ee-atherashraf-cloud-d5226bc2c456.json')
            cls.gee_auth = GEEAuth.geo_init_personal('atherashraf@gmail.com', gee_service_account_fp)
            # print("✅ Google Earth Engine Authentication Initialized")

    def set_region(self, aoi: Union[GPDVector, gpd.GeoDataFrame]):
        """Sets the area of interest (AOI) and converts it into GEE Region format."""
        if isinstance(aoi, gpd.GeoDataFrame):
            aoi = GPDVector(aoi)

        if aoi.get_gdf().crs.to_epsg() != 4326:
            aoi = aoi.get_gdf().to_crs(epsg=4326)

        polygon = aoi.union_all()
        gdf = gpd.GeoDataFrame(geometry=[polygon], crs=aoi.crs)
        self.aoi_gdv = GPDVector(gdf)
        geojson = self.aoi_gdv.to_geojson(self.aoi_gdv.get_gdf())
        self.region = GEERegion.from_geojson(geojson)
