from datetime import datetime, timedelta
from django.db.models import Count
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from .utils import get_chute_info, group_destination_code
from ....core.utils import get_list_or_none
from ....model.crossbelt import CrossbeltChuteHistory


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_chute_full(request):
    response = {
        "msg": "success",
        "data": []
    }
    now = datetime.now()
    queryset = CrossbeltChuteHistory.objects.filter(
        state=0,
        created__range=(now - timedelta(minutes=30), now)
    ).values('chute_code').annotate(
        total=Count('state')
    ).values('chute_code', 'total').order_by('-total')[:10]
    chute_his = get_list_or_none(queryset)
    if chute_his:
        response["data"] = chute_his
    return Response(status=200, data=response, content_type='application/json')


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_chute_details(request):
    response = {
        "msg": "success",
        "data": []
    }
    chute_details = get_chute_info()
    if chute_details:
        for i in chute_details:
            str_many_des_code = i.get('total_code')
            i['total_code'] = group_destination_code(str_many_des_code)
        response['data'] = chute_details
    return Response(status=200, data=response, content_type='application/json')
