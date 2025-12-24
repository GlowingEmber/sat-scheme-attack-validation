from matplotlib.pylab import beta
import numpy as np
import sklearn
import sklearn.cluster
from ..parameters import *
from ..helpers import *
import matplotlib.pyplot as plt

def _blr__simple(ciphertext_n__hdf5_file):
    if "ciphertext" in ciphertext_n__hdf5_file:

        ciphertext = ciphertext_n__hdf5_file["ciphertext"]
        ciphertext = np.array(ciphertext[:])
        ciphertext = map(tuple, ciphertext)

        lengths = map(len, ciphertext)

        ciphertext = zip(ciphertext, lengths)
        ciphertext, _ = zip(*filter(lambda x: x[1] > TERM_LENGTH_CUTOFF, ciphertext))
        ciphertext = set(ciphertext)

        groups = []

        while len(groups) < BETA and len(ciphertext) > 0:

            largest = max(ciphertext, key=len)
            group = set(largest)
            ciphertext.remove(largest)

            while True:

                if len(ciphertext) == 0:
                    groups.append(group)
                    group = set()
                    break

                closeness = np.fromiter(
                    map(lambda x: (x, len(group.difference(x))), ciphertext),
                    dtype=object,
                )

                closest = min(closeness, key=lambda x: x[1])

                MAX_DIFF_PCT = 0.5
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
    

def _blr__k_means(ciphertext_n__hdf5_file):

    if "ciphertext" in ciphertext_n__hdf5_file:

        ciphertext = ciphertext_n__hdf5_file["ciphertext"]
        ciphertext = ciphertext[:]
        dimensions = max([np.max(m) for m in ciphertext])

        def _monomial_to_vector(m):
            v = [0] * dimensions
            for l in m:
                v[l-1] = 1
            return np.array(v)
    
        ciphertext = list(map(_monomial_to_vector, ciphertext))
        ciphertext_vectors = np.array(ciphertext)
        ciphertext_vectors_copy = ciphertext
        # print(ciphertext)

        kmeans = sklearn.cluster.KMeans(n_clusters=BETA, random_state=0, n_init='auto')
        kmeans.fit(ciphertext_vectors_copy)

        
        # print(sorted(kmeans.cluster_centers_, reverse=True)[:BETA])
        _retrieve_values = lambda v: sorted(np.argsort(v)[::-1][:K*ALPHA] + 1)

        beta_literals_sets = [_retrieve_values(v) for v in kmeans.cluster_centers_]

        return beta_literals_sets