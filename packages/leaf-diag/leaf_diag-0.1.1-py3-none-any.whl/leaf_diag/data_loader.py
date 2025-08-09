import time
import px4tools
from .ros_utils import MemoryBagReader
import pandas as pd

import numpy as np
from pyparsing import col

from .data_transform import quat_to_euler, px4_rpy_to_droneleaf_rpy
from contextlib import contextmanager

from typing import Tuple, Dict, Tuple, List, Generator
from .data_transform import compute_altitude_range, get_rotations_from_attitude
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from scipy.signal import detrend
from .ros_utils import NamedBytesIO
import io

from typing import Union


@contextmanager
def load_rosbag(file_path: Union[str, bytes]) -> Generator[MemoryBagReader, None, None]:
    """
    Context manager for loading ROS bag files.
    Args:
        file_path (str): Path to the ROS bag file.
    Yields:
        MemoryBagReader: An instance of MemoryBagReader for the ROS bag file.
    Example:
        >>> with load_rosbag('path/to/your.bag') as bag:
        >>>     # Process the bag data
    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If there is an error while reading the bag file.
    """
    if isinstance(file_path, str):
        # If file_path is a string, we assume it's a file path
        bag = MemoryBagReader(file_path)
    elif isinstance(file_path, bytes):
        # If file_path is bytes, we assume it's a byte stream
        # Create a BytesIO object to read from the byte stream

        byte_stream = NamedBytesIO(file_path)
        byte_stream.seek(0)  # 2) ensure at start

        bag = MemoryBagReader(byte_stream)
    else:
        raise TypeError("file_path must be str or bytes")
    try:
        yield bag
    except Exception as e:
        raise Exception(f"Error reading ROS bag file: {e}")
    finally:
        # MemoryBagReader does not provide a close method, so no action is needed here
        pass

@contextmanager
def load_ulg(file_path: Union[str, bytes]) -> Generator[Dict[str, pd.DataFrame], None, None]:
    """
    Context manager for loading ULog files.
    Args:
        file_path (str): Path to the ULog file.
    Yields:
        dict: A dictionary containing the ULog data.
    Example:
        >>> with load_ulg('path/to/your.ulg') as ulg:
        >>>     # Process the ULog data
    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If there is an error while reading the ULog file.
    """
    if isinstance(file_path, str):
        ulg = px4tools.ulog.read_ulog(file_path)
    elif isinstance(file_path, bytes):
        # If file_path is bytes, we assume it's a byte stream
        # Create a BytesIO object to read from the byte stream
        byte_stream = io.BytesIO(file_path)
        ulg = px4tools.ulog.read_ulog(byte_stream)
    try:
        yield ulg
    finally:
        # px4tools.ulog does not require an explicit close, so no action is needed
        pass

