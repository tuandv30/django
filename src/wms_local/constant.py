from datetime import datetime
import os
from enum import Enum

# GHTK API
URL_API_COMING_PACKAGE = "https://admin.giaohangtietkiem.vn/admin/AdLegos/getComingBagsPackages"
URL_API_INFO_PACKAGE = "https://integration-ecom-service.ghtk.vn/api/v1/pkg-orders-info"
URL_API_INFO_BAG = "https://integration-ecom-service.ghtk.vn/api/v1/bag-order-info"
URL_API_CHECK_PACKAGE_IN_BAG = "https://check-pkg-in-bag.ghtk.vn/api/v1/check-pkg-in-bag"
URL_API_TRANSFER_STATION_PACKAGE = "https://admin.giaohangtietkiem.vn/admin/AdLegos/transferStationForPkgLego"
URL_API_TRANSFER_STATION_V2 = "https://admin.giaohangtietkiem.vn/admin/AdLegos/changeCurrentStation"
URL_API_TAKEOUT_PACKAGE_FROM_BAG = "https://admin.giaohangtietkiem.vn/admin/AdInter/takeOutPackagesFromBags"

# WMS CENTRAL API
URL_API_STATISTIC_PACKAGE_WAREHOUSE = "https://wms.ghtk.vn/api/statistics/packagewarehouse/"

# MQTT
MQTT_HOST = os.environ.get("MQTT_HOST")
MQTT_PORT = os.environ.get("MQTT_PORT")
MQTT_PORT = int(MQTT_PORT) if MQTT_PORT is not None else None
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PWD = os.environ.get("MQTT_PWD")
MQTT_TOPIC_PKG_IN_CHUTE = "/mobile/pkg_in_chute/{}"

# CONFIG PDA AND REJECT CHUTE CROSSBELT
NORMAL_CHUTE_ZONE_A = [1, 134]  # [from, to]
NORMAL_CHUTE_ZONE_B = [135, 272]  # [from, to]
PDA_CHUTE_ZONE_A = 276
PDA_CHUTE_ZONE_B = 274
INDUCTION_ZONE_A = [0, 1, 2, 3, 4, 5]
INDUCTION_ZONE_B = [6, 7, 8, 9, 10]
MAX_WEIGHT = 1000.0
SORTING_PROVINCE = "129,126,818,143,866,859,860,821,848,862,855,824,838,865"

# DEFAULT OPERATION CONFIG FOR CROSSBELT
REJECT_CHUTE_ZONE_A = [2, 4]
REJECT_CHUTE_ZONE_B = [138, 140]
REJECT_CHUTE_OVER_WEIGHT_ZONE_A = [6, 8]
REJECT_CHUTE_OVER_WEIGHT_ZONE_B = [142, 144]
REJECT_CHUTE_NO_SORTING_ZONE_A = [12]
REJECT_CHUTE_NO_SORTING_ZONE_B = [146]

# CONFIG BARCODE NOREAD AND INVALID FOR CROSSBELT
BARCODE_NOREAD = "?" * 10
BARCODE_INVALID = "#" * 10

# KAFKA
KAFKA_BOOTSTRAP_SERVER = os.environ.get("KAFKA_BOOTSTRAP_SERVER")
KAFKA_PRODUCER_VERIFY_BAG_TOPIC = "autosorting.ghtk.verify_bag"
KAFKA_PRODUCER_MISSING_PACKAGE_TOPIC = "autosorting.ghtk.missing_package"
KAFKA_PRODUCER_CROSSBELT_SORTING_HISTORY_TOPIC = "autosorting.crossbelt.sorting_history"
KAFKA_PRODUCER_CROSSBELT_IMAGES_TOPIC = "autosorting.crossbelt.image"
KAFKA_PRODUCER_LEGO_LOG_SCAN = "autosorting.scanner.log_scanner"
KAFKA_PRODUCER_LEGO_SYNC_SCAN_LOG = "lego.sync.scan_history"
KAFKA_PRODUCER_LEGO_SYNC_SCAN_IMAGE = "lego.sync.scan_images"
KAFKA_PRODUCER_LEGO_SYNC_IMAGES = "lego.sync.images"

