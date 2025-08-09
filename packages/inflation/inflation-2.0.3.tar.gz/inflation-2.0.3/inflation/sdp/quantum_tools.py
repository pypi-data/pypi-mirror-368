"""
This file contains helper functions to manipulate monomials and generate moment
matrices.

@authors: Emanuel-Cristian Boghiu, Elie Wolfe, Alejandro Pozas-Kerstjens
"""
import numpy as np
import sympy

from itertools import permutations, product, combinations_with_replacement
from tqdm import tqdm
from typing import Dict, List, Tuple, Union

from .fast_npa import (apply_source_perm,
                       dot_mon,
                       mon_lexsorted,
                       to_canonical_1d_internal,
                       to_name)
from ..utils import format_permutations


###############################################################################
# FUNCTIONS FOR MONOMIALS                                                     #
###############################################################################

def flatten_symbolic_powers(monomial: sympy.core.symbol.Symbol
                            ) -> List[sympy.core.symbol.Symbol]:
    """If we have powers of a monomial, such as A**3, return a list with
    the factors, [A, A, A].

    Parameters
    ----------
    monomial : sympy.core.symbol.Symbol
        Symbolic monomial, possible with powers.

    Returns
    -------
    List[sympy.core.symbol.Symbol]
        List of all the symbolic factors, with the powers expanded.
    """
    factors          = monomial.as_ordered_factors()
    factors_expanded = []
    for factor in factors:
        base, exp = factor.as_base_exp()
        factors_expanded.extend([base] * exp)
    factors = factors_expanded
    return factors


def reduce_inflation_indices(monomial: np.ndarray) -> np.ndarray:
    """Reduce the inflation indices of a monomial as much as possible. This
    procedure might not give the canonical form directly due to commutations.

    Parameters
    ----------
    monomial : numpy.ndarray
        Input monomial.

    Returns
    -------
    numpy.ndarray
        An equivalent monomial closer to its representative form.
    """
    new_mon    = monomial.copy()
    nr_sources = monomial.shape[1] - 3
    # Pad the monomial with a row a zeros at the front so as to have the
    # relevant inflation indices to begin at 1
    new_mon_padded_transposed = np.concatenate((np.zeros_like(new_mon[:1]),
                                                new_mon)).T
    for source in range(nr_sources):
        copies_used = new_mon_padded_transposed[1 + source]
        _, unique_positions = np.unique(copies_used, return_inverse=True)
        new_mon_padded_transposed[1 + source] = unique_positions
    return new_mon_padded_transposed.T[1:]

def calculate_momentmatrix_1d_internal(cols: List,
                                       notcomm: np.ndarray,
                                       orthomat: np.ndarray,
                                       commuting: bool = False,
                                       verbose: int = 0
                                       ) -> Tuple[np.ndarray, Dict]:
    r"""Calculate the moment matrix. The function takes as input the generating
    set :math:`\{M_i\}_i` encoded as a list of monomials. Each monomial is a
    matrix where each row is an operator and the columns specify the operator
    labels/indices. The moment matrix is the inner product between all possible
    pairs of elements from the generating set. The program outputs the moment
    matrix as a 2d array. Entry :math:`(i,j)` of the moment matrix stores the
    index of the monomial that represents the result of the expectation value
    :math:`\text{Tr}(\rho\cdot M_i^\dagger M_j)` for an unknown quantum state
    :math:`\rho` after applying the substitutions. The program returns the
    moment matrix and the dictionary mapping each monomial in string
    representation to its integer representation.

    Parameters
    ----------
    cols : List
        List of numpy.ndarray representing the generating set in 1d internal format.
    notcomm : numpy.ndarray
        Matrix of commutation relations, given in the format specified by
        `inflation.quantum.fast_npa.commutation_matrix`.
    orthomat : numpy.ndarray
        Matrix of orthogonality relations. Each operator can be identified by an
        integer `i` which also doubles as its lexicographic rank. Given two
        operators with ranks `i`, `j`, ``notcomm[i, j]`` is 1 if the operators
        are orthogonal, and 0 if they do.
    commuting : bool, optional
        Whether the variables in the problem commute or not. By default
        ``False``.
    verbose : int, optional
        How much information to print. By default ``0``.

    Returns
    -------
    Tuple[numpy.ndarray, Dict]
        The moment matrix :math:`\Gamma`, where each entry :math:`(i,j)` stores
        the integer representation of a monomial. The Dict is a mapping from
        string representation to integer representation.
    """
    nrcols = len(cols)
    canonical_mon_to_idx = {}
    momentmatrix = np.zeros((nrcols, nrcols), dtype=np.uint32)
    varidx = 1  # We start from 1 because 0 is reserved for 0
    for (i, mon1), (j, mon2) in tqdm(
            combinations_with_replacement(enumerate(cols), 2),
            disable=not verbose,
            desc="Calculating moment matrix",
            total=int(nrcols * (nrcols + 1) / 2),
    ):
        mon_v1 = to_canonical_1d_internal(dot_mon(mon1, mon2),
                                          notcomm,
                                          orthomat,
                                          commuting=commuting,
                                          apply_only_commutations=False)
        if np.all(mon_v1):  # a zero indicates equal to zero scalar
            if len(mon_v1) > 1 and (not commuting):
                mon_v2 = to_canonical_1d_internal(np.flipud(mon_v1),
                                                  notcomm,
                                                  orthomat,
                                                  commuting=commuting,
                                                  apply_only_commutations=True)
                mon_hash = min(tuple(mon_v1), tuple(mon_v2))
            else:
                mon_hash = tuple(mon_v1)
            try:
                known_varidx = canonical_mon_to_idx[mon_hash]
                momentmatrix[i, j] = known_varidx
                momentmatrix[j, i] = known_varidx
            except KeyError:
                canonical_mon_to_idx[mon_hash] = varidx
                momentmatrix[i, j] = varidx
                momentmatrix[j, i] = varidx
                varidx += 1
    return momentmatrix, canonical_mon_to_idx


