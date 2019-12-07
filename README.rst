=============
Resmap plugin
=============

This plugin provides a wrapper for `ResMap program <https://sourceforge.net/projects/resmap-latest>`_.

.. figure:: http://scipion-test.cnb.csic.es:9980/badges/resmap_devel.svg
   :align: left
   :alt: build status

Installation
------------

You will need to use `3.0 <https://github.com/I2PC/scipion/releases/tag/V2.0.0>`_ version of Scipion to be able to run these protocols. To install the plugin, you have two options:

a) Stable version

.. code-block::

    scipion installp -p scipion-em-resmap

b) Developer's version

    * download repository

    .. code-block::

        git clone https://github.com/scipion-em/scipion-em-resmap.git

    * install

    .. code-block::

        scipion installp -p path_to_scipion-em-resmap --devel

ResMap binaries will be installed automatically with the plugin, but you can also link an existing installation.
Default installation path assumed is ``software/em/resmap-1.95``, if you want to change it, set *RESMAP_HOME* in ``scipion.conf`` file pointing to the folder where the ResMap is installed. ResMap binary (default ResMap-1.95-cuda-Centos7x64) and CUDA lib module (default ResMap_krnl-cuda-V8.0.61-sm60_gpu.so) can be set by *RESMAP* and *RESMAP_GPU_LIB* vars, respectively.

To check the installation, simply run the following Scipion test: ``scipion test resmap.tests.test_protocols_resmap.TestResMap``

A complete list of tests can also be seen by executing ``scipion test --show --grep resmap``

Supported versions
------------------

1.95

Protocols
---------

* local resolution

References
----------

1. Kucukelbir A. et al. (2014) Quantifying the local resolution of cryo-EM density maps. Nature Methods 11, 63-65.
