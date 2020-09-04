from pwem.wizards import ColorScaleWizardBase
from resmap.viewers import ResMapViewer


class ResmapColorScaleWizard(ColorScaleWizardBase):
    _targets = ColorScaleWizardBase.defineTargets(ResMapViewer)