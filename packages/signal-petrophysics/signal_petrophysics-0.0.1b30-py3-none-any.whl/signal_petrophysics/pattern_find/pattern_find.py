import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.preprocessing import MinMaxScaler
from sklearn.cross_decomposition import CCA
from signal_petrophysics.utils.mnemonics import find_column
from ..utils.mnemonics import find_column
from ..signal_adapt import adjust_signal_length

# Log stencil from any curve of a log set stored in df based on depth
# Function to subsample a DataFrame based on depth range
def signal_sampling_by_depth(df, column_name, mindepth, maxdepth):
    """
    Subsamples a specified column of the DataFrame based on the depth range.

    Parameters:
    - df: pandas DataFrame containing the data.
    - column_name: str, the name of the column to subsample.
    - mindepth: float, the minimum depth for subsampling.
    - maxdepth: float, the maximum depth for subsampling.

    Returns:
    - pandas DataFrame containing the subsampled data.
    """
    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    # Check if the depth column exists
    if "DEPT" not in df.columns:
        raise ValueError("Depth column 'DEPT' does not exist in the DataFrame.")

    # Filter the DataFrame based on the depth range
    signal_df = df[(df["DEPT"] >= mindepth) & (df["DEPT"] <= maxdepth)]

    # Return the subsampled DataFrame
    return signal_df[[column_name, "DEPT"]]



