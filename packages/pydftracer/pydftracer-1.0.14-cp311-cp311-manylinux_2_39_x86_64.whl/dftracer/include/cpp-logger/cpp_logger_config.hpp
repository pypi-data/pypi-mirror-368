#ifndef CPP_LOGGER_CONFIG_HPP
#define CPP_LOGGER_CONFIG_HPP

/* Version string for CPP_LOGGER */
#define CPP_LOGGER_PACKAGE_VERSION @CPP_LOGGER_PACKAGE_VERSION @
/* #undef CPP_LOGGER_GIT_VERSION */

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
/* #undef CPP_LOGGER_GNU_LINUX */
#define CPP_LOGGER_GET_VERSION(MAJOR, MINOR, PATCH) (MAJOR * 100000 + MINOR * 100 + PATCH)
#define CPP_LOGGER_VERSION (CPP_LOGGER_GET_VERSION (0, 0, 4))
#define CPP_LOGGER_VERSION_MAJOR (CPP_LOGGER_VERSION / 100000)
#define CPP_LOGGER_VERSION_MINOR ((CPP_LOGGER_VERSION / 100) % 1000)
#define CPP_LOGGER_VERSION_PATCH (CPP_LOGGER_VERSION % 100)

#endif /* CPP_LOGGER_CONFIG_H */
