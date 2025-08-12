"""
Main script for estimating atom counts in supported nanoparticles.

Functions
---------
parse_input_data(input_file: str) -> tuple
    Reads the input CSV or XLXS
main:
    run all calculations
"""

import ast
from typing import Tuple, List, Literal
from sys import argv, exit
import numpy as np
import warnings
from NanoparticleAtomCounter.by_volume import calculate_by_volume
from NanoparticleAtomCounter.by_area import calculate_by_area
import pandas as pd
from numpy.typing import NDArray
from os import path
from collections import Counter
import argparse
from time import perf_counter


MODE = "volume"
OUTPUT = "output_atomcounts.csv"


def parse_input_data(
    input_file: str,
) -> Tuple[NDArray, NDArray, NDArray, NDArray, NDArray, NDArray]:
    """
    Reads the input csv or xlxs

    Expected format of the file:
        FIRST ROW ->        r (A),R (A),Theta,Element,Facet
        FOLLOWING ROWS:     a,b,c,d,[x,y,z]

    r:          Footprint (or contact) radius in Angstrom, e.g. 9.1
    R:          Radius of curvature in Angstrom, e.g. 17.12
    Theta:      Contact Angle, e.g. 80
    Element:    Element the Nanoparticle is composed of, e.g. Ag
    Interface Facet:    Facet at the nanoparticle-support interface, given as a tuple, e.g. (1, 1, 1)
    Surface Facet:      Dominant facet at the nanoparticle-gas interface, also as a tuple

    Mandatory:
        1. Theta
        2. r or R. If user supplies both, we choose r and ignore R
        3. Element

    Optional but recommended:
        Interface Facet and Surface Facet
        if not provided, will assume defaults;
        see count_utilities.calculate_constants for the defaults
    """

    ext = path.splitext(input_file)[1].lower()
    if ext in (".csv",):
        df = pd.read_csv(input_file, delimiter=",")
    elif ext in (".xls", ".xlsx"):
        with pd.ExcelFile(input_file) as xls:
            if not xls.sheet_names:
                raise ValueError(
                    f"""
                    '{input_file}' looks like an Excel container but
                    has no worksheets. Is it really an .xlsx file?
                    """
                )
            df = xls.parse(
                sheet_name=xls.sheet_names[0]
            )  # assuming the data is in the first sheet
    #        df = pd.read_excel(input_file, sheet_name = 0) #assuming the data is in the first sheet
    else:
        raise ValueError(
            f"""
        Unrecognized file type: {ext}!
                Requires .csv, .xls, or .xlsx
                """
        )  # first: pip install xlrd openpyxl

    # verify that the cols are labelled properly so we get the correct data
    df.columns = (
        df.columns.str.strip()
    )  # remove leading/trailing spaces. no unifying case or R will become r
    expected = [
        "r (A)",
        "R (A)",
        "Theta",
        "Element",
        "Interface Facet",
        "Surface Facet",
    ]
    # compare as multisets to check both presence *and* counts
    assert Counter(df.columns) == Counter(expected), (
        f"Column mismatch:\n"
        f"  found    = {df.columns.tolist()}\n"
        f"  expected = {expected}"
    )

    rs = df["r (A)"].to_numpy()  # np.nan if no values
    Rs = df["R (A)"].to_numpy()  # np.nan if no values
    thetas = df["Theta"].to_numpy()
    elements = df["Element"].to_numpy()
    interface_facets = (
        df["Interface Facet"]
        .apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [None] * 3)
        .to_numpy()
    )  # None if no values
    surface_facets = (
        df["Surface Facet"]
        .apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [None] * 3)
        .to_numpy()
    )  # None if no values

    return rs, Rs, thetas, elements, interface_facets, surface_facets


def main() -> None:
    f"""
    Main function to do all calculations through the selected method

    Requires:
        input_file (str):                   input file name, with full path
        output_file (str):                   output file name, with full path. default = 'output.txt'
        mode (Literal["volume", "area"])    whether to calculate by volume or area. Default = 'volume'


    Returns:
        NONE, but writes out the output file
    """
    parser = argparse.ArgumentParser(
        description="""Given an input file containing:
     (1) NP element type
     (2) footprint radius or radius of curvature
     (3) contact angle,
     (4) (optionally) interface facet
     (5) (optionally) surface facet

    calculates number of surface, perimeter, interfacial, and total atoms"""
    )

    parser.add_argument(
        "--input", "-i", type=str, required=True, help="Path to input file"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=OUTPUT,
        help=f"Path to output file. default = {OUTPUT}",
    )

    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        default=MODE,
        help=f"""Method for calculating: by area ("area") or by volume ("volume").
            default = 'volume' """,
        choices=("volume", "area"),
    )

    start = perf_counter()
    args = parser.parse_args()
    input_file = args.input
    output_file = args.output
    mode = args.mode.lower()

    rs, Rs, thetas, elements, interface_facets, surface_facets = parse_input_data(
        input_file
    )

    if np.all(np.isnan(rs)) or np.all(
        rs == 0
    ):  # if rs is empty or 0, convert Rs into rs
        print("converting r into R...")
        rs = Rs * np.sin(np.radians(thetas))
    elif np.any(np.isnan(rs)):  # if there is any rs value missing, exit
        raise ValueError(f"Some entries for r (A) are missing!")

    # in case some variables have more entries than others
    data = {
        "rs": rs,
        "Rs": Rs,
        "thetas": thetas,
        "elements": elements,
        "interface_facets": interface_facets,
        "surface_facets": surface_facets,
    }

    lengths = {name: len(arr) for name, arr in data.items()}
    unique_lengths = set(lengths.values())

    if len(unique_lengths) > 1:
        warnings.warn(
            f"Inconsistent data lengths: {lengths}. "
            f"Truncating all to the shortest ({min(unique_lengths)})",
            category=UserWarning,
        )

    min_len = min(unique_lengths)  # truncate everything to the same (minimum) length
    for name in data:
        data[name] = data[name][:min_len]

    mode_ = {
        "volume": calculate_by_volume,
        "area": calculate_by_area,
    }

    peri_atoms, inter_atoms, surf_atoms, tot_atoms = zip(
        *[
            mode_[mode](
                element=data["elements"][i],
                footprint_radius=data["rs"][i],
                theta=data["thetas"][i],
                interface_facet=tuple(data["interface_facets"][i]),
                surface_facet=tuple(data["surface_facets"][i]),
                # to be able to cache in calculate_constants(), facets must be immutable (i.e. tuple rather than list)
                # just in case the user had given as [x, y, z] rather than (x, y, z)
                # so, I am converting to a tuple
            )
            for i in range(min_len)
        ]
    )

    print("Success!")

    df = pd.DataFrame(
        {
            "Perimeter": peri_atoms,
            "Interface": inter_atoms,
            "Surface": surf_atoms,
            "Total": tot_atoms,
        }
    )

    df.to_csv(output_file, index=False)
    print(f"Output ({output_file}) written!")
    timing = perf_counter() - start
    print(f"Calculation took {timing} seconds")



if __name__ == "__main__":
    main()
