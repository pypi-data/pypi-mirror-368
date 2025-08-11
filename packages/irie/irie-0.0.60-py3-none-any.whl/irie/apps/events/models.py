#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
import os
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail

from irie.apps.inventory.models import Asset


class EventRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    upload_date = models.DateField(blank=False)
    event_file  = models.FileField(upload_to="events", blank=True)
    upload_data = models.JSONField(default=dict)
    motion_data = models.JSONField(default=dict)
    cesmd = models.CharField(max_length=7)
    record_identifier = models.CharField(max_length=40)

    # TODO: add field indicating if event_file and/or series data is present

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cesmd} - {self.motion_data.get('event_date', '')}"

    class Meta:
        ordering = ["-id"]

    def email_notify(self, subject, message, recipients, **kwds):
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from, recipients, **kwds)

    @property
    def pga(self):
        return round(abs(self.motion_data["peak_accel"])/980.665, 2)
    
    def plot_accel(self):
        import io
        import json
        import base64
        import quakeio
        import matplotlib 
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mdof.utilities.printing import plot_io
        from mdof.utilities.config import extract_channels, create_time_vector

        try:
            import scienceplots
            plt.style.use(["science"])
        except ImportError:
            pass


        evnt = quakeio.read(self.event_file.path, format="csmip.zip")
        try:
            channels = json.loads(self.asset.bridge_sensors)
            outputs,dt = extract_channels(evnt, channels)
            *_, time = create_time_vector(len(outputs[0]), dt)
        except:
            return None

        try:
            inputs,dt  = extract_channels(evnt, json.loads(self.asset.ground_sensors))

            fig = plot_io(inputs, outputs, time)
        except:

            fig, ax = plt.subplots()
            for output in outputs:
                ax.plot(time, output)

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

class HazardEvent(models.Model):
    id       = models.BigAutoField(primary_key=True)
    name     = models.CharField(max_length=20)
    records  = models.ManyToManyField('EventRecord', related_name='event')

    def __str__(self):
        return f"{self.name} ({self.records.count()})"



# Signal to delete the event file when the model instance is deleted
@receiver(post_delete, sender=EventRecord)
def delete_file_on_delete(sender, instance, **kwargs):
    if instance.event_file:
        if os.path.isfile(instance.event_file.path):
            os.remove(instance.event_file.path)

# Signal to delete the old event file when the file is replaced
@receiver(pre_save, sender=EventRecord)
def delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).event_file
    except sender.DoesNotExist:
        return False

    new_file = instance.event_file
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
