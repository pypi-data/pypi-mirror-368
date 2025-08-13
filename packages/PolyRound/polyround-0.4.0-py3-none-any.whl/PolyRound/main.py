# ©2020-​2021 ETH Zurich, Axel Theorell

import numpy as np
import sys
import os

sys.path.insert(0, os.getcwd())
from PolyRound.static_classes.parse_sbml_stoichiometry import StoichiometryParser
import time
import argparse
from PolyRound.api import PolyRoundApi
from PolyRound.static_classes.csv_io import CSV
from PolyRound.default_settings import default_hp_flags
from PolyRound.settings import PolyRoundSettings, pref_backend


def main(args):
    inputs = args.files
    path = args.path
    # thresh = args.thresh
    # verbose = args.v
    # reduce = not args.do_not_reduce
    # set hp flags
    hp_flags = default_hp_flags
    if args.hp:
        hp_flags = {
            "NumericFocus": 3,
            "FeasibilityTol": 1e-09,
            "OptimalityTol": 1e-09,
            "MarkowitzTol": 0.999,
        }
    settings = PolyRoundSettings(
        backend=args.backend,
        hp_flags=hp_flags,
        thresh=args.thresh,
        verbose=args.v,
        check_lps=args.check_lps,
        sgp=args.sgp,
        reduce=(not args.do_not_reduce),
    )
    for input in inputs:

        input_name = input.split("/")[-1].split(".")[0]
        # file_path = os.path.dirname(__file__)
        # logging.basicConfig(filename=os.path.join(file_path, 'logs', input_name + '.log'))
        # logging.info("starting a new run")
        if input.endswith(".xml"):
            polytope = StoichiometryParser.parse_sbml_cobrapy(input, prescale=False)
        else:
            raise (IOError("Only xml files supported at the moment"))
        start_time = time.time()
        polytope = PolyRoundApi.simplify_transform_and_round(
            polytope,
            settings=settings,
        )
        end_time = time.time()
        CSV.polytope_to_csv(
            polytope, os.path.join(path, input_name + "_reduced_rounded")
        )
        return end_time - start_time


def pars_args():
    # Create the parser
    parser = argparse.ArgumentParser(description="List the content of a folder")

    # Add the arguments
    parser.add_argument(
        "-hp", action="store_true", help="run the program with high precision option"
    )

    parser.add_argument("-sgp", action="store_true", help="show gurobi progress")
    parser.add_argument("-v", action="store_true", help="run in verbose mode")
    parser.add_argument(
        "-check_lps", action="store_true", help="make external checks on lp solutions"
    )
    parser.add_argument(
        "-do_not_reduce", action="store_true", help="run in verbose mode"
    )
    parser.add_argument(
        "-thresh",
        type=float,
        default=1e-7,
        help="Threshold parameter for minimal width of a dimension",
    )
    parser.add_argument(
        "-path", type=str, default="PolyRound/output/", help="Output path"
    )
    parser.add_argument(
        "-backend",
        type=str,
        default=pref_backend,
        help="Backend for solving linear programs. Possible inputs is gurobi and glpk. gurobi is default in case it is available.",
    )
    parser.add_argument("files", nargs="*")

    args = parser.parse_args()
    print(args)

    return args


if __name__ == "__main__":
    print(main(pars_args()))
