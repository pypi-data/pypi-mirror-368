from enum import Enum, Flag, IntFlag

class PowerLevel(Enum):
    UNKNOWN = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    AUTO = 4

# Enums for CONTrol subsystem
class RampMode(Enum):
    """Ramp mode used with CONTrol:RADAR:MPLL:RMODe"""
    SINGLE = 0
    """Perform single ramps on each trigger"""
    DOUBLE = 1
    """Perform double ramps on each trigger"""
    ALTERNATING = 2
    """Perform alternating ramps on each trigger"""


class ChannelCoupling(Enum):
    """Frontend coupling of receive channel used with CONTrol:RADAR:FRONtend:CHANnel#:COUPling"""
    GND = 0
    """Set GND channel coupling"""
    DC = 1
    """Set DC channel coupling"""
    AC = 2
    """Set AC channel coupling (R^2 compensation)"""


class ChannelForce(Enum):
    """Frontend channel force used with CONTrol:RADAR:FRONtend:CHANnel#:FORCe"""
    NONE = 0
    """Do not force channel state"""
    ON = 1,
    """Force channel to always-on"""
    OFF = 2
    """Force channel to always-off"""


# Enums for SENSe subsystem
class FrequencyMode(Enum):
    """Frequency mode used with SENSe:FREQuency:MODE"""
    CW = 0
    """Operate in continuous wave mode on a single frequency (aka zero-span)"""
    SWEEP = 1
    """Operate in swept mode (normal)"""


class SweepDirection(Enum):
    """Sweep direction used with SENSe:SWEep:DIRection"""
    DOWN = -1
    """Sweep slope of (first) sweep is down"""
    UP = 1
    """Sweep slope of (first) sweep is up"""


class SweepMode(Enum):
    """Sweep mode used with SENSe:SWEep:MODE"""
    NORMAL = 0
    """Sweep slope is constant with jump back to start frequency at the end of sweep"""
    ALTERNATING = 1
    """Sweep slope is alternating in consecutive sweeps"""


class RefOscSource(Enum):
    """Reference Oscillator source used with SENSe:ROSCillator:SOURCE"""
    NONE = 0
    """No reference oscillator, free running"""
    INTERNAL = 1
    """Internal reference oscillator source (if available)"""
    EXTERNAL = 2
    """External reference oscillator source (if available)"""


class RefOscStatus(Enum):
    """Status of reference oscillator used with SENSe:ROSCillator:STATus"""
    OFF = 0
    """Reference oscillator PLL is disabled, i.e. during power-off"""
    HOLDOVER = 1
    """Reference oscillator PLL is in holdover mode (source lost)"""
    LOCKING = 2
    """Reference oscillator PLL is trying to lock to selected reference"""
    LOCKED = 3
    """Reference oscillator PLL is locked to selected reference"""
    LOCK = 3
    """Deprecated"""


# Enums for TRIGger subsystem
class TrigSource(Enum):
    """Trigger source used with TRIGger:SOURce"""
    IMMEDIATE = 0
    """A trigger will commence immediately after the device is initiated"""
    TIMER = 1
    """Acquisitions are triggered using an internal timer"""
    EXTERNAL = 2
    """An external trigger input is used for triggering the acquisition"""
    INTERNAL = 3
    """An internal trigger signal is used for triggering the acquisition"""