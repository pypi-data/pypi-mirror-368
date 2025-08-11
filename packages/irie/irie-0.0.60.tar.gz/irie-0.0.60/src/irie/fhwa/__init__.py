#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
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


def fetch_structure(structure: str, 
                    year_id: str, 
                    headers,
                    year=2024,
                    keep_query=False):

    url = 'https://infobridge.fhwa.dot.gov/Data/getBridgeInformation'

    _headers = headers.copy()
    # payload = {
    #     "requestModel": {
    #         "SELECTED_YEAR_ID": None,
    #         "IS_NEW_RECORD": True,
    #         "Is_Overview_Bridge_Selected": False,
    #         "IS_NBI_TREE_SELECTED": False,
    #         "tabChange": False,
    #         "NEW_BRIDGE_ID": 58813,
    #     }
    # }

    payload  = {
      "requestModel":{
        "SELECTED_TAB": "NBITab", # "OverviewTab", "NBETab"
        "SELECTED_YEAR_ID": None, 
        "IS_NEW_RECORD": False,
        "IS_YEAR_SELECTED": False, 
    #   "SELECTED_YEAR": None,
        "Is_Overview_Bridge_Selected": False,
        "NEW_BRIDGE_ID": 0, 
        "STRUCTURE_NUMBER": None, 
        "STATE_NAME":       None,
        "STATE_CODE":       0,    
        "IS_EXPERIMENTAL":  False, 
        "SELECTED_NDE_TAB": "General",
       # "MERRA_ID": 0,
       # "IS_NBI_TREE_SELECTED": False,
       # "Folder_Name": None,
       # "tabChange": False,
      }
    }


    referer = 'https://infobridge.fhwa.dot.gov/Data/BridgeDetail/'


    BRIDGE_YEARLY_ID = year_id
    STRUCTURE_NUMBER = structure


    _headers['referer'] = referer + str(BRIDGE_YEARLY_ID)

    payload["requestModel"].update({
            "SELECTED_YEAR":     year,
            "CURRENT_YEARLY_ID": str(BRIDGE_YEARLY_ID),
            "BRIDGE_YEARLY_ID":  str(BRIDGE_YEARLY_ID),
    })

    r = requests.post(url, data=json.dumps(payload), headers=_headers)

    if r.status_code == 200:
        htmlcontent = r.content.decode('utf-8')
        return {
            k: (
                v if k != "Results" else {
                    kk: vv for kk, vv in v.items() if (kk != "NBIDataQuery" or keep_query)
                }
            ) for k, v in json.loads(htmlcontent).items()
        }

    else:
        raise Exception(f"Failed to get data for {STRUCTURE_NUMBER}")

