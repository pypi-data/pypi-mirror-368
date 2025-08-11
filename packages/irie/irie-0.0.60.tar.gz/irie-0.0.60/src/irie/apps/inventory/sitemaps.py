#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Asset  # Replace with your model

class InventorySitemap(Sitemap):
    changefreq = "weekly"  # Change frequency of the content
    priority = 0.5  # Priority of the URLs in the sitemap

    def items(self):
        # Return a queryset of objects for the sitemap
        return Asset.objects.exclude(cesmd__isnull=True)

    def lastmod(self, obj):
        # Return the last modification date of an object
        if event := obj.last_event:
            return event.upload_date
        return None

