import sys
import traceback

from digitalarzengine.io.managers.db_manager import DBManager
from digitalarzengine.scripts.snow_cover import *
from digitalarzengine.scripts.water.jrc_monthly import JRCMonthlyRecurrence


def test_db_manager():
    db_manager = DBManager.from_config("drm")
    gdf = db_manager.read_as_geo_dataframe("pmd_hydro_gauges")
    print(gdf.head())


def get_gee_dataset_url():
    jrc_monthly = JRCMonthlyRecurrence()
    # ymd_list = jrc_monthly.get_ymd_list()
    # print(ymd_list)
    # url_template = jrc_monthly.get_url()
    # print("Max monthly recurrence tile URL:", url_template)
    # return url_template
    print("monthly recurrence")
    jrc_monthly.download_monthly_recurrence_image()
    # print("max monthly recurrence")
    # jrc_monthly.download_max_recurrence_image()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <function_name> [args...]")
        sys.exit(1)

    function_name = sys.argv[1]
    args = sys.argv[2:]

    try:
        func = globals()[function_name]
        func(*args)
    except Exception as e:
        traceback.print_exc()
        print(f"Error running function: {e}")

