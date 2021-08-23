from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from ..views import staff_member_required
from ....model.crossbelt import CrossbeltChute, CrossbeltOperationConfig
from ....model.wms_local import Province


@staff_member_required
@permission_required('account.manage_operation_config', raise_exception=True)
def config_list(request):
    chute_config = list()
    chute_config_qs = CrossbeltOperationConfig.objects.filter(
        type__in=["chute", "province"]).all()
    for i in chute_config_qs:
        value = i.value.split(",")
        chute_config.append({
            "key": i.key,
            "value": [int(i) for i in value],
            "type": i.type,
            "description": i.description
        })
    max_weight_config = CrossbeltOperationConfig.objects.filter(
        key="max_weight").first()
    if request.method == 'POST':
        list_config = CrossbeltOperationConfig.objects.filter().all()
        if not list_config:
            return redirect('adminsorting:crossbelt-operation-config-list')
        post_data = request.POST
        for config in list_config:
            if config.key == "max_weight":
                value = post_data.get(config.key)
                try:
                    value = float(value)
                    CrossbeltOperationConfig.objects.filter(
                        key=config.key).update(
                        value=value)
                except BaseException:
                    continue
                continue
            value = post_data.getlist(config.key)
            if value:
                value = ','.join(value)
                CrossbeltOperationConfig.objects.filter(
                    key=config.key).update(
                    value=value)
        return redirect('adminsorting:crossbelt-operation-config-list')

    provinces = Province.objects.all()
    province_list = list()
    for province in provinces:
        province_list.append({
            "province_id": province.province_id,
            "province_name": "{} - {}".format(province.province_name, province.province_code)
        })
    ctx = {
        'chute_config': chute_config,
        'max_weight_config': max_weight_config,
        'chute': CrossbeltChute.objects.all(),
        'province': province_list
    }
    return TemplateResponse(request, 'adminsorting/crossbelt/operation_config/list.html', ctx)
