from typing import *
from twopilabs.utils.scpi import *


class ScpiCore(object):
    """Class containing core SCPI commands"""

    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def idn(self) -> List[str]:
        """Executes a \*IDN? command to read device identification string"""
        idn = self.device.execute('*IDN?', result=ScpiChars)
        return idn.as_string().split(',')

    def cls(self) -> None:
        """Executes a \*CLS command to clear all status data structures in the device"""
        self.device.execute('*CLS')

    def rst(self) -> None:
        """Executes a \*RST command to stop execution of all overlapped (asynchronous) commands and resets the device"""
        self.device.execute('*RST')

    def sav(self, slot: int = 0 ) -> None:
        """Executes a \*SAV command to save system state into given slot

        :param slot: Memory register slot
        """
        self.device.execute('*SAV', param=ScpiNumber(int(slot)))

    def rcl(self, slot: int = 0) -> None:
        """Executes a \*RCL command to recall system state from given slot

        :param slot: Memory register slot
        """
        self.device.execute('*RCL', param=ScpiNumber(int(slot)))

    def sds(self, slot: int = 0) -> None:
        """Executes a \*SDS command to set the system state in given slot to defaults

        :param slot: Memory register slot
        """
        self.device.execute('*SDS', param=ScpiNumber(int(slot)))

    def trg(self) -> None:
        """Executes a \*TRG command to soft-trigger the device in initiated state waiting for a trigger"""
        self.device.execute('*TRG')

    def wai(self) -> None:
        """Executes a \*WAI command to wait for all overlapped (asynchronous) commands to finish"""
        self.device.execute('*WAI')

    def opc(self) -> bool:
        """Executes a \*OPC? command to wait for all overlapped (asynchronous) commands to finish and returns '1'"""
        completed = self.device.execute('*OPC?', result=ScpiBool)
        return completed.as_bool()
