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
import sys
import logging

from threading import Thread
from django.db import models

from irie.apps.events.models import EventRecord
from irie.apps.inventory.models import Asset
from .daemon import LiveEvaluation

class Evaluation(models.Model):
    class Status(models.TextChoices):
        Finished  = "Finished"
        Running   = "Running"
        Invalid   = "Invalid"

    id = models.BigAutoField(primary_key=True)
    event = models.ForeignKey(EventRecord, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True)
    evaluation_data = models.JSONField(default=dict)
    status  = models.CharField(max_length=25,
                               choices=Status.choices,
                               default=Status.Finished)

    def __str__(self):
        return f"Evaluation {self.id} ({self.status})"

    @classmethod
    def create(cls, event: EventRecord, asset: Asset, data: dict = None):
        evaluation = cls()
        evaluation.event = event
        evaluation.asset = asset
        evaluation.status = Evaluation.Status.Running
        evaluation.save()

        if data is not None:
            evaluation.evaluation_data = data["evaluation_data"]
            evaluation.save()
        else:
            evaluate(event, evaluation)
#           Thread(target=evaluate, args=(event, evaluation)).start()

        return evaluation
    
    def evaluate(self):
        """
        Evaluate the event and update the evaluation status.
        This method can be run in a separate thread.
        """
        return evaluate(self.event, self)


def evaluate(event, evaluation)->"Evaluation":

    count_okay = 0
    daemon = LiveEvaluation(event, event.asset.predictors, evaluation)

    # assignPredictorMetrics?
    predictions = daemon.assignMetricPredictors(event)

    #with multiprocessing.dummy.Pool(3) as pool:
        # for predictor_name, run_id in pool.imap_unordered(
        #         self.runPredictor,
        #         predictions.items()
        #     ):
    if True:
        for predictor_name, run_id in map(
                daemon.runPredictor,
                predictions.items()
            ):

            print(f">>> {predictor_name} run complete.", file=sys.stderr)
            for mname in predictions[predictor_name][1]:
                print(f">>> Retrieving {predictor_name}/{mname}.", file=sys.stderr)
                data = daemon.predictors[predictor_name].getMetricData(run_id, mname)
                if data is not None:
                    count_okay += 1
                    daemon.setMetricData(mname, predictor_name, data)

            print(f">>> Completed {predictor_name}.", file=sys.stderr)

    if count_okay:
        evaluation.status = Evaluation.Status.Finished
    else:
        evaluation.status = Evaluation.Status.Invalid

    evaluation.save()
    daemon.save()
    return evaluation

