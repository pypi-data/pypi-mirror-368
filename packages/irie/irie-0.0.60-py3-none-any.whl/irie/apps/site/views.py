#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
# Each function in this file is responsible
# for rendering a web page. This generally
# consists of the following:
#
# - Extracting information from the URL (available from
#   the `request` variable. For example, the URL may contain
#   the CALID of the bridge that the page is about.
# - Collecting neccessary data into a `context` dictionary.
#   This typically involves a database querry, or reading from
#   a static record like the inventory.bridges.BRIDGES dictionary.
# - Finally, selecting an HTML template and rendering it against
#   the assembled `context` dictionary.
#
# NOTE: In the future, the static data in the inventory app should
#       be moved to the database. However, given the active pace of
#       research and development that would require changes to this
#       model, it is currently better as implemented.
#
#----------------------------------------------------------------------------#
#
# Fall 2022, BRACE2 Team
# Berkeley, CA
#
#----------------------------------------------------------------------------#

import os
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from irie.apps.site.view_utils import raise404


def index(request):
    "Return the primary landing page."
    context = {
        "segment": "index",
        "authenticated": request.user.is_authenticated
    }
    html_template = loader.get_template("site/index.html")
    return HttpResponse(html_template.render(context, request))


def about(request):
    "Return the About page."
    context = {
        "segment": "about",
        "authenticated": request.user.is_authenticated
    }
    html_template = loader.get_template("site/about.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def admin(request):
    """
    Return the administrator's dashboard page
    """
    context = {}

    try:
        page_template = request.path.split("/")[-1]
        context["segment"] = page_template

        if page_template == "admin":
            return HttpResponseRedirect(reverse("admin:index"))

        html_template = loader.get_template("site/" + page_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist as e:
        return raise404(request, context, e)

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))




