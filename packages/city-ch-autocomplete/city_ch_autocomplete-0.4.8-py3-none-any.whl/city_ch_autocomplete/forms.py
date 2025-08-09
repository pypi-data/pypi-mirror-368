from django import forms
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class CityChField(forms.CharField):
    widget = forms.TextInput(attrs={
        'class': 'city_ch_autocomplete form-control',
        'autocomplete': 'off',
        'placeholder': _('Postcode or city name'),
        'data-searchurl': reverse_lazy('city-ch-autocomplete'),
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.label:
            self.label = _("Postcode/city")

    def clean(self, value):
        return str(value) if value else ""


class CityChMixin:
    """
    Applied to forms having a CityChField, to split postal_code/city in
    two parts.
    """
    # To be defined on subclasses
    postal_code_model_field = None
    city_model_field = None

    class Media:
        js = [format_html(
            '<script type="module" src="{}"></script>', static('city_ch_autocomplete.js')
        )]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._city_field_name = next(
            (name for name, fld in self.fields.items() if isinstance(fld, CityChField)), ''
        )
        if not self._city_field_name:
            raise RuntimeError("No CityChField instance detected on this form.")
        if not self.postal_code_model_field or not self.city_model_field:
            raise RuntimeError(
                "Please define the postal_code_model_field and city_model_field attributes on your form class"
            )
        if self.postal_code_model_field in self.fields:
            # Hide the real postal code field (it will be populated later in _clean_form).
            self.fields[self.postal_code_model_field].widget = forms.HiddenInput()
            self.fields[self.postal_code_model_field].required = False
        if self.city_model_field in self.fields:
            self.fields[self.city_model_field].widget = forms.HiddenInput()
            self.fields[self.city_model_field].required = False

    def get_initial_for_field(self, field, field_name):
        if field_name == self._city_field_name:
            value = ' '.join(
                [v for v in [self.initial.get('npa', ''), self.initial.get('localite', '')] if v]
            ).strip()
            field.choices = ((value, value),)
            return value
        return super().get_initial_for_field(field, field_name)

    def _clean_form(self):
        if self.cleaned_data.get(self._city_field_name):
            if self.cleaned_data.get('pays') == 'GB':
                self.cleaned_data[self.postal_code_model_field] = ''
                self.cleaned_data[self.city_model_field] = self.cleaned_data[self._city_field_name]
            else:
                try:
                    pcode, city = self.cleaned_data[self._city_field_name].split(' ', maxsplit=1)
                except ValueError:
                    self.add_error(self._city_field_name, _("You must enter a postcode and a city"))
                else:
                    if not pcode.isdigit():
                        self.add_error(
                            self._city_field_name,
                            _("The postcode must be composed of digits only.")
                        )
                    self.cleaned_data[self.postal_code_model_field] = pcode
                    self.cleaned_data[self.city_model_field] = city.strip()
        super()._clean_form()
