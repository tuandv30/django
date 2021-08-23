from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.utils.translation import pgettext_lazy
from django.template.response import TemplateResponse
from django.shortcuts import redirect, get_object_or_404, get_list_or_404

from ....constant import NORMAL_CHUTE_ZONE_A
from ....constant import NORMAL_CHUTE_ZONE_B

from .filters import PlanFilter
from ....model.wms_local import Station
from ..views import staff_member_required
from ....core.os_config import get_all_reject_chute
from ....core.wcs_api.utils import action_switch_plan
from ....core.utils import get_paginator_items, get_list_or_none
from .utils import remove_plan, get_miss_station, get_sorting_plan_detail
from ....model.crossbelt import CrossbeltSortingPlan, CrossbeltChute, CrossbeltSortingPlanChuteDetail, \
    CrossbeltSortingPlanChute


@staff_member_required
def plan_list(request):
    plans = CrossbeltSortingPlan.objects.filter()
    plan_filter = PlanFilter(request.GET, queryset=plans)
    plan = get_paginator_items(
        plan_filter.qs.order_by(
            '-is_active', '-id'), settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    ctx = {
        'plan': plan,
        'filter_set': plan_filter,
        'is_empty': not plan_filter.queryset.exists()
    }
    return TemplateResponse(request, 'adminsorting/crossbelt/sorting_plan/list.html', ctx)


@staff_member_required
def plan_create(request):
    station = Station.objects.all()
    reject_chutes = get_all_reject_chute()
    query_set = CrossbeltChute.objects.filter(
        id__lte=NORMAL_CHUTE_ZONE_A[1],
        id__gte=NORMAL_CHUTE_ZONE_A[0]
    )
    chutes_zone_a = get_list_or_404(query_set)

    query_set = CrossbeltChute.objects.filter(
        id__lte=NORMAL_CHUTE_ZONE_B[1],
        id__gte=NORMAL_CHUTE_ZONE_B[0]
    )
    chutes_zone_b = get_list_or_404(query_set)
    ctx = {
        'chutes_zone_a': chutes_zone_a,
        'chutes_zone_b': chutes_zone_b,
        'reject_chute': reject_chutes,
        'station': station
    }
    # create new plan
    if not request.GET.get("copy"):
        template = TemplateResponse(request, 'adminsorting/crossbelt/sorting_plan/create.html', ctx)
    else:
        sorting_plan, miss_station, object_detail = copy_plan(request.GET.get("copy"))
        ctx["sorting_plan"] = sorting_plan
        ctx["object_detail"] = object_detail
        ctx["miss_station"] = miss_station
        template = TemplateResponse(request, 'adminsorting/crossbelt/sorting_plan/create_copy.html', ctx)

    if request.method == 'POST':
        save_plan(request, chutes_zone_a, chutes_zone_a)
        return redirect('adminsorting:crossbelt-plan-list')

    return template


def save_plan(request, chutes_zone_a, chutes_zone_b):
    post_data = request.POST
    sorting_plan = CrossbeltSortingPlan(
        name=post_data.get("plan-name"),
        description=post_data.get("plan-desc"),
        from_at=post_data.get("plan-from"),
        to_at=post_data.get("plan-to"),
        is_active=0
    )
    sorting_plan.save()
    plan_id = sorting_plan.id

    sorting_plan_detail_objects = list()
    sort_plan_create = list()

    # using last id to enable bulk insert
    sort_plan_chute_ids = CrossbeltSortingPlanChute.objects.all().values("id").order_by('-id')
    if sort_plan_chute_ids:
        last_plan_chute_id = sort_plan_chute_ids[0]["id"]
    else:
        last_plan_chute_id = 0

    for i in range(1, (len(chutes_zone_a) + len(chutes_zone_b) + 3)):
        # insert sorting_plan_chute table
        bt_station = post_data.get("%s-bt-station" % i)
        if bt_station and bt_station != 'None':
            sort_plan_create.append(CrossbeltSortingPlanChute(
                id=last_plan_chute_id + 1,
                chute_id=i,
                plan_id=plan_id,
                transport_type=post_data.get("chute-%s-trf-type" % i),
                bag_type=1,
                main_station_id=int(bt_station)
            ))
        else:
            sort_plan_create.append(CrossbeltSortingPlanChute(
                id=last_plan_chute_id + 1,
                chute_id=i,
                plan_id=plan_id,
                transport_type=post_data.get("chute-%s-trf-type" % i),
                bag_type=0,
                main_station_id=None
            ))
        last_plan_chute_id += 1

        # update sorting_plan_chute_detail table
        list_dest = post_data.getlist("chute-%s-list-dest" % i)
        if list_dest:
            for dest in list_dest:
                new_sorting_plan_detail = CrossbeltSortingPlanChuteDetail(
                    sorting_plan_chute_id=last_plan_chute_id + 1,
                    destination_code=dest.split("|")[0],
                    destination_type=dest.split("|")[1],
                )
                sorting_plan_detail_objects.append(new_sorting_plan_detail)

    CrossbeltSortingPlanChute.objects.bulk_create(sort_plan_create)
    CrossbeltSortingPlanChuteDetail.objects.bulk_create(sorting_plan_detail_objects)


def copy_plan(copy_from_plan):
    # copy from older plan
    sorting_plan_qs = CrossbeltSortingPlan.objects.filter(pk=copy_from_plan)
    sorting_plan = get_object_or_404(sorting_plan_qs)

    object_detail, list_plan_station_id = get_sorting_plan_detail(plan_id=copy_from_plan)
    # Lấy ra danh sách Province đã được config
    list_province_config = CrossbeltSortingPlanChuteDetail.objects.filter(
        sorting_plan_chute__plan_id=copy_from_plan,
        destination_type=0
    ).values_list('destination_code', flat=True).distinct()
    list_province_config = get_list_or_none(list_province_config)

    # Danh sách kho thiếu
    miss_station = get_miss_station(list_plan_station_id, list_province_config)

    # station bao tổng detail
    bt_station_detail = CrossbeltSortingPlanChute.objects.filter(bag_type=1, plan_id=copy_from_plan)
    if bt_station_detail:
        for i in bt_station_detail:
            if i.chute_id in object_detail.keys():
                object_detail[i.chute_id]['bt_station'] = i
            else:
                object_detail[i.chute_id] = dict()
                object_detail[i.chute_id]['bt_station'] = i

    return sorting_plan, miss_station, object_detail


@staff_member_required
def plan_details(request, plan_id):
    reject_chutes = get_all_reject_chute()
    query_set = CrossbeltChute.objects.filter(
        id__lte=NORMAL_CHUTE_ZONE_A[1],
        id__gte=NORMAL_CHUTE_ZONE_A[0]
    )
    chutes_zone_a = get_list_or_404(query_set)

    query_set = CrossbeltChute.objects.filter(
        id__lte=NORMAL_CHUTE_ZONE_B[1],
        id__gte=NORMAL_CHUTE_ZONE_B[0]
    )
    chutes_zone_b = get_list_or_404(query_set)

    sorting_plan_qs = CrossbeltSortingPlan.objects.filter(pk=plan_id)
    sorting_plan = get_object_or_404(sorting_plan_qs)

    object_detail, list_plan_station_id = get_sorting_plan_detail(plan_id=plan_id)
    # Lấy ra danh sách Province đã được config
    list_province_config = CrossbeltSortingPlanChuteDetail.objects.filter(
        sorting_plan_chute__plan_id=plan_id,
        destination_type=0
    ).values_list('destination_code', flat=True).distinct()
    list_province_config = get_list_or_none(list_province_config)
    # Danh sách kho thiếu
    miss_station = get_miss_station(list_plan_station_id, list_province_config)
    # station bao tổng detail
    bt_station_detail = CrossbeltSortingPlanChute.objects.filter(bag_type=1, plan_id=plan_id)
    if bt_station_detail:
        for i in bt_station_detail:
            if i.chute_id in object_detail.keys():
                object_detail[i.chute_id]['bt_station'] = i
            else:
                object_detail[i.chute_id] = dict()
                object_detail[i.chute_id]['bt_station'] = i

    # when updating the sorting plan
    if request.method == 'POST':
        update_plan(request, plan_id, chutes_zone_a, chutes_zone_b, sorting_plan)
        return redirect('adminsorting:crossbelt-plan-details', plan_id=plan_id)
    ctx = {
        'chutes_zone_a': chutes_zone_a,
        'chutes_zone_b': chutes_zone_b,
        'reject_chute': reject_chutes,
        'sorting_plan': sorting_plan,
        'object_detail': object_detail,
        'miss_station': miss_station,
        'station': Station.objects.all(),
    }
    return TemplateResponse(request, 'adminsorting/crossbelt/sorting_plan/detail.html', ctx)


def update_plan(request, plan_id, chutes_zone_a, chutes_zone_b, sorting_plan):
    # delete old sorting plan detail
    sorting_plan_detail_qs = CrossbeltSortingPlanChuteDetail.objects.filter(sorting_plan_chute__plan_id=plan_id)
    sorting_plan_detail_qs.delete()

    post_data = request.POST
    # update old plan
    sorting_plan.name = post_data.get("plan-name")
    sorting_plan.description = post_data.get("plan-desc")
    sorting_plan.from_at = post_data.get("plan-from")
    sorting_plan.to_at = post_data.get("plan-to")
    sorting_plan.save()

    # using last id to enable bulk insert
    sort_plan_chute_ids = CrossbeltSortingPlanChute.objects.all().values("id").order_by('-id')
    if sort_plan_chute_ids:
        last_plan_chute_id = sort_plan_chute_ids[0]["id"]
    else:
        last_plan_chute_id = 0

    sort_plan_create, sorting_plan_detail_objects = update_st_plan_chute(post_data, chutes_zone_a, chutes_zone_b,
                                                                         plan_id, last_plan_chute_id)

    CrossbeltSortingPlanChute.objects.bulk_create(sort_plan_create)
    CrossbeltSortingPlanChuteDetail.objects.bulk_create(sorting_plan_detail_objects)

    return redirect('adminsorting:crossbelt-plan-details', plan_id=plan_id)


def update_st_plan_chute(post_data, chutes_zone_a, chutes_zone_b, plan_id, last_plan_chute_id):
    # create new sorting plan detail
    sorting_plan_detail_objects = list()
    sort_plan_create = list()

    for i in range(1, (len(chutes_zone_a) + len(chutes_zone_b) + 3)):
        # update sorting_plan_chute table
        bt_station = post_data.get("%s-bt-station" % i)
        transport_type = post_data.get("chute-%s-trf-type" % i)
        sort_plan_chute = CrossbeltSortingPlanChute.objects.filter(chute_id=i, plan_id=plan_id)
        if sort_plan_chute:
            sort_plan_chute_id = sort_plan_chute.first().id
            # bao tong
            if bt_station and bt_station != 'deselect':
                sort_plan_chute_bt = sort_plan_chute.filter(main_station_id=int(bt_station),
                                                            transport_type=transport_type)
                if not sort_plan_chute_bt:
                    sort_plan_chute.update(
                        transport_type=transport_type,
                        bag_type=1,
                        main_station_id=int(bt_station)
                    )
            else:
                sort_plan_chute_normal_bag = sort_plan_chute.filter(
                    ~Q(transport_type=transport_type) | Q(main_station_id__isnull=False))
                if sort_plan_chute_normal_bag:
                    sort_plan_chute.update(
                        transport_type=transport_type,
                        bag_type=0,
                        main_station_id=None
                    )
        else:
            if bt_station and bt_station != 'deselect':
                sort_plan_create.append(CrossbeltSortingPlanChute(
                    chute_id=i,
                    plan_id=plan_id,
                    transport_type=transport_type,
                    bag_type=1,
                    main_station_id=int(bt_station)
                ))
            else:
                sort_plan_create.append(CrossbeltSortingPlanChute(
                    chute_id=i,
                    plan_id=plan_id,
                    transport_type=transport_type,
                    bag_type=0,
                    main_station_id=None
                ))

            sort_plan_chute_id = last_plan_chute_id + 1
            last_plan_chute_id += 1

        # update sorting_plan_chute_detail table
        if post_data.getlist("chute-%s-list-dest" % i):
            for dest in post_data.getlist("chute-%s-list-dest" % i):
                sorting_plan_detail_objects.append(CrossbeltSortingPlanChuteDetail(
                    sorting_plan_chute_id=sort_plan_chute_id,
                    destination_code=dest.split("|")[0],
                    destination_type=dest.split("|")[1],
                ))

    return sort_plan_create, sorting_plan_detail_objects


@staff_member_required
def plan_delete(request, plan_id):
    queryset = CrossbeltSortingPlan.objects.filter()
    sorting_plan = get_object_or_404(queryset, pk=plan_id)
    if request.method == 'POST':
        remove_plan(sorting_plan)
        msg = pgettext_lazy('Dashboard message', 'Xoá kịch bản %s') % (sorting_plan.name,)
        messages.success(request, msg)
        return redirect('adminsorting:crossbelt-plan-list')
    ctx = {'sorting_plan': sorting_plan}
    return TemplateResponse(request, 'adminsorting/crossbelt/sorting_plan/modal/confirm_delete.html', ctx)


@staff_member_required
def plan_switch(request):
    if request.method == 'POST':
        # call api wcs 205 to switch plan
        switch_plan = action_switch_plan()
        if switch_plan:
            return redirect('adminsorting:crossbelt-plan-list')
        msg = "Xảy ra lỗi trong quá trình kết nối đến DAMON WCS"
        messages.error(request, msg)
        return redirect('adminsorting:plan-list')

    return TemplateResponse(request, 'adminsorting/crossbelt/sorting_plan/modal/confirm_switch.html')


@staff_member_required
def plan_active(request):
    if request.method == 'POST':
        post_data = request.POST
        plan_id = post_data.get("plan_id")
        if not plan_id:
            msg = "Vui lòng chọn kịch bản để kích hoạt"
            messages.error(request, msg)
            return redirect('adminsorting:crossbelt-plan-list')

        CrossbeltSortingPlan.objects.filter().exclude(pk=plan_id).update(is_active=0)
        CrossbeltSortingPlan.objects.filter(pk=plan_id).update(is_active=1)
        msg = "Đã kích hoạt thành công!"
        messages.info(request, msg)

    return redirect('adminsorting:crossbelt-plan-list')
