# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se)
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk)
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

import os

import pyworkflow.protocol.params as params
from pyworkflow.em.protocol import ProtAnalysis3D
from pyworkflow.em.convert import ImageHandler
from pyworkflow.utils import exists

import resmap
from resmap.constants import *


class ProtResMap(ProtAnalysis3D):
    """
    ResMap is software tool for computing the local resolution of 3D
    density maps from electron cryo-microscopy (cryo-EM).

    Please find the manual at http://resmap.sourceforge.net
    """
    _label = 'local resolution'

    INPUT_HELP = """ Input volume(s) for ResMap.
    Required volume properties:
        1. The particle must be centered in the volume.
        2. The background must not been masked out.
    Desired volume properties:
        1. The volume has not been filtered in any way (low-pass filtering, etc.)
        2. The volume has a realistic noise spectrum.
           This is sometimes obtained by so-called amplitude correction.
           While a similar effect is often obtained by B-factor sharpening,
           please make sure that the spectrum does not blow up near Nyquist.
    """

    def __init__(self, **kwargs):
        ProtAnalysis3D.__init__(self, **kwargs)

    def _createFilenameTemplates(self):
        """ Centralize the names of the files. """
        myDict = {
            'half1': self._getExtraPath('volume1.map'),
            'half2': self._getExtraPath('volume2.map'),
            'mask': self._getExtraPath('mask.map')
        }
        self._updateFilenamesDict(myDict)

    # --------------------------- DEFINE param functions ----------------------

    def _defineParams(self, form):
        form.addHidden(params.GPU_LIST, params.StringParam, default='',
                       label="Choose GPU ID",
                       help="If no GPU ID is provided, the program "
                       "will use CPU instead.")
        form.addSection(label='Input')
        form.addParam('volumeHalf1', params.PointerParam,
                      label="Volume half 1", important=True,
                      pointerClass='Volume',
                      help=self.INPUT_HELP)
        form.addParam('volumeHalf2', params.PointerParam,
                      pointerClass='Volume',
                      label="Volume half 2", important=True,
                      help=self.INPUT_HELP)

        form.addParam('applyMask', params.BooleanParam, default=False,
                      label="Mask input volume?",
                      help="It is not necessary to provide ResMap with a mask "
                           "volume. The algorithm will attempt to estimate a "
                           "mask volume by low-pass filtering the input volume "
                           "and thresholding it using a heuristic procedure.\n"
                           "If the automated procedure does not work well for "
                           "your particle, you may provide a mask volume that "
                           "matches the input volume in size and format. "
                           "The mask volume should be a binary volume with zero "
                           "(0) denoting the background/solvent and some positive"
                           "value (0+) enveloping the particle.")
        form.addParam('maskVolume', params.PointerParam, label="Mask volume",
                      pointerClass='VolumeMask', condition="applyMask",
                      help='Select a volume to apply as a mask.')

        group = form.addGroup('Extra parameters')
        group.addParam('stepRes', params.FloatParam, default=1,
                       label='Step size (Ang):',
                       help='in Angstroms (min 0.25, default 1.0)')
        line = group.addLine('Resolution Range (A)',
                             help="Default (0): algorithm will start a just above\n"
                                  "             2*voxelSize until 4*voxelSize.   \n"
                                  "These fields are provided to accelerate computation "
                                  "if you are only interested in analyzing a specific "
                                  "resolution range. It is usually a good idea to provide "
                                  "a maximum resolution value to save time. Another way to "
                                  "save computation is to provide a larger step size.")
        line.addParam('minRes', params.FloatParam, default=0, label='Min')
        line.addParam('maxRes', params.FloatParam, default=0, label='Max')
        group.addParam('pVal', params.FloatParam, default=0.05,
                       label='Confidence level:',
                       help="P-value, usually between [0.01, 0.05].\n\n"
                            "This is the p-value of the statistical hypothesis test "
                            "on which ResMap is based on. It is customarily set to  "
                            "0.05 although you are welcome to reduce it (e.g. 0.01) "
                            "if you would like to obtain a more conservative result. "
                            "Empirically, ResMap results are not much affected by the p-value.")

    # --------------------------- INSERT steps functions ----------------------

    def _insertAllSteps(self):
        inputs = [self.volumeHalf1, self.volumeHalf2]
        locations = [i.get().getLocation() for i in inputs]

        self._createFilenameTemplates()
        self._insertFunctionStep('convertInputStep', *locations)
        args = self._prepareParams()
        self._insertFunctionStep('estimateResolutionStep', args)
        self._insertFunctionStep('createOutputStep')

    # --------------------------- STEPS functions -----------------------------

    def convertInputStep(self, volLocation1, volLocation2):
        """ Convert input volume to .mrc as expected by ResMap. """
        ih = ImageHandler()
        ih.convert(volLocation1, self._getFileName('half1'))
        ih.convert(volLocation2, self._getFileName('half2'))

    def estimateResolutionStep(self, args):
        """ Call ResMap with the appropriate parameters. """

        program = resmap.Plugin.getProgram()
        self.runJob(program, args, cwd=self._getExtraPath(), numberOfThreads=1)

    def createOutputStep(self):
        pass

        #results = self.runResmap(self._getPath())
        #
        #self.histogramData.set(dumps(results['resHisto']))
        #plotDict = {'minRes': results['minRes'],
        #            'maxRes': results['maxRes'],
        #            'orig_n': results['orig_n'],
        #            'n': results['n'],
        #            'currentRes': results['currentRes']
        #            }
        #self.plotData.set(dumps(plotDict))
        #self._store(self.histogramData, self.plotData)
        #
        #self.savePlots(results)

    #def savePlots(self, results=None):
    #    """ Store png images of the plots to be used as images, """
    #    # Add resmap libraries to the path
    #    sys.path.append(resmap.Plugin.getVar(RESMAP_HOME))
    #    # This is needed right now because we are having
    #    # some memory problem with matplotlib plots right now in web
    #    Plotter.setBackend('Agg')
    #    plot = self._plotVolumeSlices()
    #    plot.savefig(self._getExtraPath('volume1.map.png'))
    #    plot.close()
    #    plot = self._plotResMapSlices(results['resTOTALma'])
    #    plot.savefig(self._getExtraPath('volume1_resmap.map.png'))
    #    plot.close()
    #    plot = self._plotHistogram()
    #    plot.savefig(self._getExtraPath('histogram.png'))
    #    plot.close()

    # --------------------------- INFO functions ------------------------------

    def _summary(self):
        summary = []

        if exists(self._getExtraPath('histogram.png')):
            pass
            #results = self._parseOutput()
            #summary.append('Mean resolution: %0.2f A' % results[0])
            #summary.append('Median resolution: %0.2f A' % results[1])
        else:
            summary.append("Output is not ready yet.")

        return summary

    def _validate(self):
        errors = []

        half1 = self.volumeHalf1.get()
        half2 = self.volumeHalf2.get()
        if half1.getSamplingRate() != half2.getSamplingRate():
            errors.append(
                'The selected half volumes have not the same pixel size.')
        if half1.getXDim() != half2.getXDim():
            errors.append(
                'The selected half volumes have not the same dimensions.')

        return errors

    # --------------------------- UTILS functions -----------------------------

    def _prepareParams(self):
        args = " --noguiSplit %(half1)s %(half2)s"
        args += " --vxSize=%0.3f" % self.volumeHalf1.get().getSamplingRate()
        args += " --pVal=%(pVal)f --maxRes=%(maxRes)f --minRes=%(minRes)f"
        args += " --stepRes=%(stepRes)f"

        if self.applyMask:
            # convert mask to map/ccp4
            ih = ImageHandler()
            ih.convert(self.maskVolume.get().getLocation(),
                       self._getFileName('mask'))

            args += " --maskVol=%s" % os.path.basename(self._getFileName('mask'))

        params = {'half1': os.path.basename(self._getFileName('half1')),
                  'half2': os.path.basename(self._getFileName('half2')),
                  'pVal': self.pVal.get(),
                  'maxRes': self.maxRes.get(),
                  'minRes': self.minRes.get(),
                  'stepRes': self.stepRes.get()
                  }

        args = args % params

        if len(str(self.getGpuList())) > 1:
            args += " --use_gpu=yes --set_gpu=%(GPU)s"
            args += " --lib_krnl_gpu=%s" % resmap.Plugin.getGpuLib()

        return args

