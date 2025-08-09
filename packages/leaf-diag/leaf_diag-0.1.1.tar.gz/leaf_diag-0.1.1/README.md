# leaf-diag

A comprehensive diagnostic tool for analyzing and synchronizing flight logs from drone systems, supporting both PX4 ULog and ROS bag file formats with advanced correlation-based time synchronization.

## Overview

`leaf-diag` is designed to process and analyze flight log data from drone systems, providing time-synchronized data analysis, visualization, and export capabilities. The tool excels at:

**Core Features:**
- **Time Synchronization**: Advanced correlation-based algorithm to automatically synchronize PX4 ULog and ROS bag data
- **Multi-format Support**: Native support for PX4 ULog files and ROS bag files
- **Signal Processing**: Handles both single-instance and multi-instance sensor data
- **Data Transformation**: Automatic coordinate frame transformations between PX4 (NED) and DroneLeaf coordinate systems
- **Robust Correlation**: NaN-aware correlation calculations with negative offset support

**Supported Flight Types:**
- Indoor flights with optical flow and distance sensors
- Outdoor flights with GPS, magnetometer, and optical flow
- Mixed sensor configurations with flexible sensor enablement

**Data Export Formats:**
- Combined ROS bag files with synchronized timestamps
- CSV exports for data analysis
- Comprehensive visualization charts
- Correlation analysis plots

## Setup Instructions

### Prerequisites

- Python 3.9 - 3.11
- ROS environment (for bag file handling)
- HEAR-CLI tool

### Installation

1. Install PDM (Python dependency manager) using HEAR-CLI:

```bash
hear-cli local_machine run_program --p pdm_install
```

2. Clone the repository:

```bash
git clone https://github.com/your-organization/leaf-diag.git
cd leaf-diag
```

3. Install dependencies using PDM:

```bash
pdm install
```

## Usage

### Basic Workflow

1. **Configure Your Analysis**: Define log processing parameters
2. **Initialize Exporter**: Choose between indoor/outdoor analysis modes
3. **Extract and Synchronize**: Process data with automatic time alignment
4. **Export Results**: Generate synchronized outputs and visualizations

### Configuration Parameters

Each log analysis requires a configuration dictionary with the following parameters:

- `data_dir`: Directory containing input log files
- `output_dir`: Directory for analysis results and outputs
- `bag_path`: ROS bag filename (optional, can be `None`)
- `ulg_path`: PX4 ULog filename (required)
- `single_instance`: Boolean flag for single vs. multi-instance processing
- `sensor_config`: Dictionary specifying available sensors (for outdoor flights)

### Exporter Classes

**UlogExporterOutdoor**: For outdoor flights with GPS and optional optical flow
- Supports GPS position and velocity
- Handles GPS accuracy metrics and innovation ratios
- Processes magnetometer data for heading estimation
- Configurable sensor enablement

**UlogExporterIndoor**: For indoor flights using optical flow and distance sensors
- Optimized for non-GPS environments
- Focuses on optical flow velocity estimation
- Processes distance sensor data for altitude

### Example Usage

**Complete Analysis Example:**

```python
import os
from leaf_diag.ulog_export import UlogExporterOutdoor

# Configuration for outdoor flight with GPS
log_config = {
    "data_dir": "calibration_tests/CUAV_C-RTK2HP/Log2",
    "output_dir": "calibration_tests/CUAV_C-RTK2HP/output_Log2", 
    "ulg_path": "log_2_2025-6-15-14-30-24.ulg",
    "bag_path": "first_half.bag",  # Optional: set to None if not available
    "single_instance": True,
    "sensor_config": {
        "gps": True,
        "optical_flow": True,
    }
}

# Construct full paths
data_dir = log_config["data_dir"]
bag_path = os.path.join(data_dir, log_config["bag_path"]) if log_config["bag_path"] else None
ulg_path = os.path.join(data_dir, log_config["ulg_path"])

# Initialize exporter
exporter = UlogExporterOutdoor(
    rosbag_path=bag_path,
    ulog_path=ulg_path, 
    output_dir=log_config["output_dir"],
    single_instance=log_config["single_instance"],
    sensor_config=log_config["sensor_config"]
)

# Extract and synchronize data (creates correlation plots)
exporter.extract_all_data(plot_correlation=True)

# Generate combined output files
exporter.create_combined_ulog(
    output_dir=log_config["output_dir"], 
    write_csv=True,    # Export CSV files
    write_bag=True     # Create combined ROS bag
)

# Create visualization charts
exporter.create_charts("charts")
```

