# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se)
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk)
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
import re

import pyworkflow.protocol.params as params
from pwem.objects import Volume
from pwem.protocols import ProtAnalysis3D
from pwem.emlib.image import ImageHandler
from pyworkflow.utils import exists

import resmap
from resmap.constants import *



class ProtResMap(ProtAnalysis3D):
    """
    ResMap is software tool for computing the local resolution of 3D
    density maps from electron cryo-microscopy (cryo-EM).

    Please find the manual at https://sourceforge.net/projects/resmap-latest
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
            'mask': self._getExtraPath('mask.map'),
            'outVol': self._getExtraPath('volume1_ori.map'),
            RESMAP_VOL: self._getExtraPath('volume1_ori_resmap.map'),
            'outChimeraCmd': self._getExtraPath(CHIMERA_CMD),
            'logFn': self._getExtraPath('ResMaps.log')
        }
        self._updateFilenamesDict(myDict)

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addHidden(params.USE_GPU, params.BooleanParam, default=False,
                       label="Use GPU?")
        form.addHidden(params.GPU_LIST, params.StringParam, default='0',
                       label="Choose GPU ID",
                       help="GPU may have several cores. Set it to zero"
                            " if you do not know what we are talking about."
                            " First core index is 0, second 1 and so on.\n\n"
                            "ResMap can use only one GPU.\n\n"
                            "GPU calculation should not be enabled if your "
                            "maps are smaller than 140x140x140, or if "
                            "your maps are larger than 700x700x700. "
                            "If your maps have a size between 140x140x140 "
                            "and 700x700x700, you may enable GPU usage. "
                            "For maps smaller than 140x140x140, the CPU "
                            "calculation is likely to be just as fast "
                            "as the GPU (hence GPU need not be used). "
                            "For maps larger than 700x700x700, the GPU "
                            "is likely not to have sufficient memory "
                            "for the calculation (this upper limit holds "
                            "for GTX 1080 Ti GPUs.")
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
        form.addParam('show2D', params.BooleanParam, default=True,
                      expertLevel=params.LEVEL_ADVANCED,
                      label="Visualize 2D results?",
                      help="By default ResMap will display 2D results.")

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
        form.addHidden('doBenchmarking', params.BooleanParam, default=False)

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
        self.runJob(program, args, cwd=self._getExtraPath(),
                    numberOfThreads=1)

    def createOutputStep(self):
        outputVolumeResmap = Volume()
        outputVolumeResmap.setSamplingRate(self.volumeHalf1.get().getSamplingRate())
        outputVolumeResmap.setFileName(self._getFileName(RESMAP_VOL))

        self._defineOutputs(outputVolume=outputVolumeResmap)
        self._defineTransformRelation(self.volumeHalf1, outputVolumeResmap)
        self._defineTransformRelation(self.volumeHalf2, outputVolumeResmap)

    # --------------------------- INFO functions ------------------------------
    def _summary(self):
        summary = []

        self._createFilenameTemplates()
        if exists(self._getFileName('outResmapVol')):
            results = self._parseOutput()
            summary.append('Mean resolution: %0.2f A' % results[0])
            summary.append('Median resolution: %0.2f A' % results[1])
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

        if self.show2D:
            args += " --vis2D"

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

        if self.useGpu:
            args += " --use_gpu=yes --set_gpu=%s" % self.gpuList.get()
            args += ' --lib_krnl_gpu="%s"' % resmap.Plugin.getGpuLib()

        if self.doBenchmarking:
            args += ' --doBenchMarking'

        return args % params

    def _parseOutput(self):
        meanRes, medianRes = 0, 0
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        f = open(self._getFileName('logFn'), 'r')
        for line in f.readlines():
            if 'MEAN RESOLUTION in MASK' in line:
                meanRes = ansi_escape.sub('', line.strip().split('=')[1])
            elif 'MEDIAN RESOLUTION in MASK' in line:
                medianRes = ansi_escape.sub('', line.strip().split('=')[1])
        f.close()

        return tuple(map(float, (meanRes, medianRes)))
