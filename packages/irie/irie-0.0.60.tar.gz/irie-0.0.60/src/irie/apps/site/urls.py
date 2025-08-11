from django.urls import path, re_path
from irie.apps.site import views, view_sdof

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    re_path(r"^sdof/.*", view_sdof.earthquake_fitter, name="sdof"),
]
