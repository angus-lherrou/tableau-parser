import os
import argparse
import difflib
from collections import defaultdict
from typing import List

OUTPUT_PATH = "tableau.html"

def generate(file):
    lines: List[str]
    with open(file) as f:
        lines = [line for line in f]
    html = ["<table>", "</table>"]
    tableau_format = ""
    for i,j in enumerate(difflib.ndiff(lines[0], "\\begin{tableau}{}")):
        if j[0] == '-':
            tableau_format += j[2]
    terms = []
    for line in lines:
        terms.extend(line.split("\\")[1:])
    inp = [get_content_from_braces(term) for term in terms if term.__contains__("inp")][0]
    constraints = [get_content_from_braces(term) for term in terms if term.__contains__("const")]
    html.insert(-1, "<tr>")
    html.insert(-1, "<th class='input'>"+inp+"</th>")
    for const in constraints:
        html.insert(-1, "<th class='constraint'>"+const+"</th>")
    html.insert(-1, "</tr>")
    candidates = [get_content_from_braces(term) for term in terms if term.__contains__("cand")]
    viol_dict = defaultdict(list)
    viols = [get_content_from_braces(term) for term in terms if term.__contains__("vio")]
    span = 0
    for cand in candidates:
        viol_dict[cand].extend(viols[span : span+len(constraints)])
        span += len(constraints)
    for candidate in candidates:
        html.insert(-1, "<tr>")
        html.insert(-1, "<td class='candidate'>"+candidate+"</td>")
        for viol in viol_dict[candidate]:
            html.insert(-1, "<td class='vio'>"+viol+"</td>")
        html.insert(-1, "</tr>")

    return "".join(html)


def get_content_from_braces(string: str):
    brace1 = string.index('{')
    brace2 = string.index('}')
    return string[brace1+1:brace2]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store')
    args = parser.parse_args()

    path: str
    output: str
    if args.generate:
        path = args.generate
        if os.path.isfile(path):
            if os.path.exists(OUTPUT_PATH):
                print("Warning: this will overwrite an existing file. ENTER to continue or SIGINT to cancel.")
                input()
            with open(OUTPUT_PATH, "w") as out:
                out.write(generate(path))
        else:
            print("Not a file!")
    else:
        print("Please run with --generate /path/to/file")