**Indoor Flight Example:**

```python
from leaf_diag.ulog_export import UlogExporterIndoor

# Indoor flight configuration (no GPS)
indoor_config = {
    "data_dir": "indoor_tests/flight_01",
    "output_dir": "indoor_tests/output_flight_01",
    "ulg_path": "indoor_log_01.ulg",
    "bag_path": None,  # No ROS bag available
    "single_instance": True
}

# Process indoor flight data
exporter = UlogExporterIndoor(
    rosbag_path=None,
    ulog_path=os.path.join(indoor_config["data_dir"], indoor_config["ulg_path"]),
    output_dir=indoor_config["output_dir"],
    single_instance=indoor_config["single_instance"]
)

exporter.extract_all_data(plot_correlation=False)  # No ROS bag to correlate
exporter.create_combined_ulog(indoor_config["output_dir"])
```

**Sensor Configuration Options:**

```python
# Full sensor configuration for outdoor flights
sensor_config = {
    "gps": True,           # Enable GPS position/velocity processing
    "optical_flow": True,  # Enable optical flow velocity estimation
}

# GPS-only configuration
sensor_config = {
    "gps": True,
    "optical_flow": False,
}

# Minimal configuration (ULog data only)
sensor_config = {
    "gps": False,
    "optical_flow": False,
}
```
### Key Methods

**extract_all_data(plot_correlation=False)**
- Loads and processes both ULog and ROS bag data
- Performs automatic time synchronization using correlation analysis
- Applies coordinate frame transformations
- Generates correlation plots if `plot_correlation=True`

**create_combined_ulog(output_dir, write_csv=True, write_bag=True)**
- Creates synchronized combined output files
- Returns bytes of the combined ROS bag for programmatic use
- Optionally writes CSV files and ROS bag to disk

**create_charts(output_dir="charts")**
- Generates comprehensive visualization plots for all processed signals
- Creates separate charts for each data type and sensor

## Advanced Features

### Time Synchronization Algorithm

`leaf-diag` uses an advanced correlation-based synchronization algorithm that:

- **Handles Negative Offsets**: Can synchronize signals where one starts before the other
- **NaN-Aware Processing**: Robust handling of missing data points in correlation calculations
- **Multi-dimensional Correlation**: Supports correlation of vector signals (position, velocity, etc.)
- **Overlap Analysis**: Evaluates signal overlap quality and filters correlations by minimum overlap thresholds
- **Automatic Signal Type Detection**: Determines which signal is shorter/longer for optimal alignment

### Coordinate Frame Transformations

The tool automatically handles coordinate frame conversions:

- **PX4 to DroneLeaf**: Transforms from NED (North-East-Down) to DroneLeaf coordinate system
- **GPS to Local**: Converts GPS coordinates to local position with configurable calibration offsets
- **Quaternion to Euler**: Automatic conversion of attitude quaternions to roll/pitch/yaw angles
- **Optical Flow Integration**: Combines optical flow with distance sensors for velocity estimation

### Multi-Instance Data Handling

For sensors with multiple instances (e.g., multiple accelerometers):

- **Automatic Detection**: Scans ULog files to detect number of sensor instances
- **Independent Processing**: Each instance is processed and synchronized separately
- **Configurable Output**: Results can be exported per-instance or aggregated

## Output Files and Structure

The analysis generates a comprehensive set of outputs in your specified `output_dir`:

### 1. Combined ROS Bag File
- **File**: `combined_data.bag` (or your specified filename)
- **Content**: Time-synchronized data from both ULog and ROS bag sources
- **Topics**: Organized under `/px4/` and `/ros/` namespaces for easy identification
- **Format**: Standard ROS bag format compatible with analysis tools

### 2. CSV Data Exports
- **px4_position.csv**: Local position data (x, y, z coordinates)
- **px4_velocity.csv**: Velocity vectors  
- **px4_orientation.csv**: Euler angles (roll, pitch, yaw)
- **px4_acceleration.csv**: Acceleration measurements
- **ros_*.csv**: Corresponding ROS data (if available)
- **Multi-instance files**: Separate CSV files for each sensor instance

