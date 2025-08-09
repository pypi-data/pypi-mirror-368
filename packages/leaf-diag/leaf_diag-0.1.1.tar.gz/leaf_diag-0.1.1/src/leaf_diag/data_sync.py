import os
from matplotlib import lines
import numpy as np

import matplotlib.pyplot as plt
from pyparsing import line

from .data_loader import (
    load_rosbag,
    load_ulg,
    RosSignal,
    MotorCommandSignal,
    UlogMotorCommandSignal,
    CartesianSignal,
    UlogSignal,
    OrientationSignal,
    UlogOrientationSignal,
    UlogAccelerationSignal,
    UlogCartesianSignal

)

from typing import Union, List
from scipy.interpolate import interp1d
from tqdm import tqdm

def _get_signal_nan_indices(signal):
    if signal.ndim > 1:
        return ~np.isnan(signal).any(axis=1)
    else:
        return ~np.isnan(signal)

def resample_signal(orig_times, signal, new_times):
    """
    Resamples the given signal onto the new time base using linear interpolation.
    Values outside the original time range will be nan.

    signal can be a 1D array or a 2D array (time x channels).
    """
    
    # loop over channels if signal is 2D
    if signal.ndim > 1:
        resampled_signal = np.zeros((len(new_times), signal.shape[1]))
        for i in range(signal.shape[1]):
            interp_func = interp1d(orig_times, signal[:,i], kind='linear', bounds_error=False, fill_value=np.nan)
            resampled_signal[:,i] = interp_func(new_times)
        return resampled_signal
    else:
        interp_func = interp1d(orig_times, signal, kind='linear', bounds_error=False, fill_value=np.nan)
        return interp_func(new_times)

def get_common_time_base(ros_times, ulog_times):
    """
    Compute the common time base for ROS and Ulog signals.
    """
    fs_ros = 1 / np.mean(np.diff(ros_times))
    fs_ulog = 1 / np.mean(np.diff(ulog_times))
    fs = max(fs_ros, fs_ulog)
    t_min, t_max = min(ros_times[0], ulog_times[0]), max(ros_times[-1], ulog_times[-1])
    common_times = np.arange(t_min, t_max, 1 / fs)

    return common_times, fs


