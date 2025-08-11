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
import multiprocessing.dummy
from collections import defaultdict
from typing import List, Iterator, Tuple, Dict, Collection

from irie.apps.prediction.predictor import RunID
from irie.apps.prediction.metrics import HealthMetric, METRIC_CLASSES

class LiveEvaluation:
    # TODO: Merge into models.Evaluation?
    def __init__(self, event, predictors, evaluation):
        self.predictors = predictors

        self.metrics: Dict[str, Dict[str, HealthMetric]] = defaultdict(dict)
        self.active_metrics: List[str] = list(METRIC_CLASSES.keys())

        self._evaluation = evaluation

        self.evaluation_data = defaultdict(lambda: {
            "predictors": [],
            "summary": {},
            "details": {}
        })

    def update(self):
        self._evaluation.evaluation_data = dict(self.evaluation_data)
        self.save(["evaluation_data"])

    def save(self, fields=None):
        if fields is None:
            self._evaluation.save()
        else:
            self._evaluation.save(update_fields=fields)

    def runPredictor(self, args: Tuple[str, Tuple[RunID, List[HealthMetric]]]):
        predictor_name, (run_id, metrics) = args
        try:
            self.predictors[predictor_name].runPrediction(run_id)
        except:
            pass
        return predictor_name, run_id

    # met_tag, predictor_name
    def addMetric(self, mname: str, pid: str, confidence_score:int=0)->HealthMetric:
        """
        mname: metric id
        pid: predictor id
        """
        self.evaluation_data[mname]["predictors"].append(pid)
        self.update()
        return mname

    def setMetricData(self, mname: str, pid: str, data: dict):
        self.evaluation_data[mname]["details"][pid] = data.get("details", data)
        self.evaluation_data[mname]["summary"][pid] = data.get("summary", data)
        if len(self.evaluation_data[mname]["summary"]) == 1:
            self.evaluation_data[mname]["summary"][pid]["is_primary"] = True

        self.update()

    def assignMetricPredictors(self, event)->Dict[str, Tuple[RunID,List[HealthMetric]]]:
        queued_predictions : Dict[str, Tuple[RunID,List[HealthMetric]]] = {}

        for mname in self.active_metrics:
            for predictor, score in self.scorePredictors(mname, self.predictors.values(), event):

                if predictor.name not in queued_predictions and predictor.active:
                    rid = predictor.newPrediction(event)
                    queued_predictions[predictor.name] = (rid, [])

                predictor.activateMetric(mname, queued_predictions[predictor.name][0])
                queued_predictions[predictor.name][1].append(
                    self.addMetric(mname, predictor.name, score)
                )

        return queued_predictions


    def scorePredictors(self, metric, predictors: Collection["Predictor"], event)->Iterator[Tuple["Predictor", int]]:
        for predictor in predictors:
            if predictor.active and metric in predictor.getMetricList():
                yield (predictor, 0)

