from django.conf import settings


def cfg_assets_root(request):
    return {"ASSETS_ROOT": settings.ASSETS_ROOT}

def irie_apps(request):      
    return {
        'irie_apps': settings.IRIE_APPS,
        'irie_app_name': request.resolver_match.app_name,
        'namespace': request.resolver_match.namespace,
        'irie_url_name': request.resolver_match.url_name
    }
