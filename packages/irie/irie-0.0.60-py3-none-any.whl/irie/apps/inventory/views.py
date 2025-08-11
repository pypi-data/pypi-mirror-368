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
import os
import re
import json
import base64
from django.core.paginator import Paginator
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory, modelformset_factory

from irie.apps.events.models import EventRecord
# Inventory
from irie.apps.inventory.models import Asset, SensorGroup, Sensor, Datum
from irie.apps.inventory.forms import SensorGroupForm, SensorForm, SensorFormSet
from .filters import AssetFilter
# Predictors
from irie.apps.prediction.models import PredictorModel
from irie.apps.prediction.runners.hazus import hazus_fragility
from irie.apps.prediction.runners.ssid import make_mountains, ssid_stats, ssid_event_plot
# Evaluations
from irie.apps.evaluation.models import Evaluation

# Helpers
from irie.maps import AssetMap


@login_required(login_url="/login/")
def _fetch_rendering(request):
    asset_id = request.GET.get('asset')
    asset = get_object_or_404(Asset, id=asset_id)

    if asset.cesmd == "CE58658":
        template = loader.get_template(f"bridges/InteractiveTwin-{asset.cesmd}.html")
        return HttpResponse(template.render({}, request))

    for p in PredictorModel.objects.filter(asset=asset):
        if p.protocol == "IRIE_PREDICTOR_V1":
            return HttpResponse("html")

    return HttpResponse("No rendering available for this asset.")


# @login_required(login_url="/login/")
def asset_profile(request, calid):
    """
    Build the main profile page for a specific asset.
    """
    html_template = loader.get_template("inventory/asset-profile.html")

    context = {
        "segment": "assets",
        "nce_version": True,
    }

    asset = get_object_or_404(Asset, calid=calid)

    context["asset"] = asset

    # Compute Hazus fragility probabilities and curve
    try:
        hazus_results = hazus_fragility(asset.nbi_data)

        # Add fragility probabilities and plot to the context
        context["hazus"] = {
            "sa_range": json.dumps(hazus_results["sa_range"]),
            "curves":   json.dumps(hazus_results["curves"])
        }
    except Exception as e: 
        print(e)
        pass 

    context["tables"] = _make_tables(asset)

    if asset.cesmd:
        cesmd = asset.cesmd

        events = list(sorted(
            (e.event for e in Evaluation.objects.exclude(status=Evaluation.Status.Invalid).filter(asset=asset)),
                             key=lambda x: x.motion_data["event_date"], reverse=True))

        evals = [
            {"event": event,
             "pga": event.pga, #abs(event.motion_data["peak_accel"])/980., 
             "evaluation": ssid,
            }
            for i, (event, ssid) in enumerate(zip(events, ssid_stats(events, "period")))
        ]
        context["evaluations"] = Paginator(evals, 5).get_page(1)

    try:
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        import sys
        print(e, file=sys.stderr)
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
def asset_evals(request, calid):
    html_template = loader.get_template("inventory/asset-evals.html")

    context = {
        "segment": "assets",
        "nce_version": True,
    }

    page = _page_from_query(request)

    asset = get_object_or_404(Asset, calid=calid)

    context["asset"] = asset

    if asset.cesmd:
        events = list(sorted(
            (e.event for e in Evaluation.objects.exclude(status=Evaluation.Status.Invalid).filter(asset=asset)),
                             key=lambda x: x.motion_data["event_date"], reverse=True))

        evals = [
            {"event":      event,
             "pga":        event.pga, #abs(event.motion_data["peak_accel"])/980., 
             "evaluation": ssid,
            }
            for event, ssid in zip(events, ssid_stats(events, "period"))
        ]
        context["evaluations"] = Paginator(evals, 10).get_page(page)

    try:
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))


