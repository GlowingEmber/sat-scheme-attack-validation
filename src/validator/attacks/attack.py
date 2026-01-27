import argparse
import os
import sys
import h5py
import ast
import numpy as np
from collections import defaultdict
from itertools import combinations, product as cartesian
import galois
from ..parameters import *
from ..helpers import *
import secrets

secure = secrets.SystemRandom()

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def _variables_sets(ciphertext_file, public_key_file):

    if "ciphertext" not in ciphertext_file:
        raise KeyError()

    public_key_incl_sign = [tuple(c) for c in ast.literal_eval(public_key_file.read())]
    public_key = [(tuple(zip(*c))[0], c) for c in public_key_incl_sign]
    ciphertext = set(tuple(m) for m in ciphertext_file["ciphertext"][:])

    ciphertext_generator = (set((int(v) for v in m)) for m in ciphertext)
    s = (subset[0] | subset[1] for subset in combinations(ciphertext_generator, 2))

    print(0)

    clauses_sharing_variable__dict = dict(
        [
            (
                v,
                set(filter(lambda m: v in m[0], public_key)),
            )
            for v in range(2, N + 2)
        ]
    )

    print(clauses_sharing_variable__dict)

    print(1)

    s_prime = (
        (
            s_i | set().union(*(set(c[0]) for c in clauses_sharing_variable__dict[v]))
            for v in s_i
        )
        for s_i in s
    )

    print(2)

    def get_clause_group(s_prime_i_vars__set):

        beta_group_superset = flatten(
            *(clauses_sharing_variable__dict[v] for v in s_prime_i_vars__set)
        )

        beta_group = list(
            filter(lambda c: set(c[0]) <= s_prime_i_vars__set, beta_group_superset)
        )

        return beta_group

    t = (get_clause_group(s_prime_i) for s_prime_i in flatten.from_iterable(s_prime))

    t_prime = []

    for i, t_i in enumerate(t):

        keep = False

        ######### 1
        
        c_1_incl_sign = t_i[1]
        neg_anf = cnf_to_neg_anf(list(c_1_incl_sign))
        m_star = set(secure.choice(neg_anf))

        ######### 2

        t_i_all_vars = set(flatten(*(c[0] for c in t_i)))
        vars_excluding_c_1 = list(t_i_all_vars - m_star)

        ######### 3

        sampled_count = 0
        sampled_monomials = []
        appeared_count = 0

        def _sample():
            m = secure.sample(
                vars_excluding_c_1,
                secure.randint(0, len(vars_excluding_c_1))
            )

            return tuple(np.array(sorted(m)))
        
        sample_size = min(
            100,
            2 ** len(vars_excluding_c_1)
        )
        

        for _ in range(sample_size):

            m = _sample()
            while (m in sampled_monomials):
                m = _sample()

            appeared_count += int(m in ciphertext)
            sampled_count += 1
            sampled_monomials.append(m)

            ######### 4

            if appeared_count >= 30:
                keep = True
                break
            if sampled_count >= 100:
                break
        
        print(keep)
        if keep:
            t_prime.append(t_i)

    print(t_prime)



def _linearization(ciphertext_file, public_key_file):
    t = _variables_sets(ciphertext_file, public_key_file)


def attack(args):

    CIPHERTEXT_DIRPATH = f"tests/c_{args.i}"
    CIPHERTEXT_FILEPATH = f"{CIPHERTEXT_DIRPATH}/ciphertext_{args.i}.hdf5"
    CLAUSES_FILEPATH = f"{CIPHERTEXT_DIRPATH}/public_key_{args.i}.txt"

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
