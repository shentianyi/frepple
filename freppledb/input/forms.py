from django import forms

from freppledb.input.models import ForecastYear


class ForecastUploadForm(forms.Form):
    date_type = forms.ChoiceField(label='时间类型', widget=forms.Select(), choices=ForecastYear.date_types,
                                  initial=ForecastYear.date_types[0])