# Function that calculates the similarity between a log and a signal extracted from it (adjusted_stencil)
def auto_similarity(df, log_col, adjusted_stencil, rank=False, method="L2", lag=10):
    """
    Function that calculates the similarity between a log and a signal extracted from it (adjusted_stencil)

    """
    stencil_df = adjusted_stencil[
        ["DEPT", log_col]
    ]  # Pattern organizing the columns order to have in 0 the depth
    stencil_size = (
        stencil_df["DEPT"].max() - stencil_df["DEPT"].min()
    )  # Number of rows in the pattern
    print("stencil size ", stencil_size)

    log_df = df[["DEPT", log_col]]  # Log
    # print(log_df)
    y_l = log_df["DEPT"].max()  # Max depth of the log
    y_o = log_df["DEPT"].min()  # Min depth

    # Calculate the length of the top of the log to the top of the pattern
    y_st1 = stencil_df["DEPT"].min()
    top_interval_df = log_df[(log_df["DEPT"] >= y_o) & (log_df["DEPT"] <= y_st1)]
    top_length = top_interval_df["DEPT"].max() - top_interval_df["DEPT"].min()
    remainder_top = top_length % stencil_size

    # Same for the bottom of the log
    y_st2 = stencil_df["DEPT"].max()
    bottom_interval_df = log_df[(log_df["DEPT"] >= y_st2) & (log_df["DEPT"] <= y_l)]
    bottom_length = bottom_interval_df["DEPT"].max() - bottom_interval_df["DEPT"].min()
    remainder_bottom = bottom_length % stencil_size

    # complete the log
    if remainder_top > 0:
        # print("el tope necesita mas")
        # Complete the top length with the remainder
        to_add_top = stencil_size - remainder_top
        new_y_o = y_o - to_add_top * 0.5 + 0.5
        new_depths_top = np.arange(new_y_o, y_o, 0.5)
        new_depths_top_log = np.zeros(len(new_depths_top))
        top_df = pd.DataFrame({"DEPT": new_depths_top, log_col: new_depths_top_log})
    else:
        top_df = pd.DataFrame()

    if remainder_bottom > 0:
        # print("el fondo necesita mas")

        # print("rb ", remainder_bottom)
        new_y_l = y_l + remainder_bottom
        new_depths_bottom = np.arange(y_l, new_y_l + 0.5, 0.5)
        new_depths_bottom_log = np.zeros(len(new_depths_bottom))
        bottom_df = pd.DataFrame(
            {"DEPT": new_depths_bottom, log_col: new_depths_bottom_log}
        )
    else:
        bottom_df = pd.DataFrame()

    # Concatenate
    log_df = pd.concat([top_df, log_df, bottom_df], ignore_index=True)

    log_df = log_df.sort_values(by="DEPT").reset_index(drop=True)

    # print(log_df)
    log_df_copy = log_df.copy()
    # print(log_df)
    similarity_df = pd.DataFrame()
    similarity = []

    current_dept = log_df["DEPT"].min()  # Initializing depth
    i = 0  # initializing window index

    while current_dept <= log_df["DEPT"].max():

        # print("current depth ", current_dept)

        window_df = log_df[
            (log_df["DEPT"] >= current_dept)
            & (log_df["DEPT"] <= current_dept + stencil_size)
        ]
        window_array = window_df.values

        # print("window array \n", window_array.shape)

        pattern_array = stencil_df.values

        # print("pattern  \n", pattern_array.shape)

        if len(pattern_array) == len(window_array):
            pattern_array[:, 0] = window_array[
                :, 0
            ]  # Replace original depth with window depth

            # Rank Transforming this data if rank is True
            if rank:
                window_ranks = rankdata(window_array[:, 1], method="average")
                stencil_ranks = rankdata(pattern_array[:, 1], method="average")
            else:
                window_ranks = window_array[:, 1]
                stencil_ranks = pattern_array[:, 1]

            # print("window ranks \n", window_ranks, "\n stencil ranks \n", stencil_ranks)

            # Normalize the window ranks
            scaler_window = MinMaxScaler()
            normalized_window_ranks = scaler_window.fit_transform(
                window_ranks.reshape(-1, 1)
            ).flatten()
            normalized_window_ranks = np.column_stack(
                (window_array[:, 0], normalized_window_ranks)
            )
            # print("nw\n", normalized_window_ranks[:5])

            # Normalize the stencil ranks
            scaler_stencil = MinMaxScaler()
            normalized_stencil_ranks = scaler_stencil.fit_transform(
                stencil_ranks.reshape(-1, 1)
            ).flatten()
            # print("ns\n", normalized_stencil_ranks[:5])
            normalized_stencil_ranks = np.column_stack(
                (window_array[:, 0], normalized_stencil_ranks)
            )

            if method == "L2":
                similarity_value = np.sqrt(np.sum((window_ranks - stencil_ranks) ** 2))
            elif method == "L1":
                similarity_value = np.sum(np.abs(window_ranks - stencil_ranks))
            elif method == "CCF":
                similarity_value = np.dot(window_ranks, stencil_ranks)
                # print("sim value ", similarity_value)
            elif method == "ANGLE":
                cos_sim = np.dot(window_ranks, stencil_ranks) / (
                    np.linalg.norm(window_ranks) * np.linalg.norm(stencil_ranks)
                )
                angle_radians = np.arccos(cos_sim) / np.pi
                similarity_value = 1 - angle_radians
            else:
                raise ValueError(f"Unsupported method: {method}")

            ref_depth = (window_array[0, 0] + window_array[-1, 0]) / 2
            # similarity.append([i, ref_depth, window_array, pattern_array.copy(), window_ranks, stencil_ranks, float(similarity_value)])
            i += 1

            # Append the normalized ranks to the similarity list
            similarity.append(
                [
                    i,
                    ref_depth,
                    window_array,
                    pattern_array.copy(),
                    window_ranks,
                    stencil_ranks,
                    float(similarity_value),
                    normalized_window_ranks.copy(),
                    normalized_stencil_ranks.copy(),
                ]
            )
        current_dept += lag  # Update the depth for the initial point of the window

    # Update the DataFrame columns to include normalized ranks
    similarity_df = pd.DataFrame(
        similarity,
        columns=[
            "Window_Index",
            "DEPT",
            "Window",
            "Pattern",
            "Window_Ranks",
            "Stencil_Ranks",
            "Similarity_Value",
            "Normalized_Window_Ranks",
            "Normalized_Stencil_Ranks",
        ],
    )

    # similarity_df = pd.DataFrame(similarity, columns=['Window_Index', 'DEPT', 'Window', 'Pattern', 'Window_Ranks', 'Stencil_Ranks', 'Similarity_Value'])
    # print("sim", similarity_df)
    # Normalize the similarity values
    scaler = MinMaxScaler()
    similarity_df["Norm_Similarity"] = scaler.fit_transform(
        similarity_df[["Similarity_Value"]]
    )

    return similarity_df, log_df_copy



