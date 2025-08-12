from typing import *
from twopilabs.utils.scpi import *
import datetime


class ScpiSystem(object):
    """Class containing SCPI commands concerning SYSTEM subsystem"""
    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def error_next(self) -> ScpiEvent:
        return self.device.execute('SYST:ERR:NEXT?', result=ScpiEvent)

    def version(self) -> str:
        """returns supported SCPI version"""
        version = self.device.execute('SYST:VERSION?', result=ScpiChars).as_string()

        self.device.raise_error()
        return version

    def preset(self) -> None:
        """Loads the system defaults"""
        self.device.execute('SYST:PRESET')

    def time(self, time: Optional[datetime.time] = None) -> datetime.time:
        """Sets or gets the radar system time"""
        if time is not None:
            self.device.execute('SYST:TIME', param=ScpiNumberArray([time.hour, time.minute, time.second]))
        else:
            time = datetime.time(*self.device.execute('SYST:TIME?', result=ScpiNumberArray).as_int_list())

        self.device.raise_error()
        return time

    def date(self, date: Optional[datetime.date] = None) -> datetime.date:
        """Sets or gets the radar system date"""
        if date is not None:
            self.device.execute('SYST:DATE', param=ScpiNumberArray([date.year, date.month, date.day]))
        else:
            date = datetime.date(*self.device.execute('SYST:DATE?', result=ScpiNumberArray).as_int_list())

        self.device.raise_error()
        return date

    def timezone(self, posix: Optional[str] = None) -> str:
        """Sets or gets the local timezone in POSIX1003.1 format"""
        if posix is not None:
            self.device.execute('SYST:TZONE', param=ScpiString(posix))
        else:
            posix = self.device.execute('SYST:TZONE?', result=ScpiString).as_string()

        self.device.raise_error()
        return posix

    def utc(self, timestamp: Optional[float] = None):
        """Sets or gets the radar system clock as UTC POSIX timestamp"""
        if timestamp is not None:
            self.device.execute('SYST:UTC', param=ScpiNumber(timestamp))
        else:
            timestamp = self.device.execute('SYST:UTC?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return timestamp