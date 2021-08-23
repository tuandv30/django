import copy
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncHour
from .....constant import COLOR
from .....model.crossbelt import CrossbeltInduction, CrossbeltSortingHistory, CrossbeltStatisticSorting
from .....model.wms_local import PackageWarehouse, StatisticPackageWarehouse


def get_dataset_statistic_total(sorting_history, labels):
    color = copy.copy(COLOR)
    data = [0] * len(labels)
    if sorting_history:
        for i in sorting_history:
            hour_date = i.get("hour")
            index = labels.index(hour_date.strftime("%d/%m %H:00"))
            data[index] = i.get("total")
    datasets = [
        {
            "label": "Sản lượng",
            "borderColor": [color[0]] * 25,
            "data": data,
        }
    ]
    return datasets


def get_max_statistic_total(sorting_history):
    total_max, max_at = None, None
    if sorting_history:
        sorting_history_max = sorting_history[0]
        total_max = sorting_history_max.get("total")
        max_at = sorting_history_max.get('hour').strftime("%H:00")

    return total_max, max_at


def get_max_statistic_induction_per_hour(sorting_history_result):
    induction_max, max_at, max_in = None, None, None
    if sorting_history_result:
        sorting_history_max = sorting_history_result[0]
        stt_hour = sorting_history_max.get("stt_hour")
        induction_max = sorting_history_max.get("total")
        max_at = sorting_history_max.get("hour").strftime(
            "%H:00") if sorting_history_max.get("hour") else "{}:00".format(stt_hour)
        max_in = sorting_history_max.get("induction_id")

    return induction_max, max_at, max_in


def get_dataset_statistic_induction_per_hour(sorting_history_result, labels):
    color = copy.copy(COLOR)
    datasets = list()
    datasets_dict = dict()
    induction_id = CrossbeltInduction.objects.values_list(
        'id', flat=True).order_by('id')
    for i in induction_id:
        induction_code = CrossbeltInduction.objects.get(
            id=i).code
        datasets_dict[i] = {
            'label': induction_code,
            'borderColor': color.pop(),
            'data': [0] * 25
        }
    if sorting_history_result:
        for i in sorting_history_result:
            induction_id = i.get("induction_id")
            stt_hour = i.get('stt_hour')
            stt_date = i.get('stt_date')
            hour_date = i.get('hour') or datetime(
                stt_date.year, stt_date.month, stt_date.day, stt_hour)
            index = labels.index(hour_date.strftime("%d/%m %H:00"))
            datasets_dict[induction_id]['data'][index] = i.get('total')
    for data in datasets_dict.values():
        datasets.append(data)
    return datasets


def history_from_dst_type(dst_type, realtime, **kwargs):
    sorting_history = list()
    if dst_type == "total":
        if realtime == "1":
            sorting_history = CrossbeltSortingHistory.objects.filter(
                created__range=(kwargs.get('from_time'), kwargs.get('to_time'))
            ).annotate(
                hour=TruncHour('created')
            ).values('hour').annotate(
                total=Count('id')
            ).values('hour', 'total', 'induction_id').order_by('-total')
        else:
            sorting_history = CrossbeltStatisticSorting.objects.filter(
                hour__range=(kwargs.get('from_time_hour'), kwargs.get('to_time_hour'))
            ).values('induction_id').annotate(
                total=Sum('total')
            ).values('induction_id', 'stt_date', 'stt_hour', 'total').order_by('-total')
    elif dst_type and dst_type != "total":
        chute_type = "success"
        name_field_sum = "total_" + dst_type
        if realtime == "1":
            sorting_history = CrossbeltSortingHistory.objects.filter(
                created__range=(kwargs.get('from_time'), kwargs.get('to_time')),
                chute_type=chute_type
            ).annotate(
                hour=TruncHour('created')
            ).values('hour').annotate(
                total=Count('id')
            ).values('hour', 'total', 'induction_id').order_by('-total')
        else:
            sorting_history = CrossbeltStatisticSorting.objects.filter(
                hour__range=(kwargs.get('from_time_hour'), kwargs.get('to_time_hour'))
            ).values('induction_id').annotate(
                total=Sum(name_field_sum)
            ).values('induction_id', 'stt_date', 'stt_hour', 'total').order_by('-total')

    return sorting_history


def get_datasets_imexport(realtime, **kwargs):
    import_sorting_dataset = {
        'label': 'Nhập sorting',
        'borderColor': kwargs.get('color')[0],
        'data': [0] * len(kwargs.get('labels')),
    }
    import_transit_dataset = {
        'label': 'Nhập trung chuyển',
        'borderColor': kwargs.get('color')[5],
        'data': [0] * len(kwargs.get('labels')),
    }
    export_sorting_dataset = {
        'label': 'Xuất sorting',
        'borderColor': kwargs.get('color')[1],
        'data': [0] * len(kwargs.get('labels')),
    }
    export_transit_dataset = {
        'label': 'Xuất trung chuyển',
        'borderColor': kwargs.get('color')[4],
        'data': [0] * len(kwargs.get('labels')),
    }

    if realtime == "1":
        package_warehouse_import = PackageWarehouse.objects.filter(
            import_time__range=(kwargs.get('from_time'), kwargs.get('to_time')),
            created__range=(kwargs.get('from_time') - timedelta(days=1), kwargs.get('to_time') + timedelta(hours=1))
        ).values('import_type').annotate(
            total=Count('pkg_order'),
        ).values('total', 'import_type')
        package_warehouse_export = PackageWarehouse.objects.filter(
            export_time__range=(kwargs.get('from_time'), kwargs.get('to_time')),
            created__range=(kwargs.get('from_time') - timedelta(days=1), kwargs.get('to_time') + timedelta(hours=1))
        ).values('export_type').annotate(
            total=Count('pkg_order'),
        ).values('total', 'export_type')
        if package_warehouse_import:
            for i in package_warehouse_import:
                total = i.get("total")
                if i.get("import_type") == 0:
                    import_sorting_dataset["total"] = total
                elif i.get("import_type") == 1:
                    import_transit_dataset["total"] = total
        if package_warehouse_export:
            for i in package_warehouse_export:
                total = i.get("total")
                if i.get("export_type") == 0:
                    export_sorting_dataset["total"] = total
                elif i.get("export_type") == 1:
                    export_transit_dataset["total"] = total
    else:
        package_warehouse_statistic = StatisticPackageWarehouse.objects.filter(
            hour__range=(kwargs.get('from_time_hour'), kwargs.get('to_time_hour'))).all()
        if package_warehouse_statistic:
            for i in package_warehouse_statistic:
                hour_date = datetime(i.stt_date.year, i.stt_date.month, i.stt_date.day, i.stt_hour)
                index = kwargs.get('labels').index(hour_date.strftime("%d/%m %H:00"))
                import_sorting_dataset["data"][index] = i.import_sorting
                import_transit_dataset["data"][index] = i.import_transit
                export_sorting_dataset["data"][index] = i.export_sorting
                export_transit_dataset["data"][index] = i.export_transit
                import_sorting_dataset["total"] = sum(import_sorting_dataset["data"])
                import_transit_dataset["total"] = sum(import_transit_dataset["data"])
                export_sorting_dataset["total"] = sum(export_sorting_dataset["data"])
                export_transit_dataset["total"] = sum(export_transit_dataset["data"])
    return [import_sorting_dataset, import_transit_dataset, export_sorting_dataset, export_transit_dataset]