#
# Events
#
@login_required(login_url="/login/")
def asset_event_summary(request, cesmd, event):
    html_template = loader.get_template("inventory/asset-event-summary.html")

    context = {
        "segment": "events",
        "nce_version": False,
    }

    try:
        evaluation = Evaluation.objects.filter(event_id=int(event))[0]
        evaluation_data = evaluation.evaluation_data

    except Exception as e:
        # TODO: Handle case where evaluation cant be found
        evaluation_data = {}
        evaluation = None

    if request.method == 'POST':
        evaluation.evaluate()

    try:
        for metric in evaluation_data.values():
            metric["completion"] = (
                100 * len(metric["summary"])/len(metric["predictors"])
            )

        if "SPECTRAL_SHIFT_IDENTIFICATION" in evaluation_data:
            context["freq_plot_json"] = \
                    ssid_event_plot(evaluation_data["SPECTRAL_SHIFT_IDENTIFICATION"])

        context["all_evaluations"] = evaluation_data

        context["evaluation_details"] = { 
                 metric.replace("_", " ").title(): {
                    key:  [list(map(lambda i: f"{i:.3}" if isinstance(i,float) else str(i), row)) for row in table]
                    for key, table in predictors["details"].items()
                 } 
            for metric, predictors in sorted(evaluation_data.items(), key=lambda i: i[0])
        }
        context["asset"]       = evaluation and evaluation.event.asset or None
        context["nce_version"] = False
        context["event"] = EventRecord.objects.get(pk=int(event))
        context["event_data"]  = context["event"].motion_data


        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))



@login_required(login_url="/login/")
def asset_event_report(request):
    from irie.apps.evaluation.models import Evaluation
    html_template = loader.get_template("inventory/report.tex")

    context = {
        "segment": "events",
    }

    events = [
        EventRecord.objects.get(pk=evaluation.event_id)
        for evaluation in reversed(list(Evaluation.objects.all())[-6:])
    ]
    assets = list(set(
        Asset.objects.get(cesmd=event.cesmd) for event in events
    ))
    context["events"] = events
    context["assets"] = assets
    context["mountains"] = []

    if request.method == 'POST' and request.FILES.get('map_image'):
        context["map"] = base64.b64encode(request.FILES['map_image'].read()).decode("utf-8")

    for event in events:
        context["mountains"].append(make_mountains(event.asset))

    resp = html_template.render(context, request)

    return HttpResponse(resp)


@login_required(login_url="/login/")
def dashboard(request):
    from irie.apps.inventory.models import Asset

    context = {
        "segment": "dashboard",
    }

    if "demo" in request.path:
        context["demo_version"] = True

    try:
        context["recent_evaluations"] = [
            (Evaluation.objects.exclude(status=Evaluation.Status.Invalid).get(event_id=event.id), event)
            for event in sorted(EventRecord.objects.all(), 
                                key=lambda x: x.motion_data["event_date"], reverse=True)[:6]
        ]
        assets = list(set(
            Asset.objects.get(cesmd=event[1].cesmd) for event in context["recent_evaluations"]
        ))
        colors = {
            asset.id: max(event[1].pga for event in context["recent_evaluations"] if event[1].cesmd == asset.cesmd)
            for asset in assets
        }

        context["asset_map"] = AssetMap(assets, colors=colors, color_name="Peak Station Accel.").get_html()
        context["calid"] = {b.cesmd: b.calid for b in assets}

        html_template = loader.get_template("inventory/dashboard.html")
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        else:
            print(e)
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))



def california_json(request):
    with open("ca.json") as f:
        return HttpResponse(f.read(), content_type="application/json")
    with open("us_states.json") as f:
        cal = [s for s in json.load(f)["features"] if s["id"] == "CA"][0]
    return HttpResponse(json.dumps({"type": "FeatureCollection", "features": [cal]}), content_type="application/json")


