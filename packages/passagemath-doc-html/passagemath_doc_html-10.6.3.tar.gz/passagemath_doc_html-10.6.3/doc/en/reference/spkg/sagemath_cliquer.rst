.. _spkg_sagemath_cliquer:

=============================================================================================
sagemath_cliquer: Finding cliques in graphs with cliquer
=============================================================================================

This pip-installable distribution ``passagemath-cliquer`` provides an interface
to `cliquer <https://users.aalto.fi/~pat/cliquer.html>`_, an exact branch-and-bound
algorithm for finding cliques in an arbitrary weighted graph by Patric Östergård.


What is included
----------------

* `Cython interface to cliquer <https://passagemath.org/docs/latest/html/en/reference/graphs/sage/graphs/cliquer.html>`_


Examples
--------

::

   $ pipx run --pip-args="--prefer-binary" --spec "passagemath-cliquer[test]" ipython

   In [1]: from sage.all__sagemath_cliquer import *

   In [2]: from sage.graphs.cliquer import max_clique

   In [3]: C = graphs.PetersenGraph(); max_clique(C)
   Out[3]: [7, 9]

Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cliquer`
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`

Version Information
-------------------

package-version.txt::

    10.6.3

version_requirements.txt::

    passagemath-cliquer ~= 10.6.3.0


Equivalent System Packages
--------------------------

(none known)

