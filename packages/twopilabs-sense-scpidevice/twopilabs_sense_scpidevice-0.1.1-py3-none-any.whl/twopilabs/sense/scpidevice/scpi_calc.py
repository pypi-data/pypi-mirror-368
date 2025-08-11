import io
from typing import *
from twopilabs.utils.scpi import *
from .acquisition import *


class ScpiCalc(object):
    """Class containing SCPI commands concerning CALCULATE subsystem"""

    def __init__(self, device: ScpiDevice):
        self.device = device

    def trace_list(self, traces: Optional[List[int]] = None) -> List[int]:
        """Sets or gets the list of selected traces that are processed and for which CALC data is available"""
        if traces is not None:
            self.device.execute('CALCULATE:TRACE:LIST', param=ScpiNumList(traces))
        else:
            traces = self.device.execute('CALCULATE:TRACE:LIST?', result=ScpiNumList).as_list()

        self.device.raise_error()
        return traces

    def data(self, wait: bool=True) -> Optional[Acquisition]:
        # Only reads the header information and returns a stream for further reading of data
        stream = self.device.execute('*WAI;CALC:DATA?' if wait else 'CALC:DATA?', result=ScpiArbStream)
        if stream is None or stream._length == 0:
            # Radar has no data in FIFO
            self.device.raise_error()
            return None
        return Acquisition._from_stream(stream)

    def data_all(self, acq_count: int=None, wait: bool=True) -> List[Acquisition]:
        """Reads all (or given number of) acquisitions from radar and returns.
           Optionally waits for data to be available initially"""
        memory_stream = self.device.execute(f'{"*WAI;" if wait else ""}CALC:DATA:ALL?',
                                            param=ScpiNumber(acq_count) if acq_count is not None else None,
                                            result=ScpiArbBlock)
        acquisitions = []

        if memory_stream is None or memory_stream._length == 0:
            # Radar has no data in FIFO
            self.device.raise_error()
            return acquisitions

        while memory_stream._remaining > 0:
            # Create acquisition object from the in-memory stream and store into list object
            acq = Acquisition._from_stream(ScpiArbBlock(memory_stream.as_memoryview()))
            acquisitions.append(acq)
            memory_stream.seek(acq.header.header_length +
                               acq.header.sweep_count * acq.header.trace_count * acq.header.trace_size,
                               io.SEEK_CUR)

        return acquisitions

    def data_available(self, wait: bool=True) -> List[Acquisition]:
        """Reads all (or given number of) acquisitions from radar and returns.
           Optionally waits for data to be available initially"""
        memory_stream = self.device.execute(f'{"*WAI;" if wait else ""}CALC:DATA:AVAILABLE?',
                                            result=ScpiArbBlock)
        acquisitions = []

        if memory_stream is None or memory_stream._length == 0:
            # Radar has no data in FIFO
            self.device.raise_error()
            return acquisitions

        while memory_stream._remaining > 0:
            # Create acquisition object from the in-memory stream and store into list object
            acq = Acquisition._from_stream(ScpiArbBlock(memory_stream.as_memoryview()))
            acquisitions.append(acq)
            memory_stream.seek(acq.header.header_length +
                               acq.header.sweep_count * acq.header.trace_count * acq.header.trace_size,
                               io.SEEK_CUR)

        return acquisitions