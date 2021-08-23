import json
import requests
from constance import config
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import get_all_printer, collect_printer


@api_view(['GET'])
def get_printer(request):
    printer_objects = get_all_printer()
    response = {
        "message": True,
        "data": list(printer_objects.values())
    }
    return Response(
        status=status.HTTP_200_OK, content_type='application/json', data=response)


@api_view(['POST'])
def forward_printer(request):
    post_data = request.data
    printer_ip = post_data.get("printer_ip")
    printer_id = post_data.get("printer_id")
    chute_id = post_data.get("chute_id")
    if not printer_id and not chute_id and not printer_ip:
        response = {
            "success": False,
            "message": "Wrong printer_id or chute_id or printer_ip parameter"
        }
        return Response(
            status=status.HTTP_400_BAD_REQUEST, content_type='application/json', data=response)

    if printer_ip:
        printer_name = printer_ip
    else:
        printer_name = collect_printer(printer_id, chute_id)

    if not printer_name:
        response = {
            "success": False,
            "message": "Can not found printer!"
        }
        return Response(
            status=status.HTTP_404_NOT_FOUND, content_type='application/json', data=response)

    payload = {
        "namePrinter": printer_name,
        "barcode": post_data.get("barcode"),
        "dstStation": post_data.get("dstStation"),
        "transport": post_data.get("transport"),
        "codeStation": post_data.get("codeStation"),
        "numPackage": post_data.get("numPackage"),
        "type": post_data.get("type")
    }
    headers = {
        'Content-Type': 'application/json'
    }
    req = requests.post(
        config.PRINTER_FORWARD_API_URL,
        headers=headers,
        data=json.dumps(payload))
    req_status_code = req.status_code
    req_response = req.json()
    return Response(status=req_status_code, content_type='application/json', data=req_response)