#
#    def runResmap(self, workingDir, wizardMode=False):
#        """ Prepare the args dictionary to be used
#        and call the ResMap algorithm.
#        Params:
#            workingDir: where to run ResMap
#            wizardMode: some custom params to be used by the wizard
#                to display the pre-whitening GUI and only that.
#        with the  """
#        self._enterDir(workingDir)
#
#        volumes = ['volume1.map', 'volume2.map']
#
#        # Add resmap libraries to the path
#        sys.path.append(Plugin.getVar(RESMAP_HOME))
#        from ResMap_algorithm import ResMap_algorithm
#        from ResMap_fileIO import MRC_Data
#
#        # Always read the first volume as mrc data
#        data1 = MRC_Data(volumes[0], 'ccp4')
#
#        prewhitenArgs = {'display': wizardMode,
#                         'force-stop': wizardMode
#                         }
#        if (self.prewhitenAng.hasValue() and
#                self.prewhitenRamp.hasValue()):
#            prewhitenArgs['newElbowAngstrom'] = self.prewhitenAng.get()
#            prewhitenArgs['newRampWeight'] = self.prewhitenRamp.get()
#
#        args = {'pValue': self.pVal.get(),
#                'minRes': self.minRes.get(),
#                'maxRes': self.maxRes.get(),
#                'stepRes': self.stepRes.get(),
#                'chimeraLaunch': False,
#                # prevent ResMap to launch some graphical analysis
#                'graphicalOutput': False,
#                'scipionPrewhitenParams': prewhitenArgs
#                }
#
#        if self.useSplitVolume:
#            # Read the second splitted volume
#            data2 = MRC_Data(volumes[1], 'ccp4')
#            args.update({'vxSize': self.volumeHalf1.get().getSamplingRate(),
#                         'inputFileName1': 'volume1.map',
#                         'inputFileName2': 'volume2.map',
#                         'data1': data1,
#                         'data2': data2,
#                         })
#        else:
#            args.update({'vxSize': self.inputVolume.get().getSamplingRate(),
#                         'inputFileName': 'volume1.map',
#                         'data': data1,
#                         })
#
#        results = ResMap_algorithm(**args)
#        self._leaveDir()
#
#        return results
#
#    # --------- Functions related to Plotting
#
#    def _getVolumeMatrix(self, volName):
#        from ResMap_fileIO import MRC_Data
#
#        volPath = self._getPath(volName)
#        return MRC_Data(volPath, 'ccp4').matrix
#
#    def _plotVolumeSlices(self, **kwargs):
#        from ResMap_visualization import plotOriginalVolume
#        fig = plotOriginalVolume(self._getVolumeMatrix('volume1.map'), **kwargs)
#        return Plotter(figure=fig)
#
#    def _plotResMapSlices(self, data=None, **kwargs):
#        from ResMap_visualization import plotResMapVolume
#        plotDict = loads(self.plotData.get())
#        if data is None:
#            data = self._getVolumeMatrix('volume1_resmap.map')
#            data = np.ma.masked_where(data > plotDict['currentRes'], data,
#                                      copy=True)
#        kwargs.update(plotDict)
#        fig = plotResMapVolume(data, **kwargs)
#        return Plotter(figure=fig)
#
#    def _plotHistogram(self):
#        from ResMap_visualization import plotResolutionHistogram
#        histogramData = loads(self.histogramData.get())
#        fig = plotResolutionHistogram(histogramData)
#        return Plotter(figure=fig)
#
#    def _parseOutput(self):
#        meanRes, medianRes = 0, 0
#        f = open(self.getLogPaths()[0], 'r')
#        for line in f.readlines():
#            if 'MEAN RESOLUTION in MASK' in line:
#                meanRes = line.strip().split('=')[1]
#            elif 'MEDIAN RESOLUTION in MASK' in line:
#                medianRes = line.strip().split('=')[1]
#        f.close()
#
#        return tuple(map(float, (meanRes, medianRes)))
#