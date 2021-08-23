import time
from datetime import datetime
from django.db import connection

from .....model.crossbelt import CrossbeltChute, CrossbeltSortingPlanChute
from .....constant import TEMP_IMG, BagType, INTERVAL_TIME_FOR_BAG_CREATE, NORMAL_CHUTE_ZONE_A, NORMAL_CHUTE_ZONE_B


def get_chutes_by_station(plan_id, chutes_object):
    with connection.cursor() as cursor:
        raw_query_station = """
            SELECT
                c.id,
                c.code,
                c.status,
                spcd.destination_code AS dst_station_id,
                s.code,
                s.name,
                s.province_id
            FROM
                chute c
                LEFT JOIN sorting_plan_chute spc ON c.id = spc.chute_id
                LEFT JOIN sorting_plan_chute_detail spcd ON spcd.sorting_plan_chute_id = spc.id
                INNER JOIN station s ON spcd.destination_code = s.id
            WHERE
                spc.plan_id = %(plan_id)s
                AND spcd.destination_type = 1
        """
        cursor.execute(raw_query_station, {
            'plan_id': plan_id
        })
        for row in cursor.fetchall():
            chute_id = row[0]
            chute_dst = {
                "station_id": row[3],
                "station_code": row[4],
                "station_name": row[5],
                "province_id": row[6],
            }
            if chute_id not in chutes_object.keys():
                chutes_object[chute_id] = {
                    "chute_id": row[0],
                    "chute_code": row[1],
                    "chute_status": row[2],
                    "list_station_in_chute": [chute_dst]
                }
            else:
                chutes_object[chute_id]["list_station_in_chute"].append(chute_dst)

    return chutes_object


def get_chutes_by_module(plan_id, chutes_object):
    with connection.cursor() as cursor:
        raw_query_module = """
            SELECT
                c.id,
                c.code,
                c.status,
                spcd.destination_code as dst_module_id,
                m.alias,
                m.type,
                m.station_id
            FROM
                chute c
                LEFT JOIN sorting_plan_chute spc ON c.id = spc.chute_id
                LEFT JOIN sorting_plan_chute_detail spcd on spcd.sorting_plan_chute_id = spc.id
                INNER JOIN module m ON spcd.destination_code = m.id
            WHERE
                spc.plan_id = %(plan_id)s
                AND spcd.destination_type = 2
        """

        cursor.execute(raw_query_module, {
            'plan_id': plan_id
        })
        for row in cursor.fetchall():
            chute_id = row[0]
            chute_code = row[1]
            chute_status = row[2]
            module_id = row[3]
            module_alias = row[4]
            module_type = row[5]
            station_id = row[6]
            chute_dst = {
                "module_id": module_id,
                "module_alias": module_alias,
                "module_type": module_type,
                "station_id": station_id,
            }
            if chute_id not in chutes_object.keys():
                chutes_object[chute_id] = {
                    "chute_id": chute_id,
                    "chute_code": chute_code,
                    "chute_status": chute_status,
                    "list_module_in_chute": [chute_dst]
                }
            elif "list_module_in_chute" not in chutes_object[chute_id]:
                chutes_object[chute_id]["list_module_in_chute"] = [chute_dst]
            else:
                chutes_object[chute_id]["list_module_in_chute"].append(chute_dst)
    return chutes_object


def get_chutes_by_province(plan_id, chutes_object):
    with connection.cursor() as cursor:
        raw_query_province = """
            SELECT
                c.`id`,
                c.`code`,
                c.`status`,
                spcd.`destination_code` AS dst_province_id,
                p.`province_code`,
                p.`province_name`
            FROM
                chute c
                LEFT JOIN sorting_plan_chute spc ON c.`id` = spc.`chute_id`
                LEFT JOIN sorting_plan_chute_detail spcd on spcd.`sorting_plan_chute_id` = spc.`id`
                INNER JOIN province p ON spcd.`destination_code` = p.`province_id`
            WHERE
                spc.`plan_id` = %(plan_id)s
                AND spcd.`destination_type` = 0
        """

        cursor.execute(raw_query_province, {
            'plan_id': plan_id
        })
        for row in cursor.fetchall():
            chute_id = row[0]
            chute_code = row[1]
            chute_status = row[2]
            province_id = row[3]
            province_code = row[4]
            province_name = row[5]
            chute_dst = {
                "province_id": province_id,
                "province_code": province_code,
                "province_name": province_name,
            }
            if chute_id not in chutes_object.keys():
                chutes_object[chute_id] = {
                    "chute_id": chute_id,
                    "chute_code": chute_code,
                    "chute_status": chute_status,
                    "list_province_in_chute": [chute_dst]
                }
            elif "list_province_in_chute" not in chutes_object[chute_id]:
                chutes_object[chute_id]["list_province_in_chute"] = [chute_dst]
            else:
                chutes_object[chute_id]["list_province_in_chute"].append(chute_dst)
    return chutes_object


