"""
This file contains the functions to send the problems to SDP solvers.

@authors: Emanuel-Cristian Boghiu, Elie Wolfe and Alejandro Pozas-Kerstjens
"""
from __future__ import annotations
import numpy as np

from copy import deepcopy
from gc import collect
from scipy.sparse import eye, coo_array
from sys import stdout
from typing import List, Dict, Any, Iterator


def solveSDP_MosekFUSION(mask_matrices: Dict = None,
                         objective: Dict = None,
                         known_vars: Dict = None,
                         semiknown_vars: Dict = None,
                         inequalities: List[Dict] = None,
                         equalities: List[Dict] = None,
                         solve_dual: bool = True,
                         default_non_negative: bool = False,
                         feas_as_optim: bool = False,
                         verbose: int = 0,
                         solverparameters: Dict = {},
                         process_constraints: bool = True
                         ) -> Dict[str, Any]:
    r"""Internal function to solve the SDP with the `MOSEK Fusion API
    <https://docs.mosek.com/latest/pythonfusion/index.html>`_.

    Now follows an extended description of how the SDP is encoded. In general,
    it is preferred to solve using the dual formulation, which is the default.

    The primal is written as follows:

    .. math::

        \text{max}\quad & c_0 + c\cdot x\\
        \text{s.t.}\quad & F_0 + \sum F_i x_i \succeq 0

    :math:`F_0` is the constant entries of the moment matrix, and :math:`F_i`
    is the matrix whose entry :math:`(n,m)` stores the value of the coefficient
    of the moment :math:`x_i` at position :math:`(n,m)` in the moment matrix.

    The dual of the equation above is:

    .. math::

        \text{min}\quad & c_0+\text{Tr}(Z\cdot F_0)\\
        \text{s.t.}\quad & \text{Tr}(Z\cdot F_i) = - c_i \,\forall\, i,\\
        &Z \succeq 0.

    Typically, all the probability information is stored in :math:`F_0`, and
    the coefficients :math:`F_i` do not depend on the probabilities. However,
    if we use LPI constraints (see, e.g., `arXiv:2203.16543
    <http://www.arxiv.org/abs/2203.16543/>`_), then :math:`F_i` can depend on
    the probabilities. The form of the SDP does not change, in any case.

    If we have a constant objective function, then we have a feasibility
    problem. It can be rewritten into the following optimization problem:

    .. math::
        \text{max}\quad&\lambda\\
        \text{s.t.}\quad& F_0 + \sum F_i x_i - \lambda \cdot 1 \succeq 0,

    which achieves :math:`\lambda\geq 0` if the original problem is feasible
    and :math:`\lambda<0` otherwise. The dual of this problem is:

    .. math::
        \text{min}\quad & \text{Tr}(Z\cdot F_0) \\
        \text{s.t.}\quad & \text{Tr}(Z\cdot F_i) = 0 \,\forall\, i,\\
            & Z \succeq 0,\,\text{Tr} Z = 1.

    This still allows for the extraction of certificates. If we use a
    :math:`Z_{P_1}` obtained from running the problem above on the probability
    distribution :math:`P_1`, and we find that
    :math:`\text{Tr}[Z_{P_1}\cdot F_0(P_2)] < 0`, then clearly this is an upper
    bound of the optimal value of the problem, and thus we can certify that the
    optimisation will be negative when using :math:`P_2`.

    If we have upper and lower bounds on the variables, the problems change as
    follows:

    .. math::
        \text{max}\quad & c_0 + c\cdot x \\
        \text{s.t.}\quad & F_0 + \sum F_i x_i \succeq 0,\\
        & x_i - l_i \geq 0,\\
        & u_i - x_i \geq 0,

    with dual:

    .. math::
        \text{min}\quad & \text{Tr}(Z\cdot F_0 - L\cdot l + U\cdot u) \\
        \text{s.t.}\quad & \text{Tr}(Z \cdot F_i) = -c_i+U_i-L_i\,\forall\,i,\\
        & Z \succeq 0,\,L \geq 0,\,U \geq 0.

    The relaxed feasibility problems change accordingly.

    Parameters
    ----------
    mask_matrices : dict
        A dictionary with keys as monomials and values as scipy sparse arrays
        indicating the locations of the monomial in the moment matrix.
    objective : dict, optional
        Dictionary with keys as monomials and as values the monomial's
        coefficient in the objective function.
    known_vars : dict, optional
        Dictionary of values for monomials (keys).
    semiknown_vars : dict, optional
        Dictionary encoding proportionality constraints between
        different monomials.
    inequalities : list, optional
        List of inequalities encoded as dictionaries of coefficients.
    equalities : list, optional
        List of equalities encoded as dictionaries of coefficients.
    solve_dual : bool, optional
        Whether to solve the dual (True) or primal (False) formulation. By
        default ``True``.
    default_non_negative: bool, optional
        Whether to set default primal variables as non-negative (True) or not
        (False). By default, ``False``.
    feas_as_optim : bool, optional
        Whether to treat feasibility problems, where the objective is,
        constant, as an optimisation problem. By default ``False``.
    verbose : int, optional
        How much information to display to the user. By default ``0``.
    solverparameters : dict, optional
        Dictionary of parameters to pass to the MOSEK solver, see `MOSEK's
        documentation
        <https://docs.mosek.com/latest/pythonfusion/solver-parameters.html>`_.
    process_constraints: bool, optional
        Whether to remove the simple equalities constraints contained
        in the `semiknown_vars` arguments by eliminating variables (True)
        or pass them to the solver as equality constraints (False). By
        default ``True``.

    Returns
    -------
    Tuple[Dict, float, str]
        The first element of the tuple is a dictionary containing the
        optimisation information such as the 1) primal objective value,
        2) the moment matrix, 3) the dual values, 4) the certificate and
        a 5) dictionary of values for the monomials, in the following keys in
        the same order: 1) ``sol``, 2) ``G``, 3) ``Z``, 4)
        ``dual_certificate``, 5) ``xi``. The second element is the objective
        value and the last is the problem status.
    """
    import mosek
    from mosek.fusion import Matrix, Model, ObjectiveSense, Expr, Domain, \
        OptimizeError, SolutionError, \
        AccSolutionStatus, ProblemStatus

    def scipy_to_mosek(mat: coo_array) -> Matrix:
        internal_mat = mat.tocoo(copy=False)
        return Matrix.sparse(*internal_mat.shape,
                             np.asarray(internal_mat.row, dtype=np.int32),
                             np.asarray(internal_mat.col, dtype=np.int32),
                             internal_mat.data)
    def coo_getcol(mat: coo_array, i: int) -> coo_array:
        condition = (mat.col == i)
        new_col = np.zeros(condition.sum(), dtype=np.int32)
        new_row = np.asarray(mat.row, dtype=np.int32)[condition]
        new_data = np.asarray(mat.data, dtype=float)[condition]
        this_col = coo_array((new_data, (new_row, new_col)), shape=(mat.shape[0], 1))
        return this_col



    if verbose > 1:
        from time import perf_counter
        t0 = perf_counter()
        print("Starting pre-processing for the SDP solver.")

    if mask_matrices is None:
        mask_matrices = {}
    if known_vars is None:
        known_vars = {}
    if semiknown_vars is None:
        semiknown_vars = {}
    var_objective = {} if objective is None else objective.copy()
    var_inequalities = [] if inequalities is None else deepcopy(inequalities)
    var_equalities   = [] if equalities   is None else deepcopy(equalities)

    Fi = {k: v.asformat('dok', copy=False).astype(float, copy=False)
          for k, v in mask_matrices.items()}
    mat_dim = next(iter(Fi.values())).shape[0] if Fi else 0

    variables = set()
    variables.update(Fi.keys())
    variables.update(var_objective.keys())
    for eq in var_equalities:
        variables.update(eq.keys())
    for ineq in var_inequalities:
        variables.update(ineq.keys())
    variables.difference_update(known_vars.keys())

    if feas_as_optim and mask_matrices:
        if verbose > 0:
            print("Feasibility as optimisation detected: overwriting objective"
                  + " to maximize the smallest eigenvalue of the matrix"
                  + " variable.")
        lam = "lambda"
        while lam in variables:
            lam += "_"
        variables.add(lam)
        Fi[lam] = -1 * eye(mat_dim).tolil()
        var_objective = {lam: 1}

    # Calculate F0, the constant part of the matrix variable.
    F0 = coo_array((mat_dim, mat_dim), dtype=float)
    F0 += sum(known_vars[x] * Fi[x] for x in set(Fi).intersection(known_vars))

    if process_constraints:
        # For the semiknown constraint x_i = a_i * x_j, add to the Fi of x_j
        # the expression a_i*(Fi of x_i).
        for x, (c, x2) in semiknown_vars.items():
            if mask_matrices:
                val = Fi.pop(x, 0)
                Fi[x2] = Fi.get(x2, 0) + c * val

            if var_objective and not feas_as_optim:
                val = var_objective.pop(x, 0)
                var_objective[x2] = var_objective.get(x2, 0) + c * val

            for equality in var_equalities:
                val = equality.pop(x, 0)
                equality[x2] = equality.get(x2, 0) + c * val

            for inequality in var_inequalities:
                val = inequality.pop(x, 0)
                inequality[x2] = inequality.get(x2, 0) + c * val

            variables.remove(x)
            variables.add(x2)

    else:
        # Just add semiknown constraints as equality constraints.
        for x, (c, x2) in semiknown_vars.items():
            var_equalities.append({x: 1, x2: -c})
            variables.add(x2)

    # Calculate c0, the constant part of the var_objective.
    c0 = 0. + float(sum([var_objective[x] * known_vars[x]
                         for x in set(var_objective).intersection(known_vars)])
                    )

    # 'var2index' should be computed after there is no more further modification
    # to 'variables' or any of the constraint or objective dictionaries
    var2index = {x: i for i, x in enumerate(variables)}

    # Calculate the matrices A, C and vectors b, d such that
    # Ax + b >= 0, Cx + d == 0.
    nof_variables = len(variables)
    def constraint_dicts_to_sparse(constraints: List[dict]) -> (coo_array, coo_array):
        nof_constraints = len(constraints)
        A_row = []
        A_col = []
        A_data = []
        b_row = np.arange(nof_constraints, dtype=np.int32)
        b_col = np.zeros(nof_constraints, dtype=np.int32)
        b_data = []
        for i, constraint in enumerate(constraints):
            all_vars_temp = set(constraint)
            free_vars_temp = all_vars_temp.difference(known_vars)
            known_vars_temp = all_vars_temp.intersection(known_vars)
            for x in free_vars_temp:
                A_row.append(i)
                A_col.append(var2index[x])
                A_data.append(constraint[x])
            b_val = 0.
            for x in known_vars_temp:
                x_val = known_vars[x]
                coeff = constraint[x]
                b_val += (coeff * x_val)
            b_data.append(b_val)
        A = coo_array((A_data, (np.array(A_row, dtype=np.int32),
                                np.array(A_col, dtype=np.int32))),
                      shape=(nof_constraints, nof_variables),
                      dtype=float)
        b = coo_array((b_data, (b_row, b_col)),
                      shape=(nof_constraints, 1),
                      dtype=float)
        return A, b
    A, b = constraint_dicts_to_sparse(var_inequalities)
    C, d = constraint_dicts_to_sparse(var_equalities)
    collect()
    if verbose > 1:
        print("Pre-processing took",
              format(perf_counter() - t0, ".4f"),
              "seconds.")
        t0 = perf_counter()
    if verbose > 0:
        print("Building the model...")

    with Model("SDP") as M:
        if solve_dual:
            # Define variables
            if mask_matrices:
                Z = M.variable("Z", Domain.inPSDCone(mat_dim))
            if var_inequalities:
                I = M.variable("I",
                               len(var_inequalities),
                               Domain.greaterThan(0))
                I_reshaped = I.reshape(I.getShape()[0], 1)
                # It seems MOSEK Fusion API does not allow to pick index i
                # of an expression (A^T I)_i, so we do it manually row by row.
                AtI = []  # \sum_j I_j A_ji as i-th entry of AtI
                for var in variables:
                    slice_ = coo_getcol(A, var2index[var])
                    sparse_slice = scipy_to_mosek(slice_)
                    AtI.append(Expr.dot(sparse_slice, I_reshaped))
            if var_equalities:
                E = M.variable("E", len(var_equalities), Domain.unbounded())
                E_reshaped = E.reshape(E.getShape()[0], 1)
                CtI = []  # \sum_j E_j C_ji as i-th entry of CtI
                for var in variables:
                    slice_ = coo_getcol(C, var2index[var])
                    sparse_slice = scipy_to_mosek(slice_)
                    CtI.append(Expr.dot(sparse_slice, E_reshaped))

            # Define and set objective function
            # c0 + Tr Z F0 + I·b + E·d
            obj_mosek = 0.0
            if not feas_as_optim:
                obj_mosek = float(c0)
            if mask_matrices:
                F0_mosek = scipy_to_mosek(F0)
                obj_mosek = Expr.add(obj_mosek, Expr.dot(Z, F0_mosek))
                del F0_mosek
            if var_inequalities:
                b_mosek = scipy_to_mosek(b)
                obj_mosek = Expr.add(obj_mosek, Expr.dot(b_mosek, I_reshaped))
                del b_mosek
            if var_equalities:
                d_mosek = scipy_to_mosek(d)
                obj_mosek = Expr.add(obj_mosek, Expr.dot(d_mosek, E_reshaped))
                del d_mosek

            M.objective(ObjectiveSense.Minimize, obj_mosek)

            # Add constraints
            # ci + Tr Z Fi + \sum_j I_j A_ji + \sum_j E_j C_ji == 0
            ci_constraints = []
            if default_non_negative:
                domain = Domain.lessThan(0)
            else:
                domain = Domain.equalsTo(0)
            for i, x in enumerate(variables):
                lhs = 0.0
                if var_objective and x in set(var_objective
                                              ).difference(known_vars):
                    ci  = float(var_objective[x])
                    lhs += ci
                try:
                    F = Fi.pop(x)
                    lhs = Expr.add(lhs,
                                   Expr.dot(Z,
                                            scipy_to_mosek(F)))
                except KeyError:
                    pass
                if var_inequalities:
                    lhs = Expr.add(lhs, AtI[i])
                    AtI[i] = None
                if var_equalities:
                    lhs = Expr.add(lhs, CtI[i])
                    CtI[i] = None
                ci_constraints.append(M.constraint(f"c{i}", lhs, domain))
        else:
            # Set up the problem in primal formulation

            # Define variables
            if default_non_negative:
                domain = Domain.greaterThan(0)
            else:
                domain = Domain.unbounded()
            x_mosek = M.variable("x", len(variables), domain)

            if var_inequalities:
                b_mosek = scipy_to_mosek(b)
                A_mosek = scipy_to_mosek(A)
                ineq_constraint = M.constraint("Ineq",
                                               Expr.add(Expr.mul(A_mosek,
                                                                 x_mosek),
                                                        b_mosek),
                                               Domain.greaterThan(0))
                del b_mosek, A_mosek

            if var_equalities:
                d_mosek = scipy_to_mosek(d)
                C_mosek = scipy_to_mosek(C)
                eq_constraint = M.constraint("Eq",
                                             Expr.add(Expr.mul(C_mosek,
                                                               x_mosek),
                                                      d_mosek),
                                             Domain.equalsTo(0))
                del d_mosek, C_mosek

            if mask_matrices:
                G = M.variable("G", Domain.inPSDCone(mat_dim))


                # Add matrix constraints
                constraints = np.empty((mat_dim, mat_dim), dtype=object)
                for i in range(mat_dim):
                    for j in range(i, mat_dim):
                        constraints[i, j] = G.index(i, j)
                for i, j in triu_indices(F0):
                    constraints[i, j] = Expr.sub(constraints[i, j], F0[i, j])
                for i, xi in enumerate(variables.intersection(Fi.keys())):
                    for i_, j_ in triu_indices(Fi[xi]):
                        constraints[i_, j_] = \
                            Expr.sub(constraints[i_, j_],
                                    Expr.mul(Fi[xi][i_, j_],
                                              x_mosek.index(var2index[xi])))

                for i in range(mat_dim):
                    for j in range(i, mat_dim):
                        # G(i,j) - F0(i,j) - sum_i xi Fi(i,j) = 0
                        M.constraint(constraints[i, j], Domain.equalsTo(0))


            mosek_obj = c0
            for x in set(var_objective).difference(known_vars):
                ci = float(var_objective[x])
                mosek_obj = Expr.add(mosek_obj,
                                     Expr.mul(ci, x_mosek.index(var2index[x])))

            M.objective(ObjectiveSense.Maximize, mosek_obj)

        collect()
        if verbose > 1:
            print("Model built in",
                  format(perf_counter() - t0, ".4f"),
                  "seconds.")
            M.writeTask("InflationSDPModel.ptf")
            print("Model saved to InflationSDPModel.ptf.")
            t0 = perf_counter()

        # Solve the problem and process the solution
        if verbose > 0:
            print("Solving the model...")
        xmat, ymat, primal, dual = None, None, None, None
        try:
            if verbose > 0:
                M.setLogHandler(stdout)
            if solverparameters:
                for param, val in solverparameters.items():
                    M.setSolverParam(param, val)
            M.acceptedSolutionStatus(AccSolutionStatus.Anything)
            M.solve()
            if solve_dual:
                x_values = {x: float(-ci_constraints[i].dual()[0])
                            for i, x in enumerate(variables)}
                if mask_matrices:
                    ymat = Z.level().reshape([mat_dim, mat_dim])
                    xmat = F0 + sum([x_values[x] * Fi[x]
                                     for x in set(Fi).difference(known_vars)])
            else:
                x_values = dict(zip(variables, x_mosek.level()))
                if mask_matrices:
                    ymat = G.dual().reshape([mat_dim, mat_dim])
                    xmat = G.level().reshape([mat_dim, mat_dim])

            status = M.getProblemStatus()
            if status == ProblemStatus.PrimalAndDualFeasible:
                status_str = "optimal"
                primal     = M.primalObjValue()
                dual       = M.dualObjValue()

            elif status == ProblemStatus.DualInfeasible:
                status_str = "dual_infeas_cer"
            elif status == ProblemStatus.PrimalInfeasible:
                status_str = "primal_infeas_cer"
            elif status == ProblemStatus.Unknown:
                status_str = "unknown"
                code, desc = mosek.Env.getcodedesc(
                    mosek.rescode(int(M.getSolverIntInfo("optimizeResponse"))))
                error_message = f"Termination code {code}: {desc}"
                if verbose > 0:
                    print("The solution status is unknown.\n" + error_message)
                return {"status": status_str, "error": error_message}
            else:
                status_str = "other"
                error_message = ("Another unexpected problem, " +
                                 f"status {status} has been obtained.")
                print(error_message)
                return {"status": status_str, "error": error_message}
        except OptimizeError as e:
            status_str = "other"
            error_message = f"Optimization failed. Error: {e}"
            print(error_message)
            return {"status": status_str, "error": error_message}
        except SolutionError as e:
            status_str = M.getProblemStatus()
            error_message = f"Solution status: {status_str}. Error: {e}"
            print(error_message)
            return {"status": status_str, "error": error_message}
        except Exception as e:
            status_str = "other"
            error_message = f"Unexpected error: {e}"
            print(error_message)
            return {"status": status_str, "error": error_message}

        if status_str in ["optimal", "primal_infeas_cer", "dual_infeas_cer"]:
            certificate = {x: 0 for x in known_vars}

            # c0(P(a...|x...))
            if not feas_as_optim:
                for x in set(var_objective).intersection(known_vars):
                    certificate[x] += var_objective[x]

            # + Tr[Z*F0(P(a...|x...))]=\sum_i*x_{kn_i}(P(a...|x...))*F_{kn_i}
            if mask_matrices:
                for x in set(Fi).intersection(known_vars):
                    support = Fi[x].nonzero()
                    certificate[x] = np.dot(ymat[support], Fi[x][support].toarray().ravel())

            # + I · b
            if var_inequalities:
                Ivalues = I.level() if solve_dual else -ineq_constraint.dual()
                for i, inequality in enumerate(var_inequalities):
                    for x in set(inequality).intersection(known_vars):
                        certificate[x] += Ivalues[i] * inequality[x]

            # + E · d
            if var_equalities:
                Evalues = E.level() if solve_dual else -eq_constraint.dual()
                for i, equality in enumerate(var_equalities):
                    for x in set(equality).intersection(known_vars):
                        certificate[x] += Evalues[i] * equality[x]

            # Clean entries with coefficient zero
            for x in list(certificate.keys()):
                if np.isclose(certificate[x], 0):
                    del certificate[x]

            # For debugging purposes
            if status_str == "optimal" and verbose > 1:
                TOL = 1e-8  # Constraint tolerance
                if var_inequalities:
                    x = A.todense() \
                        @ np.array(list(x_values.values())) \
                        + b.T.todense()[0]
                    if np.any(x < -TOL):
                        print("Warning: Inequality constraints not satisfied" +
                              f" to {TOL} precision.")
                        print("Inequality constraints and their deviation:")
                        print([(ineq, x[i]) for i, (violated, ineq)
                               in enumerate(zip(x < -TOL, var_inequalities))
                               if violated])
                if var_equalities:
                    x = C.todense() \
                        @ np.array(list(x_values.values())) \
                        + d.T.todense()[0]
                    if np.any(np.abs(x) > TOL):
                        print("Warning: Equality constraints not satisfied " +
                              f"to {TOL} precision.")
                        print("Equality constraints and their deviation:")
                        print([(eq, x[i]) for i, (violated, eq)
                               in enumerate(zip(np.abs(x) > TOL,
                                                var_equalities))
                               if violated])

            vars_of_interest = {"primal_value": primal, "dual_value": dual,
                                "status": status_str, "F": xmat, "Z": ymat,
                                "dual_certificate": certificate,
                                "x": x_values}

            return vars_of_interest
        else:
            return {"status": status_str}


def triu_indices(A: coo_array) -> Iterator[tuple[np.int32, np.int32]]:
    """Helper functions to extract the upper triangular (i,j) matrix indices
     of the nonzero elements of a symmetric sparse matrix."""
    A_coo = A.tocoo(copy=False)
    mask = np.logical_and(A_coo.data != 0, A_coo.row <= A_coo.col)
    return zip(A_coo.row[mask].astype(np.int32).flat,
               A_coo.col[mask].astype(np.int32).flat)
