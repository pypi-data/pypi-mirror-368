import os
import pandas as pd
from signal_petrophysics.utils.mnemonics import find_column 
from ..utils.mnemonics import find_column
from ..pattern_find.pattern_find import signal_sampling_by_depth, auto_similarity
from ..signal_adapt.signal_adapt import adjust_signal_length

# Your existing functions go here...

# Function that streams the workflow for each stencil size factor and stencil,
def process_depth_ranges(
    df,
    depth_ranges,
    mnemonic_dict,
    stencil_size_factors,
    rank=False,
    method="L2",
    lag=10,
    similarity_threshold=0.9,
):
    results = {}
    # Find the gamma column using the mnemonic dictionary
    gamma_col = find_column(df, "gamma")
    if gamma_col is None:
        raise ValueError("No gamma column found in the DataFrame")

    # Process each depth range
    for i, (minsample, maxsample, color, rock_type) in enumerate(depth_ranges):
        # Sample the data for this depth range
        samplegr = signal_sampling_by_depth(df, gamma_col, minsample, maxsample)
        if samplegr.empty:
            print(f"Warning: No data sampled for depth range {minsample}-{maxsample}")
            continue

        # Process each stencil factor for this depth range
        for j, factor in enumerate(stencil_size_factors):
            # Adjust the stencil
            adjusted_stencil = adjust_signal_length(samplegr, factor)
            # Apply calc function
            result_df, log_df = auto_similarity(
                df, gamma_col, adjusted_stencil, rank=rank, method=method, lag=lag
            )
            if result_df.empty:
                print(
                    f"Warning: No similarity data generated for depth range {minsample}-{maxsample} with factor {factor}"
                )
                continue

            # Add rock type label based on similarity threshold
            condition = result_df["Norm_Similarity"] >= similarity_threshold
            result_df.loc[condition, "rock_type"] = rock_type

            # Store results with rock type and factor information
            results[f"{rock_type}_factor_{factor}"] = result_df

    return results


# Function that merges the extended labels with the main DataFrame
def merge_and_label_dataframes(extended_labels, df):
    """
    Merges each DataFrame in the extended_labels dictionary with the main DataFrame df based on the DEPT column.
    Returns two dictionaries: one with the merged DataFrames and another with specified columns.

    Parameters:
    - extended_labels: dict, a dictionary of DataFrames to be merged.
    - df: DataFrame, the main DataFrame to merge with.

    Returns:
    - merged_dict: dict, a dictionary with merged DataFrames.
    - labeled_logs: dict, a dictionary with DataFrames containing only specified columns.
    """
    # Initialize the dictionaries to store results
    merged_dict = {}
    labeled_logs = {}

    # Iterate over each key and DataFrame in the extended_labels dictionary
    for key, ext_df in extended_labels.items():
        # Merge the extended DataFrame with df on the DEPT column using a right join
        merged_df = df.merge(ext_df, on="DEPT", how="right")

        # Replace NaN values in the 'rock_type' column with 'no_match'
        merged_df["rock_type"] = merged_df["rock_type"].fillna("no_match")

        # Store the merged DataFrame in the merged_dict
        merged_dict[key] = merged_df

        # Create a new DataFrame with only the specified columns
        labeled_logs_df = merged_df[
            ["rock_type", "Norm_Similarity"] + df.columns.tolist()
        ]

        # Store this new DataFrame in the labeled_logs dictionary
        labeled_logs[key] = labeled_logs_df

    return merged_dict, labeled_logs


# Function that exports the dataframe of labeled logs to a csv in a directory
def export_labeled_logs_to_csv(
    labeled_logs,
    directory="/Users/mariafernandagonzalez/Machine-Assisted-Well-Log-Pattern/labeling_univariate/",
):
    """
    Exports each DataFrame in the labeled_logs dictionary to a separate CSV file in the specified directory.
    Rows with NaN in the 'rock_type' column are dropped before exporting.

    Parameters:
    - labeled_logs: dict, a dictionary containing DataFrames to be exported.
    - directory: str, the directory where CSV files will be saved.
    """
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Iterate over each key and DataFrame in the labeled_logs dictionary
    for key, df in labeled_logs.items():
        # Drop rows where 'rock_type' is NaN
        df_cleaned = df.dropna(subset=["rock_type"])

        # Define the file path using the key as the file name
        file_path = os.path.join(directory, f"{key}.csv")

        # Export the cleaned DataFrame to a CSV file
        df_cleaned.to_csv(file_path, index=False)
        print(f"Exported {key} to {file_path}")


# Function that concatenates all depth ranges in the dictionary into a single list of tuples
def concatenate_all_depth_ranges(new_depth_ranges_dict):
    # List to store all concatenated depth ranges
    concatenated_ranges = []

    # Iterate over each entry in the new_depth_ranges_dict
    for depth_ranges in new_depth_ranges_dict.values():
        # Extend the concatenated list with the current depth ranges
        concatenated_ranges.extend(depth_ranges)

    return concatenated_ranges



# Function that extends the labels obtained by thresholding the similarity logs by stencil size, to the whole depth range
def extend_labels(results_dict, depth_ranges):
    # Dictionary to store new depth ranges for each DataFrame
    new_depth_ranges_dict = {}

    for key, df in results_dict.items():
        # Extract the size factor from the key
        try:
            # Assuming the key format is 'rock_type_factor_X'
            size_factor = float(key.split("_")[-1])
        except ValueError:
            print(f"Invalid size factor in key: {key}")
            continue

        # Use a list to store depth ranges for the current DataFrame
        new_depth_ranges = []

        # Iterate over each depth range
        for min_d, max_d, color, rock_type in depth_ranges:
            # Calculate the full range size
            full_range = max_d - min_d

            # Find the central depths where the rock_type is not NaN
            central_depths = df[df["rock_type"] == rock_type]["DEPT"]
            print(f"central depths for {rock_type} and {size_factor}\n", central_depths)

            # Extend labels for each central depth
            for central_depth in central_depths:
                # Calculate the new min and max depths based on the size factor
                lower_bound = central_depth - (full_range * size_factor) / 2
                upper_bound = central_depth + (full_range * size_factor) / 2

                # Modify the rock_type to include the size factor
                modified_rock_type = f"{rock_type}_{size_factor}"

                # Apply the label to the extended range
                df.loc[
                    (df["DEPT"] >= lower_bound) & (df["DEPT"] <= upper_bound),
                    "rock_type",
                ] = modified_rock_type

                # Add the new depth range to the list
                new_depth_ranges.append(
                    (lower_bound, upper_bound, color, modified_rock_type)
                )

        # Store the new depth ranges in the dictionary
        new_depth_ranges_dict[key] = new_depth_ranges

    return results_dict, new_depth_ranges_dict


