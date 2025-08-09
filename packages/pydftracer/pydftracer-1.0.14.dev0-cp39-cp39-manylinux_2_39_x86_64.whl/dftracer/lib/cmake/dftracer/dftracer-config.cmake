# This will create IMPORTED targets for dftracer. The executables will be
# the library will be dftracer.

include("${CMAKE_CURRENT_LIST_DIR}/dftracer-config-version.cmake")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/modules")
list(APPEND CMAKE_MODULE_PATH "")

#include(GNUInstallDirs)
include(ExternalProject)
include(dftracer-utils)
include(CMakePackageConfigHelpers)


set(DFTRACER_VERSION ${PACKAGE_VERSION})

# Record compiler information
set(DFTRACER_C_COMPILER "/usr/bin/cc")
set(DFTRACER_CXX_COMPILER "/usr/bin/c++")

set(DFTRACER_C_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations")
set(DFTRACER_CXX_FLAGS " -Wno-empty-body -Wno-format-extra-args -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wnon-virtual-dtor -Wno-deprecated-declarations")

set(DFTRACER_C_STANDARD "11")
set(DFTRACER_CXX_STANDARD "17")

set(CMAKE_C_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Record the various flags and switches accumlated in DFTRACER
set(DFTRACER_GNU_LINUX )
set(DFTRACER_HAS_STD_FILESYSTEM TRUE)
set(DFTRACER_HAS_STD_FSTREAM_FD TRUE)

# Setup dependencies



####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was dftracer-config.cmake.install.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../../../../../lib.linux-x86_64-3.9/dftracer" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

# Now actually import the DFTRACER target
set(_TMP_INCLUDE_DIRS "/home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-3.9/dftracer/include")
foreach (_DIR ${_TMP_INCLUDE_DIRS})
  set_and_check(_INCLUDE_DIR "${_DIR}")
  list(APPEND DFTRACER_INCLUDE_DIRS "${_INCLUDE_DIR}")
endforeach (_DIR "${_TMP_INCLUDE_DIRS}")

set(_TMP_LIBRARY_DIRS "")
foreach (_DIR ${_TMP_LIBRARY_DIRS})
  set_and_check(_LIBRARY_DIR "${_DIR}")
  list(APPEND DFTRACER_LIBRARY_DIRS "${_LIBRARY_DIR}")
endforeach (_DIR ${_TMP_LIBRARY_DIRS})

if (NOT TARGET dftracer)
  include(${CMAKE_CURRENT_LIST_DIR}/dftracer-targets.cmake)
endif (NOT TARGET dftracer)

find_package(brahma REQUIRED)
if (${brahma_FOUND})
    message(STATUS "[DFTRACER] found brahma at ${BRAHMA_INCLUDE_DIRS}")
    include_directories(${BRAHMA_INCLUDE_DIRS})
     target_link_libraries(dftracer INTERFACE ${BRAHMA_LIBRARIES})
else ()
    message(FATAL_ERROR "-- [DFTRACER] brahma is needed for ${PROJECT_NAME} build")
endif ()

find_package(yaml-cpp REQUIRED)
if (${yaml-cpp_FOUND})
    message(STATUS "[DFTRACER] found yaml-cpp at ${YAML_CPP_INCLUDE_DIR}")
    include_directories(${YAML_CPP_INCLUDE_DIR})
    set(YAML_CPP_LIBRARY_DIR "${YAML_CPP_CMAKE_DIR}/../../")
    target_link_libraries(dftracer INTERFACE -L${YAML_CPP_LIBRARY_DIR} ${YAML_CPP_LIBRARIES})
else ()
    message(FATAL_ERROR "-- [DFTRACER] yaml-cpp is needed for ${PROJECT_NAME} build")
endif ()

set(DFTRACER_INCLUDE_MPI OFF)
if (DFTRACER_INCLUDE_MPI)
  find_package(MPI COMPONENTS CXX REQUIRED)
  if (MPI_FOUND)
        message(STATUS "[DFTRACER] found mpi.h at ${MPI_CXX_INCLUDE_DIRS}")
        include_directories(${MPI_CXX_INCLUDE_DIRS})
        target_link_libraries(dftracer INTERFACE ${MPI_CXX_LIBRARIES})
    else ()
        message(FATAL_ERROR "-- [DFTRACER] mpi is needed for ${PROJECT_NAME} build")
    endif ()
endif()
set(DFTRACER_ENABLE_FTRACING OFF)
if (DFTRACER_ENABLE_FTRACING)
set(DFTRACER_FUNCTION_FLAGS "-g" "-finstrument-functions" "-Wl,-E" "-fvisibility=default")
else()
set(DFTRACER_FUNCTION_FLAGS )
endif()
check_required_components(dftracer)

set(DFTRACER_LIBRARIES dftracer)
