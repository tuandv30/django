from urllib.parse import urlencode

from django import forms
from django.template import Library
from django_filters.fields import RangeField, DateRangeField

from .chips import handle_nullboolean, handle_multiple_model_choice, \
    handle_multiple_choice, \
    handle_single_model_choice, handle_single_choice, handle_range, \
    handle_default, handle_range_date

register = Library()


@register.simple_tag(takes_context=True)
def construct_get_query(context, **params):
    request_get = context['request'].GET.dict()
    if not (request_get or params):
        return ''
    all_params = {}
    all_params.update(request_get)
    all_params.update(params)
    all_params.update(context.get('default_pagination_params', {}))
    return '?' + urlencode(all_params)


@register.inclusion_tag(
    'adminsorting/includes/_pagination.html', takes_context=True)
def paginate(context, page_obj, num_of_pages=3):
    context['page_obj'] = page_obj
    context['n_forward'] = num_of_pages + 1
    context['n_backward'] = -num_of_pages - 1
    context['next_section'] = (2 * num_of_pages) + 1
    context['previous_section'] = (-2 * num_of_pages) - 1
    return context


@register.inclusion_tag(
    'adminsorting/includes/_sorting_header.html', takes_context=True)
def sorting_header(context, field, label, is_wide=False):
    """Render a table sorting header."""
    request = context['request']
    request_get = request.GET.copy()
    sort_by = request_get.get('sort_by')

    # path to icon indicating applied sorting
    sorting_icon = 'fa fa-sort'

    # flag which determines if active sorting is on field
    is_active = False

    if sort_by:
        if field == sort_by:
            is_active = True
            # enable ascending sort
            # new_sort_by is used to construct a link with already toggled
            # sort_by value
            new_sort_by = '-%s' % field
            sorting_icon = "fa fa-sort-up"
        else:
            # enable descending sort
            new_sort_by = field
            if field == sort_by.strip('-'):
                is_active = True
                sorting_icon = "fa fa-sort-down"
    else:
        new_sort_by = field

    request_get['sort_by'] = new_sort_by

    return {
        'url': '%s?%s' % (request.path, request_get.urlencode()),
        'is_active': is_active, 'sorting_icon': sorting_icon, 'label': label,
        'is_wide': is_wide}


@register.inclusion_tag('adminsorting/includes/_filters.html', takes_context=True)
def filters(context, filter_set, sort_by_filter_name='sort_by'):
    """Render the filtering template based on the filter set."""
    chips = []
    request_get = context['request'].GET.copy()
    for filter_name in filter_set.form.cleaned_data.keys():
        if filter_name == sort_by_filter_name:
            # Skip processing of sort_by filter, as it's rendered differently
            continue
        field = filter_set.form[filter_name]
        if field.value() not in ['', None]:
            if isinstance(field.field, forms.NullBooleanField):
                items = handle_nullboolean(field, request_get)
            elif isinstance(field.field, forms.ModelMultipleChoiceField):
                items = handle_multiple_model_choice(field, request_get)
            elif isinstance(field.field, forms.MultipleChoiceField):
                items = handle_multiple_choice(field, request_get)
            elif isinstance(field.field, forms.ModelChoiceField):
                items = handle_single_model_choice(field, request_get)
            elif isinstance(field.field, forms.ChoiceField):
                items = handle_single_choice(field, request_get)
            elif isinstance(field.field, DateRangeField):
                items = handle_range_date(field, request_get)
            elif isinstance(field.field, RangeField):
                items = handle_range(field, request_get)
            else:
                items = handle_default(field, request_get)
            chips.extend(items)
    return {
        'chips': chips, 'filter': filter_set,
        'sort_by': request_get.get(sort_by_filter_name, None)}


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
