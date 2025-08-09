import os
import sys
import platform
import subprocess
import shutil, glob
from pathlib import Path

import numpy
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize

# I want to use cmake for Fortran Extension and the usual setuptools Extension for cython and C
# we need a CmakeExtension and a build_ext that disciminates between them
# in .run the corresponding build step is done


class CMakeExtension(Extension):
    """Define Cmake extension class """
    def __init__(self, name, sourcedir=''):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.isCmakeExtension=True


class CMakeBuild(build_ext):
    """ Build with cmake """
    def run(self):
        """ For above CmakeExtension Class call cmake.
        For other Extensions run normal run
        """
        allextensions = self.extensions
        cextensions = []
        for ext in allextensions:
            if hasattr(ext, 'isCmakeExtension'):
                try:
                    self.build_CmakeExtension(ext)
                except subprocess.CalledProcessError:
                    UserWarning('compilation of ' + ext.name + ' failed. Fortran cannot be used. '
                                'Check if f2py and Fortran compiler are present.  ')
            else:
                cextensions.append(ext)
        # now build all NOT CmakeExtensions
        self.extensions = cextensions
        super().run()

    def build_CmakeExtension(self, ext):
        # path were the final .so will be placed
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,]

        # force cmake to use the calling python
        cmake_args += [f'-DPython3_EXECUTABLE={sys.executable}']

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        env = os.environ.copy()

        if platform.system() == "Windows":
            # not tested for Windows
            if 'CC' not in env:
               cmake_args += ['-G', "MinGW Makefiles"]
            cmake_args += ['-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE']
            
            gf = shutil.which('gfortran')
            gf = glob.glob(gf+'*')  # get installed versions
            gf.sort(key=lambda a: float('0'+''.join(filter(str.isdigit, a))))  # get highest version
            gf = gf[-1] 
            gfdir = os.path.dirname(gf)
            cmake_args += ['-DCMAKE_LIBRARY_PATH='+gfdir]
            cmake_args += ['-DCMAKE_FIND_DEBUG_MODE=ON']
            # cmake_args += ['-D CMAKE_{C,CXX,FC}_FLAGS=-m64']
            
            # still we get the error
            # ImportError: DLL load failed while importing fscatter: The specified module could not be found
            
            # build_args += ['-Wl, -Bstatic -lgfortran', '-Wl, -Bstatic -lgcc_s_seh']
        elif platform.system() == "Darwin":
            if 'CC' not in env:
                # find newest gcc on gfortran path
                # typically gfortran is installed with gcc and we need the last gcc-xx, gfortran-xx
                gf = shutil.which('gfortran')
                gf = glob.glob(gf+'*')  # get installed versions
                gf.sort(key=lambda a: float('0'+''.join(filter(str.isdigit, a))))  # get highest version
                gf = gf[-1]
                if os.path.islink(gf):
                    gf = os.readlink(gf)

                env['FC'] = gf
                env['CC'] = gf.replace('gfortran', 'gcc')
                env['CXX'] = gf.replace('gfortran', 'g++')

        else:
            # Linux is working if gcc is installed
            pass
        # add optional compiler flags
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg, ]

        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)

        subprocess.run(['cmake', ext.sourcedir] + cmake_args, cwd=build_temp, env=env, check=True)
        subprocess.run(['cmake', '--build', '.'] + build_args, cwd=build_temp, check=True)


EXTENSIONS = []
# cython and c compilation
c_extensions = [Extension(name='jscatter.libs.cubature._cubature',
                          sources=[
                              'src/jscatter/libs/cubature/cpackage/hcubature.c',
                              'src/jscatter/libs/cubature/cpackage/pcubature.c',
                              'src/jscatter/libs/cubature/get_ptr.c',
                              'src/jscatter/libs/cubature/_cubature.pyx',
                          ],
                          include_dirs=[numpy.get_include()],
                          language='c'),
                Extension('jscatter.libs.cubature._test_integrands',
                          sources=['src/jscatter/libs/cubature/_test_integrands.pyx'],
                          include_dirs=[numpy.get_include()],
                          language='c'),
                ]
EXTENSIONS.extend(cythonize(c_extensions, compiler_directives={'linetrace': True,
                                                               'language_level': "3"}))

EXTENSIONS.append(Extension(name='jscatter.libs.surface',
                             sources=['src/jscatter/source/SASA_surface.c'],
                             extra_compile_args=[],
                             include_dirs=['Include', '/usr/local/include']))
#EXTENSIONS = []
EXTENSIONS.append(CMakeExtension(name='jscatter.libs.fscatter', sourcedir='src/jscatter/source'))


setup(
    cmdclass=dict(build_ext=CMakeBuild),
    ext_modules=EXTENSIONS,
    )


