# ©2020-​2021 ETH Zurich, Axel Theorell
from optlang import glpk_interface

config = glpk_interface.Configuration()
config.verbosity = 0
import numpy as np
from PolyRound.settings import PolyRoundSettings
import scipy.sparse as sp
from PolyRound.static_classes.lp_interfacing import OptlangInterfacer
from PolyRound.default_settings import default_solver_timeout
from sympy.core import Add, Mul

from PolyRound.static_classes.lp_interfacing import solvers
from sympy import Matrix, SparseMatrix
import pandas as pd


class PolytopeReducer:
    @staticmethod
    def constraint_removal(
        polytope,
        settings,
    ):
        """
        Removes redundant constraints and removes narrow directions by turning them into equality constraints
        :param polytope: Polytope object to round
        :param hp_flags: Dictionary of gurobi flags for high precision solution
        :param thresh: Float determining how narrow a direction has to be to declare an equality constraint
        :param verbose: Bool regulating output level
        :return: Polytope object with non-empty interior and no redundant constraints, number of removed constraints,
        number of inequality constraints turned to equality constraints.
        """
        m = OptlangInterfacer.polytope_to_optlang(polytope, settings)
        m.configuration.timeout = default_solver_timeout
        # m = optModel("model")
        if settings.backend == "gurobi":
            OptlangInterfacer.configure_gurobi_model(m, settings)
        else:
            OptlangInterfacer.configure_optlang_model(m, settings.hp_flags)

        # start = time.time()
        m, removed, refunctioned = PolytopeReducer.constraint_removal_loop(m, settings)
        # print(time.time() - start)
        if settings.verbose:
            print("Number of removed constraints: " + str(removed))
            print("Number of refunctioned constraints: " + str(refunctioned))

        reduced_polytope = OptlangInterfacer.optlang_to_polytope(m)
        return reduced_polytope, removed, refunctioned

    @staticmethod
    def constraint_removal_loop(m, settings):
        interface = solvers[settings.backend]
        constrs = m.constraints
        constr_index = {i: c for i, c in enumerate(constrs) if c.lb != c.ub}
        # in case all constraints are inequalities, we only try remove redundancies
        # no_eq_constraints = len(constrs) == len(constr_index)
        # if start_ind is not None:
        #     constr_index = {i: c for i, c in constr_index.items() if i >= start_ind}
        # for each constraint, solve three lps
        removed = 0
        refunctioned = 0
        # avoided_lps = 0
        for i in constr_index:
            if settings.verbose:
                if i % 50 == 0:
                    print("\n Investigating constraint number: " + str(i) + "\n")

                # m.write("output/debug_temp.mps")
            constr_expr = constr_index[i].expression
            m.objective = interface.Objective(constr_expr, direction="max")
            # m.setObjective(constr_expr, gp.GRB.MAXIMIZE)
            # m.update()
            m.optimize()
            max_val = OptlangInterfacer.get_opt(m, settings)
            if settings.reduce:
                # now get altered problem

                orig_rhs = constr_index[i].ub
                constr_index[i].ub = orig_rhs + 1
                # m.update()
                m.optimize()
                pert_val = OptlangInterfacer.get_opt(m, settings)
                constr_index[i].ub = orig_rhs
                if np.abs(max_val - pert_val) < settings.thresh:
                    removed += 1
                    # In this case remove constraint
                    m.remove(constr_index[i])
                    continue
            elif constr_index[i].ub - max_val >= settings.thresh:
                # in this case it is clear that the constraint does not constitue a zero facette
                continue
            if not settings.simplify_only:
                # Check if it might be an equality

                m.objective = interface.Objective(constr_expr, direction="min")
                m.optimize()
                min_val = OptlangInterfacer.get_opt(m, settings)
                gap = np.abs(max_val - min_val)
                if gap < settings.thresh:

                    constr_index[i].lb = constr_index[i].ub
                    refunctioned += 1

            m.update()
        # if verbose:
        #     print(str(avoided_lps) + " lps were avoided with chebyshev center speed up")
        return m, removed, refunctioned

    @staticmethod
    def null_space(S, eps=1e-10):
        """
        Returns the null space of a matrix
        :param S: Numpy array
        :param eps: Threshold for declaring 0 singular values
        :return: Numpy array of null space
        """
        u, s, vh = np.linalg.svd(S)
        s = np.array(s.tolist())
        vh = np.array(vh.tolist())
        null_mask = s <= eps
        null_mask = np.append(null_mask, True)
        null_ind = np.argmax(null_mask)
        null = vh[null_ind:, :]
        return np.transpose(null)

    # @staticmethod
    # def create_row_col(indices, shape):

    @staticmethod
    def sparse_null_space(S_df):
        # test integrality! If float type is used, too many constraints may be found
        if not (S_df.dtypes == int).all():
            raise TypeError(
                "Polytope has to be formulated in integers for sparse null space."
            )

        react_sum = np.sum(S_df != 0, axis=0)
        order = np.argsort(react_sum)
        S = S_df.values[:, order]

        # start = time.time()
        # this funny way to create the in_matrix is an order of magintude faster than the direct way
        csr = sp.csr_matrix(S)
        dokform = csr.todok()
        in_matrix = SparseMatrix(dokform.shape[0], dokform.shape[1], dict(dokform))

        rref_m, rref_pivot = in_matrix.rref()
        rank = len(rref_pivot)
        # we need to reset the column order
        rref_inverted = list()
        for i in range(rref_m.cols):
            if i not in rref_pivot:
                rref_inverted.append(i)
        rref_inverted = tuple(rref_inverted)
        trans = SparseMatrix.zeros(in_matrix.cols, in_matrix.cols - rank)
        eye_ind = 0
        rref_ind = 0
        for ind in range(in_matrix.cols):
            if ind in rref_pivot:
                trans[ind, :] = -rref_m[rref_ind, rref_inverted]
                rref_ind += 1
            else:
                trans[ind, eye_ind] = 1
                eye_ind += 1
        back_order = list(range(len(order)))
        for ind, num in enumerate(order):
            back_order[num] = ind
        trans = trans[back_order, :]
        trans_df = pd.DataFrame(np.array(trans), index=S_df.columns, dtype=np.float64)
        return trans_df

    @staticmethod
    def linExprSeriesProd(center, lin_expr):
        val = 0.0
        if isinstance(lin_expr, Add):
            for mul in lin_expr.args:
                assert isinstance(mul, Mul)
                val += PolytopeReducer.multiplyMulObject(center, mul)
        else:
            assert isinstance(lin_expr, Mul)
            val += PolytopeReducer.multiplyMulObject(center, lin_expr)
        return val

    @staticmethod
    def multiplyMulObject(center, mul):
        val = 0.0
        mul_dict = mul.as_coefficients_dict()
        for name, coeff in mul_dict.items():
            val += center[name.name] * coeff
        return val
