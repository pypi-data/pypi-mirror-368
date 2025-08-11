import os

from digitalarzengine.settings import PAK_DATA_DIR
import geopandas as gpd

class PakData(object):

   @staticmethod
   def get_pak_basins():
       fp = os.path.join(PAK_DATA_DIR, 'pak_basins.gpkg')
       gdf = gpd.read_file(fp)
       gdf = gdf.to_crs(epsg=4326)
       return gdf

   @staticmethod
   def get_snow_covered_basins() -> gpd.GeoDataFrame:
       fp = os.path.join(PAK_DATA_DIR, 'pak_basins.gpkg')
       gdf = gpd.read_file(fp)
       gdf = gdf[gdf['is_snow_covered']==True]
       gdf = gdf.to_crs(epsg=4326)
       return gdf

   @classmethod
   def get_district_boundary(cls):
       pass