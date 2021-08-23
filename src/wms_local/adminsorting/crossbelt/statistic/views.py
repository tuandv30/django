from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from ..views import staff_member_required


@staff_member_required
def induction_per_hour(request):
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:00")
    select_time = request.GET.get("select_time") or now_str
    ctx = {
        'select_time': select_time
    }
    return TemplateResponse(request, 'adminsorting/crossbelt/statistic/statistic_hour_induction.html', ctx)


@staff_member_required
def induction(request):
    now = datetime.now()
    start_datetime = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=0,
        minute=0)
    from_time_str = start_datetime.strftime("%Y-%m-%d %H:00")
    to_time_str = now.strftime("%Y-%m-%d %H:00")
    if request.method == "POST":
        from_time = request.POST.get('from_time')
        to_time = request.POST.get('to_time')

        if to_time > from_time:
            ctx = {
                "from_time": from_time,
                "to_time": to_time,
            }
            return TemplateResponse(request, 'webview/statistic/statistic_induction.html', ctx)
        msg = "Thời gian bắt đầu phải bé hơn thời gian kết thúc. Vui lòng lựa chọn lại!!!"
        messages.error(request, msg)
        return redirect('adminsorting:crossbelt-statistic-induction')

    ctx = {
        "from_time": from_time_str,
        "to_time": to_time_str,
    }
    return TemplateResponse(request, 'adminsorting/crossbelt/statistic/statistic_induction.html', ctx)


@staff_member_required
def import_export(request):
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:00")
    select_time = request.GET.get("select_time") or now_str

    ctx = {
        'select_time': select_time
    }
    return TemplateResponse(
        request, 'adminsorting/crossbelt/statistic/statistic_imexport.html', ctx)


@staff_member_required
def statistic_chute(request):
    now = datetime.now()
    start_datetime = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=0,
        minute=0)
    from_time_str = start_datetime.strftime("%Y-%m-%d %H:00")
    to_time_str = now.strftime("%Y-%m-%d %H:00")
    if request.method == "POST":
        from_time = request.POST.get('from_time')
        to_time = request.POST.get('to_time')

        if to_time > from_time:
            ctx = {
                "from_time": datetime.strptime(from_time, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:00"),
                "to_time": datetime.strptime(to_time, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:00"),
            }
            return TemplateResponse(request, 'adminsorting/crossbelt/statistic/statistic_chute.html', ctx)
        msg = "Thời gian bắt đầu phải bé hơn thời gian kết thúc. Vui lòng lựa chọn lại!!!"
        messages.error(request, msg)
        return redirect('adminsorting:crossbelt-statistic-chute')

    ctx = {
        "from_time": from_time_str,
        "to_time": to_time_str,
    }
    return TemplateResponse(request, 'adminsorting/crossbelt/statistic/statistic_chute.html', ctx)