def get_chutes_from_plan_id_v2(plan_id):
    """
        - Function get all chutes which have destinations (station, module, province)
        and count number of packages in each chute
        - Use raw query django.db.connection
    """
    chutes_object = dict()
    if plan_id:
        # query by station id
        chutes_object = get_chutes_by_station(plan_id, chutes_object)
        # query by module id
        chutes_object = get_chutes_by_module(plan_id, chutes_object)
        # query by province id
        chutes_object = get_chutes_by_province(plan_id, chutes_object)

    with connection.cursor() as cursor:
        raw_query = """
            SELECT
                chute.`id`,
                chute.`code`,
                chute.`status`,
                count(DISTINCT(chute_detail.`pkg_order`))
            FROM
                chute
                LEFT JOIN chute_detail ON chute_detail.`chute_id` = chute.`id`
            GROUP BY
                chute.`id`
        """
        cursor.execute(raw_query)
        for row in cursor.fetchall():
            chute_id = row[0]
            count = row[3]
            if chutes_object.get(chute_id):
                # return default [] if there is no config of province, module or station
                if "list_province_in_chute" not in chutes_object[chute_id]:
                    chutes_object[chute_id]["list_province_in_chute"] = []
                if "list_module_in_chute" not in chutes_object[chute_id]:
                    chutes_object[chute_id]["list_module_in_chute"] = []
                if "list_station_in_chute" not in chutes_object[chute_id]:
                    chutes_object[chute_id]["list_station_in_chute"] = []

                # add count packages
                chutes_object[chute_id]["chute_packages"] = count
            else:
                # return default chute info
                chutes_object[chute_id] = {
                    "chute_id": chute_id,
                    "chute_code": row[1],
                    "chute_status": row[2],
                    "list_station_in_chute": [],
                    "list_province_in_chute": [],
                    "list_module_in_chute": [],
                    "chute_packages": count
                }

    return chutes_object


def get_interval_waiting_time(chute_id):
    """
    calculate waiting time by the distance ratio
    min 10s
    """
    # zone A
    if chute_id <= NORMAL_CHUTE_ZONE_A[1]:
        return INTERVAL_TIME_FOR_BAG_CREATE * (NORMAL_CHUTE_ZONE_A[1] - chute_id) // NORMAL_CHUTE_ZONE_A[1] + 10
    # zone B
    return INTERVAL_TIME_FOR_BAG_CREATE * \
           (NORMAL_CHUTE_ZONE_B[1] - chute_id) // (NORMAL_CHUTE_ZONE_B[1] - NORMAL_CHUTE_ZONE_A[1]) + 10


def check_bag_create_condition(chute_id, chute_status, chute_modified):
    """
    from chute locking event up to now > interval waiting time
    => allow creating bag
    """
    if chute_status:
        return False
    interval_waiting_time = get_interval_waiting_time(chute_id)
    if time.time() - datetime.timestamp(chute_modified) > interval_waiting_time:
        return True

    return False


