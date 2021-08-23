from django.template.response import TemplateResponse
from ..views import staff_member_required


@staff_member_required
def index(request):
    return TemplateResponse(request, 'adminsorting/crossbelt/index.html')
