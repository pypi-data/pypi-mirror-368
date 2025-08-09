# This will create IMPORTED targets for Cpp_logger. The executables will be
# cpp-logger::<exe-name>-bin (e.g., cpp-logger::cpp-logger-bin) and the library will
# be cpp-logger::cpp-logger.

include("${CMAKE_CURRENT_LIST_DIR}/cpp-logger-config-version.cmake")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/modules")
list(APPEND CMAKE_MODULE_PATH "")

#include(GNUInstallDirs)
include(ExternalProject)
include(cpp-logger-utils)
include(CMakePackageConfigHelpers)


set(CPP_LOGGER_VERSION ${PACKAGE_VERSION})

# Record compiler information
set(CPP_LOGGER_C_COMPILER "/usr/bin/cc")
set(CPP_LOGGER_CXX_COMPILER "/usr/bin/c++")

set(CPP_LOGGER_C_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations")
set(CPP_LOGGER_CXX_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wnon-virtual-dtor -Wno-deprecated-declarations")

set(CPP_LOGGER_C_STANDARD "11")
set(CPP_LOGGER_CXX_STANDARD "17")

set(CMAKE_C_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Record the various flags and switches accumlated in CPP_LOGGER
set(CPP_LOGGER_GNU_LINUX )

# Setup dependencies



####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was cpp-logger-config.cmake.install.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../../../../../../../lib.linux-x86_64-cpython-310/dftracer" ABSOLUTE)

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

# Now actually import the CPP_LOGGER target
set(_TMP_INCLUDE_DIRS "/home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-cpython-310/dftracer/include")
foreach (_DIR ${_TMP_INCLUDE_DIRS})
  set_and_check(_INCLUDE_DIR "${_DIR}")
  list(APPEND CPP_LOGGER_INCLUDE_DIRS "${_INCLUDE_DIR}")
endforeach (_DIR "${_TMP_INCLUDE_DIRS}")

set(_TMP_LIBRARY_DIRS "")
foreach (_DIR ${_TMP_LIBRARY_DIRS})
  set_and_check(_LIBRARY_DIR "${_DIR}")
  list(APPEND CPP_LOGGER_LIBRARY_DIRS "${_LIBRARY_DIR}")
endforeach (_DIR ${_TMP_LIBRARY_DIRS})

if (NOT TARGET cpp-logger::cpp-logger)
  include(${CMAKE_CURRENT_LIST_DIR}/cpp-logger-targets.cmake)
endif (NOT TARGET cpp-logger::cpp-logger)

check_required_components(cpp-logger)

set(CPP_LOGGER_LIBRARIES cpp-logger)