# GENERATE STENCILS FROM UNIVARIATE ADJUSTED STENCIL FUNCTION to handle 1+ curves as inputs
def generate_stencils(df, curve_types, mindepth, maxdepth, factor):
    """
    Generates stencils for multiple log columns over the same depth range and adjusts their lengths.

    Parameters:
        df (DataFrame): pandas DataFrame containing the data.
        curve_types (list): List of curve types to find in the mnemonic dictionary.
        mindepth (float): Minimum depth for the stencil.
        maxdepth (float): Maximum depth for the stencil.
        target_length (int): Target length for the adjusted signal.

    Returns:
        DataFrame: pandas DataFrame containing the adjusted stencils for all specified columns.

    Raises:
        ValueError: If required columns don't exist in the DataFrame.
    """
    # Check if the depth column exists
    if "DEPT" not in df.columns:
        raise ValueError("Depth column 'DEPT' does not exist in the DataFrame.")

    # Find columns using the existing find_column function
    columns = []
    for curve_type in curve_types:
        column = find_column(df, curve_type)
        if column is None:
            raise ValueError(f"No column found for curve type '{curve_type}'")
        columns.append(column)

    # Filter the DataFrame based on the depth range
    signal_df = df[(df["DEPT"] >= mindepth) & (df["DEPT"] <= maxdepth)]

    # Select DEPT plus all found columns
    selected_columns = ["DEPT"] + columns
    subsampled_df = signal_df[selected_columns]

    # Adjust the signal length
    adjusted_stencil = adjust_signal_length(subsampled_df, factor)

    return adjusted_stencil



