from datetime import datetime
from .....model.wms_local import PackageWarehouse, BagWMS
from .....model.crossbelt import CrossbeltSortingHistory, CrossbeltChuteDetail


def update_sorting_history(sorting_history, data):
    chute_no = data.get("ChuteNo") or None
    carrier_id = data.get("CarrierID") or None
    create_time = data.get("CreateTime")
    drop_time = data.get("DropTime")
    sorting_history.carrier_id = carrier_id
    sorting_history.chute_id = chute_no
    sorting_history.sorting_status = 2
    sorting_history.sorting_report_time = datetime.strptime(
        create_time, "%Y-%m-%d %H:%M:%S") if create_time else None
    sorting_history.in_chute_time = datetime.strptime(
        drop_time, "%Y-%m-%d %H:%M:%S") if drop_time else None
    sorting_history.save()
    return sorting_history.id


def save_sorting_history_with_bag(bag_order, data):
    carrier_id = data.get("CarrierID") or None
    sorting_history = CrossbeltSortingHistory.objects.filter(
        bag_order=bag_order,
        carrier_id=carrier_id,
    ).order_by("-in_carrier_time").first()
    if sorting_history:
        sorting_history_id = update_sorting_history(sorting_history, data)
        return sorting_history_id
    return None


def save_sorting_history_with_package(package_order, data):
    carrier_id = data.get("CarrierID") or None
    sorting_history = CrossbeltSortingHistory.objects.filter(
        pkg_order=package_order,
        carrier_id=carrier_id,
    ).order_by("-in_carrier_time").first()
    if sorting_history:
        sorting_history_id = update_sorting_history(sorting_history, data)
        return sorting_history_id
    return None


def save_chute_detail(package_order, sorting_history_id, data):
    chute_no = data.get("ChuteNo") or None
    drop_time = data.get("DropTime")
    chute_detail = CrossbeltChuteDetail(
        chute_id=chute_no,
        pkg_order=package_order,
        sorting_history_id=sorting_history_id,
        status=0,
        in_chute_time=datetime.strptime(
            drop_time, "%Y-%m-%d %H:%M:%S") if drop_time else None,
    )
    try:
        chute_detail.save()
    except BaseException as exe:
        print(str(exe))


def update_bag_is_scaned(package_warehouse, data):
    drop_time = data.get("DropTime")
    BagWMS.objects.filter(
        bag_order=package_warehouse.bag_import
    ).update(
        is_scan=1,
        scan_time=datetime.strptime(
            drop_time, "%Y-%m-%d %H:%M:%S") if drop_time else None
    )


def update_package_warehouse_status(package_warehouse, data):
    drop_time = data.get("DropTime")
    package_warehouse.warehouse_status = PackageWarehouse.WarehouseStatus.SORTING.value
    package_warehouse.sorting_time = datetime.strptime(
        drop_time, "%Y-%m-%d %H:%M:%S") if drop_time else None
    package_warehouse.save()
