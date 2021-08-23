import json
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import save_sorting_history_with_bag, save_sorting_history_with_package
from .utils import update_bag_is_scaned, update_package_warehouse_status, save_chute_detail
from ..utils import validate_barcode
from .....celery_tasks.background_tasks import tasks
from .....core.whitelist_ip import check_whitelist
from .....model.wms_local import PackageWarehouse
from .....constant import BARCODE_NOREAD, BARCODE_INVALID, WHITELIST_IP_ADDRESS_API_WCS


@api_view(['POST'])
@check_whitelist(WHITELIST_IP_ADDRESS_API_WCS)
def sorting_report(request):
    """
        Logic xử lý data post sẽ như sau:
        - Nếu barcode là Noread Barcode hoặc Invalid Barcode => pkg_order = None
        - Nếu barcode qua xử lý regex fail => pkg_order = None
        - Update dữ liệu sorting_history
        - Nếu pkg_order = None thì:
            + không lưu vào bảng chute_detail
            + gửi message MQTT với field pkg_order = None
        - Nếu pkg_order != None thì:
            + lưu vào bảng chute_detail
            + check pkg_order đã tồn tại trong package_wms chưa, nếu chưa thì call api để lưu vào package_wms (job)
            + gửi message MQTT
    """
    post_data = request.data
    response_data = list()
    list_data_in_chute = list()
    for data in post_data:
        barcode = data.get("BarCode") or None
        if barcode in (BARCODE_NOREAD, BARCODE_INVALID):
            pkg_order, bag_order = None, None
        else:
            # Kiểm tra barcode GHTK valid
            barcode_valid = validate_barcode(barcode)
            if not barcode_valid:
                pkg_order, bag_order = None, None
            elif not barcode_valid.startswith(("1", "2")):
                pkg_order, bag_order = barcode_valid, None
            else:
                pkg_order, bag_order = None, barcode_valid

        if bag_order:
            _ = save_sorting_history_with_bag(bag_order, data)

        if pkg_order:
            sorting_history_id = save_sorting_history_with_package(pkg_order, data)
            p_warehouse = PackageWarehouse.objects.filter(
                pkg_order=pkg_order
            ).order_by("-id").first()
            if p_warehouse and p_warehouse.bag_import:
                update_bag_is_scaned(p_warehouse, data)
            if p_warehouse and p_warehouse.warehouse_status < PackageWarehouse.WarehouseStatus.SORTING.value:
                update_package_warehouse_status(p_warehouse, data)

            if not (p_warehouse and p_warehouse.puttobag_time and
                    p_warehouse.puttobag_time + timedelta(minutes=2) > datetime.now()):
                save_chute_detail(pkg_order, sorting_history_id, data)
                # Append thông tin pub mqtt task
                list_data_in_chute.append({
                    "chute_id": data.get("ChuteNo") or None,
                    "pkg_order": pkg_order,
                    "drop_time": data.get("DropTime"),
                    "sorting_history_id": sorting_history_id
                })

        # Apend thông tin barcode nhận được vào response data
        response_data.append({
            "BarCode": barcode,
            "Result": "1",
            "errorCode": "",
            "errorMsg": ""
        })

    # Publist to MQTT by celery background task
    if list_data_in_chute:
        tasks.pub_package_in_chute.delay(json.dumps(list_data_in_chute))

    return Response(status=200, content_type='application/json', data=response_data)