class SignalSynchronizer:
    def __init__(self, bag_path: Union[str, bytes], ulg_path: Union[str, bytes]):
        self.bag_path = bag_path
        self.ulg_path = ulg_path
        self.common_times = None
        self.best_offset = None
        self.best_overlap = None
        self.overlaps = None
        self.correlations = None
        self.fs = None

    def _compute_best_offset(self, ros_times, ulog_times, ros_signal, ulog_signal):

        # Common time base
        self.common_times, self.fs = get_common_time_base(ros_times, ulog_times)

        # Resample
        self.ros_signal_resampled = resample_signal(ros_times, ros_signal, self.common_times)
        self.ulog_signal_resampled = resample_signal(ulog_times, ulog_signal, self.common_times)

        # Correlation
        signals_dict = {
            'ROS': {
                "length": len(self.ros_signal_resampled[_get_signal_nan_indices(self.ros_signal_resampled)]),
                "signal": self.ros_signal_resampled
            },
            'Ulog': {
                "length": len(self.ulog_signal_resampled[_get_signal_nan_indices(self.ulog_signal_resampled)]),
                "signal": self.ulog_signal_resampled
            }
        }
        self.shorter_type = min(signals_dict, key=lambda x: signals_dict[x]['length'])
        self.longer_type = max(signals_dict, key=lambda x: signals_dict[x]['length'])

        self.correlations = []
        
        # Extend search range to include negative offsets
        max_positive_offset = signals_dict[self.longer_type]["length"] + signals_dict[self.shorter_type]["length"]
        max_negative_offset = signals_dict[self.shorter_type]["length"]
        
        # Search from -max_negative_offset to max_positive_offset
        offset_range = range(-max_negative_offset, max_positive_offset + 1)

        corr_signal_short_clean = signals_dict[self.shorter_type]["signal"][
            _get_signal_nan_indices(signals_dict[self.shorter_type]["signal"])
        ]
        corr_signal_long_clean = signals_dict[self.longer_type]["signal"][
            _get_signal_nan_indices(signals_dict[self.longer_type]["signal"])
        ]

        self.overlaps = []

        for offset in tqdm(offset_range, desc="Calculating correlation"):
            if offset >= 0:
                # Positive offset: shorter signal starts after longer signal
                start = min(offset, len(corr_signal_long_clean))
                end = min(offset + len(corr_signal_short_clean), len(corr_signal_long_clean))

                corr_signal_long = corr_signal_long_clean[start : end]
                corr_signal_short = corr_signal_short_clean[:len(corr_signal_long)]

                self.overlaps.append((end - start) / len(corr_signal_short_clean))
            else:
                # Negative offset: shorter signal starts before longer signal
                abs_offset = abs(offset)
                start = abs_offset
                end = len(corr_signal_short_clean)

                corr_signal_short = corr_signal_short_clean[start : end]
                corr_signal_long = corr_signal_long_clean[:len(corr_signal_short)]

                self.overlaps.append((end - start) / len(corr_signal_short_clean))

            # Skip if either signal is empty
            if len(corr_signal_short) == 0 or len(corr_signal_long) == 0:
                self.correlations.append(np.nan)
                continue

            # Check if signals are multi-dimensional
            if corr_signal_short.ndim > 1 and corr_signal_long.ndim > 1:
                # Compute correlations dimension by dimension and average
                corrs = []
                for dim in range(corr_signal_short.shape[1]):
                    # Get data for this dimension
                    short_dim = corr_signal_short[:, dim]
                    long_dim = corr_signal_long[:, dim]
                    
                    # Find valid (non-NaN) indices for both signals
                    valid_indices = ~(np.isnan(short_dim) | np.isnan(long_dim))
                    if np.sum(valid_indices) < 2:  # Need at least 2 points for correlation
                        corrs.append(np.nan)
                    else:
                        short_valid = short_dim[valid_indices]
                        long_valid = long_dim[valid_indices]
                        
                        # Check if signals have enough variance
                        if np.std(short_valid) == 0 or np.std(long_valid) == 0:
                            corrs.append(np.nan)
                        else:
                            dim_corr = np.corrcoef(short_valid, long_valid)
                            corrs.append(dim_corr[0, 1])
                
                # Only compute mean over valid correlations
                valid_corrs = [c for c in corrs if not np.isnan(c)]
                if valid_corrs:
                    self.correlations.append(np.mean(valid_corrs))
                else:
                    self.correlations.append(np.nan)
            else:
                # For 1D signals, handle NaNs
                valid_indices = ~(np.isnan(corr_signal_short) | np.isnan(corr_signal_long))

                if np.sum(valid_indices) < 2:  # Need at least 2 points for correlation
                    self.correlations.append(np.nan)
                else:
                    short_valid = corr_signal_short[valid_indices]
                    long_valid = corr_signal_long[valid_indices]
                    
                    # Check if signals have enough variance
                    if np.std(short_valid) == 0 or np.std(long_valid) == 0:
                        self.correlations.append(np.nan)
                    else:
                        corr = np.corrcoef(short_valid, long_valid)
                        self.correlations.append(corr[0, 1])

        # Filter correlations by overlap threshold
        valid_correlations = np.array(self.correlations)
        overlap_mask = np.array(self.overlaps) > 0.5
        valid_correlations[~overlap_mask] = np.nan
        
        best_idx = np.nanargmax(valid_correlations)

        # Convert index back to actual offset (accounting for negative range)
        self.best_offset = (offset_range[best_idx]) / self.fs
        self.best_overlap = self.overlaps[best_idx]

    def plot_correlation(self, filename=None):
        if self.correlations is None:
            print("No correlation data. Run compute_best_offset first.")
            return
        
        # Recreate the offset range to match what was used in compute_best_offset
        signals_dict = {
            'ROS': {
                "length": len(self.ros_signal_resampled[_get_signal_nan_indices(self.ros_signal_resampled)]),
            },
            'Ulog': {
                "length": len(self.ulog_signal_resampled[_get_signal_nan_indices(self.ulog_signal_resampled)]),
            }
        }
        shorter_type = min(signals_dict, key=lambda x: signals_dict[x]['length'])
        longer_type = max(signals_dict, key=lambda x: signals_dict[x]['length'])
        
        max_positive_offset = signals_dict[longer_type]["length"] + signals_dict[shorter_type]["length"]
        max_negative_offset = signals_dict[shorter_type]["length"]
        offset_range = range(-max_negative_offset, max_positive_offset + 1)
        
        lags = np.array(offset_range) / self.fs
        plt.figure()
        plt.plot(lags, self.correlations)
        plt.axvline(self.best_offset, color='r', linestyle='--',
                    label=f'Best offset: {self.best_offset:.3f}s')
        plt.xlabel("Lag (seconds)")
        plt.ylabel("Cross correlation")
        plt.title("Cross correlation")
        plt.legend()
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        plt.close()

        overlaps = np.array(self.overlaps)
        plt.figure()
        plt.plot(lags, overlaps)
        plt.axvline(self.best_offset, color='r', linestyle='--',
                    label=f'Best offset: {self.best_offset:.3f}s')
        plt.xlabel("Lag (seconds)")
        plt.ylabel("Overlap")
        plt.title("Overlap")
        plt.legend()
        if filename:
            plt.savefig(filename.replace('.png', '_overlap.png'))
        else:
            plt.show()
        plt.close()

    def plot_angles(self, RPY_leaf, RPY_px4, filename=None):
        if RPY_leaf is None or RPY_px4 is None:
            print("No angle data. Run get_euler_angles first.")
            return
        t = np.arange(RPY_leaf.shape[1]) / self.fs
        plt.figure()
        for i, label in enumerate(['Roll', 'Pitch', 'Yaw']):
            plt.subplot(3, 1, i + 1)
            plt.plot(t, RPY_leaf[i], label='Droneleaf')
            plt.plot(t, RPY_px4[i], label='PX4')
            plt.xlabel("Time (seconds)")
            plt.ylabel(f"{label} (rad)")
            plt.title(f"{label} angle")
            plt.legend()
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        plt.close()
    
    def plot_signals(self, filename=None):
        if self.common_times is None or self.best_offset is None:
            print("No signal data. Run compute_best_offset first.")
            return
        
        # Check if signals are multidimensional
        is_multidim = False
        num_dims = 1
        
        if hasattr(self.ros_signal_resampled, 'ndim') and self.ros_signal_resampled.ndim > 1:
            is_multidim = True
            num_dims = self.ros_signal_resampled.shape[1]
        elif hasattr(self.ulog_signal_resampled, 'ndim') and self.ulog_signal_resampled.ndim > 1:
            is_multidim = True
            num_dims = self.ulog_signal_resampled.shape[1]
        
        plt.figure(figsize=(10, 3 * num_dims) if is_multidim else (10, 6))
        
        if is_multidim:
            for i in range(num_dims):
                plt.subplot(num_dims, 1, i + 1)
                
                # Extract the i-th dimension from each signal
                ros_dim = self.ros_signal_resampled[:, i] if self.ros_signal_resampled.ndim > 1 else self.ros_signal_resampled
                ulog_dim = self.ulog_signal_resampled[:, i] if self.ulog_signal_resampled.ndim > 1 else self.ulog_signal_resampled
                
                # Apply offset based on which signal is shorter
                if self.shorter_type == 'ROS':
                    # ROS is shorter, shift it by the offset
                    plt.plot(self.common_times + self.best_offset, ros_dim, label='ROS', linewidth=0.5)
                    plt.plot(self.common_times, ulog_dim, label='Ulog', linewidth=0.5)
                else:
                    # Ulog is shorter, shift it by the offset
                    plt.plot(self.common_times, ros_dim, label='ROS', linewidth=0.5)
                    plt.plot(self.common_times + self.best_offset, ulog_dim, label='Ulog', linewidth=0.5)

                plt.ylabel(f"Signal Dim {i}")
                
                if i == 0:  # Only show legend on the first subplot
                    plt.legend()
                
                if i == num_dims - 1:  # Only show x label on the last subplot
                    plt.xlabel("Time (seconds)")
        else:
            # Original code for 1D signals
            if self.shorter_type == 'ROS':
                # ROS is shorter, shift it by the offset
                plt.plot(self.common_times + self.best_offset, self.ros_signal_resampled, label='ROS', linewidth=0.5)
                plt.plot(self.common_times, self.ulog_signal_resampled, label='Ulog', linewidth=0.5)
            else:
                # Ulog is shorter, shift it by the offset
                plt.plot(self.common_times, self.ros_signal_resampled, label='ROS', linewidth=0.5)
                plt.plot(self.common_times + self.best_offset, self.ulog_signal_resampled, label='Ulog', linewidth=0.5)

            plt.xlabel("Time (seconds)")
            plt.ylabel("Signal")
            plt.legend()
        
        plt.suptitle("Resampled Signals")
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        plt.close()


