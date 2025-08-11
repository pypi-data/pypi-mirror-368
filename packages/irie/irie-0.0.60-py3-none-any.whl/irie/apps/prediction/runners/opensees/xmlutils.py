#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
import re
import warnings
import numpy as np
from collections import defaultdict
import xml.etree.ElementTree as ET

re_elem_tag = re.compile(rb'eleTag="([0-9]*)"')
re_node_tag = re.compile(rb'nodeTag="([0-9]*)"')
re_sect_num = re.compile(rb'number="([0-9]*)"')
resp_tag = re.compile(rb"<ResponseType>([A-z0-9]*)</ResponseType>")

class ParseError(Exception): pass

def getDictData(allData, curDict):
    if isinstance(curDict, (defaultdict,dict)):
        for key, item in curDict.items():
            if isinstance(item, (defaultdict,dict)):
                getDictData(allData, item)
            elif isinstance(item, int):
                curDict[key] = allData[:, item]


def read_sect_xml3(filename: str)->dict:
    data_dict = defaultdict(lambda: defaultdict(dict))
    counter = 0

    with open(filename, "rb") as f:
        # print(f.read())
        try:
            for line in f:
                if b"<ElementOutput" in line and b"/>" not in line and (elem := re_elem_tag.search(line)):
                    elem_tag = int(elem.group(1).decode())
                    while b"</ElementOutput>" not in line:
                        line = next(f)
                        if b"<GaussPointOutput" in line:
                            sect = re_sect_num.search(line).group(1).decode()

                        elif b"<ResponseType" in line:
                            r_label =  resp_tag.search(line).group(1).decode()
                            while r_label in data_dict[elem_tag][sect]:
                                r_label += "_"
                            data_dict[elem_tag][sect][r_label] = counter
                            counter += 1


                elif b"<Data>" in line:
                    lines = f.read()
                    lines = lines[:lines.find(b"</Data>")].split()
                    data = np.fromiter(lines, dtype=np.float64, count=len(lines))
        except StopIteration:
            raise ParseError(f"Failed to find end tag in XML file {filename}")

    getDictData(data.reshape((-1, counter)), data_dict)
    return data_dict

def read_sect_xml1(xml_file):
    root = ET.parse(xml_file).getroot()

    dataDict = {}
    colCtr = 0

    # time_output = root.find("TimeOutput")
    # if time_output:
    #     hdrs.append(child[0].text)
    #     dataDict[child[0].text] = colCtr
    #     colCtr += 1

    elems = root.findall("ElementOutput")
    for child in elems:

        eleKey = child.attrib["eleTag"]
        secKey = child[0].attrib["number"]

        dataDict[eleKey] = {secKey: {}}

        for respCtr in range(len(child[0][0])):
            respKey = child[0][0][respCtr].text
            if respKey in dataDict[eleKey][secKey].keys():
                respKey = respKey + "_"
            dataDict[eleKey][secKey][respKey] = colCtr
            colCtr += 1
                
    data_element = root.find("Data")
    data = np.array(data_element.text.split(), dtype=float)
    getDictData(data.reshape((-1, colCtr)), dataDict)
    return dataDict

def read_sect_xml2(xml_file):
    root = ET.parse(xml_file).getroot()

    dataDict = {}
    colCtr = 0

    # time_output = root.find("TimeOutput")
    # if time_output:
    #     hdrs.append(child[0].text)
    #     dataDict[child[0].text] = colCtr
    #     colCtr += 1

    elems = root.findall("ElementOutput")
    for child in elems:

        eleKey = child.attrib["eleTag"]
        secKey = child[0].attrib["number"]

        dataDict[eleKey] = {secKey: {}}

        for respCtr in range(len(child[0][0])):
            respKey = child[0][0][respCtr].text
            if respKey in dataDict[eleKey][secKey].keys():
                respKey = respKey + "_"
            dataDict[eleKey][secKey][respKey] = colCtr
            colCtr += 1
                
    data_element = root.find("Data")
    data = np.fromiter(
        (i for text in data_element.itertext() for i in text.split()), dtype=float,
    ).reshape((-1, colCtr))
    getDictData(data, dataDict)
    return dataDict

def read_sect_xml0(xml_file):
    "Arpit Nema"
    root = ET.parse(xml_file).getroot()

    hdrs = []
    dataDict = {}
    colCtr = 0
    for i, child in enumerate(root):
        if child.tag == "TimeOutput":
            hdrs.append(child[0].text)
            dataDict[child[0].text] = colCtr
            colCtr += 1
        elif child.tag == "ElementOutput":
            eleKey = child.attrib["eleTag"]
            secKey = child[0].attrib["number"]
            hdrPre = eleKey + "_" + secKey + "_" + child[0][0].attrib["secTag"]

            dataDict[eleKey] = {secKey: {}}
            for respCtr in range(len(child[0][0])):
                hdrs.append(hdrPre + "_" + child[0][0][respCtr].text)
                respKey = child[0][0][respCtr].text
                if respKey in dataDict[eleKey][secKey].keys():
                    respKey = respKey + "_"
                dataDict[eleKey][secKey][respKey] = colCtr
                colCtr += 1
        elif child.tag == "Data":
            tmp = child.text

    data = np.array(tmp.replace("\n", "").split(), dtype=float)
    
    data = data.reshape((-1, len(hdrs)))
    getDictData(data, dataDict)
    return dataDict



def read_nodeRH_xml(filename: str)->dict:
    data_dict = defaultdict(lambda: defaultdict(dict))
    counter = 0

    with open(filename, "rb") as f:
        try:
            for line in f:
                if b"<NodeOutput" in line and (node := re_node_tag.search(line)):
                    node_tag = int(node.group(1).decode())

                elif b"<Data>" in line:
                    lines = f.read()
                    lines = lines[:lines.find(b"</Data>")].split()
                    data = np.fromiter(lines, dtype=np.float64, count=len(lines))
        except StopIteration:
            raise ParseError(f"Failed to find end tag in XML file {filename}")

    getDictData(data.reshape((-1, counter)), data_dict)
    return data_dict


def read_xml(xml_file):
    root = ET.parse(xml_file).getroot()

    dataDict = {}
    colCtr = 0

    # time_output = root.find("TimeOutput")
    # if time_output:
    #     hdrs.append(child[0].text)
    #     dataDict[child[0].text] = colCtr
    #     colCtr += 1

    for child in root.findall("ElementOutput"):

        eleKey = child.attrib["eleTag"]
        try:
            secKey = child[0].attrib["number"]
        except IndexError:
            warnings.warn(f"Skipping element '{eleKey}'")
            continue

        dataDict[eleKey] = {secKey: {}}

        for respCtr in range(len(child[0][0])):
            respKey = child[0][0][respCtr].text
            if respKey in dataDict[eleKey][secKey].keys():
                respKey = respKey + "_"
            dataDict[eleKey][secKey][respKey] = colCtr
            colCtr += 1

    for child in root.findall("NodeOutput"):

        tag = int(child.attrib["nodeTag"])

        dataDict[tag] = {}

        for resp in child.findall("ResponseType"):
            respKey = resp.text
            if respKey in dataDict[tag].keys():
                respKey = respKey + "_"
            dataDict[tag][respKey] = colCtr
            colCtr += 1

    data_element = root.find("Data")
    data = np.array(data_element.text.split(), dtype=float)
    getDictData(data.reshape((-1, colCtr)), dataDict)
    return dataDict

