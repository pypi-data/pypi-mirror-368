import irie
import numpy as np
from irie.apps.inventory.models  import Asset
from irie.init.calid   import CESMD_LONG_LAT, CESMD
from pathlib import Path
from django.core.management.base import BaseCommand
import json
from collections import defaultdict

DATA = Path(irie.__file__).parents[0]/"init"/"data"

with open(DATA/"cgs_data.json") as f:
    CGS_DATA = json.loads(f.read())
with open(DATA/"nbi_data_cesmd.json") as f:
    NBI_DATA = json.loads(f.read())


def nbi_reshape(raw):
    data = defaultdict(dict)
    for row in raw["Results"]["NBIData"]["NBIDataList"]:
        data[row["TABLE_NAME"]][row["EXPANDED_FIELD_ALIAS"]] = row["FIELD_VALUE"]

    return dict(data)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # with open(DATA/"cgs-stations.json") as f:
        #     stations = json.load(f)

        count = 0
        try:
            for calid, (cesmd, route, name) in CESMD.items():
                try:
                    asset = Asset.objects.get(calid=calid)
                except Asset.DoesNotExist:
                    asset = Asset()
                    asset.is_complete = False

                asset.name = name
                asset.cesmd = cesmd
                asset.calid = calid
                asset.cgs_data = CGS_DATA.get(cesmd, {})
                if calid.replace("-", " ") in NBI_DATA:
                    asset.nbi_data = nbi_reshape(NBI_DATA.get(calid.replace("-", " "), [{}])[-1])

                asset.save()
                print(asset)
                count += 1

        except Exception as e:
            print(f"Updated {count} assets")
            raise e
        print(f"Updated {count} assets")