###############################################################################
# FUNCTIONS FOR INFLATIONS                                                    #
###############################################################################

def apply_inflation_symmetries(momentmatrix: np.ndarray,
                               inflation_symmetries: np.ndarray,
                               verbose: bool = False
                               ) -> Tuple[np.ndarray,
                                          Dict[int, int],
                                          np.ndarray]:
    """Applies the inflation symmetries, in the form of permutations of the
    rows and colums of a moment matrix, to the moment matrix.

    Parameters
    ----------
    momentmatrix : numpy.ndarray
        The moment matrix.
    inflation_symmetries : numpy.ndarray
        Two-dimensional array where each row represents a permutation of
        the rows and columns of the moment matrix.
    verbose : bool
        Whether information about progress is printed out.

    Returns
    -------
    sym_mm : numpy.ndarray
        The symmetrized version of the moment matrix, where each cell is
        the lowest index of all the Monomials that are equivalent to that
        in the corresponding cell in momentmatrix.
    orbits : Dict[int, int]
        The map from unsymmetrized indices in momentmatrix to their
        symmetrized counterparts in sym_mm.
    repr_values: numpy.ndarray
        An array of unique representative former (unsymmetrized) indices.
        This is later used for hashing indices and making sanitization much
        faster.
    """
    max_value = momentmatrix.max(initial=0)
    if not len(inflation_symmetries):
        repr_values = np.arange(max_value + 1)
        orbits = dict(zip(repr_values, repr_values))
        return momentmatrix, orbits, repr_values
    else:
        old_indices, flat_pos, inverse = np.unique(momentmatrix.ravel(),
                                                   return_index=True,
                                                   return_inverse=True)
        inverse           = inverse.reshape(momentmatrix.shape)
        prev_unique_count = np.inf
        new_unique_count  = old_indices.shape[0]
        new_indices       = np.arange(new_unique_count)
        inversion_tracker = new_indices.copy()
        repr_values = old_indices.copy()
        # We minimize under every element of the inflation symmetry group.
        for permutation in tqdm(inflation_symmetries,
                                disable=not verbose,
                                desc="Applying symmetries      "):
            if prev_unique_count > new_unique_count:
                rows, cols = np.unravel_index(flat_pos, momentmatrix.shape)
            prev_unique_count = new_unique_count
            assert np.array_equal(new_indices, inverse[(rows, cols)]), \
                ("The representatives of the symmetrized indices are " +
                 "not minimal.")
            np.minimum(new_indices,
                       inverse[(permutation[rows], permutation[cols])],
                       out=new_indices)
            unique_values, unique_values_pos, unique_values_inv = \
                np.unique(new_indices,
                          return_index=True,
                          return_inverse=True)
            new_unique_count = unique_values.shape[0]
            if prev_unique_count > new_unique_count:
                inverse           = unique_values_inv[inverse]
                flat_pos          = flat_pos[unique_values_pos]
                repr_values       = repr_values[unique_values_pos]
                inversion_tracker = unique_values_inv[inversion_tracker]
                del unique_values_pos, unique_values_inv
                new_indices = np.arange(new_unique_count)
        prior_min_value = old_indices.min()
        if old_indices.min() != 0:
            new_indices += prior_min_value
        orbits = dict(zip(old_indices, new_indices[inversion_tracker]))
        sym_mm = new_indices[inverse]
        return sym_mm, orbits, repr_values


