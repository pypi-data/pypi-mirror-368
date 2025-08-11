import traceback

import pandas as pd
import ee
from datetime import timedelta, datetime, date
from typing import Union

from digitalarzengine.io.gee.gee_image import GEEImage
from digitalarzengine.io.gee.gee_region import GEERegion


class GEEImageCollection:
    img_collection: ee.ImageCollection

    def __init__(self, img_coll: ee.ImageCollection):
        self.img_collection = img_coll

    @staticmethod
    def get_latest_image_collection(img_collection: ee.ImageCollection, limit: int = -1):
        img_collection = img_collection.sort('system:time_start', False)
        if limit > 0:
            img_collection = img_collection.limit(limit)
        return img_collection

    @staticmethod
    def customize_collection(tags: str, dates: list) -> ee.ImageCollection:
        """
        Filters an ImageCollection to include only images whose acquisition dates
        match any of the dates provided in the list.

        Args:
            tags (str): ImageCollection ID.
            dates (list): List of date strings (e.g. ['2023-01-01', '2023-02-01']).

        Returns:
            ee.ImageCollection: Filtered image collection with daily images.
        """
        img_col = ee.ImageCollection(tags)

        # Convert Python date strings to ee.List of ee.Dates
        ee_dates = ee.List([ee.Date(date) for date in dates])

        def get_image_on_date(date):
            date = ee.Date(date)
            image = img_col.filterDate(date, date.advance(1, 'day')).first()
            return image

        filtered_images = ee_dates.map(get_image_on_date)

        # Wrap in ee.ImageCollection and filter nulls
        return ee.ImageCollection(filtered_images).filter(ee.Filter.notNull(['system:time_start']))

    @staticmethod
    def from_tags(cls, tag: str, date_range: tuple = None, region: Union[GEERegion, dict] = None):
        """
        Parameters
        ----------
        :param tag:  dataset name or type like 'COPERNICUS/S2_SR' for other check gee documentation
        :param date_range: tuple
            range of date with start and end value like
            ('2021-01-01', '2021-12-31')
            or can be calculated through  time delta
            today = datetime.date.today()
             start_date = today - datetime.timedelta(days=365)
            self.date_range = (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        example:
              s2_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
             .filterDate(start_date, end_date) \
             .filterBounds(fc) \
             .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)
        """

        # self.image_type = image_type
        img_collection = ee.ImageCollection(tag)
        if region is not None:
            region = GEERegion.from_geojson(region) if isinstance(region, dict) else region
            img_collection = img_collection.filterBounds(region.bounds)

        if date_range is not None:
            img_collection = img_collection.filterDate(date_range[0], date_range[1])
        return cls(img_collection)

    @staticmethod
    def get_collection_max_date(img_col: ee.ImageCollection) -> date:
        max_timestamp = img_col.aggregate_max('system:time_start')
        # max_timestamp = img_col.first().get('system:time_start')
        # Convert the timestamp to an ee.Date object (server-side)
        max_date = ee.Date(max_timestamp)

        # Format the date as a string (server-side)
        formatted_date = max_date.format('YYYY-MM-dd')
        # return formatted_date.getInfo()
        return datetime.strptime(formatted_date.getInfo(), "%Y-%m-%d").date()

    @staticmethod
    def get_latest_dates(image_collection: ee.ImageCollection, delta_in_days=10, end_date: datetime = None) -> (
            str, str):
        # Calculate the date range for the latest 10 days or any delta applied

        if end_date is None:
            end_date = GEEImageCollection.get_collection_max_date(image_collection)

        if end_date is None:
            end_date = datetime.utcnow().date()

        start_date = end_date - timedelta(days=delta_in_days)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    @staticmethod
    def get_ymd_list(img_collection: ee.ImageCollection) -> list:
        def iter_func(image, newList):
            image = ee.Image(image)
            newlist = ee.List(newList)

            # Use system:time_start if available
            date = ee.Algorithms.If(
                image.propertyNames().contains('system:time_start'),
                ee.Date(image.get('system:time_start')).format('YYYY-MM-dd'),
                # fallback: try to parse from system:index
                ee.String(image.get('system:index'))  # generic fallback
            )

            return newlist.add(date)

        return ee.List(img_collection.iterate(iter_func, ee.List([]))).distinct().sort().getInfo()

    # @staticmethod
    # def get_ymd_list(img_collection: ee.ImageCollection) -> list:
    #     # Inner Function: Processes each image in the collection
    #     def iter_func(image, newList):
    #         # Extract the image date as a YYYY-MM-dd string
    #         date = ee.String(image.date().format("YYYY-MM-dd"))
    #
    #         # Convert the existing list (newList) to an EE List for manipulation
    #         newlist = ee.List(newList)
    #
    #         # Add the current date to the list, sort the list, and return it
    #         return ee.List(newlist.add(date).sort())
    #
    #     # Apply the iteration to the image collection
    #     return img_collection.iterate(iter_func, ee.List([])).getInfo()

    def enumerate_collection(self) -> (int, ee.Image):
        size = self.img_collection.size().getInfo()
        img_list = ee.List(self.img_collection.toList(self.img_collection.size()))
        for i in range(size):
            yield i, ee.Image(img_list.get(i))

    def info_ee_array_to_df(self, region: GEERegion, list_of_bands: list = None, scale: int = None) -> pd.DataFrame:
        """
        Transforms client-side ee.Image.getRegion array to pandas.DataFrame.
        Ensures that if the region is smaller than pixel size, at least one pixel is returned.

        :param region: GEERegion object defining the area of interest.
        :param list_of_bands: List of band names to extract.
        :param scale: Resolution in meters (optional).
        :return: Pandas DataFrame containing extracted data.
        """
        try:
            # Get first image in the collection
            gee_image = GEEImage(self.img_collection.first())

            # If list_of_bands is not provided, get all available bands
            list_of_bands = gee_image.get_band_names() if not list_of_bands else list_of_bands

            if not list_of_bands:  # If no bands are found, return an empty DataFrame
                return pd.DataFrame()

            if scale is None:
                region_area = region.aoi.area().getInfo()
                # Convert region area to linear meters (side length of a square)
                region_side = region_area ** 0.5
                min_scale, max_scale = gee_image.get_min_max_scale(list_of_bands)
                # Ensure scale is at least the pixel resolution and does not exceed the region's side length
                scale = min(min_scale, min(region_side, max_scale))
                # Fetch pixel data from Google Earth Engine
            arr = self.img_collection.getRegion(geometry=region.aoi, scale=scale).getInfo()

            # Ensure valid data is returned
            if not arr or len(arr) < 2:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(arr)

            # Rearrange headers correctly
            headers = df.iloc[0].values
            df = pd.DataFrame(df.values[1:], columns=headers)

            # Convert numeric columns
            for band in list_of_bands:
                df[band] = pd.to_numeric(df[band], errors="coerce")

            # Convert time field into datetime format
            df["datetime"] = pd.to_datetime(df["time"], unit="ms")

            # Ensure relevant columns are retained
            df = df[["longitude", "latitude", "time", "datetime"] + list_of_bands]

            return df

        except Exception as e:
            print("Error in info_ee_array_to_df:", str(e))
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def sum_resampler(coll: ee.ImageCollection, freq, unit, scale_factor, band_name):
        """
        This function aims to resample the time scale of an ee.ImageCollection.
        The function returns an ee.ImageCollection with the averaged sum of the
        band on the selected frequency.

        coll: (ee.ImageCollection) only one band can be handled
        freq: (int) corresponds to the resampling frequence
        unit: (str) corresponds to the resampling time unit.
                    must be 'day', 'month' or 'year'
        scale_factor (float): scaling factor used to get our value in the good unit
        band_name (str) name of the output band
        example:
        # Apply the resampling function to the precipitation dataset.
            pr_m = sum_resampler(pr, 1, "month", 1, "pr")
        # Apply the resampling function to the PET dataset.
            pet_m = sum_resampler(pet.select("PET"), 1, "month", 0.0125, "pet")
        # Combine precipitation and evapotranspiration.
            meteo = pr_m.combine(pet_m)

        """
        # Define initial and final dates of the collection.
        firstdate = ee.Date(
            coll.sort("system:time_start", True).first().get("system:time_start")
        )

        lastdate = ee.Date(
            coll.sort("system:time_start", False).first().get("system:time_start")
        )

        # Calculate the time difference between both dates.
        # https://developers.google.com/earth-engine/apidocs/ee-date-difference
        diff_dates = lastdate.difference(firstdate, unit)

        # Define a new time index (for output).
        new_index = ee.List.sequence(0, ee.Number(diff_dates), freq)

        # Define the function that will be applied to our new time index.
        def apply_resampling(date_index):
            # Define the starting date to take into account.
            startdate = firstdate.advance(ee.Number(date_index), unit)

            # Define the ending date to take into account according
            # to the desired frequency.
            enddate = firstdate.advance(ee.Number(date_index).add(freq), unit)

            # Calculate the number of days between starting and ending days.
            diff_days = enddate.difference(startdate, "day")

            # Calculate the composite image.
            image = (
                coll.filterDate(startdate, enddate)
                .mean()
                .multiply(diff_days)
                .multiply(scale_factor)
                .rename(band_name)
            )

            # Return the final image with the appropriate time index.
            return image.set("system:time_start", startdate.millis())

        # Map the function to the new time index.
        res = new_index.map(apply_resampling)

        # Transform the result into an ee.ImageCollection.
        res = ee.ImageCollection(res)

        return res

    def select_band(self, band: Union[str , list[str]]):
        """
        Select a specific band or list of bands from the current image collection.

        Parameters:
        - band (str or list of str): The name(s) of the band(s) to select.

        Example:
            self.select_band("NDVI")
            self.select_band(["NDVI", "EVI"])
        """
        if self.img_collection is None:
            raise ValueError("Image collection is not initialized.")

        self.img_collection = self.img_collection.select(band)
