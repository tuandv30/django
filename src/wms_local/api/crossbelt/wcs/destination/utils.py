import json
import random
from datetime import datetime, timedelta
from constance import config
from sentry_sdk import capture_exception
from django.db import connection
from ..utils import validate_barcode
from .....core.ghtk_api.api_base import APIBase
from .....core.os_config import get_reject_chute_zone, get_over_weight_reject_chute,\
    get_no_sorting_reject_chute, get_max_weight
from .....core.utils import get_list_or_none
from .....model.wms_local import Cart, Station, PackageWMS
from .....constant import PDA_CHUTE_ZONE_A, PDA_CHUTE_ZONE_B, REJECT_CHUTE_ZONE_A, REJECT_CHUTE_OVER_WEIGHT_ZONE_A
from .....constant import REJECT_CHUTE_NO_SORTING_ZONE_A, INDUCTION_ZONE_A, INDUCTION_ZONE_B, URL_API_INFO_PACKAGE
from .....constant import URL_API_INFO_BAG, DestinationType
from .....model.crossbelt import CrossbeltSortingHistory, CrossbeltChute
from .....constant import BARCODE_NOREAD, BARCODE_INVALID


RAW_QUERY = """
        SELECT
            chute_id, spcd.destination_code, spcd.destination_type
        FROM
            sorting_plan_chute spc
            INNER JOIN sorting_plan_chute_detail spcd on spcd.sorting_plan_chute_id = spc.id
        WHERE
            spc.plan_id=%(plan_id)s AND
            spc.transport_type in %(trf_type)s
        """


def is_valid_post_request(post_data):
    barcode = post_data.get("BarCode")
    scanner_no = post_data.get("ScannerNo") or None
    induction_no = post_data.get("InductionNO") or None
    carrier_id = post_data.get("CarrierID") or None
    loops = post_data.get("Loops") or None
    get_on_time = post_data.get("GetOnTime")
    create_time = post_data.get("CreateTime")

    if not isinstance(barcode, list):
        return False
    if not scanner_no or not induction_no or not carrier_id:
        return False
    if not loops or not get_on_time or not create_time:
        return False

    return True


def process_barcode_not_readable(request, kwargs, response):
    destination_code = lookup_pda_destination_code(request.data.get("InductionNO"))
    kwargs.update({
        "chute_id": destination_code,
        "destination_code": destination_code,
        "chute_type": CrossbeltSortingHistory.ChuteType.PDA.value
    })
    insert_or_update_sorting_history(sorting_history=None, **kwargs)
    response.update({
        "BarCode": BARCODE_NOREAD,
        "PostCode": "{}".format(destination_code) if destination_code else "",
    })
    return response


def process_no_barcode(request, kwargs, response):
    destination_code = lookup_pda_destination_code(request.data.get("InductionNO"))
    kwargs.update({
        "chute_id": destination_code,
        "destination_code": destination_code,
        "chute_type": CrossbeltSortingHistory.ChuteType.PDA.value
    })
    # insert input api has no valid barcode
    insert_or_update_sorting_history(sorting_history=None, **kwargs)
    response.update({
        "BarCode": BARCODE_INVALID,
        "PostCode": "{}".format(destination_code) if destination_code else "",
    })
    return response


def process_only_one_barcode(request, plan_id, barcode_package, kwargs, response):
    induction_no = request.data.get("InductionNO") or None
    loops = request.data.get("Loops") or None
    destination_code, chute_type, bag_order = lookup_destination_code_package(
        pkg_order=barcode_package, induction_no=induction_no, plan_id=plan_id)
    kwargs.update({
        "pkg_order": barcode_package,
        "plan_id": plan_id,
        "bag_order": bag_order,
        "chute_type": chute_type,
        "destination_code": destination_code,
        "chute_id": destination_code,
    })

    # being looped when the chute destination of the package is fulled or wrong
    if loops == "1":
        # insert into sorting_history table
        insert_or_update_sorting_history(sorting_history=None, **kwargs)
    else:
        # update existed row in sorting_history table
        sorting_history = CrossbeltSortingHistory.objects.filter(
            pkg_order=int(barcode_package)
        ).order_by("-dst_request_time").first()
        insert_or_update_sorting_history(sorting_history=sorting_history, **kwargs)

    response.update({
        "BarCode": "{}".format(barcode_package),
        "PostCode": "{}".format(destination_code),
    })

    return response


