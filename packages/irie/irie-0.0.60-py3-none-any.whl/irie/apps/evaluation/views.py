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
import json

from django.forms.models import model_to_dict
from django.shortcuts import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Evaluation
from irie.apps.events.models import EventRecord
from irie.apps.inventory import views as inventory
from irie.apps.inventory.models import Asset

def _evals_and_events(asset):
    evals = Evaluation.objects.filter(asset_id=asset.id)
    events = (EventRecord.objects.get(id=eval.event.id) for eval in evals)
    return evals, events

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_evaluations(request):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}),
                            status=status.HTTP_401_UNAUTHORIZED)

    evals_data = Evaluation.objects.all()

    evals_count = evals_data.count()

    evals_by_bridge = {
            bridge.cesmd: _evals_and_events(bridge)
            for bridge in Asset.objects.all()
    }

    summary = [
        {
            "cesmd": cesmd,
            "events": [
                {
#                   "event_file": print(eval) or str(eval.event.event_file.path),
                    "motion_data": eval.event.motion_data,
                    "evaluation": model_to_dict(eval)
                } for eval in evals
            ],
            "summary": {
                "SPECTRAL_SHIFT_IDENTIFICATION": inventory.ssid_stats(
                        events, #[inventory._find_ssid(event_id=event.id) for event in events],
                        "period"
                )
            }
        } for cesmd, (evals, events) in evals_by_bridge.items()
    ]
    return HttpResponse(json.dumps({"count": evals_count, "data": summary}),
                        status=status.HTTP_200_OK)