def map_inventory(request):
    html_template = loader.get_template("inventory/map-inventory.html")

    import json

    consumed = {
        "Partial": set(),
        "Complete": set(),
        "Instrumented": set()
    }

    data = {
        "Partial": [],
        "Complete": [],
        "Instrumented": []
    }

    for asset in Asset.objects.filter(is_complete=True):
        consumed["Complete"].add(asset.calid)
        lat, lon = asset.coordinates
        data["Complete"].append({
            "lat": lat, "lon": lon
        })

    from irie.init.calid import CESMD, CESMD_LONG_LAT
    for calid in CESMD:
        if calid not in consumed["Complete"]:
            consumed["Instrumented"].add(asset.calid)
            try:
                lat, lon = CESMD_LONG_LAT[CESMD[calid][0][2:]]
            except:
                continue
            data["Instrumented"].append({
                # "lat": lat, "lon": -lon
                "lat": lat, "lon": lon
            })

    for asset in Asset.objects.filter(is_complete=False):
        if asset.calid not in consumed["Instrumented"]:
            lat, lon = asset.coordinates
            data["Partial"].append({
                "lat": lat, "lon": lon
            })

    return HttpResponse(html_template.render({"data": json.dumps(data)}, request))

def _make_tables(asset):
    tables = []

    if asset.cesmd and isinstance(asset.cgs_data, list):
        tables.extend([
            {k: v for k,v in group.items()
                if k not in {
                    "Remarks",
                    "Instrumentation",
                    "Remarks/Notes",
                    "Construction Date"
                }
            } for group in asset.cgs_data[1:]
        ])

    # Filter out un-interesting information
    nbi_data = [
      {k: v for k,v in group.items() 
           if k not in {
               "Owner Agency",
               "Year Reconstructed",
               "Bridge Posting Code",
#              "Latitude",
#              "Longitude",
               "Structure Number",
               "NBIS Minimum Bridge Length",
               "Record Type",
               "State Name",
               "U.S. Congressional District",
               "Inventory Route NHS Code"
           }
       } for group in asset.nbi_data.values()
    ]

    tables.extend(nbi_data)
    try:
        tables = [tables[2], *tables[:2], *tables[3:]]
    except:
        pass
    condition = {}
    for table in tables:
        keys = set()
        for k in table:
            key = k.lower()
            if "condition" in key \
            or "rating" in key \
            or (re.search("^ *[0-9] - [A-Z]", table[k]) is not None and "code" not in key):
                condition[k] = table[k]
                keys.add(k)

        for k in keys:
            del table[k]

    tables.insert(3,condition)

    # for some tables, all values are empty. Filter these out
    tables = [
        table for table in tables if sum(map(lambda i: len(i),table.values()))
    ]
    return tables


@login_required(login_url="/login/")
def asset_sensors(request, calid):
    # Template
    html_template = loader.get_template("inventory/asset-sensors.html")

    # General Context
    context = {
        "segment": "assets"
    }

    # Database
    asset = get_object_or_404(Asset, calid=calid)
    context["asset"] = asset 
    context["groups"] = SensorGroup.objects.filter(asset=asset)

    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def sensor_upload(request, calid):
    html_template = "inventory/sensor-upload.html"

    context = {
        "segment": "assets",
    }

    asset = get_object_or_404(Asset, calid=calid)

    datums = Datum.objects.filter(asset=asset).values(
        'id', 'orient_x', 'locate_x', 'orient_y', 'locate_y', 'orient_z', 'locate_z'
    )
    SensorFormSet = formset_factory(SensorForm, extra=1, can_delete=False)  

    if request.method == "POST":
        group_form = SensorGroupForm(request.POST, asset=asset)
        formset = SensorFormSet(request.POST)

        if group_form.is_valid() and formset.is_valid():
            sensor_group = group_form.save(commit=False)
            sensor_group.asset = asset  # Assign the asset
            sensor_group.save()

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    sensor = form.save(commit=False)
                    sensor.group = sensor_group
                    sensor.save()
            # Redirect after successful submission
            return redirect('asset_sensors', calid=calid)

    else:
        group_form = SensorGroupForm(asset=asset)
        formset = SensorFormSet()

    context.update({
        "group_form": group_form,
        "formset": formset,
        "renderings": [
            {
                "name": predictor.name,
                "glb": predictor.render_file.url
            }
            for predictor in PredictorModel.objects.filter(asset=asset, protocol="IRIE_PREDICTOR_V1")
            if predictor.render_file and predictor.render_file.url
        ],
        "asset": asset,
        "datums": list(datums)
    })
    return render(request, html_template, context)


