from twopilabs.utils.scpi import *
from typing import *
from .constants import *

class ScpiSense(object):
    """Class containing SCPI commands concerning SENSE subsystem"""

    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def frequency_cw(self, freq: Optional[float] = None) -> float:
        """Sets or gets CW frequency

        :param freq: Continuous-Wave frequency in Hz
        """
        if freq is not None:
            self.device.execute('SENSE:FREQ:CW', param=ScpiNumber(freq, unit='HZ'))
        else:
            freq = self.device.execute('SENSE:FREQ:CW?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return freq

    def frequency_start(self, freq: Optional[float] = None) -> float:
        """Sets or gets sweep start frequency

        :param freq: Sweep start frequency in Hz
        """
        if freq is not None:
            self.device.execute('SENSE:FREQ:START', param=ScpiNumber(freq, unit='HZ'))
        else:
            freq = self.device.execute('SENSE:FREQ:START?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return freq

    def frequency_stop(self, freq: Optional[float] = None) -> float:
        """Sets or gets sweep stop frequency

        :param freq: Sweep stop frequency in Hz
        """
        if freq is not None:
            self.device.execute('SENSE:FREQ:STOP', param=ScpiNumber(freq, unit='HZ'))
        else:
            freq = self.device.execute('SENSE:FREQ:STOP?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return freq

    def frequency_center(self, freq: Optional[float] = None) -> float:
        """Sets or gets sweep center frequency. Modifies sweep frequency span to stay within allowed limits

        :param freq: Sweep center frequency in Hz
        """
        if freq is not None:
            self.device.execute('SENSE:FREQ:CENTER', param=ScpiNumber(freq, unit='HZ'))
        else:
            freq = self.device.execute('SENSE:FREQ:CENTER?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return freq

    def frequency_span(self, freq: Optional[float] = None) -> float:
        """Sets or gets sweep frequency span. Modifies sweep center frequency to stay within allowed limits.

        :param freq: Sweep frequency span in Hz (positive or negative value for up- or downslope)
        """
        if freq is not None:
            self.device.execute('SENSE:FREQ:SPAN', param=ScpiNumber(freq, unit='HZ'))
        else:
            freq = self.device.execute('SENSE:FREQ:SPAN?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return freq

    def frequency_overrange(self, enabled: Optional[bool] = None) -> bool:
        """Enables or disables frequency overrange mode

        :param enabled: Overrange mode enabled or disabled
        """
        if enabled is not None:
            self.device.execute('SENSE:FREQ:OVERRANGE', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute('SENSE:FREQ:OVERRANGE?', result=ScpiBool)

        self.device.raise_error()
        return enabled

    def frequency_mode(self, mode: Optional[FrequencyMode] = None) -> FrequencyMode:
        """Sets or gets sweep frequency mode

        :param mode: Sweep mode
        """
        if mode is not None:
            self.device.execute('SENSE:FREQ:MODE', param=ScpiChars(mode.name))
        else:
            mode = FrequencyMode[(self.device.execute('SENSE:FREQ:MODE?', result=ScpiChars)).as_string()]

        self.device.raise_error()
        return mode

    def sweep_points(self, points: Optional[int] = None) -> int:
        """Sets or gets number of points per sweep. Modifies sweep time to achieve the system sample-rate

        :param points: Number of sweep points
        """
        if points is not None:
            self.device.execute('SENSE:SWEEP:POINTS', param=ScpiNumber(points))
        else:
            points = self.device.execute('SENSE:SWEEP:POINTS?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return points

    def sweep_time(self, time: Optional[float] = None) -> float:
        """Sets or gets the sweep duration. Modifies points per sweep to achieve the system sample-rate

        :param time: Sweep duration
        """
        if time is not None:
            self.device.execute('SENSE:SWEEP:TIME', param=ScpiNumber(time, unit='S'))
        else:
            time = self.device.execute('SENSE:SWEEP:TIME?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return time

    def sweep_direction(self,
                        direction: Optional[SweepDirection] = None) -> SweepDirection:
        """Sets or gets the sweep slope of first sweep in acquisition

        :param direction: Sweep direction
        """
        if direction is not None:
            self.device.execute('SENSE:SWEEP:DIRECTION', param=ScpiChars(direction.name))
        else:
            direction = SweepDirection[self.device.execute(
                'SENSE:SWEEP:DIRECTION?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return direction

    def sweep_mode(self, mode: Optional[SweepMode] = None) -> SweepMode:
        """Sets or gets the sweep mode for multiple sweeps

        :param mode: Sweep mode (single or alternating sweeps)"""
        if mode is not None:
            self.device.execute('SENSE:SWEEP:MODE', param=ScpiChars(mode.name))
        else:
            mode = SweepMode[self.device.execute('SENSE:SWEEP:MODE?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return mode

    def sweep_count(self, count: Optional[int] = None) -> int:
        """Sets or gets the number of sweeps in an acquisition

        :param count: Number of sweeps per trigger
        """
        if count is not None:
            self.device.execute('SENSE:SWEEP:COUNT', param=ScpiNumber(count))
        else:
            count = self.device.execute('SENSE:SWEEP:COUNT?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return count

    def sweep_period(self, period: Optional[float] = None) -> float:
        """Sets or gets the sweep period for multi-sweep acquisitions

        :param period: Sweep period
        """
        if period is not None:
            self.device.execute('SENSE:SWEEP:PERIOD', param=ScpiNumber(period, unit='S'))
        else:
            period = self.device.execute('SENSE:SWEEP:PERIOD?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return period

    def refosc_source_selected(self, source: Optional[RefOscSource] = None) -> RefOscSource:
        """Sets or gets the selected reference oscillator source

        :param source: Selected reference oscillator source
        """
        if source is not None:
            self.device.execute('SENSE:ROSC:SOURCE:SELECTED', param=ScpiChars(source.name))
        else:
            source = RefOscSource[self.device.execute('SENSE:ROSC:SOURCE:SELECTED?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return source

    def refosc_source_current(self) -> RefOscSource:
        """Returns the currently used reference oscillator source"""
        source = RefOscSource[self.device.execute('SENSE:ROSC:SOURCE:CURRENT?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return source

    def refosc_status(self) -> RefOscStatus:
        """Returns the reference oscillator status"""
        status = RefOscStatus[self.device.execute('SENSE:ROSC:STATUS?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return status

    def refosc_internal_freq_adjust(self, adjustment: Optional[float] = None) -> float:
        if adjustment is not None:
            self.device.execute('SENSE:ROSC:INTERNAL:FREQ:ADJUST', param=ScpiNumber(adjustment))
        else:
            adjustment = self.device.execute('SENSE:ROSC:INTERNAL:FREQ:ADJUST?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return adjustment