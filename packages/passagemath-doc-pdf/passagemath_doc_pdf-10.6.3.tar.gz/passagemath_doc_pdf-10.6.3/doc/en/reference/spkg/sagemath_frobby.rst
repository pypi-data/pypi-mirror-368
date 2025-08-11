.. _spkg_sagemath_frobby:

======================================================================
sagemath_frobby: Computations on monomial ideals with Frobby
======================================================================

This pip-installable source distribution ``passagemath-frobby`` provides an interface to Frobby,
the package for computations on monomial ideals.


Examples
--------

A quick way to try it out interactively::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-frobby[test]" ipython

    In [1]: from sage.all__sagemath_frobby import *

Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_frobby`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`

Version Information
-------------------

package-version.txt::

    10.6.3

version_requirements.txt::

    passagemath-frobby ~= 10.6.3.0


Equivalent System Packages
--------------------------

(none known)

