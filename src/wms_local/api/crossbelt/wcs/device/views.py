from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import update_carrier, update_chute, update_induction, insert_device_state_history


@api_view(['POST'])
def upload_state(request):
    post_data = request.data
    for data in post_data:
        device_code = data.get("DeviceCode")
        device_type = data.get("DeviceType")
        state = data.get("State")
        create_time = data.get("CreateTime")

        insert_device_state_history(device_code, device_type, state, create_time)
        if device_type == "1":
            update_carrier(device_code, state)
        if device_type == "2":
            update_chute(device_code, state)
        if device_type == "4":
            update_induction(device_code, state)

    response = {
        "Result": "1",
        "errorCod ": "",
        "errorMsg": ""
    }

    return Response(status=200, content_type='application/json', data=response)
