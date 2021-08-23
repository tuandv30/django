import copy
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncHour
from rest_framework.decorators import api_view, authentication_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from .....constant import INDUCTION_ZONE_A, INDUCTION_ZONE_B, NORMAL_CHUTE_ZONE_B, NORMAL_CHUTE_ZONE_A, COLOR, \
    BASE_TIME
from .....model.crossbelt import CrossbeltSortingHistory
from .....core.utils import get_list_or_none
from .utils import get_dataset_statistic_total, get_max_statistic_total, \
    get_max_statistic_induction_per_hour, \
    get_dataset_statistic_induction_per_hour, history_from_dst_type, get_datasets_imexport

color = copy.copy(COLOR)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def chart_inbound_rate(request):
    now = datetime.now()
    when = request.GET.get("when")
    if when == "today":
        from_time = now - timedelta(days=1)
        to_time = now
    else:
        to_time = now - timedelta(days=7)
        from_time = to_time - timedelta(days=1)

    infeed_zone_a = CrossbeltSortingHistory.objects.filter(
        created__range=(from_time, to_time),
        induction_id__in=INDUCTION_ZONE_A
    ).count()

    infeed_zone_b = CrossbeltSortingHistory.objects.filter(
        created__range=(from_time, to_time),
        induction_id__in=INDUCTION_ZONE_B
    ).count()

    uncorrect_zone_a = CrossbeltSortingHistory.objects.filter(
        created__range=(from_time, to_time),
        induction_id__in=INDUCTION_ZONE_A,
        chute_id__range=NORMAL_CHUTE_ZONE_B
    ).count()

    uncorrect_zone_b = CrossbeltSortingHistory.objects.filter(
        created__range=(from_time, to_time),
        induction_id__in=INDUCTION_ZONE_B,
        chute_id__range=NORMAL_CHUTE_ZONE_A
    ).count()

    labels = ["ĐÚNG", "SAI"]
    datasets = [
        {
            "borderColor": [color[-1], color[1]],
            "data": [
                infeed_zone_a - uncorrect_zone_a,
                uncorrect_zone_a
            ]
        },
        {
            "borderColor": [color[-1], color[1]],
            "data": [
                infeed_zone_b - uncorrect_zone_b,
                uncorrect_zone_b
            ]
        }
    ]
    response = {
        "labels": labels,
        "datasets": datasets
    }
    return Response(status=status.HTTP_200_OK, content_type='application/json', data=response)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def chart_scanner_rate(request):
    def process_query_to_dataset(query_set):
        sorting_history = get_list_or_none(query_set)
        if not sorting_history:
            return [0] * 2
        read = 0
        noread = 0
        for i in sorting_history:
            if i.get("chute_type") == 2:
                noread += i.get("total")
            else:
                read += i.get("total")
        return [read, noread]

    now = datetime.now()
    if request.GET.get("when") == "today":
        from_time = now - timedelta(days=1)
        to_time = now
    else:
        to_time = now - timedelta(days=7)
        from_time = to_time - timedelta(days=1)

    query_set_zone_a = CrossbeltSortingHistory.objects.filter(
        created__range=(from_time, to_time),
        induction_id__in=INDUCTION_ZONE_A
    ).exclude(scanner_id__in=[3, 4]).values('chute_type').annotate(
        total=Count('id')
    ).values('total', 'chute_type')

    query_set_zone_b = CrossbeltSortingHistory.objects.filter(
        created__range=(from_time, to_time),
        induction_id__in=INDUCTION_ZONE_B
    ).exclude(scanner_id__in=[3, 4]).values('chute_type').annotate(
        total=Count('id')
    ).values('total', 'chute_type')

    labels = ["READ", "NOREAD"]
    datasets = [
        {
            "borderColor": [color[0], color[1]],
            "data": process_query_to_dataset(query_set_zone_a),
        },
        {
            "borderColor": [color[0], color[1]],
            "data": process_query_to_dataset(query_set_zone_b),
        },
    ]
    response = {
        "labels": labels,
        "datasets": datasets
    }

    return Response(status=status.HTTP_200_OK, content_type='application/json', data=response)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def total_quantity(request):
    now = datetime.now()
    when = request.GET.get("when")
    to_time = now if when == "today" else now - timedelta(days=1) if when == "yesterday" else now - timedelta(
        days=7) if when == "lastweek" else now
    from_time = to_time - timedelta(days=1)

    labels = list()
    for i in reversed(range(0, 25)):
        labels.append((to_time - timedelta(hours=i)).strftime("%d/%m %H:00"))

    sorting_history = CrossbeltSortingHistory.objects.filter(
        created__range=(from_time, to_time),
        chute_type__in=[
            CrossbeltSortingHistory.ChuteType.SUCCESS.value,
            CrossbeltSortingHistory.ChuteType.REJECT.value]
    ).annotate(
        hour=TruncHour('created')
    ).values('hour').annotate(
        total=Count('id')
    ).values('hour', 'total').order_by("-total")

    if request.GET.get("view") == "max":
        total_max, max_at = get_max_statistic_total(sorting_history)
        response = {
            "max": total_max,
            "max_at": max_at
        }
    else:
        datasets = get_dataset_statistic_total(sorting_history, labels)
        total_max, max_at = get_max_statistic_total(sorting_history)
        response = {
            "labels": labels,
            "datasets": datasets,
            "max": total_max,
            "max_at": max_at,
            "total": sum(datasets[0].get("data"))
        }
    return Response(status=status.HTTP_200_OK, content_type='application/json', data=response)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def power(request):
    destination_type = request.GET.get('destination_type', None)
    if request.GET.get('time'):
        to_time = datetime.strptime(request.GET.get('time'), "%Y-%m-%d %H:%M")
    else:
        now = datetime.now()
        when = request.GET.get("when")
        to_time = now if when == "today" else now - timedelta(days=1) if when == "yesterday" else now - timedelta(
            days=7) if when == "lastweek" else now

    to_time_hour = (int((to_time - BASE_TIME).total_seconds())) // 3600
    labels = list()
    for i in reversed(range(0, 25)):
        labels.append((to_time - timedelta(hours=i)).strftime("%d/%m %H:00"))
    kwargs = {
        "from_time": to_time - timedelta(hours=24),
        "to_time": to_time,
        "from_time_hour": to_time_hour - 24,
        "to_time_hour": to_time_hour
    }
    sorting_history = history_from_dst_type(destination_type, request.GET.get("realtime"), **kwargs)

    if request.GET.get("view") == "max":
        max_power, max_at, max_in = get_max_statistic_induction_per_hour(
            sorting_history)
        response = {
            "max": max_power,
            "max_at": max_at,
            "max_in": max_in
        }
    else:
        datasets = get_dataset_statistic_induction_per_hour(
            sorting_history, labels) if sorting_history else list()
        max_power, max_at, max_in = get_max_statistic_induction_per_hour(
            sorting_history)
        response = {
            "labels": labels,
            "datasets": datasets,
            "max": max_power,
            "max_at": max_at,
            "max_in": max_in
        }
    return Response(status=200, data=response, content_type='application/json')


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def imexport(request):
    select_time = request.GET.get('time') or None
    if select_time:
        to_time = datetime.strptime(select_time, "%Y-%m-%d %H:%M")
    else:
        now = datetime.now()
        when = request.GET.get("when")
        to_time = now if when == "today" else now - timedelta(days=1) if when == "yesterday" else now - timedelta(
            days=7) if when == "lastweek" else now

    from_time = to_time - timedelta(hours=24)
    to_time_hour = (int((to_time - BASE_TIME).total_seconds())) // 3600
    from_time_hour = to_time_hour - 24

    labels = list()
    for i in reversed(range(0, 25)):
        labels.append((to_time - timedelta(hours=i)).strftime("%d/%m %H:00"))
    kwargs = {
        "labels": labels,
        "color": color,
        "from_time": from_time,
        "to_time": to_time,
        "from_time_hour": from_time_hour,
        "to_time_hour": to_time_hour
    }
    datasets = get_datasets_imexport(request.GET.get('realtime'), **kwargs)

    response = {
        "labels": labels,
        "datasets": datasets,
    }
    return Response(status=200, data=response, content_type='application/json')
