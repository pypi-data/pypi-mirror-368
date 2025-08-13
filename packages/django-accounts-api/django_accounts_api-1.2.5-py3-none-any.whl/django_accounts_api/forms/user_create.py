from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField
from django.forms import ModelForm

User = get_user_model()

class UnusablePasswordUserCreationForm(ModelForm):
    """
    A form that creates a user, with no privileges, from the given username
    Sets an unusable password, and returns a reset password link
    """

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True

    def save(
        self,
        commit=True):

        user = super().save(commit=False)
        user.set_password(None)
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user
