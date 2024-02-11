=============
Resmap plugin
=============

This plugin provides a wrapper for `ResMap program <https://sourceforge.net/projects/resmap-latest>`_.

.. image:: https://img.shields.io/pypi/v/scipion-em-resmap.svg
        :target: https://pypi.python.org/pypi/scipion-em-resmap
        :alt: PyPI release

.. image:: https://img.shields.io/pypi/l/scipion-em-resmap.svg
        :target: https://pypi.python.org/pypi/scipion-em-resmap
        :alt: License

.. image:: https://img.shields.io/pypi/pyversions/scipion-em-resmap.svg
        :target: https://pypi.python.org/pypi/scipion-em-resmap
        :alt: Supported Python versions

.. image:: https://img.shields.io/sonar/quality_gate/scipion-em_scipion-em-resmap?server=https%3A%2F%2Fsonarcloud.io
        :target: https://sonarcloud.io/dashboard?id=scipion-em_scipion-em-resmap
        :alt: SonarCloud quality gate

.. image:: https://img.shields.io/pypi/dm/scipion-em-resmap
        :target: https://pypi.python.org/pypi/scipion-em-resmap
        :alt: Downloads


Installation
------------

You will need to use 3.0+ version of Scipion to be able to run these protocols. To install the plugin, you have two options:

a) Stable version

.. code-block::

    scipion installp -p scipion-em-resmap

b) Developer's version

    * download repository

    .. code-block::

        git clone -b devel https://github.com/scipion-em/scipion-em-resmap.git

    * install

    .. code-block::

        scipion installp -p /path/to/scipion-em-resmap --devel

* ResMap binaries will be installed automatically with the plugin, but you can also link an existing installation.
* Default installation path assumed is ``software/em/resmap-1.95``, if you want to change it, set *RESMAP_HOME* in ``scipion.conf`` file pointing to the folder where the ResMap is installed. ResMap binary (default ResMap-1.95-cuda-Centos7x64) and CUDA lib module (default ResMap_krnl-cuda-V8.0.61-sm60_gpu.so) can be set by *RESMAP* and *RESMAP_GPU_LIB* vars, respectively.
* You also might need to set *RESMAP_CUDA_LIB* in the config file pointing to the correct location of system CUDA libraries.

To check the installation, simply run the following Scipion test:

``scipion test resmap.tests.test_protocols_resmap.TestResMap``

Supported versions
------------------

1.95

Protocols
---------

* local resolution

References
----------

1. Kucukelbir A. et al. (2014) Quantifying the local resolution of cryo-EM density maps. Nature Methods 11, 63-65.
