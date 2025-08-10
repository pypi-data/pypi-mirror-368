import os

import ee

from build.lib.digitalarzengine.io.file_io import FileIO
from digitalarzengine.io.gee.gee_image import GEEImage
from digitalarzengine.io.gee.gee_image_collection import GEEImageCollection
from digitalarzengine.io.gee.gpd_vector import GPDVector
from digitalarzengine.pipeline.gee_pipeline import GEEPipeline
from digitalarzengine.pipeline.pak_data import PakData
from digitalarzengine.settings import MEDIA_DIR


class JRCMonthlyRecurrence:
    tag = 'JRC/GSW1_4/MonthlyRecurrence'
    scale = 30
    bands = ['monthly_recurrence', 'has_observations']

    def __init__(self, aoi_gdf=None):
        if aoi_gdf is None:
            gdf = PakData.get_pak_basins()
            aoi_gdf = GPDVector.to_aoi_gdf(gdf)
        self.gee_pipeline = GEEPipeline(aoi_gdf)
        self.img_collection = (ee.ImageCollection(self.tag)
                               .filterBounds(self.gee_pipeline.region.aoi))

    @property
    def vis_params(self):
        return {
            "bands": ['monthly_recurrence'],
            "min": 0.0,
            "max": 100.0,
            "palette": ['ffffff', 'ffbbbb', '0000ff']
        }

    def get_ymd_list(self):
        ymd_list = GEEImageCollection.get_ymd_list(self.img_collection)
        return ymd_list

    def get_url(self):
        max_recurrence_image = self.img_collection.max()
        map_id_dict = max_recurrence_image.getMapId(self.vis_params)
        url_template = map_id_dict['tile_fetcher'].url_format
        return url_template

    def download_max_recurrence_image(self):
        max_recurrence_image = self.img_collection.max()
        gee_img = GEEImage(max_recurrence_image.select(self.bands[0]))
        metadata = gee_img.get_image_metadata()
        out_fp = os.path.join(MEDIA_DIR, self.tag, 'max_recurrence.tif')
        FileIO.mkdirs(out_fp)
        if os.path.exists(out_fp):
            print(f"Skipping {out_fp}")
            return
        print(f"Downloading {out_fp}")
        gee_img.download_image(out_fp, self.gee_pipeline.region,
                               scale=self.scale, within_aoi_only=True,
                               no_of_bands=1, save_metadata=True, meta_data=metadata)

    def download_monthly_recurrence_image(self):
        gee_img_coll = GEEImageCollection(self.img_collection)
        # gee_img_coll.select_band(self.bands[0])
        for i, img in gee_img_coll.enumerate_collection():
            img = img.select(self.bands[0])
            gee_img = GEEImage(img)

            metadata = gee_img.get_image_metadata()
            id = metadata['id']
            out_fp = os.path.join(MEDIA_DIR, f"{id}.tif")
            FileIO.mkdirs(out_fp)
            if os.path.exists(out_fp):
                print(f"Skipping {out_fp}")
                continue
            print(f"Downloading {out_fp}")
            gee_img.download_image(out_fp, self.gee_pipeline.region,
                                   scale=self.scale * 3, within_aoi_only=False,
                                   no_of_bands=1, save_metadata=True, meta_data=metadata)
        print("Done")
