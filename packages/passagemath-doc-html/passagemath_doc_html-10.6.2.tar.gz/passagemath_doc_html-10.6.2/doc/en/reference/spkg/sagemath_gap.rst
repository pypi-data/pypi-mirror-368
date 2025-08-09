.. _spkg_sagemath_gap:

=======================================================================================
sagemath_gap: Computational Group Theory with GAP
=======================================================================================

This pip-installable distribution ``passagemath-gap`` is a small
distribution that provides modules that depend on the `GAP system <https://www.gap-system.org>`_.


What is included
----------------

- `Cython interface to libgap <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/gap/libgap.html>`_

- `Pexpect interface to GAP <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/gap.html>`_

- numerous modules with build-time dependencies on GAP, see `MANIFEST <https://github.com/passagemath/passagemath/blob/main/pkgs/sagemath-gap/MANIFEST.in>`_

- the binary wheels on PyPI ship a prebuilt copy of GAP


Examples
--------

A quick way to try it out interactively::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-gap[test]" IPython

    In [1]: from sage.all__sagemath_modules import *

    In [2]: from sage.all__sagemath_gap import *

    In [3]: G = libgap.eval("Group([(1,2,3), (1,2)(3,4), (1,7)])")

    In [4]: CG = G.ConjugacyClasses()

    In [5]: gamma = CG[2]

    In [6]: g = gamma.Representative()

    In [7]: CG; gamma; g
    [ ()^G, (4,7)^G, (3,4,7)^G, (2,3)(4,7)^G, (2,3,4,7)^G, (1,2)(3,4,7)^G, (1,2,3,4,7)^G ]
    (3,4,7)^G
    (3,4,7)

Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cython`
- :ref:`spkg_gap`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_modules`

Version Information
-------------------

package-version.txt::

    10.6.2

version_requirements.txt::

    passagemath-gap ~= 10.6.2.0


Equivalent System Packages
--------------------------

(none known)

