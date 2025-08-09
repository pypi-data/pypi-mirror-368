#ifndef DFTRACER_CONFIG_HPP
#define DFTRACER_CONFIG_HPP
// clang-format off
/* Version string for DFTRACER */
#define DFTRACER_PACKAGE_VERSION "3.1.0"
#define DFTRACER_GIT_VERSION "v1.0.14"
#define DFTRACER_GET_VERSION(MAJOR, MINOR, PATCH) (MAJOR * 100000 + MINOR * 100 + PATCH)
#define DFTRACER_VERSION (DFTRACER_GET_VERSION (1, 0, 14))
#define DFTRACER_VERSION_MAJOR (DFTRACER_VERSION / 100000)
#define DFTRACER_VERSION_MINOR ((DFTRACER_VERSION / 100) % 1000)
#define DFTRACER_VERSION_PATCH (DFTRACER_VERSION % 100)

/* Compiler used */
/* #undef DFTRACER_CMAKE_BUILD_TYPE */

/* #undef DFTRACER_CMAKE_C_COMPILER */
/* #undef DFTRACER_CMAKE_C_FLAGS */
/* #undef DFTRACER_CMAKE_C_FLAGS_DEBUG */
/* #undef DFTRACER_CMAKE_C_FLAGS_RELWITHDEBINFO */
/* #undef DFTRACER_CMAKE_C_FLAGS_RELEASE */

/* #undef DFTRACER_CMAKE_CXX_COMPILER */
/* #undef DFTRACER_CMAKE_CXX_FLAGS */
/* #undef DFTRACER_CMAKE_CXX_FLAGS_DEBUG */
/* #undef DFTRACER_CMAKE_CXX_FLAGS_RELWITHDEBINFO */
/* #undef DFTRACER_CMAKE_CXX_FLAGS_RELEASE */

/* #undef DFTRACER_CMAKE_C_SHARED_LIBRARY_FLAGS */
/* #undef DFTRACER_CMAKE_CXX_SHARED_LIBRARY_FLAGS */

/* Macro flags */
/* #undef DFTRACER_GNU_LINUX */
/* #undef DFTRACER_MPI_ENABLE */
/* #undef DFTRACER_FTRACING_ENABLE */
/* #undef DFTRACER_HWLOC_ENABLE */

//==========================
// Common macro definitions
//==========================

#define DFTRACER_PATH_DELIM "/"

// #define DFTRACER_NOOP_MACRO do {} while (0)
#define DFTRACER_NOOP_MACRO

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

#if !defined(DFTRACER_HASH_SEED) || (DFTRACER_HASH_SEED <= 0)
#define DFTRACER_SEED 104723u
#endif
// clang-format on
#endif /* DFTRACER_CONFIG_H */
