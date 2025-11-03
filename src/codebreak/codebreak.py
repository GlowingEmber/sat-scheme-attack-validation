import argparse
import os
import sys
import ast

from itertools import chain as flatten, combinations as subset, product as cartesian
from collections import defaultdict

from src.encrypt.encrypt import cnf_to_neg_anf, distribute

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from parameters import *

import h5py
import numpy as np

MAX_DIFF_PCT = 0.5


class Coefficient:
    def __init__(self, v):
        self.value = v

    def __repr__(self):
        return f"Coefficient(v={self.value})"


def recover_beta_literals(cipher_n__hdf5_file):
    if "expression" in cipher_n__hdf5_file:

        ciphertext = cipher_n__hdf5_file["expression"]
        ciphertext = np.array(ciphertext[:])
        ciphertext = map(tuple, ciphertext)

        lengths = map(len, ciphertext)

        ciphertext = zip(ciphertext, lengths)
        ciphertext, _ = zip(*filter(lambda x: x[1] > TERM_LENGTH_CUTOFF, ciphertext))
        ciphertext = set(ciphertext)

        groups = []

        while len(groups) < BETA:

            largest = max(ciphertext, key=len)
            group = set(largest)
            ciphertext.remove(largest)

            while True:

                closeness = map(lambda x: (x, len(group.difference(x))), ciphertext)
                closest = min(closeness, key=lambda x: x[1])

                max_diff = math.floor(MAX_DIFF_PCT * len(group))

                if closest[1] <= max_diff:
                    group = group.union(closest[0])
                    ciphertext.remove(closest[0])
                else:
                    groups.append(group)
                    group = set()
                    break

        beta_literals_sets = []
        for s in groups:
            beta_literals_sets.append(sorted([int(l) for l in s]))
        return sorted(beta_literals_sets)


def recover_plaintext(
    cipher_n__hdf5_file, clauses_n__txt_file, beta_literals_sets_n__txt_file
):
    
    beta_literals_sets = recover_beta_literals(cipher_n__hdf5_file)

    clauses = clauses_n__txt_file.read()

    # print("the beta literals sets found by recover_beta_literals():")
    # for x in beta_literals_sets:
    #     print([int(l) for l in x])

    # print("the real beta literals sets:")
    # real_beta_literals_sets = ast.literal_eval(beta_literals_sets_n__txt_file.read())
    # for x in real_beta_literals_sets:
    #     print(x)

    a_terms = defaultdict(list)

    coefficient_count = 0

    for beta_literals_set in beta_literals_sets:

        all_clauses = ast.literal_eval(clauses)
        possible_clauses = np.fromiter(
            filter(
                lambda c: all(map(lambda l: l in beta_literals_set, list(zip(*c))[0])),
                all_clauses,
            ),
            dtype=list,
        )

        if len(possible_clauses) < ALPHA:
            raise ValueError(f"<{ALPHA} clauses found")
        
        R_terms = np.fromiter(distribute(beta_literals_set), dtype=object)

        n = len(R_terms)
        coefficient_count += n
        

        v__cnf_to_neg_anf = np.vectorize(cnf_to_neg_anf)
        C = v__cnf_to_neg_anf(possible_clauses)

        for C_i in C:

            #####
            C_i = np.fromiter(C_i, dtype=object)
    
            #####
            R_i_terms = R_terms
            R_i_coefficients = map(lambda i: Coefficient(i), range(coefficient_count - n, coefficient_count))
            R_i = np.fromiter(zip(R_i_coefficients, R_i_terms), dtype=object)

            #####
            unformatted_C_iR_i = cartesian(R_i, C_i)
            C_iR_i = []


            for term in unformatted_C_iR_i:

                coefficient = term[0][0]
                literals = tuple(sorted([int(x) for x in set(term[0][1] + term[1])]))
                full_term = (coefficient, literals)

                C_iR_i.append(full_term)

            for term in C_iR_i:
                coefficient = term[0]
                literals = term[1]

                a_terms[literals].append(coefficient)
    

    def clause_vector(coefficients, cols):
        v = np.zeros(cols)
        for c in coefficients:
            v[c.value] = 1
            # NOTE: if we are using XOR we would do v[c.value] = int(not v[c.value])
            # whereas if we are using OR we would do v[c.value] = 1
        return v
    
    ciphertext = list(
        map(
            lambda t: tuple(sorted([np.int64(l) for l in t])),
            np.array(cipher_n__hdf5_file["expression"][:]),
        )
    )
    print("coefficient_count", coefficient_count) # unique r_is
    print("len(a_terms.keys())", len(a_terms.keys())) # unique monomials
    print("ciphertext", ciphertext)


    a_scalars__variable_bits = np.fromiter(a_terms.values(), dtype=object)
    a_vectors__monomials = np.fromiter(a_terms.keys(), dtype=object)

    rows = len(a_vectors__monomials)
    cols = coefficient_count
   
    a = np.zeros((rows,cols), dtype=np.int64)
    b = np.zeros(rows, dtype=np.int64)


    for i, m in enumerate(a_scalars__variable_bits):
        a[i] = clause_vector(m, cols)

    for i, m in enumerate(a_vectors__monomials):
        b[i] = int(m in ciphertext)

    # np.set_printoptions(threshold=sys.maxsize)
    print(a)
    print(b)



    # for i in range(len(a_monomials)):
    #     print(a_monomials[i])
    #     a[i] = clause_vector(a_monomials[i], coefficient_count)




    # try:
    #     sol = np.linalg.solve(lhs, rhs)
    #     print(sol)
    # except Exception as e:
    #     print(f"No solution: {e}")
    #     print(0)
    


def codebreak(n):
    cipher_n_dir = f"{os.environ.get("DATA_DIRECTORY")}/cipher_{n}_dir"
    cipher_n__hdf5 = f"{cipher_n_dir}/cipher_{n}.hdf5"
    clauses_n__txt = f"{cipher_n_dir}/clauses_{n}.txt"
    beta_literals_sets_n__txt = f"{cipher_n_dir}/beta_literals_sets_{n}.txt"

    with h5py.File(cipher_n__hdf5, "r") as cipher_n__hdf5_file:
        with open(clauses_n__txt, "r") as clauses_n__txt_file:
            with open(beta_literals_sets_n__txt, "r") as beta_literals_sets_n__txt_file:
                y = recover_plaintext(
                    cipher_n__hdf5_file,
                    clauses_n__txt_file,
                    beta_literals_sets_n__txt_file,
                )


###

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Encrypt",
        description="Generates ciphertext file from plaintext based on Sebastian E. Schmittner's SAT-Based Public Key Encryption Scheme",
        epilog="https://eprint.iacr.org/2015/771.pdf",
    )

    parser.add_argument("n", type=int)
    args = parser.parse_args()

    codebreak(args.n)
