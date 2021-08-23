from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .....model.crossbelt import CrossbeltChute


@api_view(['POST'])
def upload_chute(request):
    post_data = request.data
    response = list()
    for data in post_data:
        chute_no = data.get("ChuteNo")
        is_lock = data.get("isLock")
        try:
            chute = CrossbeltChute.objects.get(pk=int(chute_no))
            if int(is_lock) == 1:
                chute.status = CrossbeltChute.Status.LOCK
            elif int(is_lock) == 0:
                chute.status = CrossbeltChute.Status.RELEASE
            else:
                pass
            chute.save()
        except ObjectDoesNotExist:
            pass

        response.append({
            "ChuteNo": "{}".format(chute_no),
            "Result": "1",
            "errorCod ": "",
            "errorMsg": ""
        })

    return Response(status=200, content_type='application/json', data=response)