class SignalSynchronizerSingle(SignalSynchronizer):
    """
    Synchronizer for single-instance signals.
    This class is used when there is only one instance of the signal in both ROS and ULog.
    """
    def __init__(self, bag_path, ulg_path):
        super().__init__(bag_path, ulg_path)
        self.ros_signal_resampled = None
        self.ulog_signal_resampled = None

    def compute_best_offset(self, ros_signal_class: Union[RosSignal, MotorCommandSignal, CartesianSignal, OrientationSignal],
                            ulog_signal_class: Union[UlogSignal, UlogMotorCommandSignal, UlogCartesianSignal, UlogOrientationSignal],
                            ros_topic_name, ulog_msg_key, 
                            ros_signal_idx=None, ulog_signal_idx=None,
                            **signal_kwargs):
        """
        Compute the time offset between ROS and ULog signals.
        
        Args:
            ros_signal_class: Class to use for ROS signal (e.g., MotorCommandSignal, OrientationSignal)
            ulog_signal_class: Class to use for ULog signal (e.g., UlogMotorCommandSignal, UlogOrientationSignal)
            ros_topic_name: Name of the ROS topic to extract
            ulog_msg_key: Name of the ULog message key to extract
            ros_signal_idx: Index of the signal to use for correlation (None uses all dimensions)
            ulog_signal_idx: Index of the signal to use for correlation (None uses all dimensions)
            **signal_kwargs: Additional keyword arguments to pass to signal classes
        """
        # Load the ROS signal
        with load_rosbag(self.bag_path) as bag:
            ros_signal_obj = ros_signal_class(bag, ros_topic_name, **signal_kwargs)
            
        # Load the ULog signal
        with load_ulg(self.ulg_path) as ulog:
            ulog_signal_obj = ulog_signal_class(ulog, ulog_msg_key, **signal_kwargs)
            
        # Extract timestamps and data
        ros_times = ros_signal_obj.timestamps
        ulog_times = ulog_signal_obj.timestamps
        
        # Extract the specific signal dimension if specified
        if ros_signal_idx is not None:
            ros_signal = ros_signal_obj.get_signal_slice(ros_signal_idx)
        else:
            ros_signal = ros_signal_obj.data
            
        if ulog_signal_idx is not None:
            ulog_signal = ulog_signal_obj.get_signal_slice(ulog_signal_idx)
        else:
            ulog_signal = ulog_signal_obj.data

        self._compute_best_offset(ros_times, ulog_times, ros_signal, ulog_signal)

