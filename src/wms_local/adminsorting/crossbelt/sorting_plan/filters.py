from django.db.models import Q
from django_filters import CharFilter
from ....core.filters import SortedFilterSet
from ....model.crossbelt import CrossbeltSortingPlan


class PlanFilter(SortedFilterSet):
    name = CharFilter(
        label='Tên',
        method='filter_by_plan_name'
    )

    class Meta:
        model = CrossbeltSortingPlan
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return 'Tìm thấy {} kịch bản'.format(counter)

    def filter_by_plan_name(self, value):
        return self.qs.filter(
            Q(name__icontains=value))
