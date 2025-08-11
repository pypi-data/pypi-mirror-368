#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
# First run without arguments to generate list of structure numbers and
# save to JSON. Then run with that JSON as argv[1] to pull inventory data.
#
# Adapted from:
# https://github.com/psychogeekir/ScrapeNBIBridgeInfo/raw/master/getNBIClimateData.py
#
# Claudio M. Perez
#
# TODO:
#
# - Add option for "SELECTED_TAB": "NBETab", 
#
# - Perhaps add something like:
#     --filter-calid calids.txt
#   This will be useful for testing, eg, (chrystal's first version)
#     python getNBIData.py yearly.json --filter-calid <(echo "33 0214L")
#   
#   or
#     python getNBIData.py | python getNBIData.py /dev/stdin <(echo "33 0214L")
#
import sys
import json
import requests
from tqdm import tqdm

def getBridgeList(headers, start_page=1, totalpages=3, pagesize=10, totalbridges=24, page_nums=None, **kwds):
    url = 'https://infobridge.fhwa.dot.gov/Data/GetAllBridges'

    payload = {
        "isShowBridgesApplied": True,
        "gridParam": {
            "isShowBridgesApplied": True, 
            "IsFilterApplied": False, 
            "SelectedFilters": None,
            "SortOrder": "asc", 
            "SortIndex": "STATE_CODE",
        }
    }

    pages = []
    def filter(row):
        return int(row["STATE_CODE"]) > 0

    if page_nums is None:
        page_nums = range(start_page, totalpages + 1)

    for pageno in page_nums:
        try:
            payload["gridParam"]["PageNumber"] = pageno
            payload["gridParam"]["PageSize"]   = pagesize

            r = requests.post(url, headers=headers, data=json.dumps(payload))

            if r.status_code == 200:
                try:
                    resp = json.loads(eval(r.content.decode('utf-8'))) # [1:-1].replace("\\", ""))
                except:
                    print(f"Failed to get page {pageno}", file=sys.stderr)
                    continue

                bridges = [
                    {'BRIDGE_YEARLY_ID': row['BRIDGE_YEARLY_ID'], 
                     'STRUCTURE_NUMBER': row['STRUCTURE_NUMBER'].strip()}
                        for row in resp["Results"]["rows"] # if filter(row)
                ]
                pages.extend(bridges)
                print(pageno, len(pages), len(bridges), resp["Results"]["rows"][-1]["STATE_NAME"], file=sys.stderr)

        except KeyboardInterrupt:
            break

    return pages


def getNBIData(headers, bridgeTable, years,
               structure=None,
               keep_query=False):

    url = 'https://infobridge.fhwa.dot.gov/Data/getBridgeInformation'

    _headers = headers.copy()
    # payload = {
    #     "requestModel": {
    #         "SELECTED_TAB": "OverviewTab",
    #         "SELECTED_YEAR_ID": None,
    #         "IS_NEW_RECORD": True,
    #         "IS_YEAR_SELECTED": False,
    #         "Is_Overview_Bridge_Selected": False,
    #         "SELECTED_YEAR": None,
    #         "CURRENT_YEARLY_ID": "25099893",
    #         "IS_NBI_TREE_SELECTED": False,
    #         "Folder_Name": None,
    #         "tabChange": False,
    #         "BRIDGE_YEARLY_ID": "25099893",
    #         "NEW_BRIDGE_ID": 58813,
    #         "SELECTED_NDE_TAB": "General"
    #     }
    # }

    payload  = {
      "requestModel":{
        "SELECTED_TAB": "NBITab", 
        "SELECTED_YEAR_ID": None, 
        "IS_NEW_RECORD": False,
        "IS_YEAR_SELECTED": False, 
        "Is_Overview_Bridge_Selected": False,
        "NEW_BRIDGE_ID": 0, 
        "STRUCTURE_NUMBER": structure, 
        "STATE_NAME": None,
        "STATE_CODE": 0,    
        "IS_EXPERIMENTAL": False, 
        "SELECTED_NDE_TAB": "General",
       #"MERRA_ID": 0,"IS_NBI_TREE_SELECTED": False,"Folder_Name": None,"tabChange": False,
      }
    }


    referer = 'https://infobridge.fhwa.dot.gov/Data/BridgeDetail/'
    data = {}

    for i,bridge in enumerate(tqdm(bridgeTable)):

        BRIDGE_YEARLY_ID = bridge['BRIDGE_YEARLY_ID']
        STRUCTURE_NUMBER = bridge['STRUCTURE_NUMBER']

        data[STRUCTURE_NUMBER] = []

        for year in years:
            _headers['referer'] = referer + str(BRIDGE_YEARLY_ID)

            payload["requestModel"].update({
                  "SELECTED_YEAR":     year,
                  "CURRENT_YEARLY_ID": BRIDGE_YEARLY_ID,
                  "BRIDGE_YEARLY_ID":  BRIDGE_YEARLY_ID,
            })

            r = requests.post(url, data=json.dumps(payload), headers=_headers)

            if r.status_code == 200:
                htmlcontent = r.content.decode('utf-8')
                try:
                    data[STRUCTURE_NUMBER].append({
                        k: (
                            v if k != "Results" else {
                                kk: vv for kk, vv in v.items() if (kk != "NBIDataQuery" or keep_query)
                            }
                        ) for k, v in json.loads(htmlcontent).items()
                     })
                except Exception as e:
                    print(f">> Error: {e}", file=sys.stderr)
                    continue

            else:
                print(f">> Error ({year}) {r.status_code}: {r.content}", file=sys.stderr)
        
        if i % 500 == 0:
            with open(f"nbi_data-{i}.json", "w") as f:
                json.dump(data, f, indent=2)

    return data


