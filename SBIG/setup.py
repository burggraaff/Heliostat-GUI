from setuptools import setup, Extension
import numpy

Sbigudrv_module = Extension('_Sbigudrv',
                           sources=['Sbigudrv_wrap.c'],libraries=['Sbigudrv'],include_dirs=[numpy.get_include()],
                           )
						   

setup (name = 'example',
       version = '0.1',
       author      = "SWIG Docs",
       description = """Simple swig example from docs""",
       ext_modules = [Sbigudrv_module],
	   py_modules = ["Sbigudrv"],
       )
