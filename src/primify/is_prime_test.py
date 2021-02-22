import ctypes

lib = ctypes.cdll.LoadLibrary('primeLib.so')

class primeLib(object):
    def __init__(self):
        self.obj = lib.PrimalityTests_new()
    
    def is_prime(self,n):
        lib.PrimalityTests_is_prime.restype = ctypes.c_bool
        return lib.PrimalityTests_is_prime(self.obj, ctypes.c_long(n))

p = primeLib()
for i in range(50,100):
    print(i,p.is_prime(i))
# print(p.is_prime(5))

# print(p.is_prime(91))