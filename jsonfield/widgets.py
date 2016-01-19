import simplejson as json

from django import forms
from django.utils import six

from .utils import default


class JSONWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        if not isinstance(value, six.string_types):
            value = json.dumps(value, indent=4, ensure_ascii=False, default=default)
        return super(JSONWidget, self).render(name, value, attrs)


class JSONSelectWidget(forms.SelectMultiple):
    pass