class SignalSynchronizerMulti(SignalSynchronizer):
    """
    Synchronizer for multi-instance signals.
    This class is used when there are multiple instances of the signal in both ROS and ULog.
    """
    def __init__(self, bag_path, ulg_path):
        super().__init__(bag_path, ulg_path)

    def compute_best_offset(self, ros_signal_class: Union[RosSignal, MotorCommandSignal, CartesianSignal, OrientationSignal],
                            ulog_signal_class: Union[UlogSignal, UlogMotorCommandSignal, UlogCartesianSignal, UlogOrientationSignal],
                            ros_topic_name: str,
                            ulog_msg_keys: List[str],
                            ros_signal_idx=None, ulog_signal_idx=None,
                            **signal_kwargs):
        """
        Compute the time offset between ROS and ULog signals.
        
        Args:
            ros_signal_class: Class to use for ROS signal (e.g., MotorCommandSignal, OrientationSignal)
            ulog_signal_class: Class to use for ULog signal (e.g., UlogMotorCommandSignal, UlogOrientationSignal)
            ros_topic_name: Name of the ROS topic to extract
            ulog_msg_key: Name of the ULog message key to extract
            ros_signal_idx: Index of the signal to use for correlation (None uses all dimensions)
            ulog_signal_idx: Index of the signal to use for correlation (None uses all dimensions)
            **signal_kwargs: Additional keyword arguments to pass to signal classes
        """
        # Load the ROS signal
        with load_rosbag(self.bag_path) as bag:
            ros_signal_obj = ros_signal_class(bag, ros_topic_name, **signal_kwargs)
            
        # Load the ULog signal
        ulog_signal_objs:List[Union[UlogSignal, UlogMotorCommandSignal, UlogCartesianSignal, UlogOrientationSignal]] = []
        with load_ulg(self.ulg_path) as ulog:
            for ulog_msg_key in ulog_msg_keys:
                ulog_signal_objs.append(ulog_signal_class(ulog, ulog_msg_key, **signal_kwargs))

        # Extract timestamps and data
        ros_times = ros_signal_obj.timestamps
        # pick shortest Ulog signal timestamps
        ulog_times = min([ulog_signal_obj.timestamps for ulog_signal_obj in ulog_signal_objs], key=len)

        # turn multiple Ulog signals into a single signal multidimensional array
        n_instances = len(ulog_signal_objs)
        ndim_ulog = ulog_signal_objs[0].dimension
        ndim_ros = ros_signal_obj.dimension

        assert ndim_ulog == ndim_ros, "ROS and ULog signals must have the same number of dimensions"
        
        ulog_signal = np.zeros((len(ulog_times), n_instances * ndim_ulog)) # shape (n_samples, n_instances * ndim_ulog)
        ros_signal = np.zeros((len(ros_times), n_instances * ndim_ros)) # shape (n_samples, n_instances * ndim_ros)
        for instance_idx, ulog_signal_obj in enumerate(ulog_signal_objs):
            if ros_signal_idx is not None:
                ros_signal_i = ros_signal_obj.get_signal_slice(ros_signal_idx)
            else:
                ros_signal_i = ros_signal_obj.data
            
            ros_signal[:, instance_idx * ndim_ros:(instance_idx + 1) * ndim_ros] = ros_signal_i

            if ulog_signal_idx is not None:
                ulog_signal_i = ulog_signal_obj.get_signal_slice(ulog_signal_idx)
            else:
                ulog_signal_i = ulog_signal_obj.data

            ulog_signal[:, instance_idx * ndim_ulog:(instance_idx + 1) * ndim_ulog] = ulog_signal_i[:len(ulog_times)] # Ensure Ulog signal matches ROS time base

        self._compute_best_offset(ros_times, ulog_times, ros_signal, ulog_signal)