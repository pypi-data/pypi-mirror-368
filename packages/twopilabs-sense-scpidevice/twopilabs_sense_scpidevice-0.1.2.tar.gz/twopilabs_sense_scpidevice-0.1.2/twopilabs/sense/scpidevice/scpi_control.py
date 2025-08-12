from typing import *
from twopilabs.utils.scpi import *
from .constants import *


class ScpiControl(object):
    """Class containing SCPI commands concerning CONTROL subsystem"""

    def __init__(self, device: ScpiDevice) -> None:
        self.device = device

    def power_level_selected(self, level: Optional[PowerLevel] = None) -> PowerLevel:
        """sets/gets the power level"""
        if level is not None:
            self.device.execute('CONTROL:POWER:LEVEL:SELECTED', param=ScpiChars(level.name))
        else:
            level = PowerLevel[self.device.execute('CONTROL:POWER:LEVEL:SELECTED?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return level

    def power_level_detected(self) -> PowerLevel:
        """returns the detected power level"""
        level = PowerLevel[self.device.execute('CONTROL:POWER:LEVEL:DETECTED?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return level

    def power_level_current(self) -> PowerLevel:
        """returns the current effective power level"""
        level = PowerLevel[self.device.execute('CONTROL:POWER:LEVEL:CURRENT?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return level

    def radar_mainpll_nint(self, nint: Optional[int] = None) -> int:
        """sets/gets main PLL N divider (integer part)"""
        if nint is not None:
            self.device.execute('CONTROL:RADAR:MPLL:NINT', param=ScpiNumber(nint))
        else:
            nint = self.device.execute('CONTROL:RADAR:MPLL:NINT?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return nint

    def radar_mainpll_nfrac(self, nfrac: Optional[int] = None) -> int:
        """sets/gets main PLL N divider (fractional part)"""
        if nfrac is not None:
            self.device.execute('CONTROL:RADAR:MPLL:NFRAC', param=ScpiNumber(nfrac))
        else:
            nfrac = self.device.execute('CONTROL:RADAR:MPLL:NFRAC?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return nfrac

    def radar_mainpll_rampmode(self, mode: RampMode = None) -> RampMode:
        """sets/gets main PLL ramp mode"""
        if mode is not None:
            self.device.execute('CONTROL:RADAR:MPLL:RMODE', param=ScpiChars(mode.name))
        else:
            mode = RampMode[self.device.execute(
                'CONTROL:RADAR:MPLL:RMODE?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return mode

    def radar_mainpll_rampincr(self, incr: Optional[int] = None, ramp_idx: int = 0) -> int:
        """sets/gets main PLL ramp increment"""
        if incr is not None:
            self.device.execute(f'CONTROL:RADAR:MPLL:RINC{ramp_idx:d}', param=ScpiNumber(incr))
        else:
            incr = self.device.execute(f'CONTROL:RADAR:MPLL:RINC{ramp_idx:d}?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return incr

    def radar_mainpll_ramplen(self, length: Optional[int] = None, ramp_idx: int = 0) -> int:
        """sets/gets main PLL ramp length"""
        if length is not None:
            self.device.execute(f'CONTROL:RADAR:MPLL:RLEN{ramp_idx:d}', param=ScpiNumber(length))
        else:
            length = self.device.execute(f'CONTROL:RADAR:MPLL:RLEN{ramp_idx:d}?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return length

    def radar_mainpll_rampdwell(self, dwell: Optional[int] = None, ramp_idx: int = 0) -> int:
        """sets/gets main PLL ramp dwell"""
        if dwell is not None:
            self.device.execute(f'CONTROL:RADAR:MPLL:RDWELL{ramp_idx:d}', param=ScpiNumber(dwell))
        else:
            dwell = self.device.execute(f'CONTROL:RADAR:MPLL:RDWELL{ramp_idx:d}?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return dwell

    def radar_mainpll_locked(self) -> bool:
        """queries main PLL lock status"""
        locked = self.device.execute('CONTROL:RADAR:MPLL:LOCK?', result=ScpiBool).as_bool()

        self.device.raise_error()
        return locked

    def radar_auxpll_nint(self, nint: Optional[int] = None) -> int:
        """sets/gets aux PLL N divider (integer part)"""
        if nint is not None:
            self.device.execute('CONTROL:RADAR:APLL:NINT', param=ScpiNumber(nint))
        else:
            nint = self.device.execute('CONTROL:RADAR:APLL:NINT?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return nint

    def radar_auxpll_nfrac(self, nfrac: Optional[int] = None) -> int:
        """sets/gets aux PLL N divider (fractional part)"""
        if nfrac is not None:
            self.device.execute('CONTROL:RADAR:APLL:NFRAC', param=ScpiNumber(nfrac))
        else:
            nfrac = self.device.execute('CONTROL:RADAR:APLL:NFRAC?', result=ScpiNumber).as_int()

        self.device.raise_error()
        return nfrac

    def radar_auxpll_locked(self) -> bool:
        """queries main PLL lock status"""
        locked = bool(self.device.execute('CONTROL:RADAR:APLL:LOCK?', result=ScpiBool))

        self.device.raise_error()
        return locked

    def radar_frontend_enable(self, enabled: Optional[bool] = None, chan_idx: int = 0) -> bool:
        """enables/disables radar frontend channel"""
        if enabled is not None:
            self.device.execute(f'CONTROL:RADAR:FRONTEND:CHANNEL{chan_idx:d}:ENABLE', param=ScpiBool(enabled))
        else:
            enabled = self.device.execute(
                f'CONTROL:RADAR:FRONTEND:CHANNEL{chan_idx:d}:ENABLE?', result=ScpiBool).as_bool()

        self.device.raise_error()
        return enabled

    def radar_frontend_force(self, force: Optional[ChannelForce] = None,
                             chan_idx: int = 0) -> ChannelForce:
        """sets/gets radar frontend channel force on/off"""
        if force is not None:
            self.device.execute(f'CONTROL:RADAR:FRONTEND:CHANNEL{chan_idx:d}:FORCE', param=ScpiChars(force.name))
        else:
            force = ChannelForce[self.device.execute(
                f'CONTROL:RADAR:FRONTEND:CHANNEL{chan_idx:d}:FORCE?', result=ScpiChars).as_string()]

        self.device.raise_error()
        return force

    def radar_frontend_power(self, power: Optional[float] = None, chan_idx: int = 0) -> float:
        """sets/gets radar frontend channel TX power"""
        if power is not None:
            self.device.execute(f'CONTROL:RADAR:FRONTEND:CHANNEL{chan_idx:d}:POWER', param=ScpiNumber(power))
        else:
            power = self.device.execute(
                f'CONTROL:RADAR:FRONTEND:CHANNEL{chan_idx:d}:POWER?', result=ScpiNumber).as_float()

        self.device.raise_error()
        return power
