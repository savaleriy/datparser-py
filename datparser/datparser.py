import typing
from dataclasses import dataclass, field

@dataclass
class ParserState:
    """Class to holdd dynamic variables while parsing the .DAT file
    """


        def _parse_file(self):
        """Main parsing function to process the file content."""
        lines = self.file_content.splitlines()
        current_trace = None
        current_scan = None

        for line in lines:
            line = line.strip()

            # Handle trace section
            if line.startswith("TRACE"):
                if current_trace:
                    self.traces.append(current_trace)
                current_trace = {"metadata": {}, "frequencies": [], "amplitudes": []}
            elif current_trace:
                self._parse_trace_line(line, current_trace)

            # Handle scan section
            elif line.startswith("Scan"):
                if current_scan:
                    self.scans.append(current_scan)
                current_scan = {"metadata": {}}
            elif current_scan and ";" in line:
                self._parse_scan_line(line, current_scan)

            # Handle general metadata
            else:
                self._parse_metadata_line(line)

        # Add the last trace and scan if applicable
        if current_trace:
            self.traces.append(current_trace)
        if current_scan:
            self.scans.append(current_scan)

    def _parse_metadata_line(self, line: str) -> None:
        """Parse a single line of general metadata."""
        if ";" in line:
            key, *value = line.split(";")
            self.metadata[key.strip()] = ";".join(value).strip()

    def _parse_scan_line(self, line: str, scan: dict) -> None:
        """Parse a single line of scan metadata."""
        if ";" in line:
            key, *value = line.split(";")
            scan["metadata"][key.strip()] = ";".join(value).strip()

    def _parse_trace_line(self, line: str, trace: dict) -> None:
        """Parse a line of trace data or metadata."""
        if 'Values;' in line:
            trace["metadata"]["Values"] = int(line.split(';')[1].strip())
        elif ';' in line and line.split(";")[0].replace(".", "", 1).isdigit():
            try:
                freq, amp = map(float, line.split(";")[:2])
                trace["frequencies"].append(freq)
                trace["amplitudes"].append(amp)
            except ValueError:
                pass  # Ignore invalid lines
        elif ";" in line:
            key, *value = line.split(";")
            trace["metadata"][key.strip()] = ";".join(value).strip()

    def get_metadata(self):
        """Return general metadata."""
        return self.metadata

    def get_scans(self):
        """Return all scans' metadata."""
        return self.scans

    def get_traces(self):
        """Return all traces with their metadata and values."""
        return self.traces

class Dat:
    """
    It is should be basic class to store .DAT info

    like in network.py in scikit-rf
    """
    def __init__(self, file : str | typing.TextIO, encoding : str | None = None):
        """
        constructor
        """
        pass

# Example usage
if __name__ == "__main__":
    file_content = """Type;ESRP-7;
Version;3.36 SP1;
Date;03.Feb 18;
Mode;Receiver;
Start;150000.000000;Hz
Stop;1000000000.000000;Hz
x-Axis;LIN;
Detector;MAX PEAK;
Scan Count;1;
Transducer;;;;;;;
Scan 1:
Start;150000.000000;Hz
Stop;29998500.000000;Hz
Step;2250.000000;Hz
RBW;9000.000000;Hz
Meas Time;0.001000;s
Auto Ranging;OFF;
RF Att;10.000000;dB
Auto Preamp;OFF;
Preamp;0.000000;dB
Scan 2:
Start;30000000.000000;Hz
Stop;1000000000.000000;Hz
Step;2250.000000;Hz
RBW;9000.000000;Hz
Meas Time;0.001000;s
Auto Ranging;OFF;
RF Att;10.000000;dB
Auto Preamp;OFF;
Preamp;0.000000;dB
TRACE 1:
Trace Mode;MAX HOLD;
x-Unit;Hz;
y-Unit;dBµV;
Values;444380;
150000.000000;6.154694;
152250.000000;6.300735;
154500.000000;5.021690;
156750.000000;5.843552;
159000.00000;6.031052;
161250.000000;5.537994;"""

    parser = DatParser(file_content=file_content)

    print("Metadata:", parser.get_metadata())
    print("Scans:", parser.get_scans())
    print("Traces:", parser.get_traces())
0
