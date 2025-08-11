import os
import json

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

import quakeio

from irie.apps.events.models import EventRecord


@login_required(login_url="/login/")
def earthquake_fitter(request):
    try:
        load_template = "EarthquakeResponse.html"

        pk = request.path.split("/")[2]

        context = {}

        context["event"] = EventRecord.objects.filter(pk=pk)[0]

        try:
            context["event_data"] = quakeio.read(
                context["event"].event_file.path, input_format="csmip.zip"
            ).serialize(serialize_data=True, summarize=False)
        except:
            context["event_data"] = {}

        html_template = loader.get_template("events/" + load_template)
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("home/page-500.html")
        return HttpResponse(html_template.render(context, request))
