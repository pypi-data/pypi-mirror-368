#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.db import models
from django.contrib.auth.models import User

class UserNetworkPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.FloatField(default=37.806)
    longitude = models.FloatField(default=-122.365)


