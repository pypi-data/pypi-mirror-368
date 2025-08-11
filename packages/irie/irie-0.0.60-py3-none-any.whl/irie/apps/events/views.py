
import os
from django.template import loader
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from irie.apps.events.models import EventRecord


@login_required(login_url="/login/")
def event_table(request):
    """
    This view generates the event table page. It uses the event-table.html
    """
    context = {}
    page_template = "event-table.html"
    context["segment"] = "events"

    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except:
        page = 1

    asset = request.GET.get("asset", None)

    if asset is not None:
        events = [i for i in sorted(EventRecord.objects.filter(asset=asset),
                             key=lambda x: x.motion_data["event_date"], reverse=True)]
    else:
        events = [i for i in sorted(EventRecord.objects.all(),
                             key=lambda x: x.motion_data["event_date"], reverse=True)]

    paginator = Paginator(events, 20)


# reversed(sorted(Event.objects.all(),
#                                         key=lambda x: x.motion_data["event_date"]))
    context["events"] = paginator.get_page(page)


    html_template = loader.get_template("events/" + page_template)

    try:
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def event_collection(request):
    """
    This view generates the event table page. It uses the event-table.html
    """
    context = {}
    page_template = "event-table.html"
    context["segment"] = "event-table.html"

    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except:
        page = 1
    
    asset = request.GET.get("asset", None)

    if asset is not None:
        events = [i for i in reversed(sorted(EventRecord.objects.filter(asset=asset),
                             key=lambda x: x.motion_data["event_date"]))]
    else:
        events = [i for i in reversed(sorted(EventRecord.objects.all(),
                             key=lambda x: x.motion_data["event_date"]))]
    
    # Paginator for 10 items per page
    paginator = Paginator(events, 15)


# reversed(sorted(Event.objects.all(),
#                                         key=lambda x: x.motion_data["event_date"]))
    context["events"] = paginator.get_page(page)


    html_template = loader.get_template("events/" + page_template)

    try:
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))

