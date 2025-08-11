#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
import json
import fnmatch
import numpy as np

from math import pi
from collections import defaultdict
import quakeio

try:
    from xmlutils import read_sect_xml3 as read_sect_xml
    from xmlutils import read_xml
except ImportError:
    from .xmlutils import read_sect_xml3 as read_sect_xml
    from .xmlutils import read_xml

def read_model(filename:str)->dict:
    with open(filename, "r") as f:
        model = json.load(f)
    sam = model["StructuralAnalysisModel"]
    model["sections"] = {
        int(s["name"]): s for s in sam["properties"]["sections"]
    }
    model["materials"] = {
        int(m["name"]): m for m in sam["properties"]["uniaxialMaterials"]
    }
    model["elements"] = {
#       int(el["name"]): el for el in sam["geometry"]["elements"]
        int(el["name"]): {**el, "length": None} for el in sam["geometry"]["elements"]
    }
    return model

# --8<--------------------------------------------------------

def damage_states(Dcol):
    from opensees import section
    from opensees.section import patch

    cover = 2.0
    Rcol = Dcol/2
    coverl = cover + Rcol*(1/np.cos(np.pi/8)-1)
    return {
        "dsr0": {
            "regions": [
                # external radius    internal radius
                section.PolygonRing(8, Rcol, Rcol-coverl/4)
            ],
            "material": "*concr*"
        },
        "dsr1": {
            "regions": [
                section.FiberSection(areas=[
                    patch.circ(intRad=Rcol - cover - 2, extRad=Rcol - cover)
                ])
            ],
            "material": "*steel*"
        },
        "dsr2" : {
            "regions": [
                section.PolygonRing(8, Rcol,         Rcol-coverl/4)
            ]
        },
        "dsr3" : {
            "regions": [
                section.PolygonRing(8, Rcol-cover/2, Rcol-3*cover/4)
            ],
            "material": "*concr*"
        },
        "dsr4" : {
            "regions": [
                section.PolygonRing(8, Rcol-3*coverl/4, Rcol-coverl)
            ],
            "material": "*concr*"
        },
        "dsr5": {
            "regions": [
                section.FiberSection(areas=[
                    patch.circ(intRad=Rcol - cover - 2, extRad=Rcol - cover)
                ])
            ],
            "material": "*concr*"
        },
        "dsr6": {
            "regions": [
                section.FiberSection(areas=[
                    patch.circ(intRad=Rcol - cover - 2, extRad=Rcol - cover)
                ])
            ],
            "material": "*steel*"
        },
        "all": {
            "regions": [
                section.ConfinedPolygon(8, Rcol)
            ]
        }
    }

# --8<--------------------------------------------------------

def iter_section_fibers(model, s, filt=None, match=None):
    # if match is None:
    #     test = lambda a, b: a == b 
    # elif match == "pattern":
    #     pass
    if filt is not None:
        if "material" not in filt:
            filt["material"] = "*"
        for fiber in s["fibers"]:
            # print(fnmatch.fnmatch(
            #         model["materials"][fiber["material"]]["type"].lower(),
            #         filt["material"]
            #     ))
            # print([fiber["coord"] in region for region in filt["regions"]])
            if (
                ("material" not in filt) or fnmatch.fnmatch(
                    model["materials"][fiber["material"]]["type"].lower(),
                    filt["material"]
                )
            ) and any(
                fiber["coord"] in region for region in filt["regions"]
            ) :
                yield fiber
    else:
        yield from s["fibers"]


def iter_elem_fibers(model:dict, elements:list, sections: list=(0,-1), filt:dict=None):
    for tag in map(int,elements):
        el = model["elements"][int(tag)]
        for i in sections:
            idx = len(el["sections"]) - 1 if i==-1 else i
            tag = int(el["sections"][idx])
            s = model["sections"][tag]
            if "section" in s:
                s = model["sections"][int(s["section"])]
                for f in iter_section_fibers(model, s, filt):
                    yield el,idx+1,f

def fiber_strain(recorder_data, el, s, f, t=None):
    if t is not None:
        eps = recorder_data[int(el)][int(s)]["eps"][t]
        kz =  recorder_data[int(el)][int(s)]["kappaZ"][t]
        ky =  recorder_data[int(el)][int(s)]["kappaY"][t]
    else:
        eps = recorder_data[int(el)][int(s)]["eps"]
        kz =  recorder_data[int(el)][int(s)]["kappaZ"]
        ky =  recorder_data[int(el)][int(s)]["kappaY"]

    return eps - kz * f["coord"][1] + ky * f["coord"][0]


