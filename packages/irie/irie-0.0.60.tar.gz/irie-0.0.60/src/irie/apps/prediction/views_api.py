#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   This module is responsible for implementing the API endpoint for
#   scraping evaluation data
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
import json
import datetime
from threading import Thread
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.forms.models import model_to_dict

from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Event
from irie.apps.inventory.models import Asset
from irie.apps.evaluation.models import Evaluation
import quakeio


def serialize_event(event):
    serialized = model_to_dict(event)
    serialized["upload_date"] = str(event.upload_date)

    if event.event_file:
        serialized["event_file"] = event.event_file.path
    else:
        serialized["event_file"] = None

    return serialized


def save_event(request, event, success_status):
    errors = []

    # DATE
    upload_date = datetime.datetime.now()

    # UPLOAD DATA
    upload_data = request.data.get("upload_data", "{}")
    if upload_data == "":
        errors.append({"upload_data": "This field is required"})

    # EVENT FILE
    try:
        event_file = request.FILES["event_file"]
    except KeyError:
        event_file = None
#       errors.append({"event_file": "This field is required"})
    except Exception as e:
        errors.append({"event_file": str(e)})


    if len(errors) > 0:
        return HttpResponse(json.dumps(
            {
                "errors": errors
            }), status=status.HTTP_400_BAD_REQUEST)

    # MOTION DATA
    if event_file is not None:
        try:
            motion_data = (
                quakeio.read(
                    event_file.temporary_file_path(), input_format="csmip.zip"
                ).serialize(serialize_data=False, summarize=True)
            )
        except:
            return HttpResponse(json.dumps(
                {
                    "errors": ["Failed to parse ground motion file."]
                }), status=status.HTTP_400_BAD_REQUEST)
    elif "motion_data" in request.data:
        motion_data = json.loads(request.data.get("motion_data"))

    else:
        return HttpResponse(json.dumps(
            {
                "errors": ["No motion_data provided."]
            }), status=status.HTTP_400_BAD_REQUEST)

    # RECORD ID
    rec_id = motion_data.get("record_identifier", "")


    # CREATE EVENT
    if event is None:
        # Doing a PUT
        event = Event.objects.filter(record_identifier=rec_id).first()
        if event is None:
            print("PUT: creating", rec_id, "\n\n")
            event = Event()
        else:
            print("PUT: updating", rec_id, "\n\n")
            upload_date = event.upload_date


    event.upload_date = upload_date
    event.upload_data = json.loads(upload_data)
    event.record_identifier = rec_id
    event.motion_data = motion_data
    event.cesmd = "CE" + event.motion_data["station_number"]
    event.asset = Asset.objects.get(cesmd="CE" + event.motion_data["station_number"])
    event.event_file = event_file

    event.save()


    # CREATE EVALUATION
    if "evaluation" in request.data:
        # TODO: check for parse error
        eval_data = json.loads(request.data["evaluation"])
    else:
        eval_data = None


    Evaluation.create(event, event.asset, eval_data)




    # EMAIL
    # Get users
    from django.contrib.auth import get_user_model
    User  = get_user_model()
    users = User.objects.all()

    station_name = event.motion_data["station_name"]

    event.email_notify(
        subject   = f"BRACE2: New event at '{station_name}'",

        message      = ("A new event has been sent to the BRACE2 platform. "
                       'visit  https://brace2-peer.ist.berkeley.edu/static/dmp/index.html for details.'),
        html_message = ("A new event has been sent to the BRACE2 platform. "
                       'visit <a href="https://brace2-peer.ist.berkeley.edu/static/dmp/index.html">here</a> for details.'),
        fail_silently=True,
        recipients=[user.email for user in users] + ["brace2-peer@mailinator.com"]
    )

    return HttpResponse(json.dumps({"data": serialize_event(event)}), status=success_status)



def index(request):
    context = {}
    return render(request, "events/events.html", context=context)


@api_view(["GET", "POST", "PUT"])
@permission_classes([IsAuthenticated])
def events(request):
    # if request.user.is_anonymous:
    #     return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        events_data = Event.objects.all()

        events_count = events_data.count()

        page_size = int(request.GET.get("page_size", events_count))
        page_no = int(request.GET.get("page_no", 0))
        events_data = list(events_data[page_no * page_size:page_no * page_size + page_size])

        events_data = [serialize_event(event) for event in events_data]
        return HttpResponse(json.dumps({"count": events_count, "data": events_data}), status=status.HTTP_200_OK)

    elif request.method == "POST":
        event = Event()
        return save_event(request, event, status.HTTP_201_CREATED)

    elif request.method == "PUT":
        return save_event(request, None, status.HTTP_201_CREATED)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([JSONParser,MultiPartParser])
@permission_classes([IsAuthenticated])
def event(request, event_id):
    #if request.user.is_anonymous:
    #    return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    try:
        event = Event.objects.get(pk=event_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return HttpResponse(json.dumps({"data": serialize_event(event)}), status=status.HTTP_200_OK)

    if request.method == "PUT":
        return save_event(request, event, status.HTTP_200_OK)

    if request.method == "DELETE":
        event.delete()
        return HttpResponse(json.dumps({"detail": "deleted"}), status=status.HTTP_410_GONE)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)

