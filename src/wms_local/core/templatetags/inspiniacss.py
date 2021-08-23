from django import forms, template
from django.template.loader import get_template
from django_filters.widgets import RangeWidget, DateRangeWidget

from ..widgets import EditorWidget

register = template.Library()


@register.filter
def inspiniacss(element, args=None):
    if not args:
        label_cols = 'col-sm-3'
        input_cols = 'col-sm-9'
        context = ''
    else:
        args_list = [arg.strip() for arg in args.split(',')]
        label_cols = args_list[0]
        input_cols = args_list[1]
        context = args_list[2]

    markup_classes = {
        'label': label_cols,
        'input': input_cols,
        'value': '',
        'single_value': '',
        'context': context}
    return render(element, markup_classes)


@register.filter()
def to_int(value):
    return int(value)


@register.filter()
def to_str(value):
    return str(value)


@register.filter
def filter_inspiniacss(element, args=None):
    markup_classes = {'value': '', 'single_value': ''}
    return filter_render(element, markup_classes)


def add_input_classes(field):
    if not any([is_checkbox(field), is_checkbox_select_multiple(field),
                is_radio(field), is_file(field)]):
        field_classes = field.field.widget.attrs.get('class', '')
        if field.errors:
            field_classes = ' '.join([field_classes, 'invalid'])
        field.field.widget.attrs['class'] = field_classes


def filter_render(element, markup_classes):
    element_type = element.__class__.__name__.lower()

    if element_type == 'boundfield':
        add_input_classes(element)
        template = get_template("inspiniacssform/filters/field.html")
        context = {'field': element, 'classes': markup_classes}
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)

            template = get_template("inspiniacssform/filters/formset.html")
            context = {'formset': element, 'classes': markup_classes}
        else:
            for field in element.visible_fields():
                add_input_classes(field)

            template = get_template("inspiniacssform/filters/form.html")
            context = {'form': element, 'classes': markup_classes}

    return template.render(context)


def render(element, markup_classes):
    element_type = element.__class__.__name__.lower()

    if element_type == 'boundfield':
        add_input_classes(element)
        template = get_template("inspiniacssform/field.html")
        context = {'field': element, 'classes': markup_classes}
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)

            template = get_template("inspiniacssform/formset.html")
            context = {'formset': element, 'classes': markup_classes}
        else:
            for field in element.visible_fields():
                add_input_classes(field)

            template = get_template("inspiniacssform/form.html")
            context = {'form': element, 'classes': markup_classes}

    return template.render(context)


@register.filter
def is_text(field):
    return isinstance(field.field.widget, forms.TextInput)


@register.filter
def is_number(field):
    return isinstance(field.field.widget, forms.NumberInput)


@register.filter
def is_password(field):
    return isinstance(field.field.widget, forms.PasswordInput)


@register.filter
def is_email(field):
    return isinstance(field.field.widget, forms.EmailInput)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_textarea(field):
    return isinstance(field.field.widget, forms.Textarea)


@register.filter
def is_editor(field):
    return isinstance(field.field.widget, EditorWidget)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_date_input(field):
    return isinstance(field.field.widget, forms.DateInput)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)


@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def is_select_multiple(field):
    return isinstance(field.field.widget, forms.SelectMultiple)


@register.filter
def is_checkbox_select_multiple(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_range(field):
    return isinstance(field.field.widget, RangeWidget)


@register.filter
def is_date_range(field):
    return isinstance(field.field.widget, DateRangeWidget)


@register.filter
def is_url(field):
    return isinstance(field.field.widget, forms.URLInput)


@register.filter
def is_datetime_input(field):
    return isinstance(field.field.widget, forms.DateTimeInput)


@register.filter
def is_time_input(field):
    return isinstance(field.field.widget, forms.TimeInput)


@register.filter(name='range')
def filter_range(start, end):
    return range(start, end)


@register.filter(name='index')
def index(list_, i):
    try:
        return list_[int(i)]
    except BaseException:
        return None


@register.filter(name='to_str_time')
def convert_str_date(value):
    if value:
        return value.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
