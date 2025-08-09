import numpy as np
from scipy.interpolate import interpolate
import pandas as pd



# Function that adjust the depth range and resamples the signal by a factor
def adjust_signal_length(signal_df, factor):
    """
    Adjusts the depth range of the signal to be a factor times the original depth range,
    with new depths spaced every 0.5 units, reshaping the entire signal.

    Parameters:
    - signal_df: pandas DataFrame containing the signal data with 'DEPT' and other signal columns.
    - factor: float, the factor by which to multiply the original depth range.

    Returns:
    - pandas DataFrame with the adjusted signal for all columns.
    """
    # Extract the original depth values
    original_depth = signal_df["DEPT"].to_numpy()
    depth_min = original_depth.min()
    depth_max = original_depth.max()

    # Calculate the original depth range
    original_range = depth_max - depth_min

    # Calculate the new depth range
    new_range = original_range * factor

    # Create new depths with 0.5 spacing
    new_depth_min = depth_min
    new_depth_max = depth_min + new_range
    new_depths = np.arange(new_depth_min, new_depth_max + 0.5, 0.5)

    # Normalize the original depth to [0, 1] for interpolation
    x_old = (original_depth - depth_min) / original_range
    x_new = (new_depths - new_depth_min) / new_range

    # Initialize a dictionary to store interpolated columns
    interpolated_data = {}

    # Interpolate each column except 'DEPT'
    for column in signal_df.columns:
        if column != "DEPT":
            y_old = signal_df[column].to_numpy()
            interpolator = interpolate.interp1d(
                x_old, y_old, kind="linear", fill_value="extrapolate"
            )
            interpolated_data[column] = interpolator(x_new)

    # Add the new depths to the interpolated data
    interpolated_data["DEPT"] = new_depths

    # Create a new DataFrame with the adjusted signal
    adjusted_signal = pd.DataFrame(interpolated_data)

    return adjusted_signal

