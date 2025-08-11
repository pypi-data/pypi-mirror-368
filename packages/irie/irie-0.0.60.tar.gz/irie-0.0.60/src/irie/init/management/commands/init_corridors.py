"""
To run:
  python manage.py shell < scripts/init_corridors.py

This script depends on the files:
    soga_corridors.json

This file is created using the script make_corridors.py
which takes in corridor_line.geojson and soga_corridors.csv
"""

import sys
import json
from pathlib import Path

import irie
from irie.apps.inventory.models  import Asset, Corridor

from django.core.management.base import BaseCommand
DATA = Path(irie.__file__).parents[0]/"init"/"data"/"networks"

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open(DATA/"soga_corridors.json") as f:
            corridors = json.load(f)

        for cdata in corridors:
            cname = cdata["name"]

            try:
                corridor = Corridor.objects.get(name=cname)

            except:
                corridor = Corridor(id=cdata["id"], name=cname)

            corridor.save()

            for calid in cdata["bridges"]:
                try:
                    corridor.assets.add(Asset.objects.get(calid=calid))
                    print(f"Added {calid} to {corridor.name}")
                except Exception as e:
                    print(f"Failed to find assed with calid {calid} ({e})")

            corridor.save()