def process_multiple_barcode(request, plan_id, list_barcode_package, kwargs, response):
    induction_no = request.data.get("InductionNO") or None
    loops = request.data.get("Loops") or None
    tmp_destination_code = set()
    bag_order, chute_type = None, None
    for i in list_barcode_package:
        destination_code, chute_type, bag_order = lookup_destination_code_package(
            pkg_order=i,
            induction_no=induction_no,
            plan_id=plan_id
        )
        if not destination_code:
            continue
        if destination_code not in tmp_destination_code:
            tmp_destination_code.add(destination_code)

    tmp_destination_code = list(tmp_destination_code)

    package_wms = PackageWMS.objects.filter(pkg_order__in=list_barcode_package).all()
    pkg_order = random.choice(package_wms).pkg_order
    kwargs.update({
        "plan_id": plan_id,
        "bag_order": bag_order,
    })
    # if there is no des code or more than 1 des code => go to PDA chute
    if not tmp_destination_code or len(tmp_destination_code) > 1:
        destination_code = lookup_pda_destination_code(induction_no)
        kwargs.update({
            "chute_id": destination_code,
            "destination_code": destination_code,
            "chute_type": CrossbeltSortingHistory.ChuteType.PDA.value,
        })
        for i in package_wms:
            kwargs["pkg_order"] = i.pkg_order
            sorting_history = CrossbeltSortingHistory.objects.filter(
                pkg_order=i
            ).order_by("-dst_request_time").first()
            insert_or_update_sorting_history(sorting_history=sorting_history, **kwargs)
        response.update({
            "BarCode": "{}".format(pkg_order),
            "PostCode": "{}".format(destination_code) if destination_code else "",
        })
    else:
        kwargs.update({
            "chute_id": tmp_destination_code[0],
            "chute_type": chute_type,
            "destination_code": tmp_destination_code[0],
        })
        if loops == "1":
            # insert into sorting_history table
            for i in package_wms:
                kwargs["pkg_order"] = i.pkg_order
                insert_or_update_sorting_history(sorting_history=None, **kwargs)
        else:
            # update row in sorting_history table
            for i in package_wms:
                kwargs["pkg_order"] = i.pkg_order
                sorting_history = CrossbeltSortingHistory.objects.filter(
                    pkg_order=i
                ).order_by("-dst_request_time").first()
                insert_or_update_sorting_history(sorting_history=sorting_history, **kwargs)
        response.update({
            "BarCode": "{}".format(pkg_order),
            "PostCode": "{}".format(tmp_destination_code[0]),
        })

    return response


def generate_query(dst_cart_id, dst_module_id, dst_station_id):
    where_condition = []

    if dst_cart_id:
        where_condition.append("(spcd.destination_code=%(dst_cart_id)s AND"
                               " spcd.destination_type=%(dst_cart_type)s)")

    if dst_module_id:
        where_condition.append("(spcd.destination_code=%(dst_module_id)s AND"
                               " spcd.destination_type=%(dst_module_type)s)")

    if dst_station_id:
        where_condition.append("(spcd.destination_code=%(dst_station_id)s AND"
                               " spcd.destination_type=%(dst_station_type)s)")

    if not where_condition:
        return None

    where_condition = " OR ".join(where_condition)
    query = "{} AND ({})".format(RAW_QUERY, where_condition)

    return query


def generate_province_query():
    where_condition = "spcd.destination_code=%(dst_province_id)s AND " \
                      "spcd.destination_type=%(dst_province_type)s"
    query = "{} AND {}".format(RAW_QUERY, where_condition)
    return query


def get_tranfer_type(package_wms):
    trf_type = [0]
    if package_wms.transport:
        if package_wms.transport.strip() == "road":
            trf_type.append(1)  # Bộ
        if package_wms.transport.strip() == "fly":
            trf_type.append(2)  # Bay
    return trf_type


