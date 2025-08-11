#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Summer 2023, BRACE2 Team
#   Berkeley, CA
#
#----------------------------------------------------------------------------#
from django.apps import AppConfig


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "irie.apps.evaluation"
    label = "irie_apps_evaluation"

