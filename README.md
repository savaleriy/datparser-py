# datparser-py 

A Python library for parsing `.DAT` format files exported from R&S ESRP spectrum analyzer (`TRACE -> EXPORT TRACES IN ASCII`). 

## Requirements

- Python 3.11+
- Optional: pandas for DataFrame support

## Quick Start

### Basic Usage

```python
from datparser import ESRPFile

# Load ESRP file
esrp = ESRPFile("measurement.DAT")

# Basic file information
print(esrp)
# Output: ESRP File: measurement.DAT
#         Scans: 2, Traces: 3
#         File size: 1024 bytes

# Access metadata
print("Global metadata:", esrp.metadata)

# Access scan parameters
for i, scan in enumerate(esrp.scans):
    print(f"Scan {i} ({scan.name}): {len(scan.parameters)} parameters")

# Access trace information
for i, trace in enumerate(esrp.traces):
    print(f"Trace {i}: {trace.data.point_count} data points")
```

### DataFrame Conversion

```python
import pandas as pd

# Convert single trace to DataFrame (default behavior)
df_single = esrp.to_dataframe(trace_index=0)
print(f"Single trace shape: {df_single.shape}")

# Convert all traces to a combined DataFrame
df_all = esrp.get_combined_dataframe()
print(f"Combined traces shape: {df_all.shape}")
print(f"Columns: {list(df_all.columns)}")

# Convert specific trace using convenience method
df_trace1 = esrp.get_trace_dataframe(1)

# Convert traces from specific scan
df_scan0 = esrp.get_scan_dataframe(0)
```

### Advanced Usage

```python
# Flexible DataFrame conversion options
from pathlib import Path

# Using Path objects
file_path = Path("data/measurement.DAT")
esrp = ESRPFile(file_path)

# Class method alternative
esrp = ESRPFile.from_file("measurement.DAT")

# Access specific data
trace_metadata = esrp.get_trace_metadata(0)
scan_parameters = esrp.get_scan_parameters(0)
trace_data = esrp.get_trace_data(0)

print(f"X-unit: {esrp.traces[0].x_unit}")
print(f"Y-unit: {esrp.traces[0].y_unit}")
print(f"Trace name: {esrp.traces[0].trace_name}")
```

## API Reference

### ESRPFile Class

Main class for working with ESRP files.

#### Initialization
```python
ESRPFile(file_path: Union[str, Path])
```

#### Methods
- `to_dataframe(trace_index=None, scan_index=None, include_all_traces=False)` - Convert to DataFrame with flexible options
- `get_trace_dataframe(trace_index=0)` - Get DataFrame for specific trace
- `get_scan_dataframe(scan_index=0)` - Get DataFrame for traces in specific scan
- `get_combined_dataframe()` - Get DataFrame with all traces combined
- `get_trace_metadata(trace_index=0)` - Get metadata for specific trace
- `get_scan_parameters(scan_index=0)` - Get parameters for specific scan
- `get_trace_data(trace_index=0)` - Get data points for specific trace

#### Properties
- `metadata` - Global file metadata
- `scans` - List of Scan objects
- `traces` - List of Trace objects
- `scan_count` - Number of scans
- `trace_count` - Number of traces
- `file_name` - Name of the file
- `file_size` - Size of the file in bytes

### Data Classes

- `Scan(name, parameters)` - Represents a scan section
- `Trace(metadata, data, name)` - Represents a trace with metadata and data
- `TraceData(x, y)` - Container for trace data points

## Examples

### Working with Multiple Traces

```python
esrp = ESRPFile("multi_trace.DAT")

# Get combined DataFrame with all traces
df = esrp.get_combined_dataframe()

# Each trace gets its own column with descriptive names
# Columns: [x_unit, "Trace 0 y_unit", "Trace 1 y_unit", ...]
print(df.columns)
# Output: ['MHz', 'Peak Hold dBm', 'Average dBm', 'Trace 2 dB']

# Plot all traces
import matplotlib.pyplot as plt

x_col = df.columns[0]  # First column is x-axis
for y_col in df.columns[1:]:
    plt.plot(df[x_col], df[y_col], label=y_col)

plt.xlabel(x_col)
plt.legend()
plt.show()
```

### Accessing Specific Data

```python
# Get specific trace data
trace_0_data = esrp.get_trace_data(0)
print(f"X values: {trace_0_data.x[:5]}")  # First 5 x values
print(f"Y values: {trace_0_data.y[:5]}")  # First 5 y values
print(f"Total points: {trace_0_data.point_count}")

# Access scan information
scan_0_params = esrp.get_scan_parameters(0)
print(f"Scan parameters: {scan_0_params}")
```

## Testing

Run the test suite:

```bash
pytest -v
```


## Build

```bash
# Install build dependencies
uv add --dev hatchling hatch-vcs

# Build source distribution and wheel
uv build

# Build only wheel
uv build --wheel

# Build only sdist
uv build --sdist
```

