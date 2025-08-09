# Brahma v0.0.10

A C++ style interception library for application calls.
This library uses [GOTCHA](https://github.com/LLNL/GOTCHA) to intercept POSIX, STDIO, and MPI-IO calls.
The interception of MPI-IO calls are optional and the library can be compiled without MPI-IO.

## Dependencies
1. GOTCHA v1.0.7
2. CPP Logger v0.0.4

## Build Brahma with cmake

Users can install the dependency using cmake.

```bash
cd <CLONED_REPO>
mkdir build
cmake -DBRAHMA_BUILD_DEPENDENCIES=ON -S$PWD -B$PWD/build -G "Unix Makefiles"
cmake --build $PWD/build --target all -j 50
```

User can install the library using cmake.

```bash
cd <CLONED_REPO>
mkdir build
cmake -DBRAHMA_BUILD_DEPENDENCIES=OFF -S$PWD -B$PWD/build -G "Unix Makefiles"
cmake --build $PWD/build --target all -j 50
```

### Options available in Brahma

| Option                | Description                                                            |
| --------------------- | ---------------------------------------------------------------------  |
| BRAHMA_BUILD_WITH_MPI | Enable MPI and MPI-IO interceptions                                    |
| BRAHMA_LOGGER         | Enable Logging for CPP Logger (CPP_LOGGER)                             |
| BRAHMA_LOGGER_LEVEL   | Set compile time logging level (TRACE, DEBUG, INFO, WARN, and ERROR)   |
| BRAHMA_ENABLE_TESTING | Enable testing                                                         |
| BRAHMA_BUILD_DEPENDENCIES | Build Brahma dependencies                                          |
| BRAHMA_INSTALL_DEPENDENCIES | Install Brahma dependencies into CMAKE_INSTALL_PREFIX. If off its kept in build directory                                                       |


## Including brahma in your CMake Project.

```cmake
find_package(brahma 2.0.0 REQUIRED)
```
Exported variables for this package are `brahma_FOUND`, `BRAHMA_INCLUDE_DIRS`, and `BRAHMA_LIBRARIES`.

## Using Brahma library to intercept calls.

There are three main steps to use brahma
1. Enable bindings
2. Override I/O Classes
3. Disable bindings


### Binding functions

The Binding has to be done before any interception can happen.
Some recommended places are library constructor or initialization routines.
The libraries which use Brahma can initiate binding of system calls on each interface using the `bind` function.
It takes two arguments. `UNIQUE_TOOL_NAME` should be a tool name that is used for stacking different interception tools used by gotcha.
`PRIORITY` is the prioritization of the tool.

```c++
auto posix = brahma::POSIXTest::get_instance();
posix->bind<brahma::POSIXTest>(UNIQUE_TOOL_NAME, PRIORITY);
```

### Disable bindings

This routine should be called to stop the interception.
Some recommended choices for this are library destructor or finalization routine.
The free bindings call release the interception bindings from brahma.

```c++
auto posix = brahma::POSIXTest::get_instance();
posix->unbind();
```

### Override I/O Classes

By default brahma will intercept all I/O calls. 
Tools can selectively choose which I/O calls they want to access by overriding the functions within the brahma classes.
The three classes `brahma::POSIX`, `brahma::STDIO`, and `brahma::MPIIO`.

```c++

namespace brahma {
    class POSIXInterceptor : public POSIX {
        int open(const char *pathname, int flags, ...) override;

        int creat64(const char *path, mode_t mode) override;

        int open64(const char *path, int flags, ...) override;

        // ...
    };
} // namespace brahma

```

```c++

namespace brahma {
    class STDIOInterceptor : public STDIO {
        FILE *fopen(const char *path, const char *mode) override;

        FILE *fopen64(const char *path, const char *mode) override;

        int fclose(FILE *fp) override;

        // ...
    };
} // namespace brahma

```

```c++

namespace brahma {
    class MPIIOInterceptor : public MPIIO {
        int MPI_File_close(MPI_File *fh) override;
        int MPI_File_open(MPI_Comm comm, const char *filename, int amode,
                            MPI_Info info, MPI_File *fh) override;
        int MPI_File_read_at_all(MPI_File fh, MPI_Offset offset, void *buf,
                                    int count, MPI_Datatype datatype,
                                    MPI_Status *status) override;
        int MPI_File_write_at_all(MPI_File fh, MPI_Offset offset, const void *buf,
                                    int count, MPI_Datatype datatype,
                                    MPI_Status *status) override;
        // ...
    };
} // namespace brahma

```