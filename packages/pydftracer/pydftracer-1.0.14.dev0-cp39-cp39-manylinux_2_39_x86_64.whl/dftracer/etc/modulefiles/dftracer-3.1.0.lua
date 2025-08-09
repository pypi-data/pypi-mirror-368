-- LMod module file for DFTRACER

-- CMAKE_INSTALL_PREFIX: /home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-3.9/dftracer
-- CMAKE_BUILD_TYPE: Release
-- C Compiler: /usr/bin/cc
-- C FLAGS:  -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations
-- C FLAGS_DEBUG: -g
-- C FLAGS_RELWITHDEBINFO: -O2 -g -DNDEBUG
-- C FLAGS_RELEASE: -O3 -DNDEBUG
-- CXX Compiler: /usr/bin/c++
-- CXX FLAGS:  -Wno-empty-body -Wno-format-extra-args -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wnon-virtual-dtor -Wno-deprecated-declarations
-- CXX FLAGS_DEBUG: -g
-- CXX FLAGS_RELWITHDEBINFO: -O2 -g -DNDEBUG
-- CXX FLAGS_RELEASE: -O3 -DNDEBUG
-- DFTRACER_GNU_LINUX: TRUE
-- DFTRACER_HAS_DOXYGEN: 
-- DFTRACER_HAS_STD_FILESYSTEM: TRUE
-- DFTRACER_HAS_STD_FSTREAM_FD: TRUE

help(
[[
DYnamic and Asynchronous Data streamliner (DFTRACER) version (1, 0, 14).
]])

whatis("Package: DFTRACER")
whatis("Version: (1, 0, 14)")
whatis("Description: DYnamic and Asynchronous Data streamliner (DFTRACER).")
whatis("URL: https://github.com/flux-framework/dftracer")
whatis("CMAKE_INSTALL_PREFIX: /home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-3.9/dftracer")
whatis("CMAKE_BUILD_TYPE: Release")
whatis("C Compiler: /usr/bin/cc")
whatis("C FLAGS:  -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations")
whatis("C FLAGS_DEBUG: -g")
whatis("C FLAGS_RELWITHDEBINFO: -O2 -g -DNDEBUG")
whatis("C FLAGS_RELEASE: -O3 -DNDEBUG")
whatis("CXX Compiler: /usr/bin/c++")
whatis("CXX FLAGS:  -Wno-empty-body -Wno-format-extra-args -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wnon-virtual-dtor -Wno-deprecated-declarations")
whatis("CXX FLAGS_DEBUG: -g")
whatis("CXX FLAGS_RELWITHDEBINFO: -O2 -g -DNDEBUG")
whatis("CXX FLAGS_RELEASE: -O3 -DNDEBUG")
whatis("DFTRACER_GNU_LINUX: TRUE")
whatis("DFTRACER_HAS_DOXYGEN: ")
whatis("DFTRACER_HAS_STD_FILESYSTEM: TRUE")
whatis("DFTRACER_HAS_STD_FSTREAM_FD: TRUE")

prepend_path("PATH","/home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-3.9/dftracer/bin")
prepend_path("LD_LIBRARY_PATH","/home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-3.9/dftracer/lib")

pushenv("DFTRACER_DIR","/home/runner/work/dftracer/dftracer/build/lib.linux-x86_64-3.9/dftracer/")
