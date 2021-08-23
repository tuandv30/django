import json
from celery import shared_task
from ..mqtt import MqttServices
from ..utils import change_current_station_v2, get_image_path_from_sorting_history, get_info_package_and_station
from ...model.crossbelt import CrossbeltSortingPlan
from ...constant import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PWD, MQTT_TOPIC_PKG_IN_CHUTE


@shared_task(name="transfer_station_package_from_202", ignore_result=True)
def transfer_station_package_from_202(pkg_order):
    result = change_current_station_v2(pkg_order)
    if result:
        return "Done change current station for pkg {}".format(pkg_order)

    return "Fail change current station {}".format(pkg_order)


@shared_task(name="pub_mqtt", ignore_result=True)
def pub_package_in_chute(list_data_in_chute):
    # list_data_in_chute = [{"chute_id": 1, "pkg_order": 3243341321, "drop_time": "2020-09-12 12:12:12"}]
    try:
        list_data_in_chute = json.loads(list_data_in_chute)
        sorting_plan = CrossbeltSortingPlan.objects.filter(is_active=1).first()
        plan_id = sorting_plan.id if sorting_plan else None
        mqtt_services = MqttServices(host=MQTT_HOST, port=MQTT_PORT, user=MQTT_USER, pwd=MQTT_PWD)
        for data_chute in list_data_in_chute:
            chute_id = data_chute.get("chute_id")
            pkg_order = data_chute.get("pkg_order")
            drop_time = data_chute.get("drop_time")
            sorting_history_id = data_chute.get("sorting_history_id")
            package_wms, station = get_info_package_and_station(data_chute, plan_id)
            image_path = get_image_path_from_sorting_history(sorting_history_id)
            topic = MQTT_TOPIC_PKG_IN_CHUTE.format(chute_id)
            messages = json.dumps({
                "chute_id": chute_id,
                "station": {
                    "station_id": station.id if station else None,
                    "station_code": station.code if station else None,
                    "station_name": station.name if station else None
                },
                "order_info": {
                    "pkg_order": pkg_order,
                    "product_name": package_wms.product_name if package_wms else None,
                    "alias": package_wms.alias if package_wms else None,
                    "image": image_path,
                    "drop_time": drop_time
                }
            })
            mqtt_services.publish_messages(topic=topic, payload=messages, qos=1)
        mqtt_services.disconnect()
    except BaseException as exc:
        return str(exc)
    return "Success true"
