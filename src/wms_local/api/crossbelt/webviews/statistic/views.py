import copy
from datetime import datetime, timedelta

from django.db.models import Count, Sum
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from .....core.utils import get_list_or_none
from .....model.crossbelt import CrossbeltStatisticChute, CrossbeltSortingHistory, \
    CrossbeltInduction, CrossbeltStatisticSorting
from .....constant import BASE_TIME
from .....constant import COLOR


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def statistic_induction(request):
    from_time = datetime.strptime(request.GET.get('from'), "%Y-%m-%d %H:%M")
    to_time = datetime.strptime(request.GET.get('to'), "%Y-%m-%d %H:%M")
    from_time_hour = (int((from_time - BASE_TIME).total_seconds())) // 3600
    to_time_hour = (int((to_time - BASE_TIME).total_seconds())) // 3600

    color = copy.copy(COLOR)
    inductions = CrossbeltInduction.objects.filter().all()
    labels = list()
    for induction in inductions:
        labels.append(induction.code)

    data_success = [0] * len(labels)
    data_reject = [0] * len(labels)
    data_pda = [0] * len(labels)
    kwargs = {
        "from_time": from_time,
        "to_time": to_time,
        "from_time_hour": from_time_hour,
        "to_time_hour": to_time_hour
    }
    get_dataset_statistic_induction(request, data_success, data_reject, data_pda, **kwargs)
    datasets = [
        {
            "label": "SUCCESS",
            "backgroundColor": color[0],
            "data": data_success
        },
        {
            "label": "PDA",
            "backgroundColor": color[1],
            "data": data_pda
        },
        {
            "label": "REJECT",
            "backgroundColor": color[9],
            "data": data_reject
        }
    ]
    response = {
        "labels": labels,
        "datasets": datasets
    }
    return Response(status=200, data=response, content_type='application/json')


def get_dataset_statistic_induction(request, data_success, data_reject, data_pda, **kwargs):
    if request.GET.get("realtime") == "1":
        sorting_history = CrossbeltSortingHistory.objects.filter(
            created__range=(kwargs.get('from_time'), kwargs.get('to_time'))
        ).values('induction_id', 'chute_type').annotate(
            total=Count('id')
        ).values('total', 'induction_id', 'chute_type').order_by('induction_id')
        if sorting_history:
            for i in sorting_history:
                induction_id = i.get('induction_id')
                chute_type = i.get('chute_type')
                if chute_type == CrossbeltSortingHistory.ChuteType.SUCCESS.value:
                    data_success[induction_id - 1] = i.get('total')
                elif chute_type == CrossbeltSortingHistory.ChuteType.REJECT.value:
                    data_reject[induction_id - 1] = i.get('total')
                elif chute_type == CrossbeltSortingHistory.ChuteType.PDA.value:
                    data_pda[induction_id - 1] = i.get('total')
    else:
        sorting_history = CrossbeltStatisticSorting.objects.filter(
            hour__range=(kwargs.get('from_time_hour'), kwargs.get('to_time_hour'))
        ).values('induction_id').annotate(
            total_success=Sum('total_success')
        ).annotate(
            total_reject=Sum('total_reject')
        ).annotate(
            total_pda=Sum('total_pda')
        ).values('induction_id', 'total_success', 'total_reject', 'total_pda')
        if sorting_history:
            for i in sorting_history:
                induction_id = i.get('induction_id')
                total_success = i.get('total_success')
                total_reject = i.get('total_reject')
                total_pda = i.get('total_pda')
                data_success[induction_id - 1] = total_success
                data_reject[induction_id - 1] = total_reject
                data_pda[induction_id - 1] = total_pda


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def statistic_chute(request):
    response = dict()
    from_time = request.GET.get('from')
    to_time = request.GET.get('to')
    to_time = datetime.strptime(
        to_time, "%Y-%m-%d %H:%M") if to_time else datetime.now()
    from_time = datetime.strptime(
        from_time, "%Y-%m-%d %H:%M") if from_time else to_time - timedelta(hours=24)
    if from_time + timedelta(hours=1) > to_time:
        query_set = CrossbeltStatisticChute.objects.filter(
            state=0,
            created__range=(from_time, to_time)
        ).values('chute_code').annotate(
            total=Count('state')
        ).values('chute_code', 'total').order_by('-total')[:10]
    else:
        from_hour = (int((from_time - BASE_TIME).total_seconds())) // 3600
        to_hour = (int((to_time - BASE_TIME).total_seconds())) // 3600
        query_set = CrossbeltStatisticChute.objects.filter(
            state=CrossbeltStatisticChute.ChuteState.DEACTIVATE.value,
            hour__lte=to_hour,
            hour__gte=from_hour
        ).values('chute_code').annotate(total=Sum('spent_time')).order_by("-total")[:10]
    chute_full = get_list_or_none(query_set)
    if chute_full:
        response = chute_full
    return Response(status=200, data=response,
                    content_type='application/json')