# Calculation of canonical correlation components correlation coefficient
def calc_cca(df, log_columns, adjusted_stencil, lag=10, apply_rank_transform=False):
    # Validate inputs
    if not isinstance(log_columns, list) or not log_columns:
        raise ValueError("log_columns must be a non-empty list")

    # Debugging: Print columns of df
    # print("DataFrame columns:", df.columns)

    # Find actual column names using find_column
    actual_columns = []
    for column_name in log_columns:
        column = find_column(df, column_name)
        if column is None:
            raise ValueError(f"Column not found for log type: {column_name}")
        actual_columns.append(column)

    # Get unique columns including DEPT
    all_columns = ["DEPT"] + actual_columns

    # print("all columns are ", all_columns)

    # Debugging: Print columns of adjusted_stencil
    # print("Adjusted stencil\n", adjusted_stencil.head(5))

    # Check if all columns exist in adjusted_stencil
    missing_columns = [
        col for col in all_columns if col not in adjusted_stencil.columns
    ]
    if missing_columns:
        raise KeyError(f"Columns {missing_columns} not found in adjusted_stencil")

    stencil_df = adjusted_stencil[all_columns]
    #    stencil_size = len(stencil_df)
    stencil_size = (
        stencil_df["DEPT"].max() - stencil_df["DEPT"].min()
    )  # Number of rows in the pattern

    log_df = df[all_columns].sort_values(by="DEPT").reset_index(drop=True)

    # Calculate depth-based padding
    y_o = log_df["DEPT"].min()
    y_l = log_df["DEPT"].max()
    y_st1 = stencil_df["DEPT"].min()
    y_st2 = stencil_df["DEPT"].max()

    # Top padding
    top_interval_df = log_df[(log_df["DEPT"] >= y_o) & (log_df["DEPT"] <= y_st1)]
    top_length = top_interval_df["DEPT"].max() - top_interval_df["DEPT"].min()
    remainder_top = top_length % stencil_size

    if remainder_top > 0:
        to_add_top = stencil_size - remainder_top
        new_y_o = y_o - to_add_top * 0.5 + 0.5
        new_depths_top = np.arange(new_y_o, y_o, 0.5)
        top_df = pd.DataFrame({"DEPT": new_depths_top})
        for col in actual_columns:
            top_df[col] = 0
    else:
        top_df = pd.DataFrame()

    # Bottom padding
    bottom_interval_df = log_df[(log_df["DEPT"] >= y_st2) & (log_df["DEPT"] <= y_l)]
    bottom_length = bottom_interval_df["DEPT"].max() - bottom_interval_df["DEPT"].min()
    remainder_bottom = bottom_length % stencil_size

    if remainder_bottom > 0:
        new_y_l = y_l + remainder_bottom
        new_depths_bottom = np.arange(y_l, new_y_l + 0.5, 0.5)
        bottom_df = pd.DataFrame({"DEPT": new_depths_bottom})
        for col in actual_columns:
            bottom_df[col] = 0
    else:
        bottom_df = pd.DataFrame()

    # Concatenate
    log_df = pd.concat([top_df, log_df, bottom_df], ignore_index=True)
    log_df = log_df.sort_values(by="DEPT").reset_index(drop=True)

    # print(log_df.head(5))

    # Main loop for CCA
    similarity = []
    current_dept = log_df["DEPT"].min()
    i = 0
    while current_dept <= log_df["DEPT"].max() - stencil_size:
        window_df = log_df[
            (log_df["DEPT"] >= current_dept)
            & (log_df["DEPT"] <= current_dept + stencil_size)
        ]
        # print("window \n", window_df.head(5))
        # print("stencil\n", stencil_df.head(5))

        if len(window_df) == len(stencil_df):
            X = window_df[actual_columns].values
            # print("X\n", X)
            Y = stencil_df[actual_columns].values
        else:
            # print(f"Skipping {current_dept} due to size mismatch: window_df={len(window_df)}, stencil_df={len(stencil_df)}")
            current_dept += lag
            continue

        if (
            np.any(np.isnan(X))
            or np.any(np.isnan(Y))
            or np.any(np.isinf(X))
            or np.any(np.isinf(Y))
        ):
            raise ValueError("NaN or infinite values found in the data.")

        if apply_rank_transform:
            for col_idx in range(X.shape[1]):
                X[:, col_idx] = rankdata(X[:, col_idx])
                # print("X\n",X)
                Y[:, col_idx] = rankdata(Y[:, col_idx])

        # Check for zero variance columns
        # zero_variance_cols_X = np.where(np.std(X, axis=0) == 0)[0]
        # zero_variance_cols_Y = np.where(np.std(Y, axis=0) == 0)[0]

        # if zero_variance_cols_X.size > 0 or zero_variance_cols_Y.size > 0:
        #     #print(f"Zero variance columns in X: {zero_variance_cols_X}")
        #     #print(f"Zero variance columns in Y: {zero_variance_cols_Y}")
        #     raise ValueError("Zero variance detected in data.")

        scaler = MinMaxScaler()  # StandardScaler()
        X_scaled = scaler.fit_transform(X)
        # print("X scaled\n",np.mean(X_scaled[:5]))
        Y_scaled = scaler.fit_transform(Y)
        # print("Y scaled\n",np.mean(Y_scaled[:5]))

        # print(Y_scaled.shape)

        # Debugging: Check shapes and components
        # print(f"X_scaled shape: {X_scaled.shape}, Y_scaled shape: {Y_scaled.shape}")

        n_components = min(len(actual_columns), X_scaled.shape[0], Y_scaled.shape[0])
        # print(f"Number of components: {n_components}")

        cca = CCA(n_components=n_components)
        cca.fit(X_scaled, Y_scaled)
        X_c, Y_c = cca.transform(X_scaled, Y_scaled)

        # canonical_corr = np.corrcoef(X_c.T, Y_c.T)[0, 1]
        # canonical_corr = [np.corrcoef(X_c[:,i], Y_c[:,i])[0, 1] for i in range(cca.n_components)]
        # canonical_corr = [np.corrcoef(X_c[:,i], Y_c[:,i])[0, 1] for i in range(cca.n_components)]
        # canonical_corr1 = canonical_corr[0]  # Keep only the first component
        # canonical_corr2 = canonical_corr[1]  # Keep only the second component
        canonical_corrs = [
            np.corrcoef(X_c[:, i], Y_c[:, i])[0, 1] for i in range(cca.n_components)
        ]

        # Pearson corr coeff between canonically transformed X (logs) and stencils (Y) logs
        # print(np.array(canonical_corrs))

        # print("Canonical Coefficients for X:")
        # for i, coeffs in enumerate(cca.x_weights_):
        #     print(f"Canonical Variable U{i+1}:")
        #     for j, coeff in enumerate(coeffs):
        #         print(f"  Contribution of {actual_columns[j]}: {coeff:.4f}")

        # print("\nCanonical Coefficients for Y:")
        # for i, coeffs in enumerate(cca.y_weights_):
        #     print(f"Canonical Variable V{i+1}:")
        #     for j, coeff in enumerate(coeffs):
        #         print(f"  Contribution of {actual_columns[j]}: {coeff:.4f}")

        # Print coefficients only if correlation coefficient is > 0.9
        for i, canonical_corr in enumerate(canonical_corrs):
            if canonical_corr > 0.9:
                print(f"Canonical Correlation {i+1}: {canonical_corr:.4f}")
                print("Canonical Coefficients for X:")
                for j, coeff in enumerate(cca.x_weights_[:, i]):
                    print(f"  Contribution of {actual_columns[j]}: {coeff:.4f}")
                print("\nCanonical Coefficients for Y:")
                for j, coeff in enumerate(cca.y_weights_[:, i]):
                    print(f"  Contribution of {actual_columns[j]}: {coeff:.4f}")
                print(f"Reference Depth (DEPT): {ref_depth:.2f}")

        ref_depth = (window_df["DEPT"].iloc[0] + window_df["DEPT"].iloc[-1]) / 2
        # similarity.append([i, ref_depth, canonical_corr1,canonical_corr2])
        similarity.append([i, ref_depth] + canonical_corrs)
        # print(i)
        i += 1

        current_dept += lag

    column_names = ["Window_Index", "DEPT"] + [
        f"Canonical_Correlation_{i+1}" for i in range(n_components)
    ]
    similarity_df = pd.DataFrame(similarity, columns=column_names)
    # similarity_df = pd.DataFrame(
    #     similarity,
    #     columns=['Window_Index', 'DEPT', 'Canonical_Correlation_1', 'Canonical_Correlation_2']
    # )
    return similarity_df, log_df


