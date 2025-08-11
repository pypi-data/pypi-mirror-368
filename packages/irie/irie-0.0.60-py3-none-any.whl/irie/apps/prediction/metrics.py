#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
import orjson

def _serialize(data):
    return orjson.loads(orjson.dumps(data,
                        option=orjson.OPT_SERIALIZE_NUMPY))

class HealthMetric:
    metric_tag: str
    def __init__(self, predictor: str, data = None):
        self.predictor = predictor
        self.data = data


class PeriodShiftMetric(HealthMetric):
    metric_tag = "SPECTRAL_SHIFT_IDENTIFICATION"
    def buildDetails(self):
        return self.data
    def getSummary(self):
        return self.data

class ColumnStrainStateMetric01(HealthMetric):
    metric_tag = "COLUMN_STRAIN_STATES"

    def format_html(self):
        pass

class PeakAccelMetric01(HealthMetric):
    metric_tag = "PEAK_ACCEL"


class PeakDriftMetric01(HealthMetric):
    metric_tag = "PEAK_DRIFT"


class AccelRHMetric01(HealthMetric):
    metric_tag = "ACC_RESPONSE_HISTORY"

    def getSummary(self)->dict:
        return _serialize(self.data)

    def buildDetails(self)->str:
        return _serialize(self.data)


METRIC_CLASSES = {
    c.metric_tag: c for c in  [
        PeriodShiftMetric,
        PeakAccelMetric01,
        PeakDriftMetric01,
        AccelRHMetric01,
        ColumnStrainStateMetric01
    ]
}

