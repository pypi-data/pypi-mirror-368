#!/usr/bin/env python

import json
import pathlib
import random
import time
from concurrent.futures import ThreadPoolExecutor

import requests


def get(number):
    URL = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/element/{number}/JSON/"

    for _ in range(5):
        data = requests.get(URL).json()
        if "Record" in data:
            # usually because server complains about too many connections at same time
            return data
        print("sleep")
        time.sleep(1.0)

    else:
        return None
        return (number, None, None, None, None)


def fetch(number):
    data = get(number)
    if data is None:
        return (number, None, None, None, None)

    for section in data["Record"]["Section"]:
        if section["TOCHeading"] == "Isotope Mass and Abundance":
            break

    for s in section["Section"]:
        if s["TOCHeading"] == "Isotope Mass and Abundance":
            break

    isotopes = masses = abundances = None

    for information in s["Information"]:
        name = information["Name"]
        if name == "Isotope":
            isotopes = [
                i["String"].strip() for i in information["Value"]["StringWithMarkup"]
            ]
        if name.startswith("Atomic Mass"):
            masses = [
                i["String"].strip() for i in information["Value"]["StringWithMarkup"]
            ]
        if name.startswith("Abundance"):
            abundances = [
                i["String"].strip() for i in information["Value"]["StringWithMarkup"]
            ]

    name = data["Record"]["RecordTitle"]
    print(number, name)

    time.sleep(0.5 + random.random() * 0.3)
    return (number, name, isotopes, masses, abundances)


def main():
    with ThreadPoolExecutor(10) as p:
        results = list(p.map(fetch, range(1, 110)))

    here = pathlib.Path(__file__).parent

    (here / "elements_pubchem.json").write_text(json.dumps(results, indent=4))


if __name__ == "__main__":
    started = time.time()
    main()
    needed = time.time() - started
    print()
    print(f"download needed {needed:.0f} seconds")
