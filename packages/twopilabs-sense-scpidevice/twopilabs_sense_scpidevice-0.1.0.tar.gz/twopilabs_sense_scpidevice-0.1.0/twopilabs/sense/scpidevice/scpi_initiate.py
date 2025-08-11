from typing import *
from twopilabs.utils.scpi import *
from .acquisition import *

class ScpiInitiate(object):
    """Class containing SCPI commands concerning the INITIATE subsystem"""

    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def immediate(self):
        """Immediately initiates (arms) the device for a single trigger event.
        When trigger source is IMMEDIATE (default), the device will trigger immediately."""
        self.device.execute("INIT:IMM")
        self.device.raise_error()

    def immediate_and_receive(self) -> Optional[Acquisition]:
        """Immediately initiates (arms) the device, waits for trigger and returns an acquisition object."""
        self.immediate()
        return self.device.calc.data(wait=True)

    def continuous(self, enabled: Optional[bool]=None) -> bool:
        """Enters or exits the continuous initiate mode

        :param enabled: Continuous mode enabled or disabled
        """
        if enabled is not None:
            self.device.execute('INIT:CONT', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute('INIT:CONT?', result=ScpiBool).as_bool()

        self.device.raise_error()
        return enabled