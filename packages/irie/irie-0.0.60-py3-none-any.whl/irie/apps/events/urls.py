#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
import rest_framework_simplejwt.views as jwt_views

from django.urls import path
from django.conf.urls.static import static

from . import views_events, views


urlpatterns = [
    path("event-table/",                      views.event_table, name="event_table"),
    path("event-table.html", views.event_table),

    path("events/", views_events.index),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/events/', views_events.events),
    path('api/events/<int:event_id>/', views_events.event),
]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

