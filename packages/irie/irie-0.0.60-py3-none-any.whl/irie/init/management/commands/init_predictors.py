"""
NOTE: Assets must already be created
"""
from django.core.management.base import BaseCommand
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File

from irie.apps.inventory.models import Asset
from irie.apps.prediction.models  import PredictorModel
from irie.init.bridges import BRIDGES


def _create_file(path):
    temp_file = NamedTemporaryFile(delete=True)
    with open(path, "rb") as f:
        temp_file.write(f.read())
    temp_file.flush()
    return File(temp_file, name="model.zip")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for bridge in BRIDGES.values():
            print(bridge["cesmd"])
            try:
                asset = Asset.objects.get(cesmd=bridge["cesmd"])
            except Asset.DoesNotExist:
                continue

            for conf in bridge.get("predictors", []):
                print(">> ", conf["name"])
                try:
                    pred = PredictorModel.objects.get(cesmd=bridge["cesmd"])
                    pred.config = conf["config"]
                    pred.name   = conf["name"]
                    pred.save()

                    print(">> Saved ", bridge["cesmd"])
                    continue
                except:
                    protocol = PredictorModel.Protocol.TYPE2
                    for type in PredictorModel.Protocol:
                        print(f"  {type._name_}:  {conf['protocol']}")
                        if str(type) == conf["protocol"]:
                            protocol = type

                    config = conf.get("config", {})

                    a = PredictorModel(asset  = asset,
                                       name   = conf["name"],
                                       entry_point   = conf["entry_point"],
                                       config = config,
                                       description = conf.get("description", ""),
                                       active = conf.get("active", True),
                                       metrics = list(conf.get("metrics", [])),
                                       protocol = protocol
                        )

                    if "model_file" in conf:
                        a.config_file.save("model.zip", _create_file(conf["model_file"]))

                    a.save()
                    print(a)

