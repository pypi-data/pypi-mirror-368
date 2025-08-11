#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from pathlib import Path
from typing import NewType
from abc import abstractmethod
RunID = NewType("RunID", int)

MetricType = NewType("MetricType", str)

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class Runner:
    def __init__(self, pred: dict):

        if isinstance(pred, dict):
            # Create from dict when posted from API; this
            # is used to create a new PredictorModel. 
            # In the future this may be removed.
            self.name: str   = pred["name"]
            self.description = pred.get("description", "")
            self.conf        = pred["config"]
            self.metrics     = pred["metrics"]
            self.entry_point = pred["entry_point"]
            self.active = pred.get("active", True)
        else:
            # Create from existing PredictorModel when loaded from database.
            # This is done when running analysis
            self.id = pred.id
            # self.asset = pred.asset
            self.name: str = pred.name
            self.description = "" # conf.description
            self.conf = pred.config
            if pred.entry_point:
                self.entry_point = pred.entry_point
            if pred.metrics:
                self.metrics = pred.metrics
            self.active  = pred.active

            # NEW:
            self.predictor = pred

            self.runs = {}
            if pred.config_file:
                # TODO: for Amazon S3
                # self.model_file = Path(pred.config_file.path).resolve()
                self.out_dir = Path(__file__).parents[0]/"Predictions"
            else:
                self.model_file = None
                self.out_dir = None
                self.runs = {}

    @abstractmethod
    def newPrediction(self, event)->RunID: ...

    @abstractmethod
    def runPrediction(self, run_id)->bool: ...

    def getMetricList(self)->list:
        return self.metrics

    def activateMetric(self, type, rid=None)->bool:
        return False

    @abstractmethod
    def getMetricData(self, run: RunID, metric: MetricType)->dict: ...