## MULTIWELL UNIVARIATE
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.preprocessing import MinMaxScaler

def offset_similarity(df, log_col, adjusted_stencil, rank=False, method="L2", lag=10):
    stencil_df = adjusted_stencil[["DEPT", log_col]]
    stencil_size = stencil_df["DEPT"].max() - stencil_df["DEPT"].min()
    print("stencil size ", stencil_size)

    log_df = df[["DEPT", log_col]]
    y_l = log_df["DEPT"].max()
    y_o = log_df["DEPT"].min()

    # Initialize similarity list
    similarity = []

    current_dept = log_df["DEPT"].min()
    i = 0

    while current_dept <= log_df["DEPT"].max():
        window_df = log_df[
            (log_df["DEPT"] >= current_dept) & (log_df["DEPT"] <= current_dept + stencil_size)
        ]
        window_array = window_df.values
        pattern_array = stencil_df.values

        if len(pattern_array) == len(window_array):
            pattern_array[:, 0] = window_array[:, 0]

            if rank:
                window_ranks = rankdata(window_array[:, 1], method="average")
                stencil_ranks = rankdata(pattern_array[:, 1], method="average")
            else:
                window_ranks = window_array[:, 1]
                stencil_ranks = pattern_array[:, 1]

            scaler_window = MinMaxScaler()
            normalized_window_ranks = scaler_window.fit_transform(
                window_ranks.reshape(-1, 1)
            ).flatten()
            normalized_window_ranks = np.column_stack(
                (window_array[:, 0], normalized_window_ranks)
            )

            scaler_stencil = MinMaxScaler()
            normalized_stencil_ranks = scaler_stencil.fit_transform(
                stencil_ranks.reshape(-1, 1)
            ).flatten()
            normalized_stencil_ranks = np.column_stack(
                (window_array[:, 0], normalized_stencil_ranks)
            )

            if method == "L2":
                similarity_value = np.sqrt(np.sum((window_ranks - stencil_ranks) ** 2))
            elif method == "L1":
                similarity_value = np.sum(np.abs(window_ranks - stencil_ranks))
            elif method == "CCF":
                similarity_value = np.dot(window_ranks, stencil_ranks)
            elif method == "ANGLE":
                cos_sim = np.dot(window_ranks, stencil_ranks) / (
                    np.linalg.norm(window_ranks) * np.linalg.norm(stencil_ranks)
                )
                angle_radians = np.arccos(cos_sim) / np.pi
                similarity_value = 1 - angle_radians
            else:
                raise ValueError(f"Unsupported method: {method}")

            ref_depth = (window_array[0, 0] + window_array[-1, 0]) / 2
            i += 1

            similarity.append(
                [
                    i,
                    ref_depth,
                    window_array,
                    pattern_array.copy(),
                    window_ranks,
                    stencil_ranks,
                    float(similarity_value),
                    normalized_window_ranks.copy(),
                    normalized_stencil_ranks.copy(),
                ]
            )
        current_dept += lag

    similarity_df = pd.DataFrame(
        similarity,
        columns=[
            "Window_Index",
            "DEPT",
            "Window",
            "Pattern",
            "Window_Ranks",
            "Stencil_Ranks",
            "Similarity_Value",
            "Normalized_Window_Ranks",
            "Normalized_Stencil_Ranks",
        ],
    )

    scaler = MinMaxScaler()
    similarity_df["Norm_Similarity"] = scaler.fit_transform(
        similarity_df[["Similarity_Value"]]
    )

    return similarity_df, log_df


