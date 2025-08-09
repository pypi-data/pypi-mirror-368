import mercantile
from typing import List, Dict

import geopandas as gpd
from pyproj import CRS
from shapely import Polygon, box


class GPDVector(gpd.GeoDataFrame):

    def __init__(self, gdf: gpd.GeoDataFrame = None):
        if gdf is None:
            gdf = gpd.GeoDataFrame()
        elif not hasattr(gdf, 'geometry'):
            g_cols = self.get_geometry_columns(gdf)
            if len(g_cols) > 0:
                gdf.set_geometry(g_cols[0])

        super().__init__(gdf)

    @staticmethod
    def from_geojson(features: List[Dict], crs=CRS.from_epsg(4326)) -> gpd.GeoDataFrame:
        if len(features) > 0:
            gdf = gpd.GeoDataFrame.from_features(features, crs)
        else:
            gdf = gpd.GeoDataFrame()
        return gdf

    @staticmethod
    def to_geojson(gdf: gpd.GeoDataFrame):
        return gdf.__geo_interface__

    def get_gdf(self):
        return gpd.GeoDataFrame(self, crs=self.crs, geometry=self.geometry)

    @staticmethod
    def from_shapley(polygon, crs='EPSG:4326'):
        gdf = gpd.GeoDataFrame()
        gdf = gpd.GeoDataFrame(geometry=[polygon], crs=crs)
        return gdf

    @staticmethod
    def to_aoi_gdf(gdf):
        polygon = gdf.union_all()
        gdf = GPDVector.from_shapley(polygon)
        return gdf

    def is_intersects(self, gdf: gpd.GeoDataFrame):
        if str(self.crs) != str(gdf.crs):
            gdf.to_crs(self.crs)
        return self.intersects(gdf)

    @staticmethod
    def convert_tile_zxy_to_gdf(x: int, y: int, z: int) -> gpd.GeoDataFrame:
        # Get the bounds of the tile in geographic coordinates (longitude, latitude)
        bounds = mercantile.bounds(x, y, z)

        # Create a Polygon object from the bounds
        polygon = Polygon([
            (bounds.west, bounds.south),
            (bounds.west, bounds.north),
            (bounds.east, bounds.north),
            (bounds.east, bounds.south),
            (bounds.west, bounds.south)  # Close the polygon
        ])

        # Create a GeoDataFrame from the polygon
        gdf = gpd.GeoDataFrame({'tile': [(x, y, z)], 'geometry': [polygon]})

        # Set the coordinate reference system to WGS84 (EPSG:4326)
        gdf.set_crs(epsg=4326, inplace=True)
        return gdf

    @staticmethod
    def get_zxy_tiles(aoi_gdf: gpd.GeoDataFrame, zoom, inside_aoi=True) -> gpd.GeoDataFrame:
        # Ensure the input GeoDataFrame is in the correct CRS
        aoi_gdf = aoi_gdf.to_crs(epsg=4326)

        # Get the extent of the AOI in WGS84
        extent = list(aoi_gdf.total_bounds)

        # Generate tiles within the specified extent
        tiles = []
        for tile in mercantile.tiles(*extent, zooms=zoom):
            tile_bounds = mercantile.bounds(tile)
            geom = box(tile_bounds.west, tile_bounds.south, tile_bounds.east, tile_bounds.north)
            # Check if the tile intersects with the AOI
            data = {"x": tile.x, "y": tile.y, "z": tile.z, "geometry": geom}
            if inside_aoi:
                if aoi_gdf.intersects(geom).any():
                    tiles.append(data)
            else:
                tiles.append(data)

        # Create a GeoDataFrame from the list of tiles
        gdf = gpd.GeoDataFrame(tiles, crs='EPSG:4326', geometry='geometry')

        return gdf