### 3. Visualization Charts
- **position_comparison.png**: Position trajectories comparison
- **orientation_comparison.png**: Attitude angle plots
- **Signal plots**: Individual charts for each processed signal type
- **Multi-dimensional plots**: Separate subplots for x, y, z components

### 4. Correlation Analysis
- **[signal]_correlation.png**: Cross-correlation plots showing time offset analysis
- **[signal]_overlap.png**: Signal overlap analysis
- **[signal]_signals.png**: Time-aligned signal comparison plots

### 5. Metadata and Configuration
- **metadata.json**: Analysis metadata including timestamps and version info
- **Processing logs**: Detailed logs of the synchronization process

### Directory Structure Example
```
output_directory/
├── combined_data.bag              # Main synchronized output
├── csv/                          # CSV exports
│   ├── px4_position.csv
│   ├── px4_orientation.csv
│   ├── ros_position.csv
│   └── ...
├── charts/                       # Visualization plots  
│   ├── position_comparison.png
│   ├── orientation_comparison.png
│   └── ...
├── acceleration_correlation.png   # Correlation analysis
├── acceleration_overlap.png       # Overlap analysis
├── acceleration_signals.png       # Signal alignment
└── metadata.json                 # Analysis metadata
```

## Running Analysis

### Command Line Execution

Run the analysis using PDM:

```bash
# Run with main.py configuration
pdm run python main.py

# Run with custom script
pdm run python your_analysis_script.py
```

### Batch Processing

For processing multiple logs, see the examples in `main_adv.py` which demonstrates batch processing of multiple flight logs with different configurations.

### Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pdm run pytest

# Run specific test modules
pdm run pytest tests/test_signal.py
pdm run pytest tests/test_sync.py
```

> [!NOTE]  
> The `rosbag_path` parameter is optional and can be set to `None` if no ROS bag is available. The tool will still process ULog data and generate outputs.

> [!IMPORTANT]  
> Use `UlogExporterIndoor` for indoor flights and `UlogExporterOutdoor` for outdoor flights. The classes have different sensor processing capabilities optimized for their respective environments.

## Visualization and Analysis

### PlotJuggler Integration

View the combined bag files with PlotJuggler for interactive analysis:

```bash
./scripts/launch_plotjuggler.sh output_directory
```

### Data Analysis Tips

1. **Correlation Quality**: Check correlation plots to verify synchronization quality
2. **Signal Overlap**: Ensure sufficient overlap between signals for reliable correlation
3. **Coordinate Frames**: Be aware that position data is automatically transformed to DroneLeaf coordinates
4. **Multi-Instance Data**: Use instance-specific topics when analyzing sensor arrays

## Troubleshooting

### Common Issues

**Low Correlation Values**
- Check that both log files cover overlapping time periods
- Verify that the signals being correlated are actually related (e.g., same sensor type)
- Consider adjusting correlation parameters if needed

**Missing Data**
- Ensure ULog file contains the expected message types
- Check that ROS bag topics match expected naming conventions
- Verify file paths and permissions

**Synchronization Problems**
- Review correlation plots to diagnose sync issues
- Check for sufficient signal overlap in the overlap analysis plots
- Consider if negative time offsets are expected for your data

### Performance Considerations

- Large log files may require significant processing time for correlation analysis
- Consider using `single_instance=True` for faster processing when appropriate
- Correlation plots generation can be disabled for faster batch processing

## Developer Guidelines

### Extending Functionality

The modular design allows easy extension for new sensor types or data formats:

1. **New Signal Types**: Inherit from `UlogSignal` or `RosSignal` base classes
2. **Custom Transformations**: Add coordinate frame transformations in `data_transform.py`  
3. **Additional Exporters**: Create specialized exporters for new flight types

### ULog Topic Reference

For a comprehensive list of supported ULog topics and message structures, see [ulog_directory.json](ulog_directory.json).

### Code Structure

- `data_loader.py`: Signal extraction and base classes
- `data_sync.py`: Time synchronization algorithms  
- `data_transform.py`: Coordinate frame transformations
- `ulog_export.py`: Main export and processing classes
- `ros_utils.py`: ROS bag handling utilities