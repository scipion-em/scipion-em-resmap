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

from pyworkflow.protocol.params import LabelParam
from pyworkflow.viewer import ProtocolViewer, DESKTOP_TKINTER
from pyworkflow.em.viewers import ChimeraView

from resmap.protocols import ProtResMap


class ResMapViewer(ProtocolViewer):
    """Visualization tools for ResMap results. """

    _environments = [DESKTOP_TKINTER]
    _targets = [ProtResMap]
    _label = 'viewer'

    def __init__(self, *args, **kwargs):
        ProtocolViewer.__init__(self, *args, **kwargs)

    def _defineParams(self, form):
        form.addSection(label='Visualization')
        form.addParam('doShowLogFile', LabelParam,
                      label="Show log file")
        form.addParam('doShowChimera', LabelParam,
                      label="Show Chimera animation")

    def _getVisualizeDict(self):
        self.protocol._createFilenameTemplates()
        return {
                'doShowLogFile': self._showLogFile,
                'doShowChimera': self._showChimera
                }

    def _showLogFile(self, param=None):
        return [self.textView([self.protocol._getFileName('logFn')],
                              "ResMap log file")]

    def _showChimera(self, param=None):
        cmdFile = self.protocol._getFileName('outChimeraCmd')
        view = ChimeraView(cmdFile)
        return [view]
