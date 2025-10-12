import math
import random
import time

from mpi4py import MPI


# this code reference from https://www.youtube.com/watch?v=7lhlJTtCsiw
class PollardRho:
    """
    Class implementing Pollard's Rho algorithm for integer factorization
    1. Choose a function f(x) = (x^2 + c) mod
    2. Initialize two variables x and y to some starting value (e.g., 2)
    3. Initialize a variable d to 1 (this will hold the gcd)
    4. Repeat until d is a non-trivial factor of n or a maximum number
    """
    def __init__(self, max_iterations=10000):
        """
        Initialize the Pollard's Rho algorithm
        :param max_iterations:
        """
        self.max_iterations = max_iterations
        self.factors = []

    def gcd(self, a, b):
        """
        Compute the greatest common divisor using the Euclidean algorithm
        :param a:
        :param b:
        :return:
        """
        while b:
            a, b = b, a % b
        return a

    def g(self, x, n, c=1):
        """
        Polynomial function for generating the sequence
        :param x:
        :param n:
        :param c:
        :return:
        """
        return (x * x + c) % n

    def is_prime(self, n):
        """
        Check if a number is prime
        :param n : int
        :return:
        """
        if n <= 1:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True

    def pollard_rho(self, n, x0=2, c=1):
        """
        Pollard's Rho algorithm to find a non-trivial factor of n
        :param n:
        :param x0:
        :param c:
        :return:
        """
        if n <=1:
            return None
        if n % 2 == 0:
            return 2
        if self.is_prime(n):
            return n

#        initial value tortise and hare
        tortise = x0
        hare = x0
        d = 0
        iteration = 0

#         algorithm pollard rho
        while d == 0 and iteration < self.max_iterations:
            iteration += 1
            tortise = self.g(tortise, n, c)
            hare = self.g(self.g(hare, n, c), n, c)
            d = self.gcd(abs(tortise - hare), n)

        if d == n or d == 0 or iteration >= self.max_iterations:
            return None
        return d if d > 1 else None

    def factorize(self, n):
        """
        Factorize n into prime factors using Pollard's Rho algorithm sequentially.
        :param n:
        :return:
        """
        if n <= 1:
            return []
        if self.is_prime(n):
            return [n]

        factors = []
        to_factor = [n]

        while to_factor:
            current = to_factor.pop()
            if self.is_prime(current):
                factors.append(current)
                continue

            factor = None
            x0 = 2
            c = 1
            while factor is None:
                factor = self.pollard_rho(current, x0, c)
                if factor is None:
                    c += 1 # Try next c

            if factor == current:
                factors.append(current)
            else:
                to_factor.append(factor)
                to_factor.append(current // factor)

        return sorted(factors)


# this is version of parallel pollard rho using mpi4py
class ParallelFactorizer:
    """
    Class to perform parallel factorization using Pollard's Rho algorithm
    1. Distribute the search for different parameters (x0, c) across multiple
    processes using MPI.
    2. Each process runs the Pollard's Rho algorithm with its assigned parameters.
    3. Gather results from all processes to find a non-trivial factor.
    4. If a factor is found, return it; otherwise, continue searching with new
    parameters until a maximum number of iterations is reached.
    5. If no factor is found after exhausting all parameter combinations, return None.
    6. Use the found factor to recursively factor the number until all factors
    are prime.
    7. Return the list of prime factors.
    """
    def __init__(self):
        """
        Initialize MPI environment and PollardRho instance
        """
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        self.rho = PollardRho()

    def parallel_factorize(self, n):
        """
        Factorize n using parallel Pollard's Rho algorithm. Rank 0 orchestrates
        the factoring work; other ranks focus on search tasks.
        """
        if n <= 1:
            return []
        if self.rho.is_prime(n):
            return [n]

        if self.rank == 0:
            work_stack = [n]
            factors = []
        else:
            work_stack = None
            factors = None

        while True:
            current = None
            if self.rank == 0:
                while work_stack:
                    candidate = work_stack.pop()
                    if self.rho.is_prime(candidate):
                        factors.append(candidate)
                        continue
                    current = candidate
                    break
            current = self.comm.bcast(current, root=0)

            if current is None:
                break

            factor = self.parallel_search(current)

            if self.rank == 0:
                if factor is None or factor == current:
                    for sub_factor in self.rho.factorize(current):
                        factors.append(sub_factor)
                else:
                    work_stack.append(factor)
                    work_stack.append(current // factor)

        if self.rank == 0:
            result = sorted(factors)
        else:
            result = None
        result = self.comm.bcast(result, root=0)
        return result

    def parallel_search(self, n: int):
        """
        Use randomized parameters across ranks to search for a non-trivial
        factor, synchronizing via allreduce to detect success quickly.
        """
        if n % 2 == 0:
            return 2

        seed = int(time.time() * 1000) ^ (self.rank << 16)
        rng = random.Random(seed)

        batch_size = 256
        max_batches = 200
        sync_every = 16

        for b in range(max_batches):
            found_local = 0
            for _ in range(batch_size):
                x0 = rng.randrange(2, n - 1)
                c  = rng.randrange(1, n - 1)
                factor = self.rho.pollard_rho(n, x0, c)
                if factor and 1 < factor < n:
                    found_local = factor
                    break
            if (b % sync_every == 0) or found_local:
                global_found = self.comm.allreduce(found_local, op=MPI.MAX)
                if 1 < global_found < n:
                    return global_found

        return None
