from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([])
def ping(_request):
    response = "pong"
    return HttpResponse(status=200, content=response, content_type="text/plain")
