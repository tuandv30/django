from django.db.models import Q
from django.db import connection
from ....core.os_config import get_sorting_province
from ....model.wms_local import Province, Station, Module, Cart
from ....model.crossbelt import CrossbeltSortingPlanChute, CrossbeltSortingPlanChuteDetail
from ....core.utils import get_list_or_none

DESTINATION_CODE_TYPE = {
    0: "Tỉnh",
    1: "Kho",
    2: "Module",
    3: "Giỏ"
}


def remove_plan(sorting_plan):
    """
    Remove sorting plan
    """
    CrossbeltSortingPlanChuteDetail.objects.filter(sorting_plan_chute__plan_id=sorting_plan.id).delete()
    CrossbeltSortingPlanChute.objects.filter(plan_id=sorting_plan.id).delete()
    sorting_plan.delete()


def filter_permission_view_action(staff):
    """ Staff member can't view superuser

    """
    if staff.is_superuser:
        return Q()
    return ~Q(is_superuser=True)


def get_sorting_plan_detail(plan_id):
    object_detail = dict()
    list_plan_station_id = list()
    with connection.cursor() as cursor:
        raw_query = """
            SELECT
                spc.`chute_id`,
                spcd.`destination_code`,
                spcd.`destination_type`,
                spc.`transport_type`,
                CONCAT_WS(" - ", p.`province_name`, p.`province_code`) AS code_text
            FROM
                crossbelt_sorting_plan sp
                INNER JOIN crossbelt_sorting_plan_chute spc ON sp.`id` = spc.`plan_id`
                INNER JOIN crossbelt_sorting_plan_chute_detail spcd ON spc.`id` = spcd.`sorting_plan_chute_id`
                INNER JOIN province p ON p.`province_id` = spcd.`destination_code`
            WHERE
                sp.`id` = %(plan_id)s
                AND spcd.`destination_type` = 0 UNION ALL
            SELECT
                spc.`chute_id`,
                spcd.`destination_code`,
                spcd.`destination_type`,
                spc.`transport_type`,
                CONCAT_WS(" - ", s.`name`, s.`code`) AS code_text
            FROM
                crossbelt_sorting_plan sp
                INNER JOIN crossbelt_sorting_plan_chute spc ON sp.`id` = spc.`plan_id`
                INNER JOIN crossbelt_sorting_plan_chute_detail spcd ON spc.`id` = spcd.`sorting_plan_chute_id`
                INNER JOIN station s ON s.`id` = spcd.`destination_code`
            WHERE
                sp.`id` = %(plan_id)s
                AND spcd.`destination_type` = 1 UNION ALL
            SELECT
                spc.`chute_id`,
                spcd.`destination_code`,
                spcd.`destination_type`,
                spc.`transport_type`,
                m.`alias` AS code_text
            FROM
                crossbelt_sorting_plan sp
                INNER JOIN crossbelt_sorting_plan_chute spc ON sp.`id` = spc.`plan_id`
                INNER JOIN crossbelt_sorting_plan_chute_detail spcd ON spc.`id` = spcd.`sorting_plan_chute_id`
                INNER JOIN module m ON m.`id` = spcd.`destination_code`
            WHERE
                sp.`id` = %(plan_id)s
                AND spcd.`destination_type` = 2 UNION ALL
            SELECT
                spc.`chute_id`,
                spcd.`destination_code`,
                spcd.`destination_type`,
                spc.`transport_type`,
                c.`alias` AS code_text
            FROM
                crossbelt_sorting_plan sp
                INNER JOIN crossbelt_sorting_plan_chute spc ON sp.`id` = spc.`plan_id`
                INNER JOIN crossbelt_sorting_plan_chute_detail spcd ON spc.`id` = spcd.`sorting_plan_chute_id`
                INNER JOIN `cart` c ON c.`id` = spcd.`destination_code`
            WHERE
                sp.`id` = %(plan_id)s
                AND spcd.`destination_type` = 3
        """
        cursor.execute(raw_query, {
            'plan_id': plan_id
        })
        for row in cursor.fetchall():
            chute_id = row[0]
            destination_code = row[1]
            destination_type = row[2]
            trf_type = row[3]
            code_text = row[4]
            if destination_type == 1:
                list_plan_station_id.append(destination_code)
            if chute_id not in object_detail.keys():
                object_detail[chute_id] = dict()
                object_detail[chute_id]["chute_type"] = trf_type
                object_detail[chute_id]["destination"] = [{
                    "dst_code": destination_code,
                    "dst_type": destination_type,
                    "code_text": "{} ({})".format(code_text, DESTINATION_CODE_TYPE.get(destination_type)),
                }]
            else:
                object_detail[chute_id]["chute_type"] = trf_type
                object_detail[chute_id]["destination"].append({
                    "dst_code": destination_code,
                    "dst_type": destination_type,
                    "code_text": "{} ({})".format(code_text, DESTINATION_CODE_TYPE.get(destination_type)),
                })
    return object_detail, list_plan_station_id


def dump_sorting_plan_detail(sorting_plan_detail):
    chute_type = dict()
    object_detail = dict()
    list_plan_station_id = list()
    if not sorting_plan_detail:
        return object_detail, chute_type, list_plan_station_id

    for i in sorting_plan_detail:
        chute_type[i.chute_id] = i.trf_type
        key = "{}|{}".format(i.destination_code, i.type)
        val = ""
        if i.type == 0:
            province = Province.objects.get(pk=i.destination_code)
            val = "{} - {} ({})".format(
                province.province_name, province.province_code, DESTINATION_CODE_TYPE.get(
                    i.type))
        elif i.type == 1:
            list_plan_station_id.append(i.destination_code)
            station = Station.objects.get(pk=i.destination_code)
            val = "{} ({})".format(
                station, DESTINATION_CODE_TYPE.get(
                    i.type))
        elif i.type == 2:
            module = Module.objects.get(pk=i.destination_code)
            val = "{} ({})".format(
                module.alias,
                DESTINATION_CODE_TYPE.get(
                    i.type))
        elif i.type == 3:
            cart = Cart.objects.get(pk=i.destination_code)
            val = "{} ({})".format(
                cart.alias,
                DESTINATION_CODE_TYPE.get(
                    i.type))
        key_val = (key, val)
        if i.chute_id not in object_detail.keys():
            object_detail[i.chute_id] = [key_val]
        else:
            object_detail[i.chute_id] = object_detail[i.chute_id] + [key_val]

    return object_detail, chute_type, list_plan_station_id


def get_miss_station(list_plan_station_id, list_province_config):
    miss_station_list = list()
    sorting_province = get_sorting_province(list_province_config)
    query_set = Station.objects.filter(
        province_id__in=sorting_province,
        working=1,
        type='station'
    ).exclude(Q(code="") | Q(trf_level="kho_tong")).values_list('id', flat=True)
    sorting_station = get_list_or_none(query_set) or list()
    for station_id in sorting_station:
        if str(station_id) not in list_plan_station_id:
            miss_station_list.append(station_id)
    miss_station = Station.objects.filter(
        id__in=miss_station_list,
    ).all()
    return miss_station
