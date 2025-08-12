from twopilabs.utils.scpi import *

from .scpi_control import ScpiControl
from .scpi_calc import ScpiCalc
from .scpi_sense import ScpiSense
from .scpi_initiate import ScpiInitiate
from .scpi_core import ScpiCore
from .scpi_system import ScpiSystem
from .scpi_trigger import ScpiTrigger


class SenseScpiDevice(ScpiDevice):
    def __init__(self, resource: ScpiResource, **kwargs):
        ScpiDevice.__init__(self, resource, **kwargs)
        self.core = ScpiCore(self)
        self.control = ScpiControl(self)
        self.sense = ScpiSense(self)
        self.initiate = ScpiInitiate(self)
        self.calc = ScpiCalc(self)
        self.system = ScpiSystem(self)
        self.trigger = ScpiTrigger(self)