def check_pkg_not_in_chute(lst_chute_id):
    """
    return: set of chute ids have any packages which has not yet dropped into chute
    """
    query = """
        SELECT DISTINCT
            chute.id
        FROM
            chute
        INNER JOIN
            sorting_history ON chute.id = sorting_history.chute_id
        WHERE
            chute.id in %(lst_chute_id)s
            AND sorting_history.in_chute_time is Null
            AND sorting_history.created > NOW() - INTERVAL 1 minute;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, {
            "lst_chute_id": lst_chute_id
        })
        list_chutes = cursor.fetchall()

    set_chute_ids = set()
    if list_chutes:
        set_chute_ids.update([row[0] for row in list_chutes])

    return set_chute_ids


def get_package_info_by_chute(chute_id):
    with connection.cursor() as cursor:
        raw_query = """
                SELECT
                    chute_detail.`chute_id`,
                    chute_detail.`pkg_order`,
                    new_package_wms.`dst_station_id`,
                    new_package_wms.`product_name`,
                    new_package_wms.`alias`,
                    new_package_wms.`weight`,
                    new_package_wms.`pkg_id`,
                    new_package_wms.`pkg_status`,
                    new_package_wms.`transport`,
                    station.`code`,
                    station.`name`,
                    chute_detail.`in_chute_time`,
                    chute_detail.`created`,
                    images.`ghtk_path`,
                    province.`province_id`,
                    province.`province_code`,
                    province.`province_name`,
                    chute.`code`,
                    chute.`status`,
                    chute.`zone`,
                    chute.`modified`
                FROM
                    chute_detail
                    JOIN new_package_wms ON new_package_wms.`pkg_order` = chute_detail.`pkg_order`
                    LEFT JOIN sorting_history on sorting_history.`id` = chute_detail.`sorting_history_id`
                    LEFT JOIN images on images.`id` = sorting_history.`image_id`
                    LEFT JOIN station ON station.`id` = new_package_wms.`dst_station_id`
                    LEFT JOIN province ON province.`province_id` = station.`province_id`
                    LEFT JOIN chute on chute.`id` = chute_detail.`chute_id`
                WHERE
                    chute_detail.`chute_id` = %(chute_id)s
            """
        cursor.execute(raw_query, {
            'chute_id': chute_id
        })
        list_rows = cursor.fetchall()

    return list_rows


def get_package_info_by_chute_station(chute_id, staion_id):
    with connection.cursor() as cursor:
        raw_query = """
                SELECT
                    chute_detail.`chute_id`,
                    chute_detail.`pkg_order`,
                    new_package_wms.`product_name`,
                    new_package_wms.`alias`,
                    new_package_wms.`weight`,
                    new_package_wms.`pkg_id`,
                    new_package_wms.`pkg_status`,
                    new_package_wms.`transport`,
                    station.`code`,
                    station.`name`,
                    chute_detail.`in_chute_time`,
                    chute_detail.`created`,
                    images.`ghtk_path`,
                    province.`province_id`,
                    province.`province_code`,
                    province.`province_name`,
                    chute.`code`,
                    chute.`status`,
                    chute.`zone`,
                    chute.`modified`
                FROM
                    chute_detail
                    JOIN new_package_wms ON new_package_wms.`pkg_order` = chute_detail.`pkg_order`
                    LEFT JOIN sorting_history on sorting_history.`id` = chute_detail.`sorting_history_id`
                    LEFT JOIN images on images.`id` = sorting_history.`image_id`
                    LEFT JOIN station ON station.`id` = %(main_station_id)s
                    LEFT JOIN province ON province.`province_id` = station.`province_id`
                    LEFT JOIN chute on chute.`id` = chute_detail.`chute_id`
                WHERE
                    chute_detail.`chute_id` = %(chute_id)s
            """
        cursor.execute(raw_query, {
            'chute_id': chute_id,
            'main_station_id': staion_id
        })
        list_rows = cursor.fetchall()
    return list_rows


def get_chute_packages_info_with_normal_bag(chute_info, lst_chute_has_pkg_not_in_chute):
    chute_id = chute_info['chute_id']
    list_rows = get_package_info_by_chute(chute_id)
    if not list_rows:
        chute = CrossbeltChute.objects.filter(id=chute_id).first()
        chute_pkg_object = {
            "chute_id": chute_info["chute_id"],
            "chute_code": chute.code,
            "is_locked": 0 if chute.status else 1,
            "allow_bag_create": check_bag_create_condition(chute_id, chute.status, chute.modified),
            "chute_zone": chute.zone,
            "bag_type": BagType.NORMAL.value,
            "transport": chute_info["transport_type"],
            "list_stations": {}
        }
        return chute_pkg_object

    chute_status = list_rows[0][18]
    chute_modified = list_rows[0][20]
    if chute_id not in lst_chute_has_pkg_not_in_chute and chute_status == 0:
        # all packages are in chute and chute was locked => allow without waiting
        allow_bag_create = True
    else:
        # waiting an interval time before allowing to create bag
        allow_bag_create = check_bag_create_condition(chute_id, chute_status, chute_modified)

    chute_pkg_object = {
        "chute_id": chute_id,
        "chute_code": list_rows[0][17],
        "is_locked": 0 if chute_status else 1,
        "allow_bag_create": allow_bag_create,
        "chute_zone": list_rows[0][19],
        "bag_type": BagType.NORMAL.value,
        "transport": chute_info["transport_type"],
        "list_stations": {}
    }
    # group packages by station id
    for row in list_rows:
        dst_station_id = row[2]
        pkg_status = row[7]
        code = row[9]
        province_code = row[15]
        if not row[7]:
            pkg_status = None
        elif pkg_status in (3, 10):
            pkg_status = "delivery"
        else:
            pkg_status = "return"

        package = {
            "pkg_order": row[1],
            "product_name": row[3],
            "alias": '.'.join(row[4].split(".")) if row[4] else "",
            "image": row[13] if row[13] else TEMP_IMG,
            "time": row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else row[12].strftime(
                '%Y-%m-%d %H:%M:%S'),
            "weight": row[5],
            "pkg_id": row[6],
            "pkg_status": pkg_status,
            "transport": row[8]
        }
        if dst_station_id not in chute_pkg_object["list_stations"].keys():
            if province_code is None and code is not None:
                province_code = code.split('.')[0]

            chute_pkg_object["list_stations"][dst_station_id] = {
                "station_id": dst_station_id,
                "station_code": code,
                "station_name": row[10],
                "province_id": row[14],
                "province_code": province_code,
                "province_name": row[16],
                "list_packages": [package],
            }
        else:
            chute_pkg_object["list_stations"][dst_station_id]["list_packages"].append(package)

    return chute_pkg_object


def get_chute_packages_info_with_extra_bag(chute_info, lst_chute_has_pkg_not_in_chute):
    chute_id = chute_info["chute_id"]
    main_station_id = chute_info["main_station_id"]
    list_rows = get_package_info_by_chute_station(chute_id, main_station_id)
    if not list_rows:
        chute = CrossbeltChute.objects.filter(id=chute_id).first()
        chute_pkg_object = {
            "bag_type": BagType.EXTRA.value,
            "chute_id": chute_id,
            "chute_code": chute.code,
            "is_locked": 0 if chute.status else 1,
            "allow_bag_create": check_bag_create_condition(chute_id, chute.status, chute.modified),
            "chute_zone": chute.zone,
            "transport": chute_info["transport_type"],
            "list_stations": {}
        }
        return chute_pkg_object
    chute_status = list_rows[0][17]
    chute_modified = list_rows[0][19]

    if chute_id not in lst_chute_has_pkg_not_in_chute and chute_status == 0:
        # all packages are in chute and chute was locked => create without waiting
        allow_bag_create = True
    else:
        # waiting an interval time before allowing to create bag
        allow_bag_create = check_bag_create_condition(chute_id, chute_status, chute_modified)

    chute_pkg_object = {
        "bag_type": BagType.EXTRA.value,
        "chute_id": chute_id,
        "chute_code": list_rows[0][16],
        "is_locked": 0 if chute_status else 1,
        "allow_bag_create": allow_bag_create,
        "chute_zone": list_rows[0][18],
        "transport": chute_info["transport_type"],
        "list_stations": {}
    }

    # group packages by station id
    for row in list_rows:
        pkg_status = row[6]
        if not pkg_status:
            pkg_status = None
        elif pkg_status in (3, 10):
            pkg_status = "delivery"
        else:
            pkg_status = "return"
        package = {
            "pkg_order": row[1],
            "product_name": row[2],
            "alias": '.'.join(row[3].split(".")) if row[3] else "",
            "image": row[12] if row[12] else TEMP_IMG,
            "time": row[10].strftime('%Y-%m-%d %H:%M:%S') if row[10] else row[11].strftime(
                '%Y-%m-%d %H:%M:%S'),
            "weight": row[4],
            "pkg_id": row[5],
            "pkg_status": pkg_status,
            "transport": row[7]
        }
        if main_station_id not in chute_pkg_object["list_stations"].keys():
            chute_pkg_object["list_stations"][main_station_id] = {
                "station_id": main_station_id,
                "station_code": row[8],
                "station_name": row[9],
                "province_id": row[13],
                "province_code": row[14],
                "province_name": row[15],
                "list_packages": [package],
            }
        else:
            chute_pkg_object["list_stations"][main_station_id]["list_packages"].append(package)

    return chute_pkg_object


def get_packages_in_chute_v2(lst_chute_id):
    """
        - API v2
        - Function get all packages in chute, group by destination(station) and show info of package order
        - packages in chute with province config will be group by its station_id from new_package_wms table
        - extra bags (bao tong) will be group by its main station_id instead of province id
    """
    lst_chute_pkg = list()
    if not lst_chute_id:
        return lst_chute_pkg

    lst_chute_bag_info = CrossbeltSortingPlanChute.objects.filter(
        plan__is_active=1,
        chute_id__in=lst_chute_id
    ).values("chute_id", "plan_id", "bag_type", "main_station_id", "transport_type")
    if not lst_chute_bag_info:
        return lst_chute_pkg

    # check packages has not yet dropped into chute
    lst_chute_has_pkg_not_in_chute = check_pkg_not_in_chute([i['chute_id'] for i in lst_chute_bag_info])

    for chute_info in lst_chute_bag_info:
        bag_type = chute_info['bag_type']
        chute_pkg_object = None
        # get packages cho bao thuong
        if bag_type == BagType.NORMAL.value:
            chute_pkg_object = get_chute_packages_info_with_normal_bag(chute_info, lst_chute_has_pkg_not_in_chute)

        # get packages cho bao tong
        elif bag_type == BagType.EXTRA.value:
            chute_pkg_object = get_chute_packages_info_with_extra_bag(chute_info, lst_chute_has_pkg_not_in_chute)

        if chute_pkg_object:
            lst_chute_pkg.append(chute_pkg_object)

    # convert list_stations from dict to list
    for chute_pkg in lst_chute_pkg:
        chute_pkg["list_stations"] = chute_pkg["list_stations"].values()
        chute_pkg["total_packages"] = sum([len(station_info["list_packages"])
                                           for station_info in chute_pkg["list_stations"]])

    return lst_chute_pkg
