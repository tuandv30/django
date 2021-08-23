import os
from sentry_sdk import capture_exception
from ..core.utils import get_object_or_none
from ..core.ghtk_api.api_base import APIBase
from ..constant import URL_API_TRANSFER_STATION_V2
from ..system_config import get_system_config_by_key
from ..model.crossbelt import CrossbeltSortingHistory, CrossbeltSortingPlan
from ..model.wms_local import Images, PackageWMS, Station
from ..constant import DEFAULT_IMG_ERROR, BagType


DEPLOY_ENV = os.environ.get("DEPLOY_ENV")
API_CHANGE_STATION_TOKEN = get_system_config_by_key("ghtk_api.change_station.token")
CURRENT_STATION_ID = get_system_config_by_key("station_info.station_id")


def change_current_station_v2(pkg_order):
    if not DEPLOY_ENV == "production":  # only change current station in production
        print("pkg_order {} : Only change current station in production!".format(pkg_order))
        return False
    api_change_station = APIBase()
    api_change_station.add_header({
        "token": API_CHANGE_STATION_TOKEN,
    })
    api_change_station.set_max_retry(retry_time=3)
    data = {
        "station_id": CURRENT_STATION_ID,
        "package_orders": [pkg_order]
    }

    try:
        req = api_change_station.post_json(
            url=URL_API_TRANSFER_STATION_V2, json=data, timeout=3)
        if req.status_code == 200:
            res = req.json()
            if res["success"] is True:
                return True
            return False
    except BaseException as exc:
        capture_exception(exc)
        return False

    return False


def get_image_path_from_sorting_history(sorting_history_id):
    image_path = DEFAULT_IMG_ERROR
    sorting_history = get_object_or_none(CrossbeltSortingHistory, pk=sorting_history_id)
    if sorting_history is not None:
        image_id = sorting_history.image_id
        if image_id is not None:
            image = get_object_or_none(Images, pk=image_id)
            image_path = image.ghtk_path

    return image_path


def get_info_package_and_station(data_chute, plan_id):
    station = None
    chute_id = data_chute.get("chute_id")
    pkg_order = data_chute.get("pkg_order")

    package_wms = get_object_or_none(PackageWMS, pk=pkg_order)
    if package_wms is not None:
        if plan_id is None:
            station = get_object_or_none(Station, pk=package_wms.dst_station_id)
        else:
            # check bao_tong config with this chute and active plan
            sort_plan_chute = CrossbeltSortingPlan.objects.filter(
                plan_id=plan_id,
                chute_id=chute_id,
                bag_type=BagType.EXTRA.value
            ).first()
            if not sort_plan_chute:
                station = get_object_or_none(Station, pk=package_wms.dst_station_id)
            else:
                # has bao_tong config => assign the package with main station id
                main_station_id = sort_plan_chute.main_station_id
                if main_station_id:
                    station = get_object_or_none(Station, pk=main_station_id)
                else:
                    station = get_object_or_none(Station, pk=package_wms.dst_station_id)
    return package_wms, station
