#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   This module implements the predictor abstraction.
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
from __future__ import annotations
from typing import Dict

from .runners import Runner, RunID
from .runners.opensees import OpenSeesRunner
from .runners.ssid import SystemIdRunner 

PREDICTOR_TYPES : Dict[str, Runner] = {
    "IRIE_PREDICTOR_V1" : OpenSeesRunner,
    "IRIE_PREDICTOR_T2" : SystemIdRunner,
#   "" :                  SystemIdRunner,
#   "IRIE_PREDICTOR_T3" : PredictorType3,
    "IRIE_PREDICTOR_T4" : OpenSeesRunner,
}

