# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *              Yunior C. Fonseca Reyna (cfonseca@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
import pwem
from pyworkflow.utils import Environ

from resmap.constants import *

__version__ = '3.0.2'
_logo = "resmap_logo.png"
_references = ['kucukelbir2014']


class Plugin(pwem.Plugin):
    _homeVar = RESMAP_HOME
    _pathVars = [RESMAP_HOME]

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(RESMAP_HOME, 'resmap-1.95')
        cls._defineVar(RESMAP, 'ResMap-1.95-cuda-Centos7x64')
        cls._defineVar(RESMAP_GPU_LIB, 'ResMap_krnl-cuda-V8.0.61-sm60_gpu.so')

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch resmap. """
        environ = Environ(os.environ)
        environ.update({'PATH': Plugin.getHome()},
                       position=Environ.BEGIN)
        return environ

    @classmethod
    def getProgram(cls):
        """ Return the program binary that will be used. """
        return os.path.join(cls.getHome('bin'),
                            os.path.basename(cls.getVar(RESMAP)))

    @classmethod
    def getGpuLib(cls):
        """ Return CUDA lib linked to binary. """
        return os.path.join(cls.getHome('bin'),
                            os.path.basename(cls.getVar(RESMAP_GPU_LIB)))

    @classmethod
    def defineBinaries(cls, env):
        """ Define required binaries in the given Environment. """

        env.addPackage('resmap', version='1.95',
                       tar='resmap-1.95.tgz',
                       default=True)
