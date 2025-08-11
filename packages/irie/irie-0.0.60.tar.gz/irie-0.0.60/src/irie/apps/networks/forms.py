#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django import forms
from .models import UserNetworkPreferences
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserNetworkPreferences
        fields = ['latitude', 'longitude']

class WeightInput(forms.NumberInput):
    # template_name = 'styled_inputs.html'

    def __init__(self, label, attrs=None):
        default_attrs = {
            'label': label,
            'class': 'form-row form-inline', 
            'style': 'width: 100px; flex: 1; color: black;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class CorridorsForm(forms.Form):
    method = forms.TypedChoiceField(
        label='Method', 
        choices=[(0, 'A'), (1, 'B'), (2, 'B-alt')], 
        coerce=int,
        initial=0
    )
    hos_weight    = forms.IntegerField(label="Hospital", initial=1, widget=WeightInput("Hospital"))
    fire_weight   = forms.IntegerField(label="Fire station", initial=0, widget=WeightInput("Fire station"))
    police_weight = forms.IntegerField(label="Police station", initial=0, widget=WeightInput("Police station"))
    maintenance_weight = forms.IntegerField(label="Maintenance", initial=0, widget=WeightInput("Maintenance"))
    airport_weight = forms.IntegerField(label="Airport", initial=0, widget=WeightInput("Airport"))
    seaport_weight = forms.IntegerField(label="Seaport", initial=0, widget=WeightInput("Seaport"))
    ferry_weight   = forms.IntegerField(label="Ferry terminal", initial=0, widget=WeightInput("Ferry terminal"))
    consider_population = forms.TypedChoiceField(
        label='Consider population', 
        choices=[(0, 'No'), (1, 'Yes')],
        coerce=int,
        initial=0
    )

    corridor_input = forms.IntegerField(widget=forms.HiddenInput(),
                                        required=False,
                                        min_value=1,max_value=162)

    def __init__(self, *args, **kwargs):
        super(CorridorsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class  = 'form-inline'  # makes the form inline
        self.helper.label_class = 'form-row sr-only'  # hides labels if desired
        self.helper.field_class = 'form-row mr-2'  # margin for spacing between fields
        self.helper.form_method = 'get'
        # self.helper.form_style =  # 'inline'
        self.helper.add_input(Submit('update', 'Rank', css_class='btn btn-primary'))