def extract_ros_motor_signal(bag: MemoryBagReader, topic_name: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extracts the ROS signal and its corresponding timestamps.
    Modify this function if your bag data structure is different.
    """
    # Example: assuming bag provides a dictionary with a 'time' key (absolute timestamps)
    # and the desired signal is at:
    # bag['arm_commander/io_cmds_to_px4/data/data'][0]
    # Extract the messages from the specific topic
    df_data = bag.message_by_topic_memory(topic_name)

    columns = []
    for motor_id in range(4):
        columns.append('data_%i' %(
            motor_id
        ))

    ros_signal = np.array(df_data[columns].values)
    ros_times = np.array(df_data['Time'].values)

    return ros_times, ros_signal

def extract_ulog_position_estimate_signal(ulog: dict, ulog_name: str, coordinate: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extracts the Ulog signal and its timestamps.
    Modify this function if your Ulog structure is different.
    """
    # Example: assuming ulog provides a dictionary with a 'time' key (relative timestamps)
    # and the desired signal is in 'actuator_motors'
    ulog_times = np.array(ulog[ulog_name]["timestamp"])
    ulog_signal = np.array(ulog[ulog_name][coordinate])

    # convert ulog times to seconds
    ulog_times = ulog_times / 1e6

    return ulog_times, ulog_signal

def extract_ros_position_estimate_signal(bag: MemoryBagReader, topic_name: str, coordinate: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extracts the ROS signal and its corresponding timestamps.
    Modify this function if your bag data structure is different.
    """
    # Example: assuming bag provides a dictionary with a 'time' key (absolute timestamps)
    # and the desired signal is at:
    # bag['arm_commander/io_cmds_to_px4/data/data'][0]
    # Extract the messages from the specific topic
    df_data = bag.message_by_topic_memory(topic_name)

    ros_signal = np.array(df_data[coordinate].values)
    ros_times = np.array(df_data['Time'].values)

    return ros_times, ros_signal

def extract_ulog_signal(ulog: dict, ulog_name: str) -> np.ndarray:
    """
    Extracts the Ulog signal and its timestamps.
    Modify this function if your Ulog structure is different.
    """
    # Example: assuming ulog provides a dictionary with a 'time' key (relative timestamps)
    # and the desired signal is in 'actuator_motors'

    return ulog[ulog_name]

def extract_ros_signal(bag: MemoryBagReader, topic_name: str) -> pd.DataFrame:
    """
    Extracts the ROS signal and its corresponding timestamps.
    Modify this function if your bag data structure is different.
    """
    # Example: assuming bag provides a dictionary with a 'time' key (absolute timestamps)
    # and the desired signal is at:
    # bag['arm_commander/io_cmds_to_px4/data/data'][0]
    # Extract the messages from the specific topic
    df_data = bag.message_by_topic_memory(topic_name)

    return df_data


class BaseSignal:
    def __init__(self, data, timestamps, dimension=None, data_keys=None):
        self.data = np.array(data)
        self.timestamps = np.array(timestamps)
        self.dimension = dimension
        self.data_keys = data_keys
        self.sampling_freq = self._compute_sampling_freq()

        self.reset_time()

    def _compute_sampling_freq(self):
        if len(self.timestamps) < 2:
            return 0
        diffs = np.diff(self.timestamps)
        return 1.0 / np.mean(diffs) if np.mean(diffs) != 0 else 0

    def set_start_time(self, start_time):
        self.start_time = start_time
        self.timestamps = self.timestamps - self.start_time

    def reset_time(self):
        self.start_time = self.timestamps[0]
        self.timestamps = self.timestamps - self.start_time

    def get_signal_slice(self, idx=None):
        return self.data if idx is None else self.data[:, idx]

    def plot(self, ax:plt.Axes=None, idx:int=None, title:str = None, label: str = None, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot the signal data.
        Args:
            ax: Matplotlib Axes object to plot on. If None, a new figure and axes are created.
            idx: Index of the signal to plot. If None, all signals are plotted.
            **kwargs: Additional keyword arguments for the plot.
        Returns:
            fig: Matplotlib Figure object.
            ax: Matplotlib Axes object.
        """
        if idx is None and self.dimension > 1:
            # Create subplots if we're plotting multiple dimensions
            fig, axes = plt.subplots(self.dimension, 1, figsize=(10, 2*self.dimension), sharex=True)
            colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'olive', 'cyan']
            for i in range(self.dimension):
                color_idx = i % len(colors)  # Cycle through colors if more dimensions than colors
                axes[i].plot(self.timestamps, self.data[:, i], color=colors[color_idx], **kwargs)
                if self.data_keys:
                    axes[i].set_ylabel(self.data_keys[i])
                if i == 0 and title:
                    axes[i].set_title(title, pad=10)  # Add vertical padding to title
            axes[-1].set_xlabel('Time (s)')
            fig.tight_layout()
            return fig, axes
        else:
            # Single plot for one dimension or specific index
            if ax is None:
                fig, ax = plt.subplots(figsize=(10, 5))
            else:
                fig = ax.figure
            
            if idx is None:
                for i in range(self.dimension):
                    if label is None:
                        label = self.data_keys[i] if self.data_keys else f"Signal {i}"
                    ax.plot(self.timestamps, self.data[:, i], label=label, **kwargs)
                ax.legend()
            else:
                if label is None:
                    label = self.data_keys[idx] if self.data_keys else f"Signal {idx}"
                ax.plot(self.timestamps, self.data[:, idx], label=label, **kwargs)
                ax.legend()
            
            if title:
                ax.set_title(title)
                ax.set_xlabel('Time (s)')
            return fig, ax

class RosSignal(BaseSignal):
    def __init__(self, ros_bag, topic, dimension=None, data_keys=None):
        # Example extraction from a ROS bag
        
        topic_data = extract_ros_signal(ros_bag, topic).to_numpy()
        timestamps = topic_data[:, 0]
        data = topic_data[:, 1:]

        self.start_time = timestamps[0]
        self.data = data
        self.dimension = data.shape[1]
        self.topic = topic

        super().__init__(data, timestamps, dimension, data_keys)


class UlogSignal(BaseSignal):
    def __init__(self, ulog: Dict[str,pd.DataFrame], msg_key: str, data_keys: List[str]=None, dimension: int=None):
        # Example extraction from a ULog
        df = ulog[msg_key]
        timestamps = df["timestamp"].to_numpy() / 1e6
        self.start_time = timestamps[0]
        self.msg_key = msg_key

        if data_keys is None:
            data = df.drop(columns=["timestamp"]).to_numpy()
        else:
            data = df[data_keys].to_numpy()

        if data.ndim == 1:
            data = data[:, None]

        if dimension is None:
            dimension = data.shape[1]
        super().__init__(data, timestamps, dimension, data_keys)


class MotorCommandSignal(RosSignal):
    def __init__(self, ros_bag: MemoryBagReader, topic: str):
        """
        Extracts motor command signals from a ROS bag.
        Args:
            ros_bag: The ROS bag reader object.
            topic: The topic name to extract motor commands from.
        """
        # Extract one motor channel
        times, values = extract_ros_motor_signal(ros_bag, topic)

        self.dimension = values.shape[1]
        self.data = values
        self.timestamps = times
        self.sampling_freq = self._compute_sampling_freq()

        self.data_keys = [f"motor_{i}" for i in range(self.dimension)]

        self.reset_time()


class UlogMotorCommandSignal(UlogSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=[f"f_control_{i}_" for i in range(4)], dimension=4)


class OrientationSignal(RosSignal):
    def __init__(self, ros_bag, topic):
        data_keys = ["roll", "pitch", "yaw"]
        super().__init__(ros_bag, topic, dimension=3, data_keys=data_keys)


class UlogOrientationSignal(UlogSignal):
    def __init__(self, ulog, msg_key):
        df = ulog[msg_key]
        # Assume quaternion to Euler has been done externally
        times = df["timestamp"].to_numpy() / 1e6
        euler = quat_to_euler(df[["f_q_1_", "f_q_2_", "f_q_3_", "f_q_0_"]].to_numpy())
        euler = px4_rpy_to_droneleaf_rpy(euler)

        self.dimension = euler.shape[1]
        self.data = euler
        self.timestamps = times
        self.sampling_freq = self._compute_sampling_freq()

        self.data_keys = ["roll", "pitch", "yaw"]

        self.reset_time()


class UlogAngularSignal(UlogSignal):

    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_xyz_0_", "f_xyz_1_", "f_xyz_2_"], dimension=3)
        self.transform_to_droneleaf()

    def transform_to_droneleaf(self):
        x_px4 = self.data[:, 0].copy()
        y_px4 = self.data[:, 1].copy()
        z_px4 = self.data[:, 2].copy()

        self.data[:, 0] = x_px4
        self.data[:, 1] = -y_px4
        self.data[:, 2] = -z_px4


class CartesianSignal(RosSignal):
    def __init__(self, ros_bag, topic):
        data_keys = ["x", "y", "z"]
        super().__init__(ros_bag, topic, dimension=3, data_keys=data_keys)


class UlogCartesianSignal(UlogSignal):

    def get_initial_coords(self):
        return self.data[0]

    def transform_to_droneleaf(self):
        x_px4 = self.data[:, 0].copy()
        y_px4 = self.data[:, 1].copy()
        z_px4 = self.data[:, 2].copy()

        self.data[:, 0] = y_px4
        self.data[:, 1] = x_px4
        self.data[:, 2] = -z_px4


class UlogPositionSignal(UlogCartesianSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_x", "f_y", "f_z"], dimension=3)
        self.transform_to_droneleaf()


class UlogVelocitySignal(UlogCartesianSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_vx", "f_vy", "f_vz"], dimension=3)
        self.transform_to_droneleaf()


class UlogAccelerationSignal(UlogCartesianSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_ax", "f_ay", "f_az"], dimension=3)
        self.transform_to_droneleaf()

class UlogRawAccelerationSignal(UlogCartesianSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_x", "f_y", "f_z"], dimension=3)
        self.transform_to_droneleaf()

    def transform_to_droneleaf(self):
        x_px4 = self.data[:, 0].copy()
        y_px4 = self.data[:, 1].copy()
        z_px4 = self.data[:, 2].copy()

        self.data[:, 0] = x_px4
        self.data[:, 1] = -y_px4
        self.data[:, 2] = -z_px4 - 9.81

class ULogGPSPositionSignal(UlogCartesianSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_lat", "f_lon", "f_alt"], dimension=3)
        self.initial_coords: Tuple[float, float, float] = None
        # Convert GPS coordinates to local x, y, z
        self._convert_gps_to_local()

    def _convert_gps_to_local(self):
        """Convert GPS coordinates to local x, y, z coordinates"""
        # Unpack initial coordinates
        
        # Extract GPS data
        lats = self.data[:, 0].copy()
        lons = self.data[:, 1].copy()
        alts = self.data[:, 2].copy()
        
        self.initial_coords = (lats[0], lons[0], alts[0])

        # Constants for conversion
        R_EARTH = 6378137.0  # Earth radius in meters
        
        # Convert lat/lon to meters (using equirectangular approximation)
        # This is a simple approximation valid for small distances
        x = R_EARTH * np.cos(np.radians(self.initial_coords[0])) * np.radians(lons - self.initial_coords[1])
        y = R_EARTH * np.radians(lats - self.initial_coords[0])
        z = alts - self.initial_coords[2]
        
        # Replace GPS data with local coordinates
        self.data[:, 0] = x
        self.data[:, 1] = y
        self.data[:, 2] = z
    
    def apply_calibration_offset(self, calibration_offset: Tuple[float, float, float]):
        """
        Apply calibration offsets to the x, y, z position data.
        
        Args:
            calibration_offset: A tuple of (x_offset, y_offset, z_offset) in meters
        """
        if len(calibration_offset) != 3:
            raise ValueError("Calibration offset must be a tuple of 3 values (x, y, z)")
            
        # Apply offsets to the data
        self.data[:, 0] += calibration_offset[0]  # x offset
        self.data[:, 1] += calibration_offset[1]  # y offset 
        self.data[:, 2] += calibration_offset[2]  # z offset

class UlogGPSVelocitySignal(UlogCartesianSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_vel_e_m_s", "f_vel_n_m_s", "f_vel_d_m_s"], dimension=3)
        self.transform_to_droneleaf()

    def transform_to_droneleaf(self):
        x_px4 = self.data[:, 0].copy()
        y_px4 = self.data[:, 1].copy()
        z_px4 = self.data[:, 2].copy()

        self.data[:, 0] = x_px4
        self.data[:, 1] = y_px4
        self.data[:, 2] = -z_px4

class UlogOFVelocity(UlogCartesianSignal):
    def __init__(self, ulog, of_msg_key, pos_msg_key, att_msg_key, distance_sensor_msg_key):
        """
        Calculate ground velocity from optical flow data.
        
        Args:
            ulog: ULog data dictionary
            of_msg_key: Key for optical flow message
            pos_msg_key: Key for vehicle position message (for altitude)
        """
        # Create derived optical flow velocity dataset
        of_velocity_df = self._calculate_flow_velocity(ulog, of_msg_key, pos_msg_key, att_msg_key, distance_sensor_msg_key)
        
        # Add to ulog dictionary under a new key
        msg_key = "optical_flow_velocity"
        ulog[msg_key] = of_velocity_df
        
        # Initialize using the parent class with our derived data
        super().__init__(ulog, msg_key, data_keys=["f_vx", "f_vy", "f_vz"], dimension=2)
        
        # Transform to DroneLeaf coordinate system
        self.transform_to_droneleaf()
    
    def transform_to_droneleaf(self):
        x_px4 = self.data[:, 0].copy()
        y_px4 = self.data[:, 1].copy()
        z_px4 = self.data[:, 2].copy()

        self.data[:, 0] = -y_px4
        self.data[:, 1] = x_px4
        self.data[:, 2] = -z_px4

    def _calculate_flow_velocity(self, ulog, of_msg_key, pos_msg_key, att_msg_key, distance_sensor_msg_key):
        """
        Calculate velocity from optical flow, attitude, and altitude data,
        replicating the PX4 EKF sign flips and rotation compensation.
        Uses compute_altitude_range for accurate range measurement.
        """
        # -------------------------------------------------------------------
        # 1) Extract optical flow data
        #    Expect columns: 'timestamp', 'pixel_flow[0]', 'pixel_flow[1]',
        #                   'delta_angle[0]', 'delta_angle[1]', 'delta_angle[2]',
        #                   'integration_timespan_us', 'quality', ...
        #    The exact column names can differ in your logs:
        # -------------------------------------------------------------------
        of_df = ulog[of_msg_key].copy()

        # For example, rename to simpler columns:
        of_df.rename(columns={
            "f_pixel_flow_0_": "px_flow_x",
            "f_pixel_flow_1_": "px_flow_y",
            "f_delta_angle_0_": "dangle_x",
            "f_delta_angle_1_": "dangle_y",
            "f_delta_angle_2_": "dangle_z",
            "f_integration_timespan_us": "dt_us"
        }, inplace=True)

        # Make sure we have the needed columns
        needed_cols = ["timestamp", "px_flow_x", "px_flow_y", 
                       "dangle_x", "dangle_y", "dangle_z", "dt_us"]
        for c in needed_cols:
            if c not in of_df.columns:
                raise ValueError(f"Missing column '{c}' in optical flow dataset")

        # Convert timestamp to float seconds
        of_df["t"] = of_df["timestamp"] * 1e-6
        # Convert dt from microseconds to seconds
        of_df["dt"] = of_df["dt_us"] * 1e-6

        # -------------------------------------------------------------------
        # 2) Extract position and attitude data for altitude calculation
        # -------------------------------------------------------------------
        pos_df = ulog[pos_msg_key].copy()
        # Expect columns: 'timestamp', 'f_x', 'f_y', 'f_z', etc.
        pos_df.rename(columns={"f_x": "x_ned", "f_y": "y_ned", "f_z": "z_ned"}, inplace=True)
        pos_df["t"] = pos_df["timestamp"] * 1e-6

        att_df = ulog[att_msg_key].copy()
        # Typically has columns: 'timestamp', 'q[0]', 'q[1]', 'q[2]', 'q[3]'
        att_df.rename(columns={
            "f_q_0_": "qw",
            "f_q_1_": "qx",
            "f_q_2_": "qy",
            "f_q_3_": "qz"
        }, inplace=True)
        att_df["t"] = att_df["timestamp"] * 1e-6

        # We'll do an asof merge to get attitude per flow sample
        # Sort first:
        of_df.sort_values("t", inplace=True)
        att_df.sort_values("t", inplace=True)
        pos_df.sort_values("t", inplace=True)

        # Merge attitude data with optical flow data
        merged = pd.merge_asof(of_df, att_df[["t","qw","qx","qy","qz"]], 
                               on="t", direction="nearest")
        
        # -------------------------------------------------------------------
        # 3) Calculate accurate altitude range using compute_altitude_range
        # -------------------------------------------------------------------
        
        n = len(merged)
        # Create rotation matrices for each sample
        R_to_earth = np.zeros((3, 3, n))
        state_pos = np.zeros((3, n))
        
        # Interpolate position at the OF timestamps
        of_times = merged["t"].to_numpy()
        pos_times = pos_df["t"].to_numpy()
        
        # Extract NED positions
        state_pos[0, :] = np.interp(of_times, pos_times, pos_df["x_ned"].to_numpy())
        state_pos[1, :] = np.interp(of_times, pos_times, pos_df["y_ned"].to_numpy())
        state_pos[2, :] = np.interp(of_times, pos_times, pos_df["z_ned"].to_numpy())
        
        # Calculate rotation matrices for each timestamp
        for i in range(n):
            _, rot_body_to_ned = get_rotations_from_attitude(
                merged["qw"].iloc[i],
                merged["qx"].iloc[i],
                merged["qy"].iloc[i],
                merged["qz"].iloc[i]
            )
            R_to_earth[:, :, i] = rot_body_to_ned.as_matrix()
        
        # # Compute accurate altitude range
        # range_to_ground = compute_altitude_range(
        #     R_to_earth=R_to_earth,
        #     state_pos=state_pos
        # )

        distance_df = ulog[distance_sensor_msg_key].copy()
        distance_df["t"] = distance_df["timestamp"] * 1e-6
        distance_df.rename(columns={"f_current_distance": "sensor_range"}, inplace=True)
        distance_df.sort_values("t", inplace=True)

        merged = pd.merge_asof(
            merged.sort_values("t"),
            distance_df[["t", "sensor_range"]].sort_values("t"),
            on="t",
            direction="nearest"
        )

        merged.rename(columns={"sensor_range": "range"}, inplace=True)

        # -------------------------------------------------------------------
        # 4) Replicate the sign flipping & subtract gyro
        # -------------------------------------------------------------------
        # flow_xy_rad  = -pixel_flow[0..1]
        merged["flow_x_rad"] = -merged["px_flow_x"]
        merged["flow_y_rad"] = -merged["px_flow_y"]

        # gyro_xyz = -delta_angle[0..2]
        merged["gyro_x"] = -merged["dangle_x"]
        merged["gyro_y"] = -merged["dangle_y"]
        # merged["gyro_z"] = -merged["dangle_z"]  # not used for XY flow

        # compensated_flow_xy = flow_xy_rad - gyro_xyz.xy()
        merged["compensated_flow_x"] = merged["flow_x_rad"] - merged["gyro_x"]
        merged["compensated_flow_y"] = merged["flow_y_rad"] - merged["gyro_y"]

        # rad/s
        merged["of_rate_x"] = merged["compensated_flow_x"] / merged["dt"]
        merged["of_rate_y"] = merged["compensated_flow_y"] / merged["dt"]

        # -------------------------------------------------------------------
        # 5) Convert to velocity in BODY frame using accurate range
        #    v_bx = -of_rate_y * range
        #    v_by =  of_rate_x * range
        #    v_bz =  0
        # -------------------------------------------------------------------
        merged["v_bx"] = -merged["of_rate_y"] * merged["range"]
        merged["v_by"] = -merged["of_rate_x"] * merged["range"]
        merged["v_bz"] =  0.0

        # -------------------------------------------------------------------
        # 6) Rotate body->NED for final velocity
        # -------------------------------------------------------------------
        vx_ned = []
        vy_ned = []
        vz_ned = []

        
        for i, row in merged.iterrows():
            # Build the Rotation from NED->body
            rot_ned_to_body = R.from_quat([row["qx"], row["qy"], row["qz"], row["qw"]])
            rot_body_to_ned = rot_ned_to_body.inv()

            v_body = np.array([row["v_bx"], row["v_by"], row["v_bz"]])
            v_ned  = rot_body_to_ned.apply(v_body)

            vx_ned.append(v_ned[0])
            vy_ned.append(v_ned[1])
            vz_ned.append(v_ned[2])

        merged["f_vx"] = vx_ned
        merged["f_vy"] = vy_ned
        merged["f_vz"] = vz_ned

        # -------------------------------------------------------------------
        # 7) Create and return the final DF
        # -------------------------------------------------------------------
        result_df = pd.DataFrame()
        # Use original 'timestamp' in microseconds
        result_df["timestamp"] = merged["timestamp"].astype(int)
        result_df["f_vx"] = merged["f_vx"]
        result_df["f_vy"] = merged["f_vy"]
        result_df["f_vz"] = merged["f_vz"]

        return result_df
    
class UlogHeading(UlogSignal):
    def __init__(self, ulog, mag_sensor_msg_key, att_msg_key):
        """
        Calculate ground velocity from optical flow data.
        
        Args:
            ulog: ULog data dictionary
            of_msg_key: Key for optical flow message
            pos_msg_key: Key for vehicle position message (for altitude)
        """
        # Create derived optical flow velocity dataset
        heading_df = self._calculate_heading(ulog, mag_sensor_msg_key, att_msg_key)
        
        # Add to ulog dictionary under a new key
        msg_key = "calculated_heading"
        ulog[msg_key] = heading_df
        
        # Initialize using the parent class with our derived data
        super().__init__(ulog, msg_key, data_keys=["f_heading",])

    def _calculate_heading(self, ulog, mag_sensor_msg_key, att_msg_key):
        """
        Calculate velocity from magnetometer flow, attitude, and altitude data,
        replicating the PX4 EKF sign flips and rotation compensation.
        Uses compute_altitude_range for accurate range measurement.
        """

        # -------------------------------------------------------------------
        # 1) Extract magnetometer and attitude data for heading calculation
        # -------------------------------------------------------------------
        mag_df = ulog[mag_sensor_msg_key].copy()
        # Expect columns: 'timestamp', 'f_x', 'f_y', 'f_z', etc.
        mag_df.rename(columns={"f_x": "f_x", "f_y": "f_y", "f_z": "f_z"}, inplace=True)
        mag_df["t"] = mag_df["timestamp"] * 1e-6

        att_df = ulog[att_msg_key].copy()
        # Typically has columns: 'timestamp', 'q[0]', 'q[1]', 'q[2]', 'q[3]'
        att_df.rename(columns={
            "f_q_0_": "qw",
            "f_q_1_": "qx",
            "f_q_2_": "qy",
            "f_q_3_": "qz"
        }, inplace=True)
        att_df["t"] = att_df["timestamp"] * 1e-6

        # We'll do an asof merge to get attitude per flow sample
        # Sort first:
        att_df.sort_values("t", inplace=True)
        mag_df.sort_values("t", inplace=True)

        # Merge attitude data with optical flow data
        merged = pd.merge_asof(mag_df, att_df[["t","qw","qx","qy","qz"]], 
                               on="t", direction="nearest")
        
        # -------------------------------------------------------------------
        # 3) Calculate roll pitch and yaw from quaternion in dataframe
        # -------------------------------------------------------------------
        
        # Calculate roll, pitch, yaw from quaternion
        euler = quat_to_euler(
            merged[["qw", "qx", "qy", "qz"]].to_numpy()
        )

        merged["roll"] = euler[:, 0] # roll in radians
        merged["pitch"] = euler[:, 1] # pitch in radians
        merged["yaw"] = euler[:, 2] # yaw in radians
        
        # -------------------------------------------------------------------
        # 4) Calculate magnetometer heading (yaw) with inclination compensation
        # -------------------------------------------------------------------

        # Extract magnetometer data
        mag_x = merged["f_x"].to_numpy()
        mag_y = merged["f_y"].to_numpy()
        mag_z = merged["f_z"].to_numpy()

        # Interpolate roll and pitch to magnetometer timestamps
        mag_timestamps = merged["t"].to_numpy()
        att_timestamps = merged["t"].to_numpy()

        roll_raw = merged["roll"].to_numpy()
        pitch_raw = merged["pitch"].to_numpy()

        # Use numpy.interp for interpolation
        roll_interp = np.interp(mag_timestamps, att_timestamps, roll_raw)
        pitch_interp = np.interp(mag_timestamps, att_timestamps, pitch_raw)

        roll = np.radians(roll_interp)  # roll in radians
        pitch = np.radians(pitch_interp)  # pitch in radians

        # Compensate for inclination
        Xh = mag_x * np.cos(pitch) + mag_z * np.sin(pitch)
        Yh = mag_x * np.sin(roll) * np.sin(pitch)
        Yh += mag_y * np.cos(roll) - mag_z * np.sin(roll) * np.cos(pitch)

        heading_rad = np.arctan2(Yh, Xh)
        heading_deg = np.degrees(heading_rad)
        merged["f_heading"] = heading_deg

        # -------------------------------------------------------------------
        # 5) Create and return the final DF
        # -------------------------------------------------------------------
        result_df = pd.DataFrame()
        # Use original 'timestamp' in microseconds
        result_df["timestamp"] = merged["timestamp"].astype(int)
        result_df["f_heading"] = merged["f_heading"]

        return result_df

class UlogEstimatorOFVelocity(UlogSignal):
    def __init__(self, ulog, msg_key):
        super().__init__(ulog, msg_key, data_keys=["f_vel_ne_0_", "f_vel_ne_1_"], dimension=2)
        self.transform_to_droneleaf()
    
    def transform_to_droneleaf(self):
        x_px4 = self.data[:, 0].copy()
        y_px4 = self.data[:, 1].copy()

        self.data[:, 0] = y_px4
        self.data[:, 1] = x_px4

class UlogGyroHeading(UlogSignal):
    def __init__(self, ulog, gyro_msg_key, attitude_msg_key):
        """
        Initialize the UlogGyroHeading class.

        Args:
            ulog: ULog data dictionary.
            gyro_msg_key: Key for the sensor_gyro message.
            attitude_msg_key: Key for the vehicle_attitude message.
        """
        # Calculate integrated angular displacement
        integrated_angles_df = self._calculate_integrated_angles(ulog, gyro_msg_key, attitude_msg_key)

        # Add to ulog dictionary under a new key
        msg_key = "sensor_gyro_integrated"
        ulog[msg_key] = integrated_angles_df

        # Initialize using the parent class with our derived data
        super().__init__(ulog, msg_key, data_keys=["angle_x", "angle_y", "angle_z"], dimension=3)

    def _calculate_integrated_angles(self, ulog, gyro_msg_key, attitude_msg_key):
        """
        Calculate integrated angular displacement from angular velocity data.

        Args:
            ulog: ULog data dictionary.
            gyro_msg_key: Key for the sensor_gyro message.
            attitude_msg_key: Key for the vehicle_attitude message.

        Returns:
            DataFrame with columns for timestamp, angle_x, angle_y, and angle_z.
        """
        # Extract angular velocity data
        gyro_df = ulog[gyro_msg_key]
        timestamps = gyro_df["timestamp"].to_numpy() / 1e6  # Convert to seconds
        angular_velocity = gyro_df[["f_x", "f_y", "f_z"]].to_numpy()

        # --- Bias Correction ---
        # Estimate bias from stationary data (e.g., first 100 samples)
        bias = np.mean(angular_velocity[:100], axis=0)
        angular_velocity -= bias

        # --- Detrending ---
        angular_velocity = detrend(angular_velocity, axis=0)

        # Compute time deltas
        time_deltas = np.diff(timestamps, prepend=timestamps[0])

        # Integrate angular velocity to get angular displacement
        integrated_angles = np.cumsum(angular_velocity * time_deltas[:, None], axis=0)

        # Extract initial attitude from vehicle_attitude topic
        attitude_df = ulog[attitude_msg_key]
        initial_quaternion = attitude_df.iloc[0][["f_q_1_", "f_q_2_", "f_q_3_", "f_q_0_"]].to_numpy()
        initial_euler = quat_to_euler(initial_quaternion[None, :])[0]  # Convert to roll, pitch, yaw

        # Add initial angles as constants of integration
        integrated_angles[:, 0] += initial_euler[0]  # Roll
        integrated_angles[:, 1] += initial_euler[1]  # Pitch
        integrated_angles[:, 2] += initial_euler[2]  # Yaw

        # Create a DataFrame for the integrated angles
        integrated_angles_df = pd.DataFrame({
            "timestamp": timestamps * 1e6,  
            "angle_x": integrated_angles[:, 0],
            "angle_y": integrated_angles[:, 1],
            "angle_z": integrated_angles[:, 2]
        })

        return integrated_angles_df