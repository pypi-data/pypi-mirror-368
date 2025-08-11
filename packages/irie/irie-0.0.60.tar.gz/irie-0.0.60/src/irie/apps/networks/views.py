#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Fall 2024, BRACE2 Team
#   Berkeley, CA
#
#----------------------------------------------------------------------------#

import os
import json
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
import logging
from .models import UserNetworkPreferences

logger = logging.getLogger(__name__)

from .networks import BridgeNetworks_method_a, BridgeNetworks_method_b, BridgeNetworks_method_b_alt

from .forms import CorridorsForm


@login_required(login_url="/login/")
def load_network_map(request: HttpRequest)->HttpResponse:
    
    preferences, created = UserNetworkPreferences.objects.get_or_create(user=request.user)

    tab = request.GET.get('tab', None)

    form = CorridorsForm(request.GET or None)
    #
    #
    if not form.is_valid():
        return HttpResponse(json.dumps({"map_html": '<p>Invalid inputs.</p>'}))

    method = form.cleaned_data["method"]
    weights = {k: v for k,v in form.cleaned_data.items() if k.endswith("_weight")}


    if method == 0:
        Analysis = BridgeNetworks_method_a
    elif method == 1:
        Analysis = BridgeNetworks_method_b
    elif method == 2:
        Analysis = BridgeNetworks_method_b_alt
    else:
        return HttpResponse(json.dumps({"map_html": '<p>Map unavailable.</p>'}))
    

    data = {}
    if tab != "tab1":
        analysis = Analysis(preferences, weights, False, True)
        map = analysis.create_map(corridor=form.cleaned_data["corridor_input"])

    else:
        cp = form.cleaned_data["consider_population"]
        analysis = Analysis(preferences, weights, cp, False)
        map = analysis.create_map()
        data["table_html"] = loader.get_template("networks/corridor_table.html").render({
            "corridors": (i for _, i in analysis.ranked_corridors().iterrows())
        })

    data["map_html"] = map._repr_html_()
    return HttpResponse(json.dumps(data))


@login_required(login_url="/login/")
def network_maps(request: HttpRequest)->HttpResponse:

    context = {}
    context["segment"] = "networks"

    context["maps"] = {
        "tab1": {"name": "All", "form": CorridorsForm()},
    }

    try:
        html_template = loader.get_template("networks/networks.html")
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))
