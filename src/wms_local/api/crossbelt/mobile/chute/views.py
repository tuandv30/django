"""
    This lines of code is only for one reason: memory
    to thanhhm, hantt, thaitv - the persons who made
    crossbelt app great again!
    Good luck in your own roads and see you again!
"""
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import get_chutes_from_plan_id_v2, get_packages_in_chute_v2
from .....core.utils import get_object_or_none, get_list_or_none
from .....model.crossbelt import CrossbeltChuteDetail, CrossbeltSortingPlan


@api_view(['GET'])
def get_chute_v2(request):
    # get only 1 specific sorting plan is actived
    query_set = CrossbeltSortingPlan.objects.filter(is_active=1)
    try:
        sorting_plan = get_object_or_none(query_set)
        plan_id = sorting_plan.id
    except MultipleObjectsReturned:
        plan_id = None

    chutes_object = get_chutes_from_plan_id_v2(plan_id=plan_id)

    response = {
        "success": True,
        "data": sorted(list(chutes_object.values()), key=lambda x: x['chute_id'])
    }

    return Response(status=status.HTTP_200_OK, content_type='application/json', data=response)


@api_view(['GET'])
def get_package_v2(request):
    lst_chute_id = request.GET.getlist('chute_id', None)
    if not lst_chute_id:
        response = {
            "success": False,
            "message": "Wrong parameter"
        }
    else:
        pkg_orders_object = get_packages_in_chute_v2(lst_chute_id=lst_chute_id)
        response = {
            "success": True,
            "data": pkg_orders_object,
        }

    return Response(status=status.HTTP_200_OK, content_type='application/json', data=response)


@api_view(['POST'])
def clean_package(request):
    post_data = request.data
    list_packages = post_data.get("packages")
    if list_packages:
        query_set = CrossbeltChuteDetail.objects.filter(pkg_order__in=list_packages)
        chute_details = get_list_or_none(query_set)
        if chute_details:
            for chute_detail in chute_details:
                chute_detail.delete()
        response = {
            "success": True,
            "message": "Packages have been cleaned"
        }
    else:
        response = {
            "success": False,
            "message": "Wrong parameter"
        }

    return Response(status=status.HTTP_200_OK, content_type='application/json', data=response)


@api_view(['POST'])
def clean_package_chute(request):
    post_data = request.data
    chute_id = post_data.get("chute_id")
    try:
        CrossbeltChuteDetail.objects.filter(chute_id__in=chute_id).delete()
        response = {
            "success": True,
            "message": "Chutes have been cleaned"
        }
    except BaseException as exe:
        print(exe)
        response = {
            "success": False,
            "message": "Something wrong"
        }

    return Response(status=status.HTTP_200_OK, content_type='application/json', data=response)