# batch calculation for offset wells, using type well (df_origin)
def process_corr(
    df,df_origin,
    depth_ranges,
    mnemonic_dict,
    stencil_size_factors,
    rank=False,
    method="L2",
    lag=10,
    similarity_threshold=0.9,
):
    """
    Process the correlation analysis for each depth range and stencil factor.
    args:
        df: Well Logs Dataframe
        depth_ranges: List of depth ranges
        mnemonic_dict: Dictionary of mnemonic types
        stencil_size_factors: List of stencil size factors
        rank: Boolean, whether to rank the data or not
        method: Correlation method
        lag: Depth lag
        similarity_threshold: Similarity threshold
    returns:
        results: Dictionary of results
        labeled_logs: Dictionary of labeled logs
    example:
        results, labeled_logs = process_corr(df, depth_ranges, mnemonic_dict, stencil_size_factors, rank=False, method="L2", lag=10, similarity_threshold=0.9)


            
    """
    results = {}
    # Find the gamma column using the mnemonic dictionary
    gamma_col_origin = find_column(df_origin, "gamma")
    gamma_col = find_column(df, "gamma")

    if gamma_col is None:
        raise ValueError("No gamma column found in the DataFrame")
    
    # Process each depth range
    for i, (minsample, maxsample, color, rock_type) in enumerate(depth_ranges):
        # Sample the data for this depth range
        samplegr = signal_sampling_by_depth(df_origin, gamma_col_origin, minsample, maxsample)
        
        if samplegr.empty:
            print(f"Warning: No data sampled for depth range {minsample}-{maxsample}")
            continue
        
        # Process each stencil factor for this depth range
        for j, factor in enumerate(stencil_size_factors):
            # Adjust the stencil
            adjusted_stencil = adjust_signal_length(samplegr, factor)
            
            # Apply calc_corr function
            result_df, log_df = calc_corr(
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
    
    return results,samplegr


# Multiwell Correlation - same as offset similarity
def calc_corr(df, log_col, adjusted_stencil, rank=False, method="L2", lag=10):
    stencil_df = adjusted_stencil[["DEPT", log_col]]
    stencil_size = stencil_df["DEPT"].max() - stencil_df["DEPT"].min()
    print("stencil size ", stencil_size)

    log_df = df[["DEPT", log_col]]
    y_l = log_df["DEPT"].max()
    y_o = log_df["DEPT"].min()

    # Initialize similarity list
    similarity = []

    current_dept = log_df["DEPT"].min()
    i = 0

    while current_dept <= log_df["DEPT"].max():
        window_df = log_df[
            (log_df["DEPT"] >= current_dept) & (log_df["DEPT"] <= current_dept + stencil_size)
        ]
        window_array = window_df.values
        pattern_array = stencil_df.values

        if len(pattern_array) == len(window_array):
            pattern_array[:, 0] = window_array[:, 0]

            if rank:
                window_ranks = rankdata(window_array[:, 1], method="average")
                stencil_ranks = rankdata(pattern_array[:, 1], method="average")
            else:
                window_ranks = window_array[:, 1]
                stencil_ranks = pattern_array[:, 1]

            scaler_window = MinMaxScaler()
            normalized_window_ranks = scaler_window.fit_transform(
                window_ranks.reshape(-1, 1)
            ).flatten()
            normalized_window_ranks = np.column_stack(
                (window_array[:, 0], normalized_window_ranks)
            )

            scaler_stencil = MinMaxScaler()
            normalized_stencil_ranks = scaler_stencil.fit_transform(
                stencil_ranks.reshape(-1, 1)
            ).flatten()
            normalized_stencil_ranks = np.column_stack(
                (window_array[:, 0], normalized_stencil_ranks)
            )

            if method == "L2":
                similarity_value = np.sqrt(np.sum((window_ranks - stencil_ranks) ** 2))
            elif method == "L1":
                similarity_value = np.sum(np.abs(window_ranks - stencil_ranks))
            elif method == "CCF":
                similarity_value = np.dot(window_ranks, stencil_ranks)
            elif method == "ANGLE":
                cos_sim = np.dot(window_ranks, stencil_ranks) / (
                    np.linalg.norm(window_ranks) * np.linalg.norm(stencil_ranks)
                )
                angle_radians = np.arccos(cos_sim) / np.pi
                similarity_value = 1 - angle_radians
            else:
                raise ValueError(f"Unsupported method: {method}")

            ref_depth = (window_array[0, 0] + window_array[-1, 0]) / 2
            i += 1

            similarity.append(
                [
                    i,
                    ref_depth,
                    window_array,
                    pattern_array.copy(),
                    window_ranks,
                    stencil_ranks,
                    float(similarity_value),
                    normalized_window_ranks.copy(),
                    normalized_stencil_ranks.copy(),
                ]
            )
        current_dept += lag

    similarity_df = pd.DataFrame(
        similarity,
        columns=[
            "Window_Index",
            "DEPT",
            "Window",
            "Pattern",
            "Window_Ranks",
            "Stencil_Ranks",
            "Similarity_Value",
            "Normalized_Window_Ranks",
            "Normalized_Stencil_Ranks",
        ],
    )

    scaler = MinMaxScaler()
    similarity_df["Norm_Similarity"] = scaler.fit_transform(
        similarity_df[["Similarity_Value"]]
    )

    return similarity_df, log_df