# TODO @Cristian add this to InflationSDP
def commutation_relations(infSDP):
    """Return a user-friendly representation of the commutation relations.

    Parameters
    ----------
    infSDP : inflation.InflationSDP
        The SDP object for which the commutation relations are to be extracted.

    Returns
    -------
    Tuple[sympy.core.expr.Expr]
        The list of commutators (given as sympy Expressions) that are nonzero.
    """
    from collections import namedtuple
    nonzero = namedtuple("NonZeroExpressions", "exprs")
    data = []
    lexorder = infSDP._lexorder
    lexorder_len = lexorder.shape[0]
    for i in range(lexorder_len):
        for j in range(i, lexorder_len):
            # Most operators commute as they belong to different parties,
            if infSDP._notcomm[i, j] != 0:
                (op1_name, op2_name) = to_name(lexorder[[i, j]],
                                               infSDP.names).split('*')
                op1 = sympy.Symbol(op1_name, commutative=False)
                op2 = sympy.Symbol(op2_name, commutative=False)
                if infSDP.verbose > 0:
                    print(f"{str(op1 * op2 - op2 * op1)} ≠ 0.")
                data.append(op1 * op2 - op2 * op1)
    return nonzero(data)


def construct_normalization_eqs(column_equalities: List[Tuple[int, List[int]]],
                                momentmatrix: np.ndarray,
                                verbose=0,
                                ) -> List[Tuple[int, List[int]]]:
    """Given a list of column level normalization equalities and the moment
    matrix, this function computes the implicit normalization equalities
    between matrix elements. Column-level and monomial-level equalities share
    nearly the same format, they differ merely in whether integers pertain to
    column indices or the indices that represent the unique moment matrix
    elements.

    Parameters
    ----------
    column_equalities : List[Tuple[int, List[int]]]
        The list of equalities between columns in the moment matrix, in the
        form of tuples whose first element is the index of one of the columns,
        and the second element is the list of indices of the columns whose
        corresponding operators sum up to the operator corresponding to the
        first element.
    momentmatrix : numpy.ndarray
        The moment matrix of which the identification between variables shall
        be computed.
    verbose : int, optional
        Verbosity level. By default 0.

    Returns
    -------
    List[Tuple[int, List[int]]]
        The equalities between variables. For each tuple, the first element is
        the index of one of the variables in ``momentmatrix``, and the second
        is the list of variables whose sum corresponds to the first.
    """
    equalities = []
    seen_already = set()
    nof_seen_already = len(seen_already)
    for equality in tqdm(column_equalities,
                         disable=not verbose,
                         desc="Imposing normalization   "):
        for i, row in enumerate(iter(momentmatrix)):
            (normalization_col, summation_cols) = equality
            norm_idx       = row[normalization_col]
            summation_idxs = row[summation_cols]
            if summation_idxs.all():
                summation_idxs.sort()
                seen_already.add(tuple(summation_idxs.flat))
                if len(seen_already) > nof_seen_already:
                    equalities.append((norm_idx, summation_idxs.tolist()))
                    nof_seen_already += 1
    del seen_already
    return equalities


def expand_moment_normalisation(moment: np.ndarray,
                                outcome_cardinalities: List[int],
                                skip_party: List[bool]):
    """Helper function that identifies operators within the monomial that
    correspond to the last outcome, and uses normalisation to produce
    an equality constraint with other monomials. The constraint is expressed as
    `(i, (i1, i2, i3, ...))`, where the moment corresponding to index `i` is
    equal to the sum of moments corresponding to indices
    `(i1, i2, i3, ...)`.

    Parameters
    ----------
    moment : numpy.ndarray
        Moment encoded as a 2D array.
    outcome_cardinalities : List[int]
        List of the cardinalities for the outcomes of the parties.
    skip_party : List[bool]
        Whether each of the parties is considered for normalisation or not.
    """
    eqs = []
    for k, operator in enumerate(moment):
        party = operator[0] - 1
        # Operators that are involved in normalization equalities are
        # those which are unpacked in non-network scenarios
        if (not skip_party[party]
                and operator[-1] == outcome_cardinalities[party] - 2):
            operator_2d = np.expand_dims(operator, axis=0)
            prefix = moment[:k]
            suffix = moment[(k + 1):]
            moments = [moment]
            true_cardinality = outcome_cardinalities[party] - 1
            for outcome in range(true_cardinality - 1):
                variant_operator        = operator_2d.copy()
                variant_operator[0, -1] = outcome
                variant_mon             = np.vstack((prefix,
                                                     variant_operator,
                                                     suffix))
                moments.append(variant_mon)
            if len(moments) == true_cardinality:
                normalization_mon = np.vstack((prefix, suffix))
                eqs.append((normalization_mon, moments))
    return eqs


def lexicographic_order(infSDP) -> Dict[str, int]:
    """Return a user-friendly representation of the lexicographic order.

    Parameters
    ----------
    infSDP : inflation.InflationSDP
        The SDP object for which the commutation relations are to be extracted.

    Returns
    -------
    Dict[str, int]
        The lexicographic order as a dictionary where keys are the monomials in
        the problem and the values are their positions in the lexicographic
        ordering.
    """
    lexorder = {}
    for i, op in enumerate(infSDP._lexorder):
        lexorder[sympy.Symbol(to_name([op], infSDP.names),
                              commutative=False)] = i
    return lexorder
