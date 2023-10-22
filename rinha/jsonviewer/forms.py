from django import forms
from .models import JSONData


class JSONDataForm(forms.ModelForm):
    class Meta:
        model = JSONData
        fields = ['json_file']
