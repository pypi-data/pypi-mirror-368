#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
# Chrystal Chern
#
import numpy as np
from pathlib import Path
from .utilities import getPeak, husid, read_sect_xml, get_DS

def _get_node(model, tag)->dict:
    for node in model["StructuralAnalysisModel"]["geometry"]["nodes"]:
        if node["name"] == tag:
            return node
    return {}

def _get_elem(model, tag)->dict:
    for elem in model["StructuralAnalysisModel"]["geometry"]["elements"]:
        if elem["name"] == tag:
            return elem
    return {}

def _get_bot_nodes(model,toptags, column_tags)->list:
    bot_nodes=[[tag for tag in _get_elem(model,elemtag)["nodes"] 
                if tag not in toptags][0] 
               for elemtag in column_tags]
    return bot_nodes



def peak_drift_metric(model, output_directory, config):
    VERT = 2
    nodes = [node["node"] for node in config["bents"]]
    bents = {node["node"]: node["label"] for node in config["bents"]}

    column_tags = [elem["key"] for elem in config["columns"]]
    output_directory = Path(output_directory)



    heights = np.array([
        _get_node(model,top)["crd"][VERT] - _get_node(model,bot)["crd"][VERT]
        for top, bot in zip(nodes, _get_bot_nodes(model,nodes, column_tags))
    ])
    peaksX, timePeaksX, maxPeakColX = getPeak(output_directory/"TopColDrift_X_txt.txt")
    peaksY, timePeaksY, maxPeakColY = getPeak(output_directory/"TopColDrift_Y_txt.txt")
    out =  {"column": [bents.get(n, "NA") for n in nodes],
            "peak_drf_X": (100*peaksX/np.append(heights,heights[maxPeakColX])).tolist(),
            "peak_drf_Y": (100*peaksY/np.append(heights,heights[maxPeakColY])).tolist(),
            "time_peak_X": timePeaksX.tolist(),
            "time_peak_Y": timePeaksY.tolist(),
            }

    # BUILD SUMMARY
    peaks = np.array([ out["peak_drf_X"], out["peak_drf_Y"] ])
    maxPeaks = np.max(peaks, axis=1)
    maxPeak = max(maxPeaks)
    maxPeakdir = np.argmax(maxPeak)
    maxPeakLoc = np.argmax(peaks[maxPeakdir])
    col = out["column"][maxPeakLoc]
    timesPeaks = np.array([ out["time_peak_X"], out["time_peak_Y"] ])
    timeMaxPeak = timesPeaks[maxPeakdir][maxPeakLoc]
    summary = {
        "peak": str(maxPeak),
        "units": '%',
        "col": col,
        "time": timeMaxPeak,
        "metric_completion": 50
        }
    # BUILD DETAILS
    details = [["column", *[k for k in out if k != "column"]]] + [
        [c, *[out[k][i] for k in out if k != "column"]] for i,c in enumerate(out["column"])
    ]
    return {"summary": summary, "details": details}


def peak_acceleration_metric(output_directory, config):
    nodes = [node["node"] for node in config["bents"]]
    bents = {node["node"]: node["label"] for node in config["bents"]}
    peaksX, timePeaksX, maxPeakColX = getPeak(output_directory/"TopColAccel_X_txt.txt")
    peaksY, timePeaksY, maxPeakColX = getPeak(output_directory/"TopColAccel_Y_txt.txt")
    out =  {"column": [bents.get(n, "NA") for n in nodes],
            "peak_acc_X": peaksX.tolist(),
            "peak_acc_Y": peaksY.tolist(),
            "time_peak_X": timePeaksX.tolist(),
            "time_peak_Y": timePeaksY.tolist(),
            }
    
    # BUILD SUMMARY
    peaks = np.array([ out["peak_acc_X"], out["peak_acc_Y"] ])
    maxPeaks = np.max(peaks, axis=1)
    maxPeakins2 = max(maxPeaks)
    maxPeakg = maxPeakins2*0.00259007918
    maxPeakdir = np.argmax(maxPeaks)
    maxPeakLoc = np.argmax(peaks[maxPeakdir])
    col = out["column"][maxPeakLoc]
    timesPeaks = np.array([ out["time_peak_X"], out["time_peak_Y"]])
    timeMaxPeak = timesPeaks[maxPeakdir][maxPeakLoc]
    summary = {
        "peak": str(maxPeakg),
        "units": 'g',
        "col": col,
        "time": timeMaxPeak,
        "metric_completion": 70
    }
    # BUILD DETAILS
    details = [["column", *[k for k in out if k != "column"]]] + [
        [c, *[out[k][i] for k in out if k != "column"]] for i,c in enumerate(out["column"])
    ]
    return {"summary": summary, "details": details}


def accel_response_history_plot(output_directory, config):
    nodes = [node["node"] for node in config["bents"]]
    RH = np.loadtxt(output_directory/"TopColAccel_Y_txt.txt")[:,nodes.index(403)]
    dt = 0.01
    window = husid(RH, False, dt, lb=0.005, ub=0.995)
    RH = RH[window[0]:window[1]]
    return {"accel_RH": RH}


def column_strain_state_metric(model, output_directory, config):
    elems = [int(elem["key"]) for elem in config["columns"] if elem["strain"]]
    columns = {item["key"]: item["label"] for item in config["columns"]}

    output_directory = Path(output_directory)

    strain_data = {
        file.name: read_sect_xml(file) for file in output_directory.glob("eleDef*.txt")
    }
    DSbyEle = get_DS(output_directory, model, elems, strain_data)

    keys = {
        0: "No damage",
        1: "Minor damage: flexural cracks",
        2: "Minor spalling",
        3: "Extensive cracks and spalling",
        4: "Visible reinforcing bars",
        5: "Core edge failure",
        6: "Bar fracture"
    }

    out =  {
        "col_ids": list(DSbyEle.keys()), 
        "column": np.array([columns[int(elem)] for elem in DSbyEle]),
        "ds": np.array([elem["state"] for elem in DSbyEle.values()]),
        "damage_state": np.array([keys[elem["state"]] for elem in DSbyEle.values()]),
        "time_of_ds": np.array([elem["time"]  for elem in DSbyEle.values()])
    }

    # BUILD SUMMARY
    colsMaxDS = list(np.array(out["column"])[out["ds"]==np.max(out["ds"])])
    MaxDS = list(np.array(out["damage_state"])[out["ds"]==np.max(out["ds"])])[0]
    DStimes = np.array(out["time_of_ds"])[out["ds"] == np.max(out["ds"])]
    DStimes = [t for t in DStimes if t>0.0]
    summary = {
        "max_ds": "DS"+str(max(out["ds"])),
        "col": colsMaxDS,
        "col_ids": list(np.array(out["col_ids"])[out["ds"]==np.max(out["ds"])]),
        "no_col": len(colsMaxDS),
        "ds_descr": MaxDS,
        "time": min(DStimes, default=0.0),
        "metric_completion": 15
    }
    # BUILD DETAILS
    details = [["column", "damage_state", "time_of_ds"]] + [
        [c, *[out[k][i] for k in ["damage_state", "time_of_ds"]]] for i,c in enumerate(out["column"])
    ]
    return {"summary": summary, "details": details}
