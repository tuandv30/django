from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import is_valid_post_request, get_barcode_package_valid
from .utils import process_barcode_not_readable, process_no_barcode, process_only_one_barcode, process_multiple_barcode
from .....celery_tasks.background_tasks import tasks
from .....core.whitelist_ip import check_whitelist
from .....model.crossbelt import CrossbeltSortingPlan
from .....model.wms_local import PackageWarehouse
from .....constant import BARCODE_NOREAD, WHITELIST_IP_ADDRESS_API_WCS


@api_view(['POST'])
@check_whitelist(WHITELIST_IP_ADDRESS_API_WCS)
def destination(request):
    """
    API endpoint for WCS to get chute id of packages on local cross-belt
    """
    response = {
        "errorCod": "",
        "errorMsg": "",
    }
    post_data = request.data
    kwargs = post_data
    kwargs["sorting_status"] = 1
    # Validate input, if invalid => save input into sorting_history table
    if not is_valid_post_request(request.data):
        response.update({
            "BarCode": "",
            "PostCode": "",
            "wmsMsg": "Invalid input"
        })
        return Response(status=200, content_type='application/json', data=response)

    barcode = post_data.get("BarCode")

    # Case barcode not readable
    if len(barcode) == 1 and barcode[0] == BARCODE_NOREAD:
        response = process_barcode_not_readable(request, kwargs, response)
        return Response(status=200, content_type='application/json', data=response)

    barcode_package_valid = get_barcode_package_valid(barcode)

    # Case: không có mã đơn => chia về cổng PDA (for manual scanning and re-induction)
    if not barcode_package_valid:
        response = process_no_barcode(request, kwargs, response)
        return Response(status=200, content_type='application/json', data=response)

    # Get plan is active
    sorting_plan = CrossbeltSortingPlan.objects.filter(is_active=1).first()
    plan_id = sorting_plan.id if sorting_plan else None

    # Case: có 1 mã đơn  => tìm đích theo mã đơn
    if len(barcode_package_valid) == 1:
        response = process_only_one_barcode(request, plan_id, barcode_package_valid[0], kwargs, response)
        package_warehouse = PackageWarehouse.objects.filter(pkg_order=barcode_package_valid[0]).order_by("-id").first()

        if not package_warehouse \
            or package_warehouse.warehouse_status < package_warehouse.WarehouseStatus.IMPORT_WAREHOUSE.value \
            or package_warehouse.import_type == package_warehouse.ImportExportType.TRANSIT.value \
                or package_warehouse.modified < datetime.now() - timedelta(hours=12):
            tasks.transfer_station_package_from_202.delay(pkg_order=barcode_package_valid[0])
        return Response(status=200, content_type='application/json', data=response)

    # Case: Có nhiều mã đơn
    if len(barcode_package_valid) > 1:
        response = process_multiple_barcode(request, plan_id, barcode_package_valid, kwargs, response)
        return Response(status=200, content_type='application/json', data=response)

    return Response(status=200, content_type='application/json', data=response)
