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
from django.db import models
from django.core.validators import int_list_validator
from django.urls import reverse

class Corridor(models.Model):
    id       = models.BigAutoField(primary_key=True)
    name     = models.CharField(max_length=20)
    route    = models.CharField(max_length=100, blank=True)
    assets   = models.ManyToManyField('Asset', related_name='corridors')

    def __str__(self):
        return f"{self.name} ({self.assets.count()})"


class Asset(models.Model):
    id = models.BigAutoField(primary_key=True)
    cesmd = models.CharField(max_length=7, blank=True, null=True)
    calid = models.CharField(max_length=15)
    name  = models.CharField(max_length=100,  blank=True)
    notes = models.CharField(max_length=1024, blank=True, null=True)

    is_complete = models.BooleanField(help_text="Is the asset a complete digital twin")

    nbi_data  = models.JSONField(default=dict, blank=True)
    cgs_data  = models.JSONField(default=list, blank=True)

    # Ground motion sensors
    ground_sensors = models.CharField(validators=[int_list_validator],
                                      max_length=400, blank=True,
                                      help_text="Comma-separated list of ground channel numbers")
    bridge_sensors = models.CharField(validators=[int_list_validator],
                                      max_length=400, blank=True,
                                      help_text="Comma-separated list of bridge channel numbers")

    def __str__(self):
        return f"{self.calid} - {self.name}"

    def get_absolute_url(self):
        return reverse("asset_profile", args=[self.calid])
    
    @property 
    def last_event(self):
        from irie.apps.events.models import EventRecord
        # TODO: use event_date
        try:
            return EventRecord.objects.filter(asset=self).latest("upload_date")
        except EventRecord.DoesNotExist:
            return None

    @property
    def predictors(self):
        from irie.apps.prediction.predictor import PREDICTOR_TYPES
        from irie.apps.prediction.models import PredictorModel
        return {
            p.name: PREDICTOR_TYPES[p.protocol](p)
            for p in reversed(PredictorModel.objects.filter(asset=self))
        }

    @property
    def event_count(self):
        from irie.apps.events.models import EventRecord
        return EventRecord.objects.filter(asset=self).count()

    @property
    def rendering(self):
        from irie.apps.prediction.models import PredictorModel
        for predictor in PredictorModel.objects.filter(asset=self):
            if predictor.render_file:
                return predictor.render_file.url

    @property
    def coordinates(self):
        if self.nbi_data:
            for table in self.nbi_data.values():
                if "Latitude" in table:
                    return map(float, map(table.get, ["Latitude", "Longitude"]))

        if self.cgs_data:
            lat, lon = map(self.cgs_data[0].get, ["Latitude", "Longitude"])
            return (float(lat.replace("N", "")), -float(lon.replace("W", "")))

        
        return (None, None)

    class Meta:
        ordering = ["-id"]



class Vulnerability: # (models.Model):
    type    = None
    asset   = None
    notes   = models.CharField(max_length=1024, blank=True, null=True)


class Datum(models.Model):
    name  = models.CharField(max_length=100)
    orient_x = models.CharField(max_length=240) # eg, longitudinal axis of the deck from west to east
    locate_x = models.CharField(max_length=240) # eg, east abutment-to-deck interface
    orient_y = models.CharField(max_length=240) # eg, transverse axis of the deck from north to south
    locate_y = models.CharField(max_length=240) # eg, center of deck
    orient_z = models.CharField(max_length=240) # eg, vertical upwards
    locate_z = models.CharField(max_length=240) # eg, deck surface

    angle_x = models.DecimalField(decimal_places=2, max_digits=10, default=0.0, null=True, blank=True)
    angle_y = models.DecimalField(decimal_places=2, max_digits=10, default=0.0, null=True, blank=True)
    asset    = models.ForeignKey(Asset, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.name}"

    def to_cardinal(self):
        """
        Create rotation matrix from datum basis to cardinal basis.
        The cardinal basis is defined as:
        cx = North, 
        cy = East, 
        cz = Up

        The datum basis is defined as:
        ex = Exp(orient_x cz) cx
        ey = Exp(orient_y cz) cy
        ez = Exp(orient_z cz) cz
        where orient_x, orient_y, and orient_z are the angles in radians and
        Exp is the exponential map which encodes the Rodrigues' rotation formula.

        We want to return the rotation Rec  such that:
            Rec @ [ex, ey, ez] = [cx, cy, cz]
        """
        import numpy as np
        from shps.rotor import exp

        orient_x = self.angle_x
        orient_y = self.angle_y

        ex, ey, ez = np.eye(3)
        cz = ez
        cx = exp(-orient_x*cz) @ ex
        cy = exp(-orient_y*cz) @ ey

        rotation = np.column_stack((cx, cy, cz))

        return rotation
    
    def to_other(self, other: "Datum"):
        """
        Create rotation matrix from this datum to another datum.
        """
        R_cs = self.to_cardinal()
        R_cm = other.to_cardinal()
        return R_cm.T @ R_cs

class SensorGroup(models.Model):
    name    = models.CharField(max_length=100)
#   sensors; access with .sensor_set.all()
    asset   = models.ForeignKey(Asset, on_delete=models.RESTRICT)
    datum   = models.ForeignKey(Datum, on_delete=models.RESTRICT)
#   network = models.CharField(max_length=100)
#   events  = None

    def __str__(self):
        return f"{self.asset.calid} - {self.name} ({self.datum})"


class Sensor(models.Model):
    # class Status:
    #     active: bool

    name = models.CharField(max_length=100)
    x    = models.DecimalField(decimal_places=2, max_digits=10)
    y    = models.DecimalField(decimal_places=2, max_digits=10)
    z    = models.DecimalField(decimal_places=2, max_digits=10)

    dx   = models.DecimalField(decimal_places=2, max_digits=10)
    dy   = models.DecimalField(decimal_places=2, max_digits=10)
    dz   = models.DecimalField(decimal_places=2, max_digits=10)

    group  = models.ForeignKey(SensorGroup,
                               related_name="sensors",
                               on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.group.asset.cesmd} / {self.name}"


    def acceleration(self, event):
        import quakeio

        motion_data = (
            quakeio.read(
                event.event_file.path, input_format="csmip.zip"
            )
        )

        series = motion_data.match("l", station_channel=f"{self.name}").accel.data

        return [
            (series*float(self.dx)).tolist(),
            (series*float(self.dy)).tolist(),
            (series*float(self.dz)).tolist()
        ]


# class Rendering:
#     def __init__(self, url=None, units, datum):
#         self._url = url


#     def url(self):
#         return self._url
    
#     def url_or_data(self):
#         pass
    
#     def scale_meter(self):
#         pass

# class PersistentRendering(models.Model):
#     asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
#     datum = models.ForeignKey(Datum, on_delete=models.CASCADE)
#     units = models.CharField(max_length=3) 

# class TemporaryRendering(Rendering):
#     def __init__(self, data, units, datum, asset):
#         self._data  = data
#         self._units = units 
#         self._datum = datum