REGIONS1 = damage_states(84.0)
REGIONS2 = damage_states(66.0)
REGIONS3 = damage_states(48.0)

def getDamageStateStrains(a, dsr, model, elems, strain_data=None):
    if strain_data is None:
        strain_data = {}

    intFrames = 1

    epsEle = []
    for ele in elems:
        # TODO!!!!!
        if ele < 12000:
            regions = REGIONS1
        elif ele < 13000:
            regions = REGIONS2
        else:
            regions = REGIONS3

        # TODO!!!!!!!!!!!
        if np.isin(ele, [2010, 2020, 12010, 12020, 12030, 13010, 13020, 14010, 14020, 14030]):
            sec = 4
        else:
            sec = 1

        data_file = f"eleDef{sec}.txt"
        if data_file in strain_data:
            strains = strain_data[data_file]
        else:
            strains = strain_data[data_file] = read_sect_xml(a/f"{data_file}")

        # print(list(iter_elem_fibers(model, [ele], [int(sec)-1], filt=regions["dsr1"])))

        X,Y,epsRaw = zip(*(
                (
                    fib["coord"][0], fib["coord"][1],
                    fiber_strain(strains, int(e["name"]), s, fib)
                ) for ds in dsr
            for e,s,fib in iter_elem_fibers(model, [ele], [int(sec)-1], filt=regions[ds])
        ))

        eps = np.array([e.T for e in epsRaw])
        epsElei = X, Y, eps, intFrames, np.arange(eps.shape[1])
        epsEle.append(epsElei)
    return epsEle

def get_DS(a, model, elems, strain_data):
    dsrs = list(map(lambda x: f"dsr{x}", range(1,7)))
    thresholds = list(reversed([0.09, -0.011, -0.005, -0.005, -0.005, 0.002]))
    ds_by_elem = {el: {"state": 0, "time": np.nan} for el in elems}
    for i in range(len(dsrs)):
        dsr = dsrs[i]
        th = thresholds[i]
        epsEle = getDamageStateStrains(a, [dsr], model, elems, strain_data)
        for j in range(len(elems)):
            X, Y, eps = epsEle[j][:3]

            for t in range(eps.shape[1]):
                epst = eps[:, t]
                if (th < 0 and any(epst <= th)) or (th > 0 and any(epst >= th)):
                    ds_by_elem[elems[j]] = {"state": i+1, "time": t}
                    break
    return ds_by_elem


def getPeakXML(file, filter="*"):
    nodeOutputs = read_xml(file)
    return {
        node:
            {resp: max(abs(nodeOutputs[node][resp])) for resp in nodeOutputs[node]} 
            for node in nodeOutputs
    }

def getPeak(file, other=None):
    nodeOutputs = np.loadtxt(file)
    peakVals = np.max(np.abs(nodeOutputs), axis=0)
    peakVals = np.append(peakVals, max(peakVals))
    timePeakVals = np.argmax(np.abs(nodeOutputs), axis=0)
    maxPeakCol = np.argmax(peakVals)
    timePeakVals = np.append(timePeakVals, timePeakVals[maxPeakCol])
    return peakVals, timePeakVals, maxPeakCol

def husid(accRH, plothusid, dt, lb=0.05, ub=0.95):
    from matplotlib import pyplot as plt
    ai = np.tril(np.ones(len(accRH)))@accRH**2
    husid = ai/ai[-1]
    ilb = next(x for x, val in enumerate(husid) if val > lb)
    iub = next(x for x, val in enumerate(husid) if val > ub)
    if plothusid:
        fig, ax = plt.subplots()
        if dt is not None:
            print("duration between ", f"{100*lb}%", " and ", f"{100*ub}%", " (s): ", dt*(iub-ilb))
            ax.plot(dt*np.arange(len(accRH)), husid)
            ax.set_xlabel("time (s)")
        else:
            ax.plot(np.arange(len(accRH)), husid)
            ax.set_xlabel("timestep")
        ax.axhline(husid[ilb], linestyle=":", label=f"{100*lb}%")
        ax.axhline(husid[iub], linestyle="--", label=f"{100*ub}%")
        ax.set_title("Husid Plot")
        ax.legend()
    return (ilb, iub)

def get_node_values(filename, channels, quant=None):
    if quant is None:
        quant = "accel"

    event = quakeio.read(filename)
    rotated = set()

    nodes = defaultdict(dict)
    for nm,ch in channels.items():
        channel = event.match("l", station_channel=nm)
        if id(channel._parent) not in rotated:
            channel._parent.rotate(ch[2])
            rotated.add(id(channel._parent))
        series = getattr(channel, quant).data
        nodes[ch[0]][ch[1]] = series

    return nodes

