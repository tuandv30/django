from sentry_sdk import capture_exception

from ..model.crossbelt import CrossbeltOperationConfig
from ..constant import MAX_WEIGHT, REJECT_CHUTE_ZONE_A, REJECT_CHUTE_ZONE_B, SORTING_PROVINCE
from ..constant import REJECT_CHUTE_NO_SORTING_ZONE_A, REJECT_CHUTE_NO_SORTING_ZONE_B
from ..constant import REJECT_CHUTE_OVER_WEIGHT_ZONE_A, REJECT_CHUTE_OVER_WEIGHT_ZONE_B


def get_os_config(key):
    value = None
    try:
        value = CrossbeltOperationConfig.objects.get(
            key=key,
            status=1
        ).value
    except BaseException as exc:
        capture_exception(exc)
    return value


def get_max_weight():
    max_weight_config = get_os_config(key="max_weight")
    if max_weight_config:
        try:
            max_weight_config = float(max_weight_config)
            return max_weight_config
        except ValueError:
            return MAX_WEIGHT
    else:
        return MAX_WEIGHT


def get_reject_chute_zone(zone_key="A"):
    if zone_key == "A":
        reject_chute = REJECT_CHUTE_ZONE_A
        config = get_os_config(key="reject_zone_a")
    else:
        reject_chute = REJECT_CHUTE_ZONE_B
        config = get_os_config(key="reject_zone_b")

    if config:
        try:
            reject_chute = [int(i) for i in config.split(",")]
        except BaseException as exc:
            capture_exception(exc)
    return reject_chute


def get_over_weight_reject_chute(zone_key="A"):
    if zone_key == "A":
        over_weight_reject_chute = REJECT_CHUTE_OVER_WEIGHT_ZONE_A
        config = get_os_config(key="reject_over_weight_zone_a")
    else:
        over_weight_reject_chute = REJECT_CHUTE_OVER_WEIGHT_ZONE_B
        config = get_os_config(key="reject_over_weight_zone_b")

    if config:
        try:
            over_weight_reject_chute = [int(i) for i in config.split(",")]
        except BaseException as exc:
            capture_exception(exc)
    return over_weight_reject_chute


def get_no_sorting_reject_chute(zone_key="A"):
    if zone_key == "A":
        no_sorting_reject_chute = REJECT_CHUTE_NO_SORTING_ZONE_A
        config = get_os_config(key="reject_no_sorting_zone_a")
    else:
        no_sorting_reject_chute = REJECT_CHUTE_NO_SORTING_ZONE_B
        config = get_os_config(key="reject_no_sorting_zone_b")

    if config:
        try:
            no_sorting_reject_chute = [int(i) for i in config.split(",")]
        except BaseException as exc:
            capture_exception(exc)
    return no_sorting_reject_chute


def get_all_reject_chute():
    reject_normal_chute = get_reject_chute_zone(
        zone_key="A") + get_reject_chute_zone(zone_key="B")
    reject_over_weight_chute = get_over_weight_reject_chute(
        zone_key="A") + get_over_weight_reject_chute(zone_key="B")
    reject_no_sorting_chute = get_no_sorting_reject_chute(
        zone_key="A") + get_no_sorting_reject_chute(zone_key="B")
    reject_chute = reject_normal_chute + reject_over_weight_chute + reject_no_sorting_chute
    return reject_chute


def get_sorting_province(list_province_config: list):
    sorting_province = SORTING_PROVINCE
    config = get_os_config(key="sorting_province")
    if config:
        try:
            sorting_province = (set(int(i) for i in config.split(",")))
        except BaseException as exc:
            capture_exception(exc)
    if list_province_config:
        list_province_config = set(int(i) for i in list_province_config)
        sorting_province = sorting_province - set(list_province_config)
    return list(sorting_province)
