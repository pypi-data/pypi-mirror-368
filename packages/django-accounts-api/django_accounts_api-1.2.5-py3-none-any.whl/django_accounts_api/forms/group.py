from django.contrib.auth.models import Group
from django.forms import ModelForm


class GroupForm(ModelForm):
    """
    A form that creates a group
    """

    class Meta:
        model = Group
        fields = ["name"]