# COLOR DASHBOARD CROSSBELT
COLOR = [
    'rgba(0, 51, 102, 0.8)',
    'rgba(229, 50, 62, 0.8)',
    'rgba(191, 191, 63, 0.8)',
    'rgba(38, 38, 114, 0.8)',
    'rgba(63, 191, 191, 0.8)',
    'rgba(140, 114, 114, 0.8)',
    'rgba(191, 63, 125, 0.8)',  # pink
    'rgba(96, 114, 38, 0.8)',  # green plus
    'rgba(153, 63, 191, 0.8)',  # purple
    'rgba(63, 121, 191, 0.8)',  # blue
    'rgba(191, 146, 63, 0.8)',  # yellow
    'rgba(191, 63, 63, 0.8)',  # red
    'rgba(63, 191, 127, 0.8)',  # green
]

# CONFIG PAGINATE FOR NATIVE QUERY
NATIVE_QUERY_PAGINATE_BY = 100

# BASE TIME 00:00:00 01-01-1970
BASE_TIME = datetime(1970, 1, 1, 0, 0, 0)

# WHITELIST IP FOR API WCS CROSSBELT
WHITELIST_IP_ADDRESS_API_WCS = [
    '10.160.12.82',
    '10.160.12.83',
    '10.160.12.84',
    '10.160.12.92',
    '10.160.12.93'
]

# GHTK ID CONFIG
CLIENT_GHTK_ID = os.environ.get("CLIENT_GHTK_ID")
CLIENT_GHTK_SECRET = os.environ.get("CLIENT_GHTK_SECRET")
GHTK_ID_DOMAIN_URL = os.environ.get("GHTK_ID_DOMAIN_URL")
AUTHORIZE_GHTK_ID_URL = "{}/{}".format(GHTK_ID_DOMAIN_URL, "api/v1/oauth2/authorize")
TOKEN_GHTK_ID_URL = "{}/{}".format(GHTK_ID_DOMAIN_URL, "api/v1/oauth2/token")
USER_INFO_GHTK_ID_URL = "{}/{}".format(GHTK_ID_DOMAIN_URL, "api/v1/oauth2/userinfo")
LOGOUT_GHTK_ID_URL = "{}/{}".format(GHTK_ID_DOMAIN_URL, "api/v1/logout")

REMOTE_GHTK_ID_URL = os.environ.get("REMOTE_GHTK_ID_URL") or "{}/api/v1/oauth2/keys".format(GHTK_ID_DOMAIN_URL)
GHTK_ID_VALIDATE_ACCESS_TOKEN_ONLINE_URL = os.environ.get("GHTK_ID_VALIDATE_ACCESS_TOKEN_ONLINE") or \
                                           "{}/api/v1/oauth2/introspect".format(GHTK_ID_DOMAIN_URL)

# SERVICE CODE SYNC
SERVICE_CODE_SYNC_SCAN_LOG = "sync_scan_log"
SERVICE_CODE_SYNC_WMS_CENTRAL = "sync_wms_central"

# IMAGE DEFAULT CROSSBELT
TEMP_IMG = "https://cache.giaohangtietkiem.vn/image/show/3b386088-50d4-41c3-a3aa-b8003cdac7a5/" \
           "d0a9e871-898b-4f20-b524-e30ee663beb4.png"
DEFAULT_IMG_ERROR = "https://cache.giaohangtietkiem.vn/image/show/41235f6c-e390-4cd9-979d-c95667e7d772/" \
                   "image-error-icon-5.jpg"

# token for creating dummy user when authenticating by access_token
DEFAULT_TOKEN = "134b387b3bcfd2cc5abdefaultdefault"
LAST_TIME_MODIFIED_CHUTE_CONFIG_KEY = "update_device_state.last_update"

# interval time from chute blocking event to create bag
INTERVAL_TIME_FOR_BAG_CREATE = 30


class DestinationType(Enum):
    PROVINCE = 0
    STATION = 1
    MODULE = 2
    CART = 3


class BagType(Enum):
    NORMAL = 0  # bao thuong
    EXTRA = 1  # bao tong
