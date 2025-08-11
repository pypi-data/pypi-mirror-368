from typing import *
from twopilabs.utils.scpi import *
from .constants import *


class ScpiTrigger(object):
    """Class containing SCPI commands concerning the TRIGGER subsystem"""

    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def immediate(self):
        self.device.execute("TRIG:IMMEDIATE")
        self.device.raise_error()

    def source(self, source: Optional[TrigSource] = None) -> TrigSource:
        """Sets or gets the trigger source

        :param source: Trigger source
        """
        if source is not None:
            self.device.execute('TRIG:SOURCE', param=ScpiChars(source.name))
        else:
            source = TrigSource[self.device.execute('TRIG:SOURCE?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return source

    def count(self, count: Optional[int] = None) -> int:
        """Sets the number of trigger (acquisitions) per one initiate (arming)

        :param count: Trigger count
        """
        if count is not None:
            self.device.execute('TRIG:COUNT', param=ScpiNumber(count))
        else:
            count = self.device.execute('TRIG:COUNT?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return count

    def eventcount(self, eventcount: Optional[int] = None) -> int:
        """Sets the number of trigger events required to trigger one acquisition

        :param eventcount: Trigger event count
        """
        if eventcount is not None:
            self.device.execute('TRIG:ECOUNT', param=ScpiNumber(eventcount))
        else:
            eventcount = self.device.execute('TRIG:ECOUNT?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return eventcount

    def delay(self, delay: Optional[float] = None) -> float:
        """Sets the delay time between a trigger and the actual start of the acquisition in seconds

        :param delay: Trigger delay
        """
        if delay is not None:
            self.device.execute('TRIG:DELAY', param=ScpiNumber(delay))
        else:
            delay = self.device.execute('TRIG:DELAY?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return delay

    def timer_period(self, period: Optional[float] = None) -> float:
        """Sets the time period for the internal timer used for triggering

        :param period: Trigger period
        """
        if period is not None:
            self.device.execute('TRIG:TIMER:PERIOD', param=ScpiNumber(period))
        else:
            period = self.device.execute('TRIG:TIMER:PERIOD?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return period

    def timer_compare(self, timestamp: Optional[float] = None) -> float:
        """Sets the timestamp for the internal timer used for triggering

        :param timestamp: Timestamp when to trigger
        """
        if timestamp is not None:
            self.device.execute('TRIG:TIMER:COMPARE', param=ScpiNumber(timestamp))
        else:
            timestamp = self.device.execute('TRIG:TIMER:COMPARE?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return timestamp