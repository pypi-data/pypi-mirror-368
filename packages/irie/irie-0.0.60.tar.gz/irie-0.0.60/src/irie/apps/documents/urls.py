from django.urls import path
from django.conf.urls.static import static
from irie.core import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path("documents/", views.document_list, name="documents"),
    path("documents.html", views.document_list),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

