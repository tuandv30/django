from django.template import Library

register = Library()

LABEL_DANGER = 'danger'
LABEL_SUCCESS = 'success'
LABEL_PRIMARY = 'primary'
LABEL_INFORMATION = 'information'
LABEL_DISABLE = ''
LABEL_WARNING = 'warning'


@register.inclusion_tag('inspiniacssform/components/status_label.html')
def render_bool_status(status, status_display=None):
    if status:
        label_cls = LABEL_SUCCESS
    else:
        label_cls = LABEL_DISABLE
    return {'label_cls': label_cls, 'status': status_display or status}
