# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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

from matplotlib import cm

from pwem.constants import COLOR_OTHER, AX_Z
from pwem.emlib.image import ImageHandler
from pwem.wizards import ColorScaleWizardBase
from pyworkflow.protocol.params import LabelParam, EnumParam, \
    LEVEL_ADVANCED, IntParam
from pyworkflow.viewer import ProtocolViewer, DESKTOP_TKINTER
from pwem.viewers import (ChimeraView, LocalResolutionViewer, DataView,
                          EmPlotter)

from resmap import RESMAP_VOL
from resmap.protocols import ProtResMap
import matplotlib.pyplot as plt



binaryCondition = ('(colorMap == %d) ' % COLOR_OTHER)

class ResMapViewer(LocalResolutionViewer):
    """Visualization tools for ResMap results. """

    _environments = [DESKTOP_TKINTER]
    _targets = [ProtResMap]
    _label = 'viewer'

    @staticmethod
    def getColorMapChoices():
        return plt.colormaps()

    def __init__(self, *args, **kwargs):
        ProtocolViewer.__init__(self, **kwargs)

    def _defineParams(self, form):
        form.addSection(label='Visualization')
        form.addParam('doShowLogFile', LabelParam,
                      label="Show log file")

        form.addParam('doShowVolumeSlices', LabelParam,
                      label="Show resolution slices")

        form.addParam('doShowOriginalVolumeSlices', LabelParam,
                      label="Show original volume slices")

        form.addParam('doShowResHistogram', LabelParam,
                      label="Show resolution histogram")

        group = form.addGroup('Colored resolution Slices and Volumes')
        group.addParam('sliceAxis', EnumParam, default=AX_Z,
                       choices=['x', 'y', 'z'],
                       display=EnumParam.DISPLAY_HLIST,
                       label='Slice axis')

        group.addParam('doShowVolumeColorSlices', LabelParam,
                       label="Show colored slices")

        group.addParam('doShowOneColorslice', LabelParam,
                       expertLevel=LEVEL_ADVANCED,
                       label='Show selected slice')
        group.addParam('sliceNumber', IntParam, default=-1,
                       expertLevel=LEVEL_ADVANCED,
                       label='Show slice number')

        group.addParam('doShowChimera', LabelParam,
                       label="Show Resolution map in Chimera")

        # get default values
        imageFile = self.protocol._getFileName(RESMAP_VOL)
        _, min_Res, max_Res, _ = self.getImgData(imageFile)

        ColorScaleWizardBase.defineColorScaleParams(group, defaultLowest=min_Res, defaultHighest=max_Res)

    def getImgData(self, imgFile):
        return LocalResolutionViewer.getImgData(self, imgFile,maxMaskValue = 99.9)

    def _getVisualizeDict(self):
        self.protocol._createFilenameTemplates()
        return {
                'doShowLogFile': self._showLogFile,
                'doShowOriginalVolumeSlices': self._showOriginalVolumeSlices,
                'doShowVolumeSlices': self._showVolumeSlices,
                'doShowVolumeColorSlices': self._showVolumeColorSlices,
                'doShowOneColorslice': self._showOneColorslice,
                'doShowResHistogram': self._plotHistogram,
                'doShowChimera': self._showChimera
            }

    def _showLogFile(self, param=None):
        return [self.textView([self.protocol._getFileName('logFn')],
                              "ResMap log file")]

    def _showVolumeSlices(self, param=None):
        cm = DataView(self.protocol._getFileName(RESMAP_VOL))

        return [cm]


    def _showOriginalVolumeSlices(self, param=None):

        cm = DataView(self.protocol.volumeHalf1.get().getFileName())
        cm2 = DataView(self.protocol.volumeHalf2.get().getFileName())
        return [cm, cm2]


    def _showVolumeColorSlices(self, param=None):
        imageFile = self.protocol._getFileName(RESMAP_VOL)
        imgData, _, _, _ = self.getImgData(imageFile)

        xplotter = EmPlotter(x=2, y=2, mainTitle="Local Resolution Slices "
                                                    "along %s-axis."
                                                    % self._getAxis())
        # The slices to be shown are close to the center. Volume size is divided
        # in segments, the fourth central ones are selected i.e. 3,4,5,6
        for i in list(range(3, 7)):
            sliceNumber = self.getSlice(i, imgData)
            a = xplotter.createSubPlot("Slice %s" % (sliceNumber + 1), '', '')
            matrix = self.getSliceImage(imgData, sliceNumber, self._getAxis())
            plot = xplotter.plotMatrix(a, matrix, self.lowest.get(), self.highest.get(),
                                       cmap=self.getColorMap(),
                                       interpolation="nearest")
        xplotter.getColorBar(plot)
        return [xplotter]

    @classmethod
    def getBackGroundValue (cls, data):
        return max(data) - 1

    def _showOneColorslice(self, param=None):
        imageFile = self.protocol._getFileName(RESMAP_VOL)
        imgData, _, _, volDims = self.getImgData(imageFile)
        print(volDims)
        xplotter = EmPlotter(x=1, y=1, mainTitle="Local Resolution Slices "
                                                    "along %s-axis."
                                                    % self._getAxis())
        sliceNumber = self.sliceNumber.get()
        if sliceNumber < 0:
            sliceNumber = volDims[0] / 2
        else:
            sliceNumber -= 1
        # sliceNumber has no sense to start in zero
        a = xplotter.createSubPlot("Slice %s" % (sliceNumber + 1), '', '')
        matrix = self.getSliceImage(imgData, sliceNumber, self._getAxis())
        plot = xplotter.plotMatrix(a, matrix, self.lowest.get(), self.highest.get(),
                                   cmap=self.getColorMap(),
                                   interpolation="nearest")
        xplotter.getColorBar(plot)
        return [xplotter]

    def _plotHistogram(self, param=None):
        imageFile = self.protocol._getFileName(RESMAP_VOL)
        img = ImageHandler().read(imageFile)
        imgData = img.getData()
        imgList = imgData.flatten()
        imgDataMax = self.getBackGroundValue(imgList)
        imgListNoZero = filter(lambda x: 0 < x < imgDataMax, imgList)
        nbins = 30
        plotter = EmPlotter(x=1,y=1,mainTitle="  ")
        plotter.createSubPlot("Resolution histogram",
                              "Resolution (A)", "# of Counts")
        plotter.plotHist(imgListNoZero, nbins)
        return [plotter]

    def _getAxis(self):
        return self.getEnumText('sliceAxis')


    def _showChimera(self, param=None):

        fnResVol = self.protocol._getFileName(RESMAP_VOL)
        vol = self.protocol.volumeHalf1.get()

        fnOrigMap = vol.getFileName()
        sampRate = vol.getSamplingRate()

        cmdFile = self.protocol._getExtraPath('chimera_resolution_map.py')
        self.createChimeraScript(cmdFile, fnResVol, fnOrigMap, sampRate,
                                 numColors=self.intervals.get(),
                                 lowResLimit=self.highest.get(),
                                 highResLimit=self.lowest.get())
        view = ChimeraView(cmdFile)
        return [view]

    def getColorMap(self):
        cmap = cm.get_cmap(self.colorMap.get())
        if cmap is None:
            cmap = cm.jet
        return cmap
