"""
ESRP Spectrum Analyzer Trace export file format parser
"""

try:
    import pandas as pd
except ImportError:
    pd = None


class ESRPFile:
    def __init__(self, file_path):
        self.metadata = {}
        self.scans = []
        self.traces = []
        self._parse(file_path)

    def _parse(self, file_path):
        current_scan = None
        current_trace = None
        in_trace = False
        in_trace_data = False

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Split line into parts and remove empty/whitespace-only parts
            parts = [p.strip() for p in line.split(";") if p.strip()]
            if not parts:
                continue

            key = parts[0]

            # Handle Scan sections
            if key.startswith("Scan") and key.endswith(":"):
                current_scan = {"name": key[:-1].strip(), "parameters": {}}
                self.scans.append(current_scan)
                in_trace = False
                in_trace_data = False
                current_trace = None

            # Handle Trace sections
            elif key.startswith("TRACE"):
                current_trace = {"metadata": {}, "data": {"x": [], "y": []}}
                self.traces.append(current_trace)
                in_trace = True
                in_trace_data = False

            # Handle Trace data and metadata
            elif in_trace:
                if key == "Values":
                    current_trace["metadata"][key] = parts[1:]
                    in_trace_data = True
                elif in_trace_data:
                    if len(parts) >= 2:
                        try:
                            x = float(parts[0])
                            y = float(parts[1])
                            current_trace["data"]["x"].append(x)
                            current_trace["data"]["y"].append(y)
                        except ValueError:
                            pass
                else:
                    current_trace["metadata"][key] = parts[1:]

            # Handle Scan parameters and global metadata
            else:
                if current_scan is not None:
                    current_scan["parameters"][key] = parts[1:]
                else:
                    self.metadata[key] = parts[1:]

    def get_scan_parameters(self, scan_index=0):
        """
        Get parameters for a specific scan.

        Args:
            scan_index (int): Index of the scan to retrieve (default: 0)

        Returns:
            dict: Dictionary of scan parameters
        """
        try:
            return self.scans[scan_index]["parameters"]
        except IndexError:
            raise ValueError(f"Scan index {scan_index} out of range")

    def get_trace_metadata(self, trace_index=0):
        """
        Get metadata for a specific trace.

        Args:
            trace_index (int): Index of the trace to retrieve (default: 0)

        Returns:
            dict: Dictionary of trace metadata
        """
        try:
            return self.traces[trace_index]["metadata"]
        except IndexError:
            raise ValueError(f"Trace index {trace_index} out of range")

    def to_df(self, trace_index=0):
        """
        Convert trace data to pandas DataFrame.

        Args:
            trace_index (int): Index of the trace to convert (default: 0)

        Returns:
            pd.DataFrame: DataFrame containing x and y values
        """
        if not self.traces:
            return pd.DataFrame() if pd else None

        metadata = self.get_trace_metadata(trace_index=trace_index)
        columns = [metadata["x-Unit"][0], metadata["y-Unit"][0]]

        try:
            trace = self.traces[trace_index]
            return pd.DataFrame(
                {columns[0]: trace["data"]["x"], columns[1]: trace["data"]["y"]}
            )
        except IndexError:
            raise ValueError(f"Trace index {trace_index} out of range")
        except ImportError as e:
            raise RuntimeError("pandas is required for DataFrame conversion") from e


# Example usage:
if __name__ == "__main__":
    esrp = ESRPFile("../test.DAT")

    # Access global metadata
    print("File metadata:", esrp.metadata)

    # Access scan parameters
    for i, scan in enumerate(esrp.scans):
        print(f"Scan {i} parameters:", scan["parameters"])

    # Access trace data and metadata
    for i, trace in enumerate(esrp.traces):
        print(f"Trace {i} metadata:", trace["metadata"])
        df = esrp.to_dataframe(i)
        print(f"Data points in trace {i}: {len(df)}")
