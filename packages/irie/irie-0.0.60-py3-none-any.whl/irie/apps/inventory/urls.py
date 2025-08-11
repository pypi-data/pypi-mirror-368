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
from django.urls import path, re_path
from irie.apps.inventory import views

urlpatterns = [
    path("summarize/",     views.asset_event_report),
    path("dashboard/",     views.dashboard, name="dashboard"),
    path("dashboard.html", views.dashboard),

    path("asset-table.html", views.asset_table),
    path("asset-table/",     views.asset_table, name="asset_table"),
    path("asset_table/export", views.asset_table_export, name="asset_table_export_csv"),
    re_path(
        "^evaluations/(?P<event>[0-9 A-Z-]*)/(?P<cesmd>[0-9 A-Z-]*)/.*", views.asset_event_summary,
                                                                         name="asset_event_summary"
    ),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/evaluations/$",  views.asset_evals,   name="asset_evals"),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/$",              views.asset_profile, name="asset_profile"),
    # Sensors
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/sensors/$",      views.asset_sensors, name="asset_sensors"),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/sensor_upload",  views.sensor_upload, name="sensor_upload"),
    path("inventory/<slug:calid>/sensors/<int:group_id>/edit/", views.sensor_edit, name="sensor_edit"),


    path("inventory/map2/", views.map_inventory),
    path("california.json", views.california_json),
]
