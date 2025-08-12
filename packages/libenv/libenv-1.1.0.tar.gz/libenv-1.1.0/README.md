![LibEnv logo - software stack with smoking pipe](libenv.png)

LibEnv - declare an environment
===============================

Most modern programming languages come with their
own package managers - pip for python, go modules
for go, cabal for haskell, crate for rust, opam for ocaml,
Pkg.jl for Julia, etc.
Multiple community standards have emerged for other
programming languages, such as FPM for Fortran,
and CPM or Spack for C.

Operating-system level package managers also
abound, including yum, apt, brew, cocoa, etc.
Installing system packages as a user is a killer 
application for Docker/Apptainer containers.
Additionally, lmod modules
can be built on top of all of the above.

At this point, we must acknowledge that there
are a variety of different ways to setup a user
environment.  So, libenv attempts to provide a specification
for using these various strategies simultaneously.

Usage
=====

This package is pip-installable,

    pip install libenv

You will also need a configuration file at $HOME/.config/libenv.json
with contents like the following,

    { "data_dir": "/home/<username>/venvs",
      "cache_dir": "/scratch/cache",
      "build_dir: "/tmp/builds",
      "concurrency": 8
    }

Libenv has two functions -- install and load.
Environments are installed into a prefix, either
`data_dir/<env file name>` or whatever is specified
in the `prefix` key of the env file.

To install an env, use

    libenv install my_envname.yaml

Once installed, the environment contains an `env.json`
file that documents the install steps that created
that environment.  This is extremely helpful when
building the environment, so you can iterate on
partially successful installs.

In fact, `libenv install -s my_envname.yaml` will
just install one step of your build and then stop.

Once fully installed, you can translate an environment
spec into its install or load commands using:

    libenv load my_envname.yaml


How it Works
============

LibEnv operates by translating an environment
spec into install and load shell-scripts.
The install script is generated and run one step
at a time.  All listed artifacts are downloaded
into the `cache/mirror` directory before starting.
This is helpful in case you want to download from
one host and then build on another one.

At each build step, its artifacts are extracted/
copied into the build directory.  Then a build script
is written and run.  The build script for step 5, for example,
appends the load scripts for steps 1-4 with the install script
for step 5.

Each successful step is documented in the environment's
`env.json` file.  Subsequent steps double-check that
this file matches what is requested.  If you alter
steps after they've been installed, you need to
start again or manually resolve differences between the
two env files (expected and installed).

The load script sets up all the environment
variables so that the installed programs
can rely on their own conventions to find things.
Note this will also load developer environment
variables like `CMAKE_PREFIX_PATH`.

