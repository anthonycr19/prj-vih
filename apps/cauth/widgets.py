from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
from .models import User


class UserChoiceField(ModelChoiceField):

    def __init__(self, *args, **kwargs):
        super(UserChoiceField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            value = User.objects.get(**{key: value})
        except (ValueError, TypeError, User.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value
