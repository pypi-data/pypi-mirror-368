#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.contrib import admin
from .models import PredictorModel, SensorAssignment

admin.site.register(PredictorModel)
admin.site.register(SensorAssignment)