def get_info_package(pkg_order):
    new_package_wms = None
    api_get_info_package = APIBase()
    api_get_info_package.add_header({
        "Authorization": "Bearer {}".format(config.API_INFO_PACKAGE_TOKEN),
        "Content-Type": "application/json",
    })
    api_get_info_package.set_max_retry(retry_time=3)
    payload = {
        "pkg_order": [pkg_order]
    }
    try:
        packages = list()
        req = api_get_info_package.post_body(
            url=URL_API_INFO_PACKAGE, data=json.dumps(payload), timeout=2)
        if req.status_code == 200:
            packages = req.json()
        if packages and isinstance(packages, list):
            pkg = packages[0]
            if pkg.get("package_status_id") in [3, 10]:
                dst_station_id = pkg.get("transfer_station_id")
                dst_cart_id = pkg.get("deliver_cart_id")
            else:
                dst_station_id = pkg.get("return_station_id")
                dst_cart_id = pkg.get("return_cart_id")
            dst_module_id = get_module_from_cart(cart_id=dst_cart_id)
            new_package_wms = PackageWMS(
                pkg_order=pkg.get("pkg_order"),
                bag_import=pkg.get("bag_order"),
                pkg_status=pkg.get("package_status_id"),
                pkg_id=pkg.get("pkg_id"),
                dst_station_id=dst_station_id,
                dst_cart_id=dst_cart_id,
                dst_module_id=dst_module_id,
                alias=pkg.get("alias"),
                product_name=",".join(pkg.get("product_name"))[:80],
                weight=pkg.get("weight"),
                transport=pkg.get("transport"),
                done_at=datetime.strptime(
                    pkg.get("done_at"),
                    "%Y-%m-%d %H:%M:%S") if pkg.get("done_at") else None,
                rt_delay=pkg.get("rt_delay"),
                created=datetime.now(),
                modified=datetime.now()
            )
            new_package_wms.save()
    except BaseException as exc:
        capture_exception(exc)

    return new_package_wms


def get_info_bag(bag_order):
    dst_station_id = None
    api_get_info_bag = APIBase()
    api_get_info_bag.add_header({
        "Authorization": "Bearer {}".format(config.API_INFO_PACKAGE_TOKEN),
        "Content-Type": "application/json",
    })
    api_get_info_bag.set_max_retry(retry_time=3)
    try:
        url = "{}/{}".format(URL_API_INFO_BAG, bag_order)
        req = api_get_info_bag.get(url=url)
        if req.status_code == 200:
            bag = req.json()
            if bag:
                dst_station_id = bag.get("dst_id")
    except BaseException as exc:
        capture_exception(exc)

    return dst_station_id


def get_module_from_cart(cart_id):
    module_id = None
    cart = Cart.objects.filter(id=cart_id).first()
    if cart:
        module_id = cart.module_id

    return module_id


def get_barcode_package_valid(barcode):
    barcode_package_valid = set()
    for bcd in barcode:
        barcode_valid = validate_barcode(bcd)
        if barcode_valid:
            if not barcode_valid.startswith(("1", "2")) and barcode_valid not in barcode_package_valid:
                barcode_package_valid.add(barcode_valid)
    return list(barcode_package_valid)


def get_available_chute(list_chute):
    query_set = CrossbeltChute.objects.filter(
        id__in=list_chute,
        status=1
    )
    available_chute_obj = get_list_or_none(query_set)
    if available_chute_obj:
        return random.choice(available_chute_obj).id
    return random.choice(list_chute)


def lookup_destination_code_package(pkg_order, induction_no, plan_id):
    """This function find the chute for package to optimize sorting,
    find the chute order by cart -> module -> station -> province

    Args:
        pkg_order (int): Package order
        induction_no (int): Induction No
        plan_id (int): id plan
    Returns:
        [str, int, int]: [Destination Code, Chute Type, Bag order]
    """
    bag_order = None

    if not plan_id:
        return lookup_reject_destination_code(induction_no),\
               CrossbeltSortingHistory.ChuteType.REJECT.value, bag_order

    # get package info from local database or get from API if not existed
    package_wms = PackageWMS.objects.filter(pkg_order=pkg_order).first() or get_info_package(pkg_order=int(pkg_order))
    if not package_wms:
        return lookup_reject_destination_code(induction_no),\
               CrossbeltSortingHistory.ChuteType.REJECT.value, bag_order
    bag_order = package_wms.bag_import
    # Đơn quá cân, chia về máng reject cho đơn quá cân
    if package_wms.weight and package_wms.weight >= get_max_weight():
        return lookup_reject_over_weight_destination_code(induction_no),\
               CrossbeltSortingHistory.ChuteType.REJECT.value, bag_order

    if package_wms.pkg_status in [1, 2, 7, 8, 12]:
        return lookup_reject_no_sorting_destination_code(induction_no),\
               CrossbeltSortingHistory.ChuteType.REJECT.value, bag_order

    if package_wms.pkg_status in [5, 6, 9, 11, 20] and package_wms.done_at and package_wms.rt_delay\
            and package_wms.done_at + timedelta(package_wms.rt_delay) > datetime.now():
        return lookup_reject_no_sorting_destination_code(induction_no),\
               CrossbeltSortingHistory.ChuteType.REJECT.value, bag_order

    return find_destination_code_flow_piority(package_wms, induction_no, plan_id)


