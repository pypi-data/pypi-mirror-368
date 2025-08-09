#ifndef BRAHMA_CONFIG_HPP
#define BRAHMA_CONFIG_HPP

/* Version string for BRAHMA */
#define BRAHMA_PACKAGE_VERSION "2.2.0"
/* #undef BRAHMA_GIT_VERSION */

#define BRAHMA_GET_VERSION(MAJOR, MINOR, PATCH) (MAJOR * 100000 + MINOR * 100 + PATCH)
#define BRAHMA_VERSION (BRAHMA_GET_VERSION (0, 0, 10))
#define BRAHMA_VERSION_MAJOR (BRAHMA_VERSION / 100000)
#define BRAHMA_VERSION_MINOR ((BRAHMA_VERSION / 100) % 1000)
#define BRAHMA_VERSION_PATCH (BRAHMA_VERSION % 100)


/* Compiler used */
#define CMAKE_BUILD_TYPE "Release"

#define CMAKE_C_COMPILER "/usr/bin/cc"
#define CMAKE_C_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations"
#define CMAKE_C_FLAGS_DEBUG "-g"
#define CMAKE_C_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG"
#define CMAKE_C_FLAGS_RELEASE " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations_RELEASE"

#define CMAKE_CXX_COMPILER "/usr/bin/c++"
#define CMAKE_CXX_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wnon-virtual-dtor -Wno-deprecated-declarations"
#define CMAKE_CXX_FLAGS_DEBUG "-g"
#define CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG"
#define CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG"

/* #undef CMAKE_C_SHARED_LIBRARY_FLAGS */
/* #undef CMAKE_CXX_SHARED_LIBRARY_FLAGS */

/* Macro flags */
/* #undef BRAHMA_GNU_LINUX */
#define BRAHMA_HAS_STD_FILESYSTEM 1
#define BRAHMA_HAS_STD_FSTREAM_FD 1
/* #undef BRAHMA_ENABLE_MPI */
// Logger
/* #undef BRAHMA_LOGGER_CPP_LOGGER */
// Logger level
/* #undef BRAHMA_LOGGER_NO_LOG */
#define BRAHMA_LOGGER_LEVEL_ERROR 1
#define BRAHMA_LOGGER_LEVEL_WARN 1
/* #undef BRAHMA_LOGGER_LEVEL_INFO */
/* #undef BRAHMA_LOGGER_LEVEL_DEBUG */
/* #undef BRAHMA_LOGGER_LEVEL_TRACE */


//==========================
// Common macro definitions
//==========================

#define BRAHMA_PATH_DELIM "/"

// #define BRAHMA_NOOP_MACRO do {} while (0)
#define BRAHMA_NOOP_MACRO

// Detect VAR_OPT
// https://stackoverflow.com/questions/48045470/portably-detect-va-opt-support
#if __cplusplus <= 201703 && defined __GNUC__ && !defined __clang__ && \
    !defined __EDG__
#define VA_OPT_SUPPORTED false
#else
#define PP_THIRD_ARG(a, b, c, ...) c
#define VA_OPT_SUPPORTED_I(...) PP_THIRD_ARG(__VA_OPT__(, ), true, false, )
#define VA_OPT_SUPPORTED VA_OPT_SUPPORTED_I(?)
#endif

#if !defined(BRAHMA_HASH_SEED) || (BRAHMA_HASH_SEED <= 0)
#define BRAHMA_SEED 104723u
#endif

#endif /* BRAHMA_CONFIG_H */
