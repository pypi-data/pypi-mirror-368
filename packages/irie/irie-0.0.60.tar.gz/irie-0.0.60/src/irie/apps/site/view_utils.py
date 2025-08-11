import os
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

def raise404(request, context={}, error=None):
    "Convenience function for responding with a 404 code (page not found)"
    if error is not None and "DEBUG" in os.environ and os.environ["DEBUG"]:
        raise error
    if "segment" in context:
        html_template = loader.get_template("site/page-404-sidebar.html")
    else:
        html_template = loader.get_template("site/page-404.html")
    return HttpResponse(html_template.render(context, request))
