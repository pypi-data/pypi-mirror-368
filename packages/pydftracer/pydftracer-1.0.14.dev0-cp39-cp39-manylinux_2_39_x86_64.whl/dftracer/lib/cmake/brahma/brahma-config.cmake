# This will create IMPORTED targets for Brahma. The executables will be
# brahma::<exe-name>-bin (e.g., brahma::brahma-bin) and the library will
# be brahma::brahma.

include("${CMAKE_CURRENT_LIST_DIR}/brahma-config-version.cmake")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/modules")
list(APPEND CMAKE_MODULE_PATH "")

#include(GNUInstallDirs)
include(ExternalProject)
include(brahma-utils)
include(CMakePackageConfigHelpers)


set(BRAHMA_VERSION ${PACKAGE_VERSION})

# Record compiler information
set(BRAHMA_C_COMPILER "/usr/bin/cc")
set(BRAHMA_CXX_COMPILER "/usr/bin/c++")

set(BRAHMA_C_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations")
set(BRAHMA_CXX_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wnon-virtual-dtor -Wno-deprecated-declarations")

set(BRAHMA_C_STANDARD "11")
set(BRAHMA_CXX_STANDARD "17")

set(CMAKE_C_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Record the various flags and switches accumlated in BRAHMA
set(BRAHMA_GNU_LINUX )
set(BRAHMA_HAS_STD_FILESYSTEM TRUE)
set(BRAHMA_HAS_STD_FSTREAM_FD TRUE)

# Setup dependencies



####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was brahma-config.cmake.install.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../../../../../../../lib.linux-x86_64-3.9/dftracer" ABSOLUTE)

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

# Now actually import the BRAHMA target
set(_TMP_INCLUDE_DIRS "/home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-3.9/dftracer/include")
foreach (_DIR ${_TMP_INCLUDE_DIRS})
  set_and_check(_INCLUDE_DIR "${_DIR}")
  list(APPEND BRAHMA_INCLUDE_DIRS "${_INCLUDE_DIR}")
endforeach (_DIR "${_TMP_INCLUDE_DIRS}")

set(_TMP_LIBRARY_DIRS "")
foreach (_DIR ${_TMP_LIBRARY_DIRS})
  set_and_check(_LIBRARY_DIR "${_DIR}")
  list(APPEND BRAHMA_LIBRARY_DIRS "${_LIBRARY_DIR}")
endforeach (_DIR ${_TMP_LIBRARY_DIRS})

if (NOT TARGET brahma::brahma)
  include(${CMAKE_CURRENT_LIST_DIR}/brahma-targets.cmake)
endif (NOT TARGET brahma::brahma)


find_package(gotcha 2.1.2 REQUIRED)
if (${gotcha_FOUND})
    message(STATUS "[Brahma] found gotcha at ${gotcha_INCLUDE_DIRS}")
    include_directories(${gotcha_INCLUDE_DIRS})
    target_link_libraries(brahma INTERFACE ${gotcha_LIBRARIES})
else ()
    message(FATAL_ERROR "-- [Brahma] gotcha is needed for ${PROJECT_NAME} build")
endif ()

set(BRAHMA_INCLUDE_MPI OFF)
if (BRAHMA_INCLUDE_MPI)
  find_package(MPI COMPONENTS CXX REQUIRED)
  if (MPI_FOUND)
        message(STATUS "[Brahma] found mpi.h at ${MPI_CXX_INCLUDE_DIRS}")
        include_directories(${MPI_CXX_INCLUDE_DIRS})
        target_link_libraries(brahma INTERFACE ${MPI_CXX_LIBRARIES})
    else ()
        message(FATAL_ERROR "-- [Brahma] mpi is needed for ${PROJECT_NAME} build")
    endif ()
endif()

set(BRAHMA_LOGGER NONE)
if (BRAHMA_LOGGER STREQUAL "CPP_LOGGER")
    find_package(cpp-logger REQUIRED
                 HINTS ${CPP_LOGGER_DIR} ${cpp-logger_DIR}
                       ${CPP_LOGGER_PATH} ${cpp-logger_PATH}
                       $ENV{CPP_LOGGER_DIR} $ENV{cpp-logger_DIR}
                       $ENV{CPP_LOGGER_PATH} $ENV{cpp-logger_PATH})
    if (${cpp-logger_FOUND})
        message(STATUS "[Brahma] found cpp-logger at ${CPP_LOGGER_INCLUDE_DIRS}")
        include_directories(SYSTEM ${CPP_LOGGER_INCLUDE_DIRS})
        target_link_libraries(brahma INTERFACE ${CPP_LOGGER_LIBRARIES})
    else ()
        message(FATAL_ERROR "-- [Brahma] cpp-logger is not found but selected in cmake options for Brahma build")
    endif ()
endif()

check_required_components(brahma)

set(BRAHMA_LIBRARIES brahma)
