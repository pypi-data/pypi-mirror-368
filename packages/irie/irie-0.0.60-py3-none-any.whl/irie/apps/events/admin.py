#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.contrib import admin
from .models import HazardEvent, EventRecord

admin.site.register(EventRecord)