def lookup_destination_code_bag(bag_order):
    destination_code = None
    chute_query = """
        SELECT
            chute_id
        FROM
            sorting_plan_chute spc
            INNER JOIN sorting_plan_chute_detail spcd on spcd.sorting_plan_chute_id = spc.id
        WHERE
            spc.plan_id=%(plan_id)s AND
            spcd.destination_code=%(dst_id)s AND
            spcd.destination_type=%(dst_type)s;
        """

    sorting_plan = CrossbeltSortingHistory.objects.filter(is_active=1).first()
    plan_id = sorting_plan.id if sorting_plan else None
    if not plan_id:
        return destination_code, plan_id, bag_order

    dst_station_id = get_info_bag(bag_order)
    if dst_station_id:
        sorting_plan = CrossbeltSortingHistory.objects.filter(is_active=1).first()
        plan_id = sorting_plan.id if sorting_plan else None

        with connection.cursor() as cursor:
            cursor.execute(chute_query, {
                "plan_id": plan_id,
                "dst_id": dst_station_id,
                "dst_type": 1
            })
        sorting_plan_detail = cursor.fetchall()

        if sorting_plan_detail:
            destination_code = random.choice(sorting_plan_detail)[0]
            return destination_code, plan_id, bag_order

    return destination_code, plan_id, bag_order


def find_destination_code_flow_piority(package_wms, induction_no, plan_id):
    bag_order = package_wms.bag_import
    trf_type = get_tranfer_type(package_wms)
    chute_query = generate_query(package_wms.dst_cart_id, package_wms.dst_module_id, package_wms.dst_station_id)
    if chute_query:
        # lookup chute id by cart, module and station
        with connection.cursor() as cursor:
            cursor.execute(chute_query, {
                "plan_id": plan_id,
                "trf_type": tuple(trf_type),
                "dst_cart_id": package_wms.dst_cart_id,
                "dst_cart_type": 3,
                "dst_module_id": package_wms.dst_module_id,
                "dst_module_type": 2,
                "dst_station_id": package_wms.dst_station_id,
                "dst_station_type": 1
            })
            sorting_plan_detail = cursor.fetchall()

        if sorting_plan_detail:
            # group by cart, module and station
            group_dict = dict()
            for row in sorting_plan_detail:
                des_type = row[2]
                if des_type not in group_dict:
                    group_dict[des_type] = [row]
                else:
                    group_dict[des_type].append(row)

            # prioritize in order: cart, module, station
            if DestinationType.CART.value in group_dict:
                return random.choice(group_dict[DestinationType.CART.value])[0],\
                       CrossbeltSortingHistory.ChuteType.SUCCESS.value, bag_order

            if DestinationType.MODULE.value in group_dict:
                return random.choice(group_dict[DestinationType.MODULE.value])[0],\
                       CrossbeltSortingHistory.ChuteType.SUCCESS.value, bag_order

            if DestinationType.STATION.value in group_dict:
                return random.choice(group_dict[DestinationType.STATION.value])[0],\
                       CrossbeltSortingHistory.ChuteType.SUCCESS.value, bag_order
        else:
            # look up chute id by province id
            station = Station.objects.filter(id=package_wms.dst_station_id).first()
            if not station:
                return lookup_reject_destination_code(
                    induction_no), CrossbeltSortingHistory.ChuteType.REJECT.value, bag_order

            with connection.cursor() as cursor:
                cursor.execute(generate_province_query(), {
                    "plan_id": plan_id,
                    "dst_province_id": station.province_id,
                    "dst_province_type": 0,
                    "trf_type": tuple(trf_type)
                })
                sorting_plan_detail = cursor.fetchall()
            if sorting_plan_detail:
                return random.choice(sorting_plan_detail)[0], CrossbeltSortingHistory.ChuteType.SUCCESS.value, bag_order

    return lookup_reject_destination_code(induction_no), CrossbeltSortingHistory.ChuteType.REJECT.value, bag_order


