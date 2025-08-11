#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class IrieSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        # Return the names of your static views
        return ["home", "about", "dashboard", "asset_table"]

    def location(self, item):
        return reverse(item)

