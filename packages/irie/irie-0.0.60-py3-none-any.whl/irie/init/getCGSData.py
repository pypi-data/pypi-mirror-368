#!/usr/bin/env python
#  ____  _____          _____ ______ ___
# |  _ \|  __ \   /\   / ____|  ____|__ \
# | |_) | |__) | /  \ | |    | |__     ) |
# |  _ <|  _  / / /\ \| |    |  __|   / /
# | |_) | | \ \/ ____ \ |____| |____ / /_
# |____/|_|  \_\/    \_\_____|______|____|
#
# claudio perez
"""
This script takes an HTML page, extracts its tables, and prints
a JSON representation of the data.

Example:
$ pandoc ../el-centro/documentation/summary-table.md 2>/dev/null | python html2json.py
"""
import sys
import json
import requests
from bs4 import BeautifulSoup # install package 'beautifulsoup4'

# from elstir.contrib.pandoc import Pandoc

def cesmd_bridges():
    url = "https://www.strongmotioncenter.org/wserv/stations/query?sttype=Br&format=json&nodata=404"
    return requests.get(url).text

def pull_csmip(csmip_id:str)->str:
    return requests.get(
            f"https://www.strongmotioncenter.org/cgi-bin/CESMD/stationhtml.pl?stationID={csmip_id}&network=CGS"
           ).text


def dict2latex(data:dict, i=0)->str:
    """
    take a dictionary and return a string defining a LaTeX table.
    """

    head = f"""
\\begin{{table}}[!htbp]
    \\centering
    \\begin{{tabular}}{{|p{{35mm}}|p{{8cm}}|}} \\hline
"""
    body = "\n    ".join([f"{k} & {v}\\\\ \\hline" for k,v in data.items()])
    tail = f"""
    \\end{{tabular}}
    \\label{{tab:num-{i}}}
\\end{{table}}
\\vspace*{{2cm}}
"""
    return head + "    " + body + tail

def table2dict(html_table, output=None)->dict:
    """
    This function takes HTML tables with rows of the form:

        <tr>
          <td>key1</td> <td>value1</td>
        </tr>
    """
    output = {} if output is None else output
    tree = html_table
    tables = tree.find_all("table")

    if tables:
        # the tree has multiple tables, recurse
        table_dicts = [table2dict(table) for table in tables if table]
        return [table for table in table_dicts if table]

    else:
        table = tree

        for row in table.find_all("tr"):
            header = row.find("th")
            if header:
                output.update({"headers": header.text.split()})

            data = row.find_all("td")
            if "Photograph" in data[0].text:
                continue
            elif data[0].text == "" and len(data) > 1:
                print(data[1].find("img").attrs["src"], file=sys.stderr)
                continue
            elif len(data) > 1 and data[1].text == "\u00a0":
                continue

            try:
                output.update({data[0].text: data[1].text})
            except:
                pass

        return output


if __name__=="__main__":
    import sys

    if len(sys.argv) == 1:
        print(cesmd_bridges())


    dat = {}
    for cesmd in sys.argv[1:]:
        html = pull_csmip(cesmd)
        dat.update({cesmd: table2dict(BeautifulSoup(html, "html.parser"))})

    print(json.dumps(dat, indent=4))