if __name__ == '__main__':
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    request_verification_token = 'CfDJ8M6CuWz5hhxGnmUVXw2yDHQlfeNDzVoF03IbAJ0p3LdaDW7poklPvy74ykYda-qwcrtUXD4rnNzn583Ug7PWbR9IlomGzQh1OQIw_pa9d5TNwdN5p77SDfIfz3yq1nWPzxemEn_8bbh7TGGK9FIwcRY' 
    cookie = "_ga=GA1.1.478241025.1718907711; _ga_0623JYSC1Q=GS1.1.1718922743.2.0.1718922743.0.0.0; _ga_VW1SFWJKBB=GS1.1.1730789269.3.0.1730789272.0.0.0; _ga_CSLL4ZEK4L=GS1.1.1730789269.3.0.1730789272.0.0.0; _ga_NQ5ZN114SB=GS1.1.1730789269.3.0.1730789272.0.0.0; .AspNetCore.Session=CfDJ8M6CuWz5hhxGnmUVXw2yDHRQxNlIdqc8pBGKOJhMcHphMelhCyOQD7cnzYLVUWcsfCE8KOO8TNogarX5FbmvNQeSW1pTphWgR%2B6RLzPiUWuR4yPiDmb6rg82isfHqoEBhFoziXpFlU2o9pMgQICLsy7WbaeZbSgOl6FTg5Y0vLQ5; __RequestVerificationToken=CfDJ8M6CuWz5hhxGnmUVXw2yDHQXNjHWpjZ61I-CMSrl0yWsdWpCyt2QhUoeZ2L2aY0sqNpGy-wrD8ToMph6-wbfcRPpqORdlVci0ghxWu-3i4PCuWsiOkq90E1WupEYErSXnhsQVwHHGcD63WI7qyXZd7w; _ga_GNYE9X3V7H=GS1.1.1730825963.2.1.1730825988.0.0.0"

    headers = {
        'authority':       'infobridge.fhwa.dot.gov',
        'origin':          'https://infobridge.fhwa.dot.gov',
        'sec-fetch-site':  'same-origin',
        'sec-fetch-mode':  'cors',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',

        '__requestverificationtoken': request_verification_token,
        'user-agent': user_agent,
        'cookie': cookie
    }

    if len(sys.argv) == 1:

        headers.update({
            'x-requested-with': 'XMLHttpRequest',
            'content-type':     'application/json; charset=UTF-8',
            'accept':           'application/json, text/javascript, */*; q=0.01',
            'referer':          'https://infobridge.fhwa.dot.gov/Data',
        })

        bridgeTable = getBridgeList(headers, start_page=511, totalpages=808, pagesize=100)
        print(json.dumps(bridgeTable, indent=2))
        sys.exit()

    elif sys.argv[1] == "-S":
        headers.update({
            'datatype':     'json',
            'content-type': 'application/json; charset=UTF-8',
            'accept':       'application/json, text/plain, */*'
        })
        bridgeTable = json.load(open(sys.argv[1]))

        # calids = list(map(str.strip, open("init/calid.txt").readlines()))
        # bridgeTable = [i for i in bridgeTable if i["STRUCTURE_NUMBER"] in calids]


        # print(json.dumps(nbi_data, indent=2))

    else:
        headers.update({
            'datatype':     'json',
            'content-type': 'application/json; charset=UTF-8',
            'accept':       'application/json, text/plain, */*'
        })
        bridgeTable = json.load(open(sys.argv[1]))

        bridgeTable = [
            i for i in bridgeTable 
            if " " in i["STRUCTURE_NUMBER"] and len(i["STRUCTURE_NUMBER"]) in {7, 8}
        ]

        # calids = list(map(str.strip, open("init/calid.txt").readlines()))
        # bridgeTable = [i for i in bridgeTable if i["STRUCTURE_NUMBER"] in calids]
        if len(sys.argv) > 3:
            bridgeTable = [
                i for i in bridgeTable 
                if i["STRUCTURE_NUMBER"] == sys.argv[3]
            ]
            if len(bridgeTable) == 0:
                print(f"Structure {sys.argv[3]} not found", file=sys.stderr)
                sys.exit(1)
        else:
            bridgeTable = [
                i for i in bridgeTable 
                if " " in i["STRUCTURE_NUMBER"] and len(i["STRUCTURE_NUMBER"]) in {7, 8}
            ]

        nbi_data = getNBIData(headers, bridgeTable[:], years=(2024,)) #range(2020, 2024))
        print(json.dumps(nbi_data, indent=2))

