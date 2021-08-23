import json
from enum import Enum
from .model.wms_local import SystemConfig


class SystemConfigKey(Enum):
    # STATION INFOR
    STATION_ID = "station_infor.station_id"
    STATION_CODE = "station_infor.station_code"
    STATION_NAME = "station_infor.station_name"
    STATION_TYPE = "station_infor.station_type"

    # SYNC ADMIN LOG
    SYNC_ADMIN_LOG_LAST_SCAN_LOG_ID = "sync_admin_log.last_scan_log_id"
    SYNC_ADMIN_LOG_LAST_SORTING_HISTORY_ID = "sync_admin_log.last_sorting_history_id"

    # SYNC LOCAL
    SYNC_LOCAL_IGNORE_PACKAGE_INFO = "sync_local.ignore_package_info"
    SYNC_LOCAL_LIST_STATION_ID = "sync_local.list_station_id"

    # SYNC_WMS_CENTRAL
    SYNC_WMS_CENTRAL_LAST_IMAGE_ID = "sync_wms_central.last_images_id"
    SYNC_WMS_CENTRAL_LAST_SCAN_IMAGES_ID = "sync_wms_central.last_scan_images_id"
    SYNC_WMS_CENTRAL_LAST_SCAN_LOG_ID = "sync_wms_central.last_scan_log_id"
    SYNC_WMS_CENTRAL_LAST_SORTING_HISTORY_ID = "sync_wms_central.last_sorting_history_id"

    # GHTK API
    GHTK_API_CHANGE_STATION_DEVICE_SORTING_DISABLE = "ghtk_api.change_station.device_sorting_disable"
    GHTK_API_CHANGE_STATION_TOKEN = "ghtk_api.change_station.token"
    GHTK_API_TAKEOUT_PACKAGE_SECRET_KEY = "ghtk_api.takeout_package_secret_key"

    # OTHER
    TASK_TAKEOUT_PKG_LAST_SORTING_HISTORY_ID = "task_takeout_pkg.last_sorting_history_id"
    UPDATE_DEVICE_STATE_LAST_UPDATE = "update_device_state.last_update"

    # KAFKA BOOTSTRAP SERVER TMP
    KAFKA_BOOTSTRAP_SERVER = "kafka_bootstrap_server"  # use when can not read from environment


def get_system_config_by_key(key):
    return_value = None
    system_config = SystemConfig.objects.filter(
        key=key,
        status=1
    ).first()
    if system_config:
        if system_config.data_type == "int":
            return_value = int(system_config.value)
        elif system_config.data_type == "string":
            return_value = system_config.value
        elif system_config.data_type == "json":
            return_value = json.loads(system_config.value)
    return return_value


def update_system_config(key, value):
    system_config = SystemConfig.objects.filter(
        key=key,
        status=1
    ).first()
    if system_config:
        system_config.value = value
    else:
        system_config = SystemConfig(
            key=key,
            value=value,
            status=1
        )
    system_config.save()
