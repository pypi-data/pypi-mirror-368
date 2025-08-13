# ©2020-​2021 ETH Zurich, Axel Theorell
from optlang import glpk_interface

config = glpk_interface.Configuration()
config.verbosity = 0
import warnings
from typing import Dict

from PolyRound.default_settings import (
    default_hp_flags,
    default_0_width,
    default_numerics_threshold,
    default_accepted_tol_violation,
)
import optlang

try:
    import gurobipy
except:
    gurobipy = None

if gurobipy:
    pref_backend = "gurobi"
else:
    pref_backend = "glpk"


class PolyRoundSettings:
    """
    Settings object specifying numerical tolerance and other program options
    """

    def __init__(
        self,
        backend: str = pref_backend,
        hp_flags: Dict = default_hp_flags,
        thresh: float = default_0_width,
        verbose: bool = False,
        sgp: bool = False,
        reduce: bool = True,
        regularize: bool = False,
        check_lps: bool = False,
        simplify_only: bool = False,
        presolve: bool = False,
        numerics_threshold: float = default_numerics_threshold,
        accepted_tol_violation: float = default_accepted_tol_violation,
    ):
        """
        @param backend: set the optlang backend. At this point gurobi (default when installed) and glpk are supported.
        @param hp_flags: dictionary with gurobi flags as keys and related numbers as values. Passed directly to the gurobi object if gurobi is the backend. If not, the only allowed keywords are FeasibilityTol and OptimalityTol that are passed directly to optlang.
        @param thresh: numerical threshold determining the smallest facette width in absolute values (default 1e-7).
        @param verbose: allow runtime information to be printed to terminal.
        @param sgp: specifically control the terminal print level of gurobi.
        @param reduce: remove redundant constraints (True by default). Setting it False is only for testing purposes.
        @param regularize: impose quadratic penalty term to control position of Chebyshec center. Currently not functional.
        @param check_lps: perform extra checks on whether solutions to linear programs really fulfill the imposed tolerances. Degrades performance significantly.
        @param simplify_only: only remove redundant constraints (and not zero facettes). Does not yield roundable polytope.
        @param presolve: use linear programming solver presolve option.
        """
        self.backend = backend
        self.hp_flags = hp_flags
        if backend != "gurobi":
            if "OptimalityTol" in hp_flags:
                # if the user requests a specific OptimalityTol and the interface cannot take this parameter, the user is informed.
                if hp_flags["OptimalityTol"] != default_hp_flags["OptimalityTol"]:
                    # check the optlang version
                    version = optlang.__version__
                    number = int(version.split(".")[1])
                    allowed_flags = list(default_hp_flags.keys())
                    if number > 4:
                        allowed_flags.remove("OptimalityTol")
                    for key in self.hp_flags:
                        if key not in allowed_flags:
                            warnings.warn(
                                "hp_flag "
                                + key
                                + " not supported by backend "
                                + self.backend
                                + " passed"
                            )
                else:
                    del hp_flags["OptimalityTol"]
        self.thresh = thresh
        self.verbose = verbose
        self.sgp = sgp
        self.reduce = reduce
        self.regularize = regularize
        self.check_lps = check_lps
        self.simplify_only = simplify_only
        self.presolve = presolve
        self.numerics_threshold = numerics_threshold
        self.accepted_tol_violation = accepted_tol_violation