def lookup_pda_destination_code(induction_no):
    """
    drop to PDA for manual scanning and re-induction
    """

    if int(induction_no) in INDUCTION_ZONE_A:
        destination_code = PDA_CHUTE_ZONE_A
    elif int(induction_no) in INDUCTION_ZONE_B:
        destination_code = PDA_CHUTE_ZONE_B
    else:
        destination_code = None

    return destination_code


def lookup_reject_destination_code(induction_no):
    list_reject_chute = REJECT_CHUTE_ZONE_A  # default REJECT ZONE A
    if int(induction_no) in INDUCTION_ZONE_A:
        list_reject_chute = get_reject_chute_zone(zone_key="A")
    elif int(induction_no) in INDUCTION_ZONE_B:
        list_reject_chute = get_reject_chute_zone(zone_key="B")

    return get_available_chute(list_reject_chute)


def lookup_reject_over_weight_destination_code(induction_no):
    # default REJECT CHUTE OVER WEIGHT ZONE A
    list_reject_chute = REJECT_CHUTE_OVER_WEIGHT_ZONE_A
    if int(induction_no) in INDUCTION_ZONE_A:
        list_reject_chute = get_over_weight_reject_chute(zone_key="A")
    elif int(induction_no) in INDUCTION_ZONE_B:
        list_reject_chute = get_over_weight_reject_chute(zone_key="B")

    return get_available_chute(list_reject_chute)


def lookup_reject_no_sorting_destination_code(induction_no):
    # default REJECT CHUTE NO SORTING ZONE A
    list_reject_chute = REJECT_CHUTE_NO_SORTING_ZONE_A
    if int(induction_no) in INDUCTION_ZONE_A:
        list_reject_chute = get_no_sorting_reject_chute(zone_key="A")
    elif int(induction_no) in INDUCTION_ZONE_B:
        list_reject_chute = get_no_sorting_reject_chute(zone_key="B")

    return get_available_chute(list_reject_chute)


def insert_or_update_sorting_history(sorting_history, **kwargs):
    barcode_input = kwargs.get("BarCode")
    create_time = kwargs.get("CreateTime")
    get_on_time = kwargs.get("GetOnTime")
    if sorting_history:
        sorting_history.scanner_id = kwargs.get("ScannerNo")
        sorting_history.induction_id = kwargs.get("InductionNO")
        sorting_history.carrier_id = kwargs.get("CarrierID")
        sorting_history.loop = kwargs.get("Loops")
        sorting_history.chute_id = kwargs.get("chute_id")
        sorting_history.chute_type = kwargs.get("chute_type")
        sorting_history.destination_code = kwargs.get("destination_code")
        sorting_history.dst_request_time = datetime.strptime(
            create_time, "%Y-%m-%d %H:%M:%S") if create_time else None
        sorting_history.in_carrier_time = datetime.strptime(
            get_on_time, "%Y-%m-%d %H:%M:%S") if get_on_time else None
    else:
        sorting_history = CrossbeltSortingHistory(
            barcode_input=",".join(barcode_input),
            pkg_order=kwargs.get("pkg_order"),
            bag_order=kwargs.get("bag_order"),
            induction_id=kwargs.get("InductionNO"),
            carrier_id=kwargs.get("CarrierID"),
            scanner_id=kwargs.get("ScannerNo"),
            chute_id=kwargs.get("chute_id"),
            chute_type=kwargs.get("chute_type"),
            loop=kwargs.get("Loops"),
            destination_code=kwargs.get("destination_code"),
            dst_request_time=datetime.strptime(
                create_time, "%Y-%m-%d %H:%M:%S") if create_time else None,
            in_carrier_time=datetime.strptime(
                get_on_time, "%Y-%m-%d %H:%M:%S") if get_on_time else None,
            sorting_status=kwargs.get("sorting_status"),
            sorting_plan_id=kwargs.get("plan_id"),
        )
    sorting_history.save()
    return True
