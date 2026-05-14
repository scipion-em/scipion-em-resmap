# **************************************************************************
# *
# * Authors:    Josue Gomez Blanco (josue.gomez-blanco@mcgill.ca)
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

from pyworkflow.tests import BaseTest, DataSet, setupTestProject
from pyworkflow.utils import magentaStr
from pwem.protocols import ProtImportVolumes, ProtImportMask

from resmap.protocols import ProtResMap


class TestResMapBase(BaseTest):
    @classmethod
    def setData(cls, dataProject='resmap'):
        cls.dataset = DataSet.getDataSet(dataProject)
        cls.vol = cls.dataset.getFile('betagal')
        cls.half1 = cls.dataset.getFile('betagal_half1')
        cls.half2 = cls.dataset.getFile('betagal_half2')
        cls.mask = cls.dataset.getFile('betagal_mask')

    @classmethod
    def runImportVolumes(cls, samplingRate, pattern, **kwargs):
        """ Run an Import volumes protocol. """
        print(magentaStr("\n==> Importing data - volumes:"))
        cls.protImport = cls.newProtocol(ProtImportVolumes,
                                         setHalfMaps=True,
                                         filesPath=pattern,
                                         samplingRate=samplingRate,
                                         **kwargs)
        cls.launchProtocol(cls.protImport)
        return cls.protImport

    @classmethod
    def runImportMask(cls, pattern, samplingRate):
        """ Run an Import volumes protocol. """
        print(magentaStr("\n==> Importing data - mask:"))
        cls.protImport = cls.newProtocol(ProtImportMask,
                                         maskPath=pattern,
                                         samplingRate=samplingRate)
        cls.launchProtocol(cls.protImport)
        return cls.protImport


class TestResMap(TestResMapBase):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        TestResMapBase.setData()
        cls.protImportVol = cls.runImportVolumes(3.54,
                                                 cls.vol,
                                                 half1map=cls.half1,
                                                 half2map=cls.half2)
        cls.protImportMask = cls.runImportMask(cls.mask, 3.54)

    def _runTest(self, label, useMask=False):
        print(magentaStr(f"\n==> Testing resmap {label}:"))
        resMap = self.newProtocol(ProtResMap,
                                  objLabel=f"resmap {label}",
                                  inputType=0,
                                  volume=self.protImportVol.outputVolume,
                                  stepRes=0.5,
                                  minRes=7.5,
                                  maxRes=20,
                                  show2D=False,
                                  doBenchmarking=True)
        if useMask:
            resMap.applyMask.set(True)
            resMap.maskVolume.set(self.protImportMask.outputMask)

        output = resMap._possibleOutputs.Volume.name
        self.launchProtocol(resMap)
        self.assertIsNotNone(output, f"Resmap ({label}) has failed")

    def testResmap(self):
        self._runTest("- with mask", useMask=True)
        self._runTest("- no mask")
