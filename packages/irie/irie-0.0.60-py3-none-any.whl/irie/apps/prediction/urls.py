#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
from django.urls import path, re_path
from .views import (
    asset_predictors, predictor_profile, predictor_render, predictor_table,
    create_mdof, create_model, asset_map, CsiUpload, FORMS
)

_ROOT = "^inventory/(?P<calid>[0-9 A-Z-]*)/predictors"

urlpatterns = [
    re_path(f"{_ROOT}/(?P<preid>[0-9]{{1,}})/$",        predictor_profile),
    re_path(f"{_ROOT}/(?P<preid>[0-9]{{1,}})/render/",  predictor_render),
    re_path(f"{_ROOT}/(?P<preid>[0-9]{{1,}})/properties/",   predictor_table),
    re_path(f"{_ROOT}/create/map/$",                    asset_map),
    # re_path(f"{_ROOT}/create/model/$",                  create_model),
    re_path(f"{_ROOT}/create/model/$",                  CsiUpload.as_view(FORMS), name="csi_upload"),
    re_path(f"{_ROOT}/create/v1/$",                     create_mdof),
    re_path(f"{_ROOT}/$",                               asset_predictors, name="asset_predictors")
]
