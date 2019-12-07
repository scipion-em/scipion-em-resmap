# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
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
from os.path import abspath
import os
import numpy as np
from matplotlib import cm

from pwem.constants import (COLOR_CHOICES, COLOR_JET, COLOR_OTHER, AX_Z)
from pwem.convert import ImageHandler
from pyworkflow.protocol.params import LabelParam, EnumParam, StringParam, \
    LEVEL_ADVANCED, IntParam
from pyworkflow.viewer import ProtocolViewer, DESKTOP_TKINTER
from pwem.viewers import (ChimeraView, LocalResolutionViewer, DataView,
                          EmPlotter)

from resmap import CHIMERA_CMD, RESMAP_VOL
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
        ProtocolViewer.__init__(self, *args, **kwargs)

    def _defineParams(self, form):
        form.addSection(label='Visualization')
        form.addParam('doShowLogFile', LabelParam,
                      label="Show log file")
        form.addParam('doShowChimeraAnimation', LabelParam,
                      label="Show Chimera animation")

        form.addParam('doShowVolumeSlices', LabelParam,
                      label="Show resolution slices")

        form.addParam('doShowOriginalVolumeSlices', LabelParam,
                      label="Show original volume slices")

        form.addParam('doShowResHistogram', LabelParam,
                      label="Show resolution histogram")

        group = form.addGroup('Colored resolution Slices and Volumes')
        group.addParam('colorMap', EnumParam, choices=COLOR_CHOICES,
                       default=COLOR_JET,
                       label='Color map',
                       help='Select the color map to apply to the resolution map. '
                            'http://matplotlib.org/1.3.0/examples/color/colormaps_reference.html.')

        group.addParam('otherColorMap', StringParam, default='jet',
                       condition=binaryCondition,
                       label='Customized Color map',
                       help='Name of a color map to apply to the resolution map.'
                            ' Valid names can be found at '
                            'http://matplotlib.org/1.3.0/examples/color/colormaps_reference.html')
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

    def _getVisualizeDict(self):
        self.protocol._createFilenameTemplates()
        return {
                'doShowLogFile': self._showLogFile,
                'doShowChimeraAnimation': self._showChimeraAnimation,
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

    def _showChimeraAnimation(self, param=None):

        view = ChimeraView(CHIMERA_CMD, cwd=self.protocol._getExtraPath())
        return [view]


    def _showVolumeSlices(self, param=None):
        cm = DataView(self.protocol._getFileName(RESMAP_VOL))

        return [cm]


    def _showOriginalVolumeSlices(self, param=None):

        cm = DataView(self.protocol.volumeHalf1.get().getFileName())
        cm2 = DataView(self.protocol.volumeHalf2.get().getFileName())
        return [cm, cm2]


    def _showVolumeColorSlices(self, param=None):
        imageFile = self.protocol._getFileName(RESMAP_VOL)
        imgData, min_Res, max_Res = self.getImgData(imageFile)

        xplotter = EmPlotter(x=2, y=2, mainTitle="Local Resolution Slices "
                                                    "along %s-axis."
                                                    % self._getAxis())
        # The slices to be shown are close to the center. Volume size is divided
        # in segments, the fourth central ones are selected i.e. 3,4,5,6
        for i in list(range(3, 7)):
            sliceNumber = self.getSlice(i, imgData)
            a = xplotter.createSubPlot("Slice %s" % (sliceNumber + 1), '', '')
            matrix = self.getSliceImage(imgData, sliceNumber, self._getAxis())
            plot = xplotter.plotMatrix(a, matrix, min_Res, max_Res,
                                       cmap=self.getColorMap(),
                                       interpolation="nearest")
        xplotter.getColorBar(plot)
        return [xplotter]

    def getImgData(self, imgFile):
        import numpy as np
        img = ImageHandler().read(imgFile)
        imgData = img.getData()

        minRes = np.amin(imgData)
        background = self.getBackGroundValue(imgData.flatten())
        imgData2 = np.ma.masked_where(
            np.logical_or(np.greater_equal(imgData, background), np.less_equal(imgData,0.1)), imgData, copy=True)
        maxRes = np.amax(imgData2)
        return imgData2, minRes, maxRes

    @classmethod
    def getBackGroundValue (cls, data):
        return max(data) - 1

    def _showOneColorslice(self, param=None):
        imageFile = self.protocol._getFileName(RESMAP_VOL)
        imgData, min_Res, max_Res = self.getImgData(imageFile)

        xplotter = EmPlotter(x=1, y=1, mainTitle="Local Resolution Slices "
                                                    "along %s-axis."
                                                    % self._getAxis())
        sliceNumber = self.sliceNumber.get()
        if sliceNumber < 0:
            x, _, _, _ = ImageHandler().getDimensions(imageFile)
            sliceNumber = x / 2
        else:
            sliceNumber -= 1
        # sliceNumber has no sense to start in zero
        a = xplotter.createSubPlot("Slice %s" % (sliceNumber + 1), '', '')
        matrix = self.getSliceImage(imgData, sliceNumber, self._getAxis())
        plot = xplotter.plotMatrix(a, matrix, min_Res, max_Res,
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
        fnOrigMap = self.protocol.volumeHalf1.get().getFileName()
        cmdFile = self.protocol._getExtraPath('chimera_resolution_map.cmd')
        sampRate = self.protocol.volumeHalf1.get().getSamplingRate()
        self.createChimeraScript(cmdFile, fnResVol, fnOrigMap, sampRate)
        view = ChimeraView(cmdFile)
        return [view]

    def getColorMap(self):
        if (COLOR_CHOICES[self.colorMap.get()] is 'other'):
            cmap = cm.get_cmap(self.otherColorMap.get())
        else:
            cmap = cm.get_cmap(COLOR_CHOICES[self.colorMap.get()])
        if cmap is None:
            cmap = cm.jet
        return cmap
