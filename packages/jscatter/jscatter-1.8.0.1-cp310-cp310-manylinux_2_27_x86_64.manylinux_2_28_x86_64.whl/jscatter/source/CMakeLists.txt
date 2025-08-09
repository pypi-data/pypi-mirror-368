# inspired from
# https://numpy.org/devdocs/f2py/buildtools/cmake.html
# but added support for openmp and included the f2py generated wrappers which were missing in the target
# without wrappers we get undefined symbol error during import
# we define custom OUTPUTS and BYPRODUCTS that cmake generates dependencies automatically
cmake_minimum_required(VERSION 3.12) # Needed to avoid requiring embedded Python libs too

project(fscatter
  VERSION 1.0
  DESCRIPTION "jscatter.fscatter module"
  LANGUAGES C Fortran)

# Grab Python, 3.8 or newer
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module NumPy)

# find openmp and define some locations
find_package(OpenMP COMPONENTS Fortran )

# Grab variables from a local Python installation to find F2PY headers
execute_process(
  COMMAND "${Python3_EXECUTABLE}" -c "import numpy.f2py; print(numpy.f2py.get_include())"
  OUTPUT_VARIABLE F2PY_INCLUDE_DIR
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
# on windows we force the / separator from above output; on Linx its doing nothing
cmake_path(CONVERT "${F2PY_INCLUDE_DIR}" TO_CMAKE_PATH_LIST F2PY_INCLUDE_DIR)


# Print out the discovered paths and other stuff
include(CMakePrintHelpers)
cmake_print_variables(Python3_INCLUDE_DIRS)
cmake_print_variables(F2PY_INCLUDE_DIR)
cmake_print_variables(Python3_NumPy_INCLUDE_DIRS)
cmake_print_variables(CMAKE_CURRENT_BINARY_DIR)
cmake_print_variables(CMAKE_SOURCE_DIR)
cmake_print_variables(Python3_EXECUTABLE)
cmake_print_variables(CMAKE_PROJECT_NAME)
cmake_print_variables(GFORTRANLIB)
cmake_print_variables(CMAKE_LIBRARY_PATH)

# Common variables
set(f2py_module_name "fscatter")
# source files given explicit
set(fortran_src_files ${CMAKE_SOURCE_DIR}/a_typesandconstants.f95
                     ${CMAKE_SOURCE_DIR}/a_halton.f95
                     ${CMAKE_SOURCE_DIR}/a_qshep3d.f95
                     ${CMAKE_SOURCE_DIR}/autil.f95
                     ${CMAKE_SOURCE_DIR}/erfr.f90
                     ${CMAKE_SOURCE_DIR}/cloud.f95
                     ${CMAKE_SOURCE_DIR}/dynamic.f95)

set(f2py_module_c "${f2py_module_name}module.c")  # default name used in f2py

add_custom_target(
  genpyf
  DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/${f2py_module_c}"
)

# add f2py custom_command that creates the wrappers and f2py_module_c triggered by OUTPUT and BYPRODUCTS dependencies
# all three files need to be named as this marks them as GENERATED to avoid error as they are missing before build
add_custom_command(
  OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${f2py_module_c}"
  BYPRODUCTS "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-f2pywrappers.f"
             "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-f2pywrappers2.f90"
  COMMAND ${Python3_EXECUTABLE}  -m numpy.f2py
                   ${fortran_src_files}
                   -m "fscatter"
                   --lower                                  # important; name conversion for f2py
  DEPENDS "${fortran_src_files}"         # depend on fortran source files
)

# Set up target to build the library including the wrappers and f2py_module_c
Python3_add_library(${CMAKE_PROJECT_NAME} MODULE WITH_SOABI
  "${CMAKE_CURRENT_BINARY_DIR}/${f2py_module_c}" # Generated from above
  "${F2PY_INCLUDE_DIR}/fortranobject.c"          # From NumPy
  "${fortran_src_files}"                            # Fortran source(s)
  "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-f2pywrappers.f"         # Generated from above f2py
  "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-f2pywrappers2.f90"      # Generated from above f2py
)

# linking to the needed libraries
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE Python3::NumPy)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE OpenMP::OpenMP_Fortran)
add_dependencies(${CMAKE_PROJECT_NAME} genpyf)
# add include directories
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE "${F2PY_INCLUDE_DIR}")
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE "${OpenMP_Fortran_INCLUDE_DIRS}")
if(MSVC OR MSYS OR MINGW)
  cmake_print_variables('windows compiler' MSVC OR MSYS OR MINGW)
  # for detecting Windows compilers
  target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE libgfortran libgomp KERNEL32)
endif()
