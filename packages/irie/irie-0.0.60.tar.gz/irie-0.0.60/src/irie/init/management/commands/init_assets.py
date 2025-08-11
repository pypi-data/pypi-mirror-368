import irie
import lzma
import tarfile
from pathlib import Path
from django.core.management.base import BaseCommand
import json
try:
    import orjson
except ImportError:
    import json as orjson

DATA = Path(irie.__file__).parents[0]/"init"/"data"

with open(DATA/"cgs_data.json") as f:
    CGS_DATA = json.loads(f.read())


from collections import defaultdict
from irie.apps.inventory.models  import Asset
from irie.init.calid   import CALID, CESMD
from irie.init.bridges import BRIDGES

DRY = False
UPDATE_ASSETS = True

DISTRICTS = {
    # "01 - District 1",
    "04 - District 4",
    # "05 - District 5",
    # "06 - District 6",
    # "07 - District 7",
    # "08 - District 8",
    # "09 - District 9",
    # "11 - District 11",
    # "12 - District 12"
}

MIN_ADTT = 0 #  1_500
MIN_ADT  = 0 # 15_000

SKIP_DESIGN = {
    "19 - Culvert"
}

#-----------------------------------

def nbi_reshape(raw):
    data = defaultdict(dict)
    for row in raw["Results"]["NBIData"]["NBIDataList"]:
        data[row["TABLE_NAME"]][row["EXPANDED_FIELD_ALIAS"]] = row["FIELD_VALUE"]

    return dict(data)


def load_assets(NBI_DATA):

    def find_bridge(bridges, calid):
        for bridge in bridges.values():
            if "calid" in bridge and bridge["calid"].split(" ")[0] == calid:
                return bridge
        return {}

    def get_nbi(calid, missing_ok=False):

        if missing_ok and calid not in NBI_DATA:
            return None

        blocks = NBI_DATA[calid][-1]
        return nbi_reshape(blocks)


    def get_route(bridge):
        return "-".join(bridge["NBI_BRIDGE"]["Location"].split("-")[:3])


    def skip(bridge, routes):
        return not (
            (
                get_route(bridge) in routes
#               and bridge["NBI_BRIDGE"]["Highway Agency District"] in DISTRICTS
#               and bridge["NBI_POSTING_STATUS"]["Structure Operational Status Code"] == "A - Open"
            ) or (
                bridge["NBI_BRIDGE"]["Highway Agency District"] in DISTRICTS
#               and bridge["NBI_BRIDGE"]["Type of Service on Bridge Code"] == "1 - Highway"
#               and bridge["NBI_BRIDGE"]["Owner Agency"] == "1 - State Highway Agency"
#               and bridge["NBI_SUPERSTRUCTURE_DECK"]["Main Span Design"] not in SKIP_DESIGN
#               and (
#                   "Concrete" in bridge["NBI_SUPERSTRUCTURE_DECK"]["Main Span Material"]
#                   or "Steel" in bridge["NBI_SUPERSTRUCTURE_DECK"]["Main Span Material"]
#               )
#               # and bridge["NBI_FEATURE"]["Inventory Route NHS Code"] == "1 - On NHS"
#               and int(bridge["NBI_FEATURE"]["Average Daily Truck Traffic (Volume)"]) >= MIN_ADTT
#               and int(bridge["NBI_FEATURE"]["Average Daily Traffic"]) >= MIN_ADT
                # and bridge["NBI_BRIDGE"]["Coulverts Condition Rating"] == "N - Not a culvert"
            )
        )


# 1. Collect routes of interest
    ROUTES = set()
    for calid in CESMD: #BRIDGES.values():
        # if "calid" not in bridge:
        try:
            calid = Asset.objects.get(calid=calid).calid
        except:
            continue

        calid = calid.split(" ")[0].replace("-", " ")
        nbi = get_nbi(calid, missing_ok=True)
        if nbi is not None:
            ROUTES.add(get_route(nbi))


    count = 0

    for item in NBI_DATA:
        calid  = item.replace(" ", "-")
        nbi    = get_nbi(item)
        config = None # find_bridge(BRIDGES, calid)
        try:
            if skip(nbi, ROUTES) or item == "33 0726L":
                continue
        except:
            print("Failed to skip ", calid)
            continue

        if DRY:
            continue

        try:
            asset = Asset.objects.get(calid=calid)
            if UPDATE_ASSETS and nbi:
                asset.nbi_data = nbi
                asset.save()


        except Asset.DoesNotExist:
            if nbi is None:
                print(">> Skipping ", calid)
                continue

            name = config.get("name", nbi["NBI_BRIDGE"]["Location"])
            asset = Asset(calid=calid,
                      name = name,
                      nbi_data = nbi,
                      is_complete=False)

            count += 1

        if asset.nbi_data or asset.cgs_data:
            asset.save()

        continue

    print(f"Created {count} of {len(NBI_DATA)} assets")


class Command(BaseCommand):
    help = "Populate the database with assets using NBI data"

    def handle(self, *args, **kwargs):

        # Load assets outside of district 4
        with open(DATA/"nbi_data-california.json") as f:
            load_assets(json.load(f)) 


        # Open the district tar file 
        with tarfile.open(DATA/"nbi"/"04.tar", "r") as tar:
            # Iterate through each file in the tar archive
            for member in tar.getmembers():
                # Process only .xz files
                if member.name.endswith(".xz"):
                    print(f"Loading {member.name}...")

                    # Extract the xz-compressed file content
                    xz_file = tar.extractfile(member)

                    if xz_file is None:
                        print(f"Failed to extract {member.name}")
                        continue

                    # Decompress the .xz file
                    with lzma.LZMAFile(xz_file) as decompressed_file:
                        # Load the JSON content
                        try:
                            data = orjson.loads(decompressed_file.read())
                            load_assets(data)

                        except orjson.JSONDecodeError as e:
                            print(f"Failed to parse JSON in {member.name}: {e}")
