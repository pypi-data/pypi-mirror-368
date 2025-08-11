.. _spkg_pysingular:

pysingular: A basic Python interface to Singular
==============================================================

Description
-----------

A basic interface to call Singular from python

This python module is meant to be used in Singulars Jupyter interface.

License
-------

GPL version 2 or later


Upstream Contact
----------------

-  https://github.com/sebasguts/SingularPython

Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_singular`

Version Information
-------------------

package-version.txt::

    0.9.7

version_requirements.txt::

    pysingular >=0.9.5


Equivalent System Packages
--------------------------

.. tab:: conda-forge

   .. CODE-BLOCK:: bash

       $ conda install pysingular 


.. tab:: Fedora/Redhat/CentOS

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-pysingular 



See https://repology.org/project/pysingular/versions, https://repology.org/project/python:pysingular/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure``
will check if the system package can be used.

