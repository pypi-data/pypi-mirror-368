#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django import forms
from irie.apps.prediction.models import PredictorModel

class PredictorForm(forms.ModelForm):
    class Meta:
        model = PredictorModel
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
