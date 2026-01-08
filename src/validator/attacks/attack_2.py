import argparse
import os
import sys
import galois
import h5py
import numpy as np
import itertools
from ..parameters import *
from ..helpers import *

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def _literals_sets(ciphertext_file, clauses_file):

    if "ciphertext" in ciphertext_file:
        ciphertext = ciphertext_file["ciphertext"][:]
        k = np.arange(2, M+1)
        # s_1 = [np.unique(np.concatenate(x)) for x in itertools.combinations(ciphertext, 2)]
        # s_1 = [set(np.concatenate(x)) for x in itertools.combinations(ciphertext, 2)]
        s_1 = [
            set(np.concatenate(x)).union()
            # a         ->
            # b         ->
            # c         ->
            for x in itertools.combinations(ciphertext, 2)
        ]

        # For each variable in s,
        # for each clause from the public key that shares a variable with s,
        # union the variables in that clause with s.
        print(s_1)


def _recover_plaintext(ciphertext_file, clauses_file):

    clauses = _literals_sets(ciphertext_file, clauses_file)

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
            y = _recover_plaintext(CIPHERTEXT_FILE, CLAUSES_FILE)
            return y


def main():
    parser = argparse.ArgumentParser(prog="Attack")
    parser.add_argument("i", type=int)
    args = parser.parse_args()
    y = attack(args)
    print(y)


if __name__ == "__main__":
    main()
