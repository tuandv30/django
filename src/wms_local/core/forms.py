from django import forms


class PermissionMultipleChoiceField (forms.ModelMultipleChoiceField):
    """ Permission multiple choice field with label override."""

    def label_from_instance(self, obj):
        return obj.name
