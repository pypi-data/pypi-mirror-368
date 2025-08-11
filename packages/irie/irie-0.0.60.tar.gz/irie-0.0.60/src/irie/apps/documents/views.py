from django.shortcuts import render

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .documents import DOCUMENTS

@login_required(login_url="/login/")
def document_list(request):

    context = {}
    load_template = "documents.html"
    context["documents"] = sorted(DOCUMENTS, key=lambda i: i["date"], reverse=True)
    context["segment"] = load_template

    try:
        html_template = loader.get_template("documents/" + load_template)
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("home/page-500.html")
        return HttpResponse(html_template.render(context, request))

