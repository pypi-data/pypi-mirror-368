# Netlib Scalapack

![Actions Status](https://github.com/scivision/scalapack/workflows/ci/badge.svg)

Scalapack with CMake enhancements to make Scalapack easier to use directly in other projects.
The Scalapack
[source code](http://www.netlib.org/scalapack/)
is unmodified.
MPI is required for Scalapack.
Scalapack 2.1 works with OpenMPI 4.x, while Scalapack 2.0 worked with OpenMPI &lt; 4.

## Prereq

* Linux: `apt install cmake gfortran libopenmpi-dev liblapack-dev`
* Mac: `brew install gcc cmake open-mpi lapack`

### Windows MSYS2

```sh
pacman -S mingw-w64-x86_64-gcc-fortran mingw-w64-x86_64-msmpi mingw-w64-x86_64-lapack
```

and install
[Microsoft MS-MPI](https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi-release-notes)
to get mpiexec.exe

## Build

```sh
cmake -B build
cmake --build build

# optional self-tests
ctest --test-dir build
```

To avoid searching for Lapack (forcing Lapack to be built) use CMake option:

```sh
cmake -B build -Dfind_lapack=off
```

### options

The default is to build real32, real64.
The options for precision are just like LAPACK:

```cmake
option(BUILD_SINGLE "Build single precision real" ON)
option(BUILD_DOUBLE "Build double precision real" ON)
option(BUILD_COMPLEX "Build single precision complex")
option(BUILD_COMPLEX16 "Build double precision complex")
```

## Notes

Scalapack is included with
[Intel oneAPI](https://software.intel.com/content/www/us/en/develop/articles/free-intel-software-developer-tools.html),
for Windows as well.
