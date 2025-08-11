#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Fall 2022
#
#----------------------------------------------------------------------------#
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

admin.site.site_header = "IRiE"
admin.site.index_title = "IRiE"
admin.site.site_title  = "IRiE"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="site/robots.txt", content_type="text/plain"),
    ),
    path(
        "qr-0001",
        TemplateView.as_view(template_name="site/qr-0001.html", content_type="text/html"),
    ),
    path(
        "qr-0002",
        TemplateView.as_view(template_name="site/qr-0002.html", content_type="text/html"),
    ),
    path(
        "qr-0003",
        TemplateView.as_view(template_name="site/qr-0003.html", content_type="text/html"),
    ),
    path(
        "qr-0004",
        TemplateView.as_view(template_name="site/qr-0004.html", content_type="text/html"),
    ),


    # Authentication routes
    path("", include("irie.apps.authentication.urls")),

    # Application routes
    path("", include("irie.apps.events.urls")),

    path("", include("irie.apps.evaluation.urls")),

    path("", include("irie.apps.prediction.urls")),

    path("", include("irie.apps.inventory.urls")),

#   path("", include("irie.apps.recovery.urls")),

    path("", include("irie.apps.documents.urls")),

    # Leave `site.urls` as last the last line
    path("", include("irie.apps.site.urls"))


# Ensure we can serve files stored with models (eg, bridge renderings)
] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

