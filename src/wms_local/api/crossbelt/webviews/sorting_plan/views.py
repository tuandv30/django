from django.db.models import Q
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from .....core.utils import get_list_or_none
from .....model.wms_local import Station, Module, Cart, Province


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_dst(request):
    result = list()
    search = request.GET.get('search', None)
    if not search:
        return Response(status=200, data=result,
                        content_type='application/json')

    len_search = len(search)
    queryset = Province.objects.filter(
        Q(province_name__icontains=search) | Q(province_code__icontains=search))
    provinces = get_list_or_none(queryset)
    if provinces:
        for i in provinces:
            result.append({
                'id': "{}|0".format(i.province_id),
                'text': "{} - {} (Tỉnh)".format(i.province_name, i.province_code)
            })
    queryset = Station.objects.filter(
        Q(name__icontains=search) | Q(code__icontains=search))
    stations = get_list_or_none(queryset)
    if stations:
        for i in stations:
            result.append({
                'id': "{}|1".format(i.id),
                'text': "{} - {} (Kho)".format(i.name, i.code)
            })

    queryset = Module.objects.filter(
        alias__icontains=search,
    )
    modules = get_list_or_none(queryset)
    if modules:
        for i in modules:
            result.append({
                'id': "{}|2".format(i.id),
                'text': "{} (Module)".format(i.alias)
            })

    if len_search >= 3:
        queryset = Cart.objects.filter(
            alias__icontains=search,
            is_visible=1
        )
        carts = get_list_or_none(queryset)
        if carts:
            for i in carts:
                result.append({
                    'id': "{}|3".format(i.id),
                    'text': "{} (Giỏ)".format(i.alias)
                })

    return Response(status=200, data=result, content_type='application/json')


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_dst_station(request):
    result = [{
        'id': 'deselect',
        'text': 'Bỏ chọn'
    }]
    search = request.GET.get('search', None)
    if not search:
        return Response(status=200, data=result,
                        content_type='application/json')
    queryset = Station.objects.filter(
        Q(name__icontains=search) | Q(code__icontains=search))
    stations = get_list_or_none(queryset)
    if stations:
        result = list()
        for i in stations:
            result.append({
                'id': i.id,
                'text': "{} - {}".format(i.code, i.name)
            })
    return Response(status=200, data=result, content_type='application/json')
