#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.db import models

from irie.apps.inventory.models import Asset, Sensor


class PredictorModel(models.Model):
    # https://docs.djangoproject.com/en/4.2/ref/models/fields/
    class Protocol(models.TextChoices):
        TYPE1 = "IRIE_PREDICTOR_V1"
        TYPE2 = "IRIE_PREDICTOR_T2"

    id          = models.BigAutoField(primary_key=True)
    name        = models.CharField(max_length=35)
    asset       = models.ForeignKey(Asset, on_delete=models.CASCADE)
    description = models.TextField(default="")

    protocol    = models.CharField(max_length=25, 
                                   choices=Protocol.choices, 
                                   default=Protocol.TYPE2)

    entry_point = models.JSONField(default=list)
    config      = models.JSONField(default=dict)
    config_file = models.FileField(upload_to="predictor_configs/", null=True, blank=True)
    render_file = models.FileField(upload_to="renderings/", null=True, blank=True)
    metrics     = models.JSONField(default=list)

    active      = models.BooleanField()

    def __str__(self):
        return f"{self.asset.calid} - {self.name} : {self.description}"
    
    @property
    def runner(self):
        from irie.apps.prediction.predictor import PREDICTOR_TYPES
        return PREDICTOR_TYPES[self.protocol](self) 

    def get_artist(self):
        pass


class SensorAssignment(models.Model):
    predictor = models.ForeignKey(PredictorModel, on_delete=models.CASCADE)
    sensor    = models.ForeignKey(Sensor,         on_delete=models.CASCADE)
    node      = models.IntegerField()
    role      = models.CharField(
        max_length=16,
        choices=[
            ('input',   'Input'),
            ('output',  'Output'),
        ]
    )

    def __str__(self):
        return f"{self.predictor.name} - {self.sensor.name} ({self.role})"

    # orient_z  = models.FloatField()
    # orient_x  = models.FloatField()
    # orient_y  = models.FloatField()
    # show_x    = models.FloatField()
    # show_y    = models.FloatField()
    # show_z    = models.FloatField()


# class PhysicsPredictor(models.Model):
#     class Units(models.TextChoices):
#         iks = "IKS"
#         ips = "IPS"
#         fps = "FPS"
#         mks = "MKS"
#         cgs = "CGS"

#     id          = models.BigAutoField(primary_key=True)
#     name        = models.CharField(max_length=35)
#     active      = models.BooleanField()
#     asset       = models.ForeignKey(Asset, on_delete=models.CASCADE)
#     description = models.TextField(default="")

#     config_file = models.FileField(upload_to="predictor_configs/", null=True, blank=True)
#     render_file = models.FileField(upload_to="renderings/", null=True, blank=True)
#     metrics     = models.JSONField(default=list)

#     units       = models.CharField(max_length=3, choices=Units.choices)


#     def __str__(self):
#         return f"{self.name} : {self.asset.calid}"
