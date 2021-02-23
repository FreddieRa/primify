import ctypes

lib = ctypes.cdll.LoadLibrary('primeLib.so')

class primeLib(object):
    def __init__(self):
        self.obj = lib.PrimalityTests_new()
    
    def is_prime(self,n):
        lib.PrimalityTests_is_prime.restype = ctypes.c_bool
        return lib.PrimalityTests_is_prime(self.obj, ctypes.c_long(n))


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

    for _ in range(1, s):
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

# an 'almost certain' primality check


def is_prime(n):
    # Baillie-PSW
    # this is technically a probabalistic test, but there are no known pseudoprimes
    if not is_sprp(n):
        return False
    a = 5
    s = 2
    print(a,n,pow(a, (n-1) >> 1), legendre(a,n))
    while legendre(a, n) != n-1:
        s = -s
        a = s-a
        print(a,n,pow(a, (n-1) >> 1), legendre(a,n))
    return is_lucas_prp(n, a)

p = primeLib()
# for i in range(2,100):
#     print(i,p.is_prime(i),is_prime(i))
print(p.is_prime(41))
