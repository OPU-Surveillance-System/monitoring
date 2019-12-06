from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
# from Cython.Build import cythonize
from Cython.Compiler import Options

Options.annotate = True

# ext_modules = [Extension('vrp_firefly', ['vrp_firefly.pyx'])]
# setup(
#     name        ='vrp app',
#     cmdclass    ={'build_ext':build_ext},
#     ext_modules =ext_modules
# )
ext_modules = [Extension("vrp_firefly", ["vrp_firefly.pyx"], language="c++")]
# ext_modules = [Extension("test", ["test.pyx"], language="c++")]

setup(
    # name        ='vrp firefly app',
    cmdclass    ={'build_ext':build_ext},
    ext_modules =ext_modules
)
