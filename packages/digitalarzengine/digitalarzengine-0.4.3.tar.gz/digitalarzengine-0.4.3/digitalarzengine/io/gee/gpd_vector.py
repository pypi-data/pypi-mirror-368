from typing import List, Dict, Iterable, Union, Optional

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Polygon, box, base as shapely_base
import mercantile


class GPDVector(gpd.GeoDataFrame):
    """
    A light subclass of GeoDataFrame with a few convenience constructors and helpers.
    """

    # Tell pandas/geopandas which attributes to carry over in operations
    _metadata: list[str] = []

    def __init__(self, gdf: Optional[gpd.GeoDataFrame] = None):
        if gdf is None:
            gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        elif not hasattr(gdf, "geometry"):
            g_cols = self.get_geometry_columns(gdf)
            if g_cols:
                gdf = gdf.set_geometry(g_cols[0], crs=getattr(gdf, "crs", None))

        super().__init__(gdf)

    @property
    def _constructor(self):
        # ensure geopandas operations return our subclass
        return GPDVector

    # --------------------------
    # Constructors / converters
    # --------------------------
    @staticmethod
    def from_geojson(features: List[Dict], crs: Union[CRS, str, int] = CRS.from_epsg(4326)) -> "GPDVector":
        gdf = gpd.GeoDataFrame.from_features(features, crs=crs) if features else gpd.GeoDataFrame(geometry=[], crs=crs)
        return GPDVector(gdf)

    @staticmethod
    def to_geojson(gdf: gpd.GeoDataFrame) -> Dict:
        # Returns a GeoJSON-like mapping
        return gdf.__geo_interface__

    def get_gdf(self) -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(self.copy(), crs=self.crs, geometry=self.geometry.name)

    @staticmethod
    def from_shapely(geom: shapely_base.BaseGeometry, crs: Union[str, int, CRS] = "EPSG:4326") -> "GPDVector":
        gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[geom], crs=crs)
        return GPDVector(gdf)

    @staticmethod
    def to_aoi_gdf(gdf: gpd.GeoDataFrame) -> "GPDVector":
        # robust union that works across versions
        union_geom = gdf.geometry.unary_union
        return GPDVector.from_shapely(union_geom, crs=gdf.crs)

    # --------------------------
    # Spatial ops
    # --------------------------
    def is_intersects(self, other: Union[gpd.GeoDataFrame, shapely_base.BaseGeometry]) -> gpd.GeoSeries:
        """
        Intersects test against another GeoDataFrame (using its unary union) or a single geometry.
        Returns a boolean Series aligned to self.
        """
        if isinstance(other, gpd.GeoDataFrame):
            other2 = other if str(other.crs) == str(self.crs) else other.to_crs(self.crs)
            target = other2.geometry.unary_union
        else:
            # assume shapely geometry; project if necessary (user responsibility)
            target = other
        return self.geometry.intersects(target)

    # --------------------------
    # Tiling helpers
    # --------------------------
    @staticmethod
    def convert_tile_zxy_to_gdf(x: int, y: int, z: int) -> "GPDVector":
        b = mercantile.bounds(x, y, z)
        poly = Polygon([(b.west, b.south), (b.west, b.north), (b.east, b.north), (b.east, b.south)])
        gdf = gpd.GeoDataFrame({"x": [x], "y": [y], "z": [z]}, geometry=[poly], crs="EPSG:4326")
        return GPDVector(gdf)

    @staticmethod
    def get_zxy_tiles(aoi_gdf: gpd.GeoDataFrame, zoom: Union[int, Iterable[int]], inside_aoi: bool = True) -> "GPDVector":
        # Ensure WGS84
        aoi_4326 = aoi_gdf.to_crs(epsg=4326)
        xmin, ymin, xmax, ymax = aoi_4326.total_bounds

        tiles = []
        for t in mercantile.tiles(xmin, ymin, xmax, ymax, zooms=zoom):
            tb = mercantile.bounds(t)
            geom = box(tb.west, tb.south, tb.east, tb.north)
            if not inside_aoi or aoi_4326.intersects(geom).any():
                tiles.append({"x": t.x, "y": t.y, "z": t.z, "geometry": geom})

        if not tiles:
            return GPDVector(gpd.GeoDataFrame(geometry=[], crs="EPSG:4326"))

        return GPDVector(gpd.GeoDataFrame(tiles, crs="EPSG:4326", geometry="geometry"))

    # --------------------------
    # Utility
    # --------------------------
    @staticmethod
    def get_geometry_columns(df) -> list[str]:
        # GeoPandas stores geometry dtype as 'geometry'
        return [c for c, dt in df.dtypes.items() if str(dt) == "geometry"]

    @classmethod
    def extent_2_envelop(cls, min_x: float, min_y: float, max_x: float, max_y: float, crs: Union[str, int, CRS]) -> "GPDVector":
        # Normalize reversed inputs
        if min_x > max_x:
            min_x, max_x = max_x, min_x
        if min_y > max_y:
            min_y, max_y = max_y, min_y

        geom = box(min_x, min_y, max_x, max_y)
        gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[geom], crs=crs)
        return cls(gdf)
