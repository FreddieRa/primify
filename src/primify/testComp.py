import ctypes

lib = ctypes.cdll.LoadLibrary('testLib.so')

class Test(object):
    def __init__(self):
        self.obj = lib.Foo_new()
    
    def bar(self):
        lib.Foo_bar(self.obj)

t = Test()
t.bar()

# import ctypes
# import pathlib

# if __name__ == "__main__":
#     # Load the shared library into ctypes
#     libname = pathlib.Path().absolute() / "testLib.so"
#     c_lib = ctypes.CDLL(libname)

#     c_lib.bar()