In the intended usage, environment specs (for example
`env.yaml` at the top level of a package),
get built into a `/usr`-like subdirectory inside libenv's
`data_dir` (see [Usage][#Usage]).
That subdirectory contains the usual layout of
`bin`, `include`, `lib`, etc.

Within libenv scripts, this top-level directory
is available as the environment variable, `$prefix`.
Appropriate parts of `$prefix` are added to
`PATH`, `MANPATH`, `CMAKE_PREFIX_PATH`, and `PKG_CONFIG_PATH`.
Python-pip installs, for example, ensure that a
python virtual environment is located at `$prefix`.
Manual source installs (e.g. make, cmake, autotools, etc.)
are done with `DESTDIR=$prefix`, `CMAKE_INSTALL_PREFIX=$prefix`,
`--prefix=$prefix`, etc.


Writing an Environment
======================

We'll introduce this by way of example.
To create the build environment
for the C++ program "DFT-FE", one would use:

```
# env.yaml

environment:
  - type: Var
    vars:
      CC:        cc
      FC:        ftn
      CXX:       CC
      CFLAGS:   "-O2 -march=znver3 -fPIC"
      CXXFLAGS: "-O2 -march=znver3 -fPIC"
      FFLAGS:   "-fPIC -march=znver3 -fallow-argument-mismatch"

  - type: Script
    artifacts: [ "https://www.alglib.net/translator/re/alglib-3.20.0.cpp.gpl.tgz" ]
    install: |
      [ -d alglib-cpp ] || tar xzf alglib-3.20.0.cpp.gpl.tgz
      cd alglib-cpp
      g++ -o libAlglib.so -shared -fPIC -O2 *.cpp
      mkdir -p $prefix/lib
      mv libAlglib.so $prefix/lib/
      mkdir -p $prefix/include/alglib
      cp *.h $prefix/include/alglib/

  - type: CMake
    artifacts: [ "git+https://gitlab.com/libxc/libxc@6.2.2" ]
    source: libxc

  - type: CMake
    artifacts: [ "git+https://github.com/atztogo/spglib.git@02159eef6e7349535049a43fe2272bb634c77945" ]
    source: spglib
    #cmake: {}

  - type: Autotools
    artifacts: [ "git+https://github.com/cburstedde/p4est.git@v2.2" ]
    source: p4est
    env:
      CPPFLAGS: "-DSC_LOG_PRIORITY=SC_LP_ESSENTIAL"
    configure:
      - "--enable-mpi"
      - "--enable-shared"
      - "--disable-vtk-binary"
      - "--without-blas"
      - "--enable-openmp=-fopenmp"
    post_configure: "make -C sc"

  - type: CMake
    artifacts: [ "git+https://github.com/Reference-ScaLAPACK/scalapack.git@v2.2.0" ]
    source: scalapack
    cmake:
      BUILD_SHARED_LIBS: ON
      BUILD_STATIC_LIBS: OFF
      BUILD_TESTING: OFF
      USE_OPTIMIZED_LAPACK_BLAS: ON

  - type: Autotools
    artifacts: [ "https://elpa.mpcdf.mpg.de/software/tarball-archive/Releases/$ver/elpa-2022.11.001.tar.gz" ]
    patches: [ https://.../blob/src/elpa-2022.11.001.patch ]
    source: elpa-2022.11.001
    env:
      - CXX: hipcc
      - CC:  hipcc
      - FC:  ftn
      - CXXFLAGS: "-std=c++14 $CXXFLAGS"
    configure:
      - "--enable-amd-gpu"
      - "--disable-sse"
      - "--disable-sse-assembly"
      - "--disable-avx"
      - "--disable-avx2"
      - "--disable-avx512"
      - "--enable-c-tests=no"
      - "--enable-option-checking=fatal"
      - "--enable-shared"
      - "--enable-cpp-tests=no"
      - "--enable-hipcub"
    
  - type: CMake
    artifacts: [ "https://github.com/dftfeDevelopers/dealii.git@dealiiCustomizedCUDARelease" ]
    source: dealii
    cmake:
      CMAKE_CXX_STANDARD: "14"
      CMAKE_CXX_FLAGS: "-march=native -std=c++14"
      CMAKE_C_FLAGS: "-march=native -std=c++14"
      DEAL_II_ALLOW_PLATFORM_INTROSPECTION: OFF
      DEAL_II_WITH_TASKFLOW: OFF
      CMAKE_BUILD_TYPE: Release
      DEAL_II_CXX_FLAGS_RELEASE: "-O2"
      DEAL_II_WITH_TBB: OFF
      DEAL_II_COMPONENT_EXAMPLES: OFF
      DEAL_II_WITH_MPI: ON
      DEAL_II_WITH_64BIT_INDICES: ON
      P4EST_DIR: "$prefix"
      DEAL_II_WITH_LAPACK: ON
      LAPACK_DIR: "$OLCF_OPENBLAS_ROOT;$prefix"
      LAPACK_FOUND: true
      LAPACK_LIBRARIES: "$OLCF_OPENBLAS_ROOT/lib/libopenblas.so"
      SCALAPACK_DIR: "$prefix"
      SCALAPACK_LIBRARIES: "$prefix/lib/libscalapack.so"
```

This shows most of the major types of install steps.
Installation runs these steps in order.

To install the environment, use

    % libenv install env.yaml

On failure, libenv's exit code will be nonzero
and you can diagnose what happened through reading
the build output.

Once installed, the environment can be loaded:

    % eval `{libenv load dftfe_env.yaml}

On success, all dependencies specified in the file above
will be loaded into appropriate shell variables.


New Step Types
==============

Adding a new type of install step currently requires
adding a file into `libenv/types`.
In the future, we plan to make
providers loadable from external sources.

Each possible `type` value is implemented
as a class with the type's name,
inside a file with type's name (in all lowercase).

Looking at libenv's source shows that these type-classes
are pydantic Model-s (since they inherit from `EnvType`).
They must contain `installScript` and `loadScript` methods
that return `cmd.Script` objects.

For example, 

```
# loadscript.py
from libenv.envtype import EnvType
from libenv import cmd

class LoadScript(EnvType):
    # A script that just runs at load-time.
    script: str

    def installScript(self, config) -> cmd.Script:
        return cmd.Script() # no action
    def loadScript(self, config) -> cmd.Script:
        return cmd.run(self.script) # run the script
```

Now `env.yaml` files can contain corresponding
entries like,
```
- type: LoadScript
  script: "echo 'hello'"
```


FAQs
====

How does this differ from lmod?
-------------------------------

lmod uses a DSL to document specific environment
variables to set (and commands to run) to load or unload
individual packages.  In order for this to work, each
package needs to have a module file.  In contrast,
libenv defines "schemes" that are parameterized over
packages.  This way, we document how to use a package manager,
and then defer to that manager whenever we want to install
(and source) a package from it.


How does this differ from spack?
--------------------------------

Spack uses package.py files to define the install strategy
for individual packages.  These are similar to the environment
definitions above, except that every package is named
and known to spack.

This prevents using parameterized packages from other package managers.
So, for example, to use a pure python package from pypi,
one would have to add a trivial package definition for
that package to spack (whose purpose is to dereference pypi).

Also spack is built around package loading,
not environment setup in general.
Thus, there are no options in spack to add variables,
source modules, or execute arbitrary shell scripts
during environment setup.

In other words, libenv is flexible enough to load
a spack package, but spack is not flexible enough
to load a libenv environment definition.


How do you avoid package manager conflicts?
-------------------------------------------

Multiple package managers may occasionally have conflicts
with one another.  For example, spack can install
packages (like py-torch) that are already available with pip.
Moreover, those packages can be installed with different
options.  Rather than avoid these kinds of conflicts,
libenv blindly executes the environment steps in order.
If an environment installs conflicting packages,
then all subsequent steps in that environment will
have to deal with the consequences.

Why not just use conda?
---------------------------

Conda's package definitions can use
[rich metadata in meta.yaml](https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html)
to define dependencies, along with build, run, and test
environments.  This makes them similar in spirit to
libenv `env.yaml` files.

However, they have some important differences,

1. They come from community channels, and are not
   packaged with the source they build.

   This creates a bunch of binary packages built by
   (potentially) untrusted sources in a non-CPU optimized way.
   Pre-packaged binaries are not ideal from either
   a security or an efficiency perspective.

   Note: Pip-installed packages have the same drawback.

2. Conda has limited flexibility to include package
   requirements using other toolchains.
   Hence, to use a package in conda, it needs a
   conda build definition.

3. Conda package metadata files are only used at build time,
   so they can't be used to setup the environment for
   running a given package.


Why not just use containers?
----------------------------

Rather than specify packages that can be obtained by
correctly using package managers and install commands,
it is possible to write all the install commands
into containers.  This has one major drawback, and two
consequences.  First, it forces one to write shell
scripts instead of being declarative.  Package managers
are usually declarative, so this breaks declarative-ness.
Consequence one is that we end up needing to maintain separate
code to install and to use the environment.
Consequence two is that composing containers is more
difficult than environments (which are more declarative).

There are ways to make containers more declarative
and composable.  However, they involve translating
environment specs like the ones provided by libenv
into shell scripts.  Thus, libenv's functionality
is still needed.

Case in point: it is possible to install libenv
in a container, and then run `libenv install env.yaml`
to install a package's required environment.

It is not possible to mix containerized and non-containerized
environments the way libenv mixes python and cmake
builds.  For a composable, scripted way to build containers,
see [Contaminate](https://code.ornl.gov/99R/contaminate).
