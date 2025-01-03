#!/usr/bin/python

from setuptools import setup, Extension, find_packages
import glob
import os
import sys
from setuptools.command.build_ext import build_ext as build_ext_orig

import os
import pathlib

NAME = 'fann_homeassistant'
VERSION = '1.0.0'

LONG_DESCRIPTION = """\
    FANN Library for homeassistant.
    
    Compiles and generates the libraries for homeassistant.
    C Libraries are copied in to the custom_libraries/libfann folder
    and this folder is added to the os.path
"""

INSTALL_DIR = "custom_libraries/libfann"

class CMakeExtension(Extension):

    def __init__(self, name):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[])


class build_ext(build_ext_orig):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)
        super().run()

    def build_cmake(self, ext):
        cwd = pathlib.Path().absolute()

        # these dirs will be created in build_py, so if you don't have
        # any python sources to bundle, the dirs will be missing
        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name))
        extdir.mkdir(parents=True, exist_ok=True)


        os.chdir(str(build_temp))
        self.spawn(['cmake', str(cwd)+"/fann", '-DCMAKE_BUILD_TYPE=Debug'])
        
        self.spawn(['make', 'preinstall'])
        
        # Find the config folder
        installLoc = pathlib.Path("/").glob("**/config/deps")
        installLoc = pathlib.Path(list(installLoc)[0]).parent
        
        # Create install folder
        installLocStr = str(installLoc) + INSTALL_DIR;
        installLoc = pathlib.Path(installLocStr)
        installLoc.mkdir(parents=True, exist_ok=True)
        
        print("Install location: "+installLocStr)
        
        # Find all lib* files from compile
        libFiles = pathlib.Path(".").glob("src/lib*")
        print(list(libFiles))
        
        # Copy files
        for each in pathlib.Path(".").glob("src/lib*"):
            print("Copying "+str(each)+" to "+installLocStr)
            self.spawn(['cp', str(each), installLocStr])
        
        # Add to system path
        sys.path.append(installLocStr)
        os.chdir(str(cwd))

setup(
    name=NAME,
    description='Fast Artificial Neural Network Library (fann)',
    long_description=LONG_DESCRIPTION,
    version=VERSION,
    author='plutomedia987',
    include_package_data=True,
    packages=find_packages(),
    ext_modules=[CMakeExtension('fannlib_ha/'),
                
    ],
    cmdclass={
        'build_ext': build_ext,
    }
)