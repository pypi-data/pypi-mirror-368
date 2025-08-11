# forms.py
from django import forms
from irie.apps.inventory.models import Datum
from irie.apps.prediction.models import PredictorModel, SensorAssignment

class DatumSelectForm(forms.Form):
    """
    Step 0 – choose an existing datum or say 'create new'.
    The empty choice means 'I want to add a new datum'.
    """
    datum = forms.ModelChoiceField(
        queryset=Datum.objects.none(),
        required=False,
        empty_label="-- create new datum --",
        label="Select Datum",
        help_text="Select an existing datum or create a new one."
    )

    def __init__(self, *args, asset=None, datum_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["datum"].queryset = datum_queryset or Datum.objects.none()

class DatumCreateForm(forms.ModelForm):
    class Meta:
        model = Datum
        fields = ("angle_x", "angle_y")

    def __init__(self, *args, asset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.asset = asset

class PredictorForm(forms.ModelForm):
    class Meta:
        model = PredictorModel
        help_text = {
            "config_file": "File exported from CSi Bridge or SAP2000 (.b2k or .s2k).",
        }
        fields = "__all__"
        exclude = [
            "render_file", 
            "asset", 
            "metrics", 
            "active",
            "description",
            "entry_point", 
            "config", 
            "protocol"
        ]
    def __init__(self, *args, asset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.asset = asset
        self.fields['name'].widget.attrs["class"] = "rounded-0"
        self.fields['config_file'].widget.attrs["class"] = "rounded-0"

class SensorForm(forms.ModelForm):
    class Meta:
        model = SensorAssignment
        fields = (
            "role",
            "sensor"
        )

    def __init__(self, *args,  **kwargs): 
        super().__init__(*args, **kwargs)

class ConfirmForm(forms.Form):
    # no fields – just a read-only summary screen
    pass
