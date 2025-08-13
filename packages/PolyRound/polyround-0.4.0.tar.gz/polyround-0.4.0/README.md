# PolyRound

Efficient random sampling in convex polytopes relies on a 'rounding' preprocessing step, in which the polytope is rescaled so that the width is as uniform as possible across different dimensions.
PolyRound rounds polytopes on the general form:

$`P:=\{x \in \mathcal{R}^n: A_{eq} x = b_{eq}, A_{ineq} x \leq b_{ineq}\}`$ with matrices $`A_{eq} \in \mathcal{R}^{m,n}`$ and $`A_{ineq} \in \mathcal{R}^{k,n}`$ and vectors $`b_{eq} \in \mathcal{R}^{m}`$ and $`b_{ineq} \in \mathcal{R}^{k}`$.

This formulation often arises in Systems Biology as the flux space of a metabolic network.

As output, PolyRound produces a polytope on the form $`P^{r}:=\{v \in \mathcal{R}^l: A^{r}_{ineq}v \leq b^{r}_{ineq}\}`$ where $`l \leq n`$ and the zero vector is a stricly interior point. For transforming points back to the original space, it also provides a matrix $`S \in \mathcal{R}^{n,l}`$ and a vector $`t \in \mathcal{R}^{n}`$, so that $`x=Sv + t`$.

Currently, PolyRound is supported for python 3.8 to 3.12.

PolyRound comes with two optional dependencies: 1) Gurobi (for the best linear programming) and 2) Cobrapy (for SBML support)
Both dependencies are fetched by installing the extras: "pip install 'PolyRound[extras]'".
When Gurobi is not installed, PolyRound uses optlang (https://github.com/opencobra/optlang) to delegate linear programs to GLPK. However, PolyRound is more reliable with Gurobi. Free Gurobi licenses for academic use can be obtained at https://www.gurobi.com/. Once the license is installed, gurobipy can be installed directly through pip, or by getting the optional requirements as described above.


An easy example of how to get started is presented in the jupyter notebook cells below.


They show how to: <br>
1) create a polytope object from a file path <br>
2) simplify, reduce, and round a polytope in separate steps, togehter with some printed checks <br>
3) simplify, reduce and round a polytope in one step <br>
4) save the rounded polytope

``` python
import os
from PolyRound.api import PolyRoundApi
from PolyRound.static_classes.lp_utils import ChebyshevFinder
from PolyRound.settings import PolyRoundSettings
from pathlib import Path

model_path = os.path.join("PolyRound", "models", "e_coli_core.xml")
```

``` python
# Create a settings object with the default settings.
settings = PolyRoundSettings()
```

``` python
# Import model and create Polytope object
polytope = PolyRoundApi.sbml_to_polytope(model_path)
```

``` python
# Remove redundant constraints and refunction inequality constraints that are de-facto equalities.
# Due to these inequalities, the polytope is empty (distance from chebyshev center to boundary is zero)
x, dist = ChebyshevFinder.chebyshev_center(polytope, settings)
print(dist)
simplified_polytope = PolyRoundApi.simplify_polytope(polytope)
# The simplified polytope has non-zero border distance
x, dist = ChebyshevFinder.chebyshev_center(simplified_polytope, settings)
print(dist)
```

``` python
# Embed the polytope in a space where it has non-zero volume
transformed_polytope = PolyRoundApi.transform_polytope(simplified_polytope)
# The distance from the chebyshev center to the boundary changes in the new coordinate system
x, dist = ChebyshevFinder.chebyshev_center(transformed_polytope, settings)
print(dist)
```

``` python
# Round the polytope
rounded_polytope = PolyRoundApi.round_polytope(transformed_polytope)
# After rounding, the distance from the chebyshev center to the boundary is set to be close to 1
x, dist = ChebyshevFinder.chebyshev_center(rounded_polytope, settings)
print(dist)

# The chebyshev center can be back transformed into an interior point in the simplified space.
print(simplified_polytope.border_distance(rounded_polytope.back_transform(x)))
```

``` python
# simplify, transform and round in one call
one_step_rounded_polytope = PolyRoundApi.simplify_transform_and_round(polytope)
```

``` python
# save to csv
out_csv_dir = os.path.join("PolyRound", "output", "e_coli_core")
Path(out_csv_dir).mkdir(parents=True, exist_ok=True)
PolyRoundApi.polytope_to_csvs(one_step_rounded_polytope, out_csv_dir)
```

``` python
# Special use case: remove redundant constraints without removing zero facettes. This will leave th polytope with its original border distance.
x, dist = ChebyshevFinder.chebyshev_center(polytope, settings)
print(dist)
settings.simplify_only = True
simplified_polytope = PolyRoundApi.simplify_polytope(polytope, settings=settings)
# The simplified polytope still has zero border distance
x, dist = ChebyshevFinder.chebyshev_center(simplified_polytope, settings)
print(dist)
```
