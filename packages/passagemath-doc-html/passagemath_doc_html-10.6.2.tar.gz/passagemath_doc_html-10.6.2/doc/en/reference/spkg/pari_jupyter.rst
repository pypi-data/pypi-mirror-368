.. _spkg_pari_jupyter:

pari_jupyter: Jupyter kernel for PARI/GP
==================================================

Description
-----------

Jupyter kernel for PARI/GP

License
-------

GPL version 3 or later


Upstream Contact
----------------

-  https://github.com/sagemath/pari-jupyter

Dependencies
------------

-  Python >= 3.6.1
-  Jupyter 4
-  PARI version 2.13 or later
-  Readline (any version which works with PARI)
-  Optional: Cython version 0.25 or later

Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cython`
- :ref:`spkg_jupyter_core`
- :ref:`spkg_notebook`
- :ref:`spkg_pari`

Version Information
-------------------

package-version.txt::

    1.4.3

version_requirements.txt::

    pari_jupyter >=1.3.2


Equivalent System Packages
--------------------------

.. tab:: conda-forge

   .. CODE-BLOCK:: bash

       $ conda install pari_jupyter 


.. tab:: Fedora/Redhat/CentOS

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-pari-jupyter 



See https://repology.org/project/pari-jupyter/versions, https://repology.org/project/python:pari-jupyter/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure``
will check if the system package can be used.