@login_required(login_url="/login/")
def sensor_edit(request, calid, group_id):
    """
    Edit an existing SensorGroup + its Sensors while re-using the
    sensor-upload.html template.
    """
    html_template = "inventory/sensor-upload.html"

    context = {
        "segment": "assets",
    }

    asset = get_object_or_404(Asset, calid=calid)
    sensor_group = get_object_or_404(SensorGroup, pk=group_id, asset=asset)

    #
    SensorFormSet = modelformset_factory(
        Sensor,
        form=SensorForm,
        extra=0,
        can_delete=True,
    )

    if request.method == "POST":
        group_form = SensorGroupForm(request.POST, instance=sensor_group, asset=asset)
        formset = SensorFormSet(request.POST, queryset=sensor_group.sensors.all())

        if group_form.is_valid() and formset.is_valid():
            # update the group fields
            group_form.save()

            # saves edits, additions (extra rows you may allow), and deletions
            sensors = formset.save(commit=False)
            for sensor in sensors:
                sensor.group = sensor_group
                sensor.save()

            # any forms flagged for deletion come back in formset.deleted_objects
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect("asset_sensors", calid=calid)
    else:
        group_form = SensorGroupForm(instance=sensor_group, asset=asset)
        formset = SensorFormSet(queryset=sensor_group.sensors.all())


    context.update({
        "group_form": group_form,
        "formset": formset,
        "is_edit": True,
        "renderings": [
            {"name": p.name, "glb": p.render_file.url}
            for p in PredictorModel.objects.filter(asset=asset, protocol="IRIE_PREDICTOR_V1")
            if p.render_file and p.render_file.url
        ],
        "asset": asset,
        "datums": list(
            Datum.objects.filter(asset=asset).values(
                "id", "orient_x", "locate_x", "orient_y", "locate_y", "orient_z", "locate_z"
            )
        ),
    })
    return render(request, html_template, context)

def _page_from_query(request)->int:
    """
    Extracts the page number from a query dictionary.
    """
    page = request.GET.get("page", 1)
    try:
        return int(page)
    except ValueError:
        return 1

def _filter_asset_table(request):
    # Copy the GET parameters and remove the 'page' parameter
    page_query = request.GET.copy()
    page_query.pop('page', None)

    filter_set = AssetFilter(request.GET, queryset=Asset.objects.all())
    order_query = page_query.copy()
    if order := order_query.pop("order", None):
        try:
            assets = filter_set.qs.order_by(order[0])
        except:
            assets = sorted(filter_set.qs, key=lambda x: getattr(x, order[0]), reverse=True)
    else:
        assets = filter_set.qs
    return assets, (order_query, page_query, filter_set)


# @login_required(login_url="/login/")
def asset_table_export(request):
    """
    Returns a table of all assets in the database, paginated
    """
    import csv

    assets, _ = _filter_asset_table(request)
    
    # Create HTTP response with content type as CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="assets.csv"'

    # Write to CSV
    writer = csv.writer(response)
    # Write headers (replace with your model field names)
    writer.writerow(['ID', 'CGS ID', 'Name', 'District', 'Event Count'])

    # Write data rows (customize according to your model fields)
    for asset in assets:
        if asset.nbi_data and "NBI_BRIDGE" in asset.nbi_data and \
              "Highway Agency District" in asset.nbi_data["NBI_BRIDGE"]:
            district = asset.nbi_data["NBI_BRIDGE"]["Highway Agency District"].split(" - ")[-1]
        else:
            district = ""
        writer.writerow([asset.calid, asset.cesmd, asset.name, district, asset.event_count])

    return response


# @login_required(login_url="/login/")
def asset_table(request):
    """
    Returns a table of all assets in the database, paginated
    """

    context = {
        "segment": "assets",
    }

    assets, (order_query, page_query, filter_set) = _filter_asset_table(request)
    page = _page_from_query(request)

    context["page_query"] = page_query.urlencode()
    context["order_query"] = order_query.urlencode()
    context["bridges"]   = Paginator(assets, 10).get_page(page)
    context["asset_map"] = AssetMap(assets=assets).get_html()
    context["filter"] = filter_set


    html_template = loader.get_template("inventory/asset-table.html")
    try:
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))


