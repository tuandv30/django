from django import forms

from ....model.crossbelt import CrossbeltSortingPlan


class SortingPlanFormCreate(forms.ModelForm):
    class Meta:
        model = CrossbeltSortingPlan
        fields = ['name', 'description', 'from_at', "to_at"]
        labels = {
            # 'email': pgettext_lazy('Email', 'Email')
            # 'is_active': pgettext_lazy('User active toggle', 'User is active')
        }
