import sys
import threading
import multiprocessing
import os
import time

# legendre symbol (a|m)
# note: returns m-1 if a is a non-residue, instead of -1
def legendre(a, m):
    return pow(a, (m-1) >> 1, m)

# strong probable prime


def is_sprp(n, b=2):
    d = n-1
    s = 0
    while d & 1 == 0:
        s += 1
        d >>= 1

    x = pow(b, d, n)
    if x == 1 or x == n-1:
        return True

    for r in range(1, s):
        x = (x * x) % n
        if x == 1:
            return False
        elif x == n-1:
            return True

    return False

# lucas probable prime
# assumes D = 1 (mod 4), (D|n) = -1


def is_lucas_prp(n, D):
    P = 1
    Q = (1-D) >> 2

    # n+1 = 2**r*s where s is odd
    s = n+1
    r = 0
    while s & 1 == 0:
        r += 1
        s >>= 1

    # calculate the bit reversal of (odd) s
    # e.g. 19 (10011) <=> 25 (11001)
    t = 0
    while s > 0:
        if s & 1:
            t += 1
            s -= 1
        else:
            t <<= 1
            s >>= 1

    # use the same bit reversal process to calculate the sth Lucas number
    # keep track of q = Q**n as we go
    U = 0
    V = 2
    q = 1
    # mod_inv(2, n)
    inv_2 = (n+1) >> 1
    while t > 0:
        if t & 1 == 1:
            # U, V of n+1
            U, V = ((U + V) * inv_2) % n, ((D*U + V) * inv_2) % n
            q = (q * Q) % n
            t -= 1
        else:
            # U, V of n*2
            U, V = (U * V) % n, (V * V - 2 * q) % n
            q = (q * q) % n
            t >>= 1

    # double s until we have the 2**r*sth Lucas number
    while r > 0:
        U, V = (U * V) % n, (V * V - 2 * q) % n
        q = (q * q) % n
        r -= 1

    # primality check
    # if n is prime, n divides the n+1st Lucas number, given the assumptions
    return U == 0


# primes less than 212
small_primes = set([
    2,  3,  5,  7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211])

# pre-calced sieve of eratosthenes for n = 2, 3, 5, 7
indices = [
    1, 11, 13, 17, 19, 23, 29, 31, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73, 79, 83,
    89, 97, 101, 103, 107, 109, 113, 121, 127, 131,
    137, 139, 143, 149, 151, 157, 163, 167, 169, 173,
    179, 181, 187, 191, 193, 197, 199, 209]

# distances between sieve values
offsets = [
    10, 2, 4, 2, 4, 6, 2, 6, 4, 2, 4, 6,
    6, 2, 6, 4, 2, 6, 4, 6, 8, 4, 2, 4,
    2, 4, 8, 6, 4, 6, 2, 4, 6, 2, 6, 6,
    4, 2, 4, 6, 2, 6, 4, 2, 4, 2, 10, 2]

max_int = 2147483647

# an 'almost certain' primality check


def is_prime(n):
    # Baillie-PSW
    # this is technically a probabalistic test, but there are no known pseudoprimes
    if not is_sprp(n):
        return False
    a = 5
    s = 2
    while legendre(a, n) != n-1:
        s = -s
        a = s-a
    return is_lucas_prp(n, a)

# next prime strictly larger than n


def next_prime(n, expected, progress, parallel=False):
    if n < 2:
        return 2
    # first odd larger than n
    n = (n + 1) | 1
    if n < 212:
        while True:
            if n in small_primes:
                return n
            n += 2

    # find our position in the sieve rotation via binary search
    x = int(n % 210)
    s = 0
    e = 47
    m = 24
    while m != e:
        if indices[m] < x:
            s = m
            m = (s + e + 1) >> 1
        else:
            e = m
            m = (s + e) >> 1

    number = int(n + (indices[m] - x))


    p = ProgressBar(expected)

    if (not parallel):
        # adjust offsets
        offs = offsets[m:]+offsets[:m]
        j = 1
        while True:
          for o in offs:
              if(progress): 
                  p.show(j)
              if is_prime(number):
                  return (number, j)
              number += o
              j += 1
    else:
        index = m

        tests = 0

        # Create a pool with a set number of workers
        pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())
        
        # This will need to be adapted based on size of number and available ram
        # TODO look into psutil library
        sizeOfArray = 10000     
        results = []

        # Create all of the jobs, which the pool will automatically assign free workers to
        for i in range(sizeOfArray):
            results.append(pool.apply_async(worker, (number,)))
            number += offsets[index % len(offsets)]
            index += 1

        running = True
        while running:
            j = 0
            # Continually loop through results, removing them if they're done and
            # not prime
            while j < len(results):
                result = results[j]
                if result.ready():
                    tests += 1
                    p.show(tests)
                    if result.get() == 0:
                        results.pop(j)
                        j -= 1
                    else:
                        prime = result.get()
                        pool.close()
                        pool.terminate()
                        running = False
                        break
                j += 1
            
            # If running out of jobs, add as many as expected to be required
            if len(results) < multiprocessing.cpu_count():
                for i in range(expected-tests):
                    results.append(pool.apply_async(worker, (number,)))
                    number += offsets[index % len(offsets)]
                    index += 1

        return (prime, tests)


def worker(num):
    if is_prime(num):
        return num
    else:
        return 0


class ProgressBar():
    def __init__(self, total, barLength=20):
        self.__total = total
        self.__barLength = barLength
        self.__current = 0
        
    def update(self):
        self.__current += 1
        self.show(self.__current)

    def getCurrent(self):
        return self.__current

    def show(self, num):
        percent = float(num) * 100 / self.__total
        arrow = '-' * int(percent/100 * self.__barLength - 1) + '>'
        spaces = ' ' * (self.__barLength - len(arrow))
        print('Progress: [%s%s] %d %% %s/%s' % (arrow, spaces, percent, num, self.__total), end='\r')
        sys.stdout.flush()

