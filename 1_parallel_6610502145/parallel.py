from calendar import c
from linecache import cache
from mpi4py import MPI
from sys import argv
from math import sqrt
import numpy as np
from numpy._typing import DTypeLike


def factor(num, start, end):
    # init value
    factor_list = np.zeros(0, dtype=int)
    for i in range(start, end):
        if num % i == 0:
            factor_list = np.append(factor_list, i)

    return factor_list


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    number = int(argv[1])
    limit = int(sqrt(number)) + 1

    # split side for process
    chunk = limit // size
    start = rank * chunk + 2
    end = (rank + 1) * chunk + 2 if rank != size - 1 else limit

    local_factors = factor(number, start, end)
    all_factors = comm.gather(local_factors, root=0)

    if rank == 0:
        # รวม array ทั้งหมดเป็นอันเดียว
        all_factors = np.concatenate(all_factors)
        all_factors = np.unique(all_factors)
        print(f"Factors of {number}: {all_factors}")


if __name__ == "__main__":
    main()
