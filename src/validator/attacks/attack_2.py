import argparse
import os
import sys
import h5py
import ast
import numpy as np
from itertools import combinations
from ..parameters import *
from ..helpers import *
from functools import partial

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def _variables_sets(ciphertext_file, clauses_file):

    if "ciphertext" in ciphertext_file:

        #########
        ######### STEP 1
        #########

        ciphertext = [tuple(set(x)) for x in ciphertext_file["ciphertext"][:]]
        s = [set().union(*subset) for subset in combinations(ciphertext, 2)]

        #########
        ######### STEP 2
        #########

        def variable_contained(monomial, variable):
            return variable in monomial

        r = np.arange(2, N + 2)
        shared = dict(
            zip(
                r,
                [
                    set().union(
                        *filter(partial(variable_contained, variable=l), ciphertext)
                    )
                    for l in r
                ],
            )
        )

        s2 = set(
            flatten(
                *[
                    [
                        tuple(sorted(set().union(subset, shared.get(variable, set()))))
                        for variable in subset
                    ]
                    for subset in s
                ]
            )
        )

        clauses = np.array(ast.literal_eval(clauses_file.read()))
        clauses_variables_only = np.fromiter(
            map(lambda c: (c.T[0], c), clauses), dtype=object
        )

        #########
        ######### STEP 3
        #########

        def monomial_contained(monomial, subset):
            return set(monomial[0]).issubset(set(subset))

        t1 = [
            list(filter(partial(monomial_contained, subset=s), clauses_variables_only))
            for s in s2
        ]

        # optimization: record vars:clauses in a dictionary for redundant cases

        #########
        ######### STEP 4
        #########

        t2 = []

        for collection in t1:

            abort = False

            for clause in collection:

                if abort:
                    break

                negative_anf = list(cnf_to_neg_anf(list(clause[1])))

                for monomial in negative_anf:

                    m_set = set(monomial)
                    excluding_set = set(clause[0]) - m_set

                    m1 = (monomial,)
                    R = list(distribute(excluding_set))

                    count = sum(
                        [
                            (tuple(sorted(m1m2)) in ciphertext)
                            for m1m2 in product_simplify(m1, R)
                        ]
                    )

                    if count / len(R) < 1/4:
                        abort = True
                        break

            t2.append(collection)
        return t2


def _linearization(ciphertext_file, clauses_file):

    clauses = _variables_sets(ciphertext_file, clauses_file)
    for x in clauses:
        print(x)

    # rows = len(a_terms.keys())
    # cols = coefficient_count

    # a = np.zeros((rows, cols), dtype=np.int64)
    # b = np.zeros(rows, dtype=np.int64)

    # for i, term in enumerate(a_terms):

    #     a[i] = clause_vector(a_terms[term], cols)
    #     b[i] = int(term in ciphertext)
    #     if sum(a[i]) == 0 and b[i] == 1:
    #         return -4

    # GF = galois.GF(2)
    # a = GF(a)
    # b = GF(b)

    # rank_a = np.linalg.matrix_rank(a)
    # augmented_matrix = np.hstack((a, b.reshape(-1, 1)))
    # rank_augmented = np.linalg.matrix_rank(augmented_matrix)
    # y = int(rank_a != rank_augmented)

    # return y


def attack(args):

    CIPHERTEXT_DIRPATH = f"tests/c_{args.i}"
    CIPHERTEXT_FILEPATH = f"{CIPHERTEXT_DIRPATH}/ciphertext_{args.i}.hdf5"
    CLAUSES_FILEPATH = f"{CIPHERTEXT_DIRPATH}/clauses_{args.i}.txt"

    with h5py.File(CIPHERTEXT_FILEPATH, "r") as CIPHERTEXT_FILE:
        with open(CLAUSES_FILEPATH, "r") as CLAUSES_FILE:
            y = _linearization(CIPHERTEXT_FILE, CLAUSES_FILE)
            return y


def main():
    parser = argparse.ArgumentParser(prog="Attack")
    parser.add_argument("i", type=int)
    args = parser.parse_args()
    y = attack(args)
    print(y)


if __name__ == "__main__":
    main()
