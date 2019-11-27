"""
tableau-parser
    v. 0.1.1

Author: Angus L'Herrou
Date: 2019-11-26
"""

import os
import argparse
import difflib
from collections import defaultdict
from typing import List
from html5print import HTMLBeautifier

CHAR_DICT = {r"\Optimal": "&#9758;", r"\HandRight": "&#9758;", r"\HandLeft": "&#9756;"}
CSS = """
    table, th, tr, td.outer {
        border-collapse: collapse;
        padding: 0;
    }
    table {
        border: 1px solid black;
    }
    th, td {
        border-collapse: collapse;
        padding: 2px 10px;
    }
    table.outer {
        border: none;
        border-collapse: separate;
        padding: 0;
    }
    .constraint, .vio {
        text-align: center;
        border-bottom: 1px solid black;
        border-right: 1px solid black;
        border-left: none;
    }
    .input, .candidate {
        text-align: left;
    }
    .indicator {
        border: none;
        text-align: right;
        height: 2px;
        width: 2px;
        display:block;
        vertical-align: middle;
        horizontal-align: right;
    }
    .candidate {
        border-top: 1px solid black;
        border-bottom: 1px solid black;
    }
    .noshow {
        visibility: collapse;
    }
    .unranked {
        border-right: 1px dashed black;
    }
    """


def generate(file):
    """
    Method to generate the HTML given an ot-tableau tableau.
    :param file: a text file containing only the text of the tableau
    :return: the HTML as a string, prettified with html5print
    """
    lines: List[str]
    with open(file) as f:
        lines = [line for line in f]
    terms = get_commands(lines)

    inp = [get_args_from_command(term)[1] for term in terms if term.__contains__("inp")][0]
    constraints = [get_args_from_command(term)[1] for term in terms if term.__contains__("const")]
    candidates = [get_args_from_command(term) for term in terms if term.__contains__("cand")]
    viols = [get_args_from_command(term)[1] for term in terms if term.__contains__("vio")]

    viol_dict = defaultdict(list)
    span = 0
    for cand in candidates:
        viol_dict[cand[1]].extend(viols[span:span + len(constraints)])
        span += len(constraints)

    html = ["<!DOCTYPE html><meta charset='UTF8'><html lang='en'><head><style>", CSS, "</style>",
            "<title></title>", "</head><body><table class='outer'>", "</table></body></html>"]

    tableau_format = ""
    for i, j in enumerate(difflib.ndiff(lines[0], "\\begin{tableau}{}")):
        if j[0] == '-':
            tableau_format += j[2]

    ranking_info = tableau_format.split('c')[1:]

    html.insert(-1, "<tr><td class='outer'><table class='in'><thead><tr>")
    html.insert(-1, "<th class='input' colspan='2'>"+inp+"</th>")
    html.insert(-1, "</tr></thead><tbody class='noshow'>")

    candidate_column = ""
    for candidate in candidates:
        candidate_column += "<tr class='candidate'>"
        candidate_column += "<td class='indicator'>"
        if candidate[0]:
            to_insert = CHAR_DICT[candidate[0]] if CHAR_DICT[candidate[0]] else "ERR"
            candidate_column += to_insert
        candidate_column += "</td>"
        candidate_column += "<td class='candidate'>"+candidate[1]+"</td>"
        candidate_column += "</tr>"
    html.insert(-1, candidate_column)
    html.insert(-1, "</tbody></table></td>")
    html.insert(-1, "<td class='outer'><table class='const'><tr>")

    constraint_row = ""
    for i in range(len(constraints)):
        if ranking_info[i] == ':':
            constraint_row += "<th class='constraint unranked'>"+constraints[i]+"</th>"
        else:
            constraint_row += "<th class='constraint'>" + constraints[i] + "</th>"

    html.insert(-1, constraint_row)
    html.insert(-1, "</tr></table></td></tr>")

    html.insert(-1, "<tr><td class='outer'><table class='cand'>" + "<tr class='noshow'></tr>" + candidate_column)
    html.insert(-1, "</table></td>")
    html.insert(-1, "<td class='outer'><table class='viol'><tr class='noshow'>")
    html.insert(-1, constraint_row)
    html.insert(-1, "</tr>")

    for candidate in candidates:
        html.insert(-1, "<tr>")
        for i in range(len(viol_dict[candidate[1]])):
            if ranking_info[i] == ':':
                html.insert(-1, "<td class='vio unranked'>"+viol_dict[candidate[1]][i]+"</td>")
            else:
                html.insert(-1, "<td class='vio'>"+viol_dict[candidate[1]][i]+"</td>")
        html.insert(-1, "</tr>")

    html.insert(-1, "</table></td></tr>")
    return HTMLBeautifier.beautify("".join(html), 4)


def get_args_from_command(string: str):
    """
    Method to extract the arguments from a LaTeX command
    with one argument and up to one optional argument.
    :param string: the command
    :return: a list of length 2 with the optional argument (or None)
             in position 0 and the main argument in position 1
    """
    lbrace = string.find('{')
    rbrace = string.rfind('}')
    lbracket = string.find('[') if string.__contains__('[') else None
    rbracket = string.find(']') if string.__contains__(']') else None
    return [string[lbracket + 1:rbracket] if lbracket and rbracket else None, string[lbrace + 1:rbrace]]


def get_commands(lines):
    """
    Method to get all the LaTeX commands from a list of lines.
    Only collects outermost commands if there are commands nested in arguments.
    :param lines: the list of lines
    :return: a list of commands
    """
    terms = []
    for line in lines:
        terms.extend(line.split("\\")[1:])
    mark_for_del = defaultdict(bool)
    for i in range(0, len(terms)).__reversed__():
        if terms[i][-1] in {'[', '{'}:
            terms[i] += "\\" + terms[i+1]
            mark_for_del[i+1] = True
    for idx in mark_for_del.keys():
        if mark_for_del[idx]:
            terms.pop(idx)
    return terms


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', type=str, action='store', help='generate HTML from ot-tableau code at /path/to/file')
    parser.add_argument('-n', '--name', action='store', help="choose a custom filepath for the generated HTML file "
                                                             "(default is 'tableau.html')")
    args = parser.parse_args()

    output_path = "tableau.html"
    path: str
    output: str
    if args.name:
        output_path = args.name
    if args.filepath:
        path = args.filepath
        if os.path.isfile(path):
            overwrite = "y"
            if os.path.exists(output_path):
                overwrite = " "
                while overwrite[0].lower() not in 'yn':
                    user_input = input("Warning: this will overwrite an existing file. "
                                       "Overwrite? (y/N) ")
                    overwrite = user_input if user_input else 'n'
            if overwrite[0].lower() == 'y':
                with open(output_path, "w") as out:
                    out.write(generate(path))
                    print("File generated at " + output_path + ".")
            else:
                print("Operation cancelled. File at "+output_path+" was not overwritten.")
        else:
            print("Not a file!")
    else:
        print("Please run with an argument: /path/to/file")
