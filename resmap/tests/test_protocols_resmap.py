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
        cls.half1 = cls.dataset.getFile('betagal_half1')
        cls.half2 = cls.dataset.getFile('betagal_half2')
        cls.mask = cls.dataset.getFile('betagal_mask')

    @classmethod
    def runImportVolumes(cls, pattern, samplingRate):
        """ Run an Import volumes protocol. """
        print(magentaStr("\n==> Importing data - volumes:"))
        cls.protImport = cls.newProtocol(ProtImportVolumes,
                                         filesPath=pattern,
                                         samplingRate=samplingRate
                                         )
        cls.launchProtocol(cls.protImport)
        return cls.protImport

    @classmethod
    def runImportMask(cls, pattern, samplingRate):
        """ Run an Import volumes protocol. """
        print(magentaStr("\n==> Importing data - mask:"))
        cls.protImport = cls.newProtocol(ProtImportMask,
                                         maskPath=pattern,
                                         samplingRate=samplingRate
                                         )
        cls.launchProtocol(cls.protImport)
        return cls.protImport


class TestResMap(TestResMapBase):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        TestResMapBase.setData()
        cls.protImportHalf1 = cls.runImportVolumes(cls.half1, 3.54)
        cls.protImportHalf2 = cls.runImportVolumes(cls.half2, 3.54)
        cls.protImportMask = cls.runImportMask(cls.mask, 3.54)

    def testResmap1(self):
        print(magentaStr("\n==> Testing resmap - no mask:"))
        resMap = self.newProtocol(ProtResMap,
                                  volumeHalf1=self.protImportHalf1.outputVolume,
                                  volumeHalf2=self.protImportHalf2.outputVolume,
                                  stepRes=0.5,
                                  minRes=7.5,
                                  maxRes=20)
        resMap._createFilenameTemplates()
        output = resMap._getFileName("outResmapVol")
        resMap.show2D.set(False)
        resMap.doBenchmarking.set(True)
        self.launchProtocol(resMap)
        self.assertIsNotNone(output, "Resmap has failed")

    def testResmap2(self):
        print(magentaStr("\n==> Testing resmap - with mask:"))
        resMap = self.newProtocol(ProtResMap,
                                  volumeHalf1=self.protImportHalf1.outputVolume,
                                  volumeHalf2=self.protImportHalf2.outputVolume,
                                  applyMask=True,
                                  maskVolume=self.protImportMask.outputMask,
                                  stepRes=0.5,
                                  minRes=7.5,
                                  maxRes=20)
        resMap._createFilenameTemplates()
        output = resMap._getFileName("outResmapVol")
        resMap.show2D.set(False)
        resMap.doBenchmarking.set(True)
        self.launchProtocol(resMap)
        self.assertIsNotNone(output, "Resmap (with mask) has failed")
