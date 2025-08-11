#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Fall 2024, BRACE2 Team
#
#   Berkeley, CA
#
#----------------------------------------------------------------------------#
from django.urls import path
from irie.apps.networks import views

urlpatterns = [
    path("recovery/",     views.network_maps,     name="recovery"),
    path("api/recovery/", views.load_network_map, name='load_recovery_map'),
]
