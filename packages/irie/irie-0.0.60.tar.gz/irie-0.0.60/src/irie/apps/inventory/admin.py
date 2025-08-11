#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.contrib import admin
from .models import Asset, Corridor, SensorGroup, Sensor, Datum

admin.site.register(Corridor)
admin.site.register(Asset)
admin.site.register(SensorGroup)
admin.site.register(Sensor)
admin.site.register(Datum)