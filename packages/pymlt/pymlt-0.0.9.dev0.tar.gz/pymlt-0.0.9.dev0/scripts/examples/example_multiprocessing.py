"""
example multiprocessing
- https://sebastianraschka.com/Articles/2014_multiprocessing.html
- https://tutorialedge.net/python/python-multiprocessing-tutorial/
"""

import multiprocessing as mp
import time

import pandas as pd


def hf(x):
    """
    heavy function that needs parallel processing
    """
    r = x**x
    time.sleep(2)
    print(x, round(time.perf_counter(), 5))
    return x, r


def main():
    # check available cores
    n_cores = mp.cpu_count()
    print(n_cores)
    n_cores = 8

    # create pool with n_cores
    pool = mp.Pool(n_cores)

    if False:
        print("map")
        # map() obtains results in a particular order
        output = pool.map(hf, list(range(10, 21, 1)))
        df = pd.DataFrame({"output": output})

    if True:
        print("async")
        # apply_async() obtains results as soon as they are finished
        results = [pool.apply_async(hf, args=(x,)) for x in range(10, 21, 1)]
        output = [p.get() for p in results]
        df = pd.DataFrame({"output": output})

    # terminate pool
    pool.terminate()

    return df


if __name__ == "__main__":
    start = time.perf_counter()
    print(main())
    print("total duration", round(time.perf_counter() - start, 5))
