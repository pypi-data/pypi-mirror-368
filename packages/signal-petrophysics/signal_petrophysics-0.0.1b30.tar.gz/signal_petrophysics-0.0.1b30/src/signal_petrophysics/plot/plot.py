import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.ticker import MultipleLocator, LogLocator
from scipy.stats import rankdata
from sklearn.preprocessing import MinMaxScaler
from signal_petrophysics.utils.mnemonics import find_column 

# Function to plot the well logs
def plot_well_logs(df, mindepth, maxdepth, mnemonic_dict):
    """
    Function to plot the well logs
    args:
        df: Well Logs Dataframe
        mindepth: minimum depth
        maxdepth: maximum depth
        mnemonic_dict: mnemonic dictionary
    returns:
        plot

    """
    fig, ax = plt.subplots(figsize=(15, 25), sharey=True)
    fig.patch.set_visible(False)
    plt.axis("off")

    # Set up the plot axes
    ax1 = plt.subplot2grid((1, 5), (0, 0), rowspan=1, colspan=1)  # GR
    ax2 = plt.subplot2grid((1, 5), (0, 1), rowspan=1, colspan=1)  # RES
    ax3 = plt.subplot2grid((1, 5), (0, 2), rowspan=1, colspan=1)  # RHOB
    ax4 = plt.subplot2grid((1, 5), (0, 3), rowspan=1, colspan=1)  # SONIC
    ax5 = (
        ax3.twiny()
    )  # Twins the y-axis for the density track with the neutron track # NEU

    # Set common y-limits (Depth limits) for all subplots
    common_ylim = (mindepth, maxdepth)

    # Find columns for each log type
    # Find columns for each log type
    gamma_col = find_column(df, "gamma")  # , mnemonic_dict)
    deepres_col = find_column(df, "deepres")  # , mnemonic_dict)
    rxo_col = find_column(df, "rxo")  # , mnemonic_dict)
    density_col = find_column(df, "density")  # , mnemonic_dict)
    dtc_col = find_column(df, "dtc")  # , mnemonic_dict)
    neutron_col = find_column(df, "neutron")  # , mnemonic_dict)
    caliper_col = find_column(df, "caliper")  # , mnemonic_dict)

    # Gamma Ray track
    if gamma_col:
        ax1.plot(df[gamma_col], df["DEPT"], color="green")
        ax1.set_xlabel("Gamma")
        ax1.xaxis.label.set_color("green")
        ax1.set_xlim(0, 150)
        ax1.set_ylabel("Depth (ft)")
        ax1.tick_params(axis="x", colors="green")
        ax1.spines["top"].set_edgecolor("green")
        ax1.title.set_color("green")
        ax1.set_xticks([0, 50, 100, 150])
        ax1.set_ylim(common_ylim)

    # Twin ax1 for plotting CALIPER_inches simultaneously as GR
    if caliper_col:
        ax1_twiny = ax1.twiny()
        ax1_twiny.plot(df[caliper_col], df["DEPT"], color="black", label="CALI")
        ax1_twiny.set_xlabel("CALI")
        ax1_twiny.xaxis.label.set_color("black")
        ax1_twiny.set_xlim(5, 20)
        ax1_twiny.tick_params(axis="x", colors="black")
        ax1_twiny.spines["top"].set_position(("axes", 1.02001))
        ax1_twiny.spines["top"].set_edgecolor("black")

    # Resistivity track
    if deepres_col:
        ax2.plot(df[deepres_col], df["DEPT"], color="red")
        ax2.set_xlabel("Deep Resistivity (ohm.m)")
        ax2.set_xlim(0.2, 200)
        ax2.xaxis.label.set_color("red")
        ax2.tick_params(axis="x", colors="red")
        ax2.spines["top"].set_edgecolor("red")
        ax2.semilogx()
        ax2.set_ylim(common_ylim)
        ax2.grid(
            which="both", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )

    # Density track
    if density_col:
        ax3.plot(df[density_col], df["DEPT"], color="red")
        ax3.set_xlabel("Density (g/cc)")
        ax3.set_xlim(1.95, 2.95)
        ax3.xaxis.label.set_color("red")
        ax3.tick_params(axis="x", colors="red")
        ax3.spines["top"].set_edgecolor("red")
        ax3.set_xticks([1.95, 2.45, 2.95])
        ax3.set_ylim(common_ylim)

    # Sonic track
    if dtc_col:
        ax4.plot(df[dtc_col], df["DEPT"], color="purple")
        ax4.set_xlabel("DTC (µs/ft)")
        ax4.set_xlim(160, 60)
        ax4.xaxis.label.set_color("purple")
        ax4.tick_params(axis="x", colors="purple")
        ax4.spines["top"].set_edgecolor("purple")
        ax4.set_ylim(common_ylim)
        ax4.set_xticks([160, 130, 100, 70, 60])
        ax4.set_xticklabels([160, 130, 100, 70, 60])

    # Neutron track placed on top of density track
    if neutron_col:
        ax5.plot(df[neutron_col], df["DEPT"], color="blue")
        ax5.set_xlabel("Neutron Porosity (dec)")
        ax5.xaxis.label.set_color("blue")
        ax5.set_xlim(0.6, 0)
        ax5.set_ylim(common_ylim)
        ax5.tick_params(axis="x", colors="blue")
        ax5.spines["top"].set_position(("axes", 1.0200001))
        ax5.spines["top"].set_visible(True)
        ax5.spines["top"].set_edgecolor("blue")
        ax5.set_xticks([0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0])

    # Steps needed to shade
    if density_col and neutron_col:
        nphi_display = ax5.transData.transform(np.c_[df[neutron_col], df["DEPT"]])
        nphi_data = ax3.transData.inverted().transform(nphi_display)
        ax3.fill_betweenx(
            df["DEPT"],
            df[density_col],
            nphi_data[:, 0],
            where=(df[density_col] < nphi_data[:, 0]),
            color="yellow",
            alpha=0.3,
        )

    # Add a rectangle with text above the NPHI label
    rect = patches.Rectangle(
        (0, 1.05),
        1.0,
        0.005,
        transform=ax5.transAxes,
        color="yellow",
        alpha=0.3,
        clip_on=False,
    )
    ax5.add_patch(rect)
    ax5.text(
        0.6,
        1.05,
        "Light Fluid",
        transform=ax5.transAxes,
        fontsize=10,
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
    )

    # Remove y-axis tick labels for all axes except ax1
    for ax in [ax3, ax2, ax4, ax5]:
        ax.set_yticklabels([])

    # Common functions for setting up the plot
    for ax in [ax1, ax2, ax3, ax4]:
        ax.grid(which="major", color="lightgrey", linestyle="-")
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

    # List of all resistivity-related axes
    resistivity_axes = [ax2]

    # Set specific x-ticks and add gridlines for all resistivity-related axes
    resistivity_ticks = [0.2, 2, 20, 200]
    for ax in resistivity_axes:
        ax.set_xticks(resistivity_ticks)
        ax.set_xticklabels(resistivity_ticks)
        ax.grid(
            which="major", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )

    # List of all axes including twinned axes
    all_axes = [ax1, ax2, ax3, ax4]

    # Invert the y-axis for all axes
    for ax in all_axes:
        ax.yaxis.set_minor_locator(MultipleLocator(20))
        ax.grid(
            which="minor", axis="y", color="lightgrey", linestyle="-", linewidth=0.5
        )
        ax.tick_params(axis="y", which="minor", labelleft=False)
        ax.invert_yaxis()

    # Adjust layout
    plt.tight_layout(pad=2.0)
    return fig



def plot_well_logs_withsample_scaled(
    df,
    log_type,
    mindepth,
    maxdepth,
    subsample_mindepth,
    subsample_maxdepth,
    stencil_sizes,
    method,
    mnemonic_dict,
    lag=1,
    rank=False,
    plt_stencil=True,
    plt_window=True,
):
    # Validate depth values
    if mindepth >= maxdepth:
        raise ValueError("mindepth must be less than maxdepth")

    #    def find_column(df, curve_type):
    #        df_columns_lower = {col.lower(): col for col in df.columns}
    #        for mnemonic in mnemonic_dict[curve_type]:
    #            if mnemonic.lower() in df_columns_lower:
    #                return df_columns_lower[mnemonic.lower()]
    #        return None

    # Find columns for each log type
    gamma_col = find_column(df, "gamma")
    print("gamma col is ", gamma_col)
    deepres_col = find_column(df, "deepres")
    rxo_col = find_column(df, "rxo")
    density_col = find_column(df, "density")
    dtc_col = find_column(df, "dtc")
    neutron_col = find_column(df, "neutron")

    # Sample data for each log type if the column exists
    samplegr = (
        signal_sampling_by_depth(df, gamma_col, subsample_mindepth, subsample_maxdepth)
        if gamma_col
        else None
    )
    samplert = (
        signal_sampling_by_depth(
            df, deepres_col, subsample_mindepth, subsample_maxdepth
        )
        if deepres_col
        else None
    )
    samplerxo = (
        signal_sampling_by_depth(df, rxo_col, subsample_mindepth, subsample_maxdepth)
        if rxo_col
        else None
    )
    samplerhs = (
        signal_sampling_by_depth(
            df, density_col, subsample_mindepth, subsample_maxdepth
        )
        if density_col
        else None
    )
    sampledtc = (
        signal_sampling_by_depth(df, dtc_col, subsample_mindepth, subsample_maxdepth)
        if dtc_col
        else None
    )
    samplenphi = (
        signal_sampling_by_depth(
            df, neutron_col, subsample_mindepth, subsample_maxdepth
        )
        if neutron_col
        else None
    )

    # Map log_type to the actual column name
    log_col = find_column(df, log_type)
    if log_col is None:
        raise ValueError(f"No column found for log type: {log_type}")

    axis_titles = {
        "gamma": "Gamma Ray (API)",
        "deepres": "Deep Resistivity (ohm.m)",
        "rxo": "Shallow Resistivity (ohm.m)",
        "density": "Density (g/cc)",
        "dtc": "Sonic (µs/ft)",
        "neutron": "Neutron Porosity (dec)",
    }

    sampled_data_dict = {}
    num_main_plots = 4
    num_corr_plots = len(stencil_sizes)
    total_plots = num_main_plots + num_corr_plots
    depth_range = maxdepth - mindepth
    fig_height = max(depth_range / 100, 1)
    fig, axes = plt.subplots(
        nrows=1,
        ncols=total_plots,
        figsize=(15, fig_height + 5),
        gridspec_kw={"width_ratios": [5] + [2] * num_corr_plots + [5, 5, 5]},
        sharey=True,
        layout="constrained",
    )
    fig.patch.set_visible(False)
    common_ylim = (maxdepth, mindepth)

    for ax in axes:
        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(which="major", axis="y", linestyle="-", color="lightgrey")
        ax.grid(which="minor", axis="y", linestyle="-", color="lightgrey")
        ax.tick_params(axis="x", labelsize=8)

    # Gamma ray log
    if gamma_col:
        axes[0].plot(
            samplegr[gamma_col],
            samplegr["DEPT"],
            color="#00FFFF",
            label="sample_gr",
            alpha=0.6,
            linewidth=4,
        )
        axes[0].plot(gamma_col, "DEPT", data=df, color="green", linewidth=1)
        axes[0].set_xlabel(axis_titles["gamma"])
        axes[0].xaxis.label.set_color("green")
        axes[0].set_xlim(0, 150)
        axes[0].set_ylabel("Depth (ft)")
        axes[0].tick_params(axis="x", colors="green")
        axes[0].spines["top"].set_edgecolor("green")
        axes[0].title.set_color("green")
        axes[0].set_xticks([0, 50, 100, 150])  # ([0, 25,50,75,100,125, 150])
        axes[0].set_ylim(common_ylim)

    # Caliper plotting
    caliper_col = find_column(df, "caliper")
    if caliper_col:
        ax1_twiny = axes[0].twiny()
        ax1_twiny.plot(
            caliper_col,
            "DEPT",
            data=df,
            color="black",
            label="CALI",
            linewidth=1,
            alpha=0.2,
        )
        ax1_twiny.set_xlabel("Caliper (inches)")
        ax1_twiny.xaxis.label.set_color("black")
        ax1_twiny.set_xlim(0, 20)
        ax1_twiny.tick_params(axis="x", colors="black")
        ax1_twiny.spines["top"].set_position(("axes", 1.02001))
        ax1_twiny.spines["top"].set_edgecolor("black")
        ax1_twiny.set_ylim(common_ylim)

    corr_df_dict = {}
    # Normalizing the correlation values for colormap
    norm = Normalize(vmin=0, vmax=1)
    cmap = plt.get_cmap("coolwarm")
    for i, sizef in enumerate(stencil_size_factors):
        if samplegr is not None:
            print("size is ", sizef)
            # print("samplegr \n", samplegr)
            adjusted_stencil = adjust_signal_length(
                samplegr, sizef
            )  # this effectively changes the samplegr of size, by just changing the depths
            # print("adjusted stencil is\n", adjusted_stencil)

            # corr_result, ws = calc(df, log_col, mindepth, maxdepth, adjusted_stencil, type=method, rank=rank, lag=lag)
            corr_result, ws = calc(
                df, "GR", adjusted_stencil, rank=rank, method=method, lag=lag
            )

            # print(f"combined data for {size} \n", ws.head(size+2))#,"\n and tail \n",ws.tail(size+2))
            sampled_data_dict[sizef] = (
                adjusted_stencil  # stores for each size, the adjusted stencil
            )
            # print(f"sampled data dict for {size}", sampled_data_dict[size])

            depth_values = corr_result["DEPT"]  # corr_result[:, 0]
            ##print("obtaining depth values from first column from calc\n",depth_values)
            correlation_values = corr_result["Norm_Similarity"]  # corr_result[:, 2]

            norm_window = np.array(corr_result["Normalized_Window_Ranks"].tolist())
            input_depths = norm_window[:, 0]

            axes[1 + i].plot(
                correlation_values,
                depth_values,
                color="black",
                linestyle="-",
                linewidth=0.3,
            )  # ,marker='*',markersize=5) #plot similarity
            axes[1 + i].set_xticks([0, 0.25, 0.5, 0.75, 1])

            # Extract and plot both windows and stencils in the same loop
            if plt_window or plt_stencil:
                for index, row in corr_result.iterrows():
                    # Extract depths and values for both windows and stencils
                    normalized_window_ranks = row["Normalized_Window_Ranks"]
                    normalized_stencil_ranks = row["Normalized_Stencil_Ranks"]

                    # Extract depths and values for windows
                    window_depths = [pair[0] for pair in normalized_window_ranks]
                    window_ranks = [pair[1] for pair in normalized_window_ranks]

                    # Extract depths and values for stencils
                    stencil_depths = [pair[0] for pair in normalized_stencil_ranks]
                    stencil_ranks = [pair[1] for pair in normalized_stencil_ranks]

                    # Plot windows in blue if plt_window is True
                    if plt_window:
                        axes[1 + i].plot(
                            window_ranks,
                            window_depths,
                            color="blue",
                            linestyle="-",
                            linewidth=0.8,
                        )

                    # Plot stencils in green if plt_stencil is True
                    if plt_stencil:
                        axes[1 + i].plot(
                            stencil_ranks,
                            stencil_depths,
                            color="green",
                            linestyle="-",
                            linewidth=0.8,
                        )

            corr_df = pd.DataFrame(
                {"Depth": depth_values, "Correlation": correlation_values}
            )

            corr_df_dict[sizef] = corr_df
            axes[1 + i].set_ylim(max(depth_values), min(depth_values))
            axes[1 + i].grid(which="major", axis="x", color="lightgrey", linestyle="-")
            axes[1 + i].grid(which="minor", axis="x", color="lightgrey", linestyle=":")
            axes[1 + i].set_title(f"{sizef} {method}", fontsize=7)

            # Fill between with varying colors
            for j in range(len(depth_values) - 1):
                color = cmap(norm(correlation_values[j]))
                axes[1 + i].fill_betweenx(
                    [depth_values[j], depth_values[j + 1]],
                    0,
                    [correlation_values[j], correlation_values[j + 1]],
                    color=color,
                    # alpha=0.9
                )
            axes[1 + i].set_xlim(0, 1)

    # Plotting resistivity logs
    resistivity_index = 1 + num_corr_plots
    if deepres_col:
        axes[resistivity_index].plot(
            samplert[deepres_col],
            samplegr["DEPT"],
            color="#00FFFF",
            label="sample_rt",
            alpha=0.6,
            linewidth=4,
        )
        axes[resistivity_index].plot(
            deepres_col, "DEPT", data=df, color="red", linewidth=1
        )
        axes[resistivity_index].set_xlabel(axis_titles["deepres"])
        axes[resistivity_index].xaxis.label.set_color("red")
        axes[resistivity_index].set_xlim(0.2, 2000)
        axes[resistivity_index].tick_params(axis="x", colors="red")
        axes[resistivity_index].spines["top"].set_edgecolor("red")
        axes[resistivity_index].semilogx()
        axes[resistivity_index].set_ylim(common_ylim)
        axes[resistivity_index].xaxis.set_minor_locator(
            LogLocator(base=10.0, subs="auto", numticks=10)
        )
        axes[resistivity_index].grid(
            which="minor", axis="x", linestyle=":", color="lightgrey"
        )

    # Shallow resistivity (RXO)
    if rxo_col:
        ax2_twiny1 = axes[resistivity_index].twiny()
        ax2_twiny1.plot(
            samplerxo[rxo_col], samplerxo["DEPT"], color="green", linewidth=1
        )
        ax2_twiny1.set_xlabel(axis_titles["rxo"])
        ax2_twiny1.xaxis.label.set_color("green")
        ax2_twiny1.tick_params(axis="x", colors="green")
        ax2_twiny1.spines["top"].set_position(("axes", 1.025))
        ax2_twiny1.spines["top"].set_edgecolor("green")
        ax2_twiny1.semilogx()
        ax2_twiny1.set_ylim(common_ylim)

    # Plotting density log
    density_index = 2 + num_corr_plots
    if density_col:
        axes[density_index].plot(
            samplerhs[density_col],
            samplerhs["DEPT"],
            color="#00FFFF",
            label="sample_rhob",
            alpha=0.6,
            linewidth=5,
        )
        axes[density_index].plot(
            density_col, "DEPT", data=df, color="red", linewidth=0.8
        )
        axes[density_index].set_xlabel(axis_titles["density"])
        axes[density_index].xaxis.label.set_color("red")
        axes[density_index].set_xlim(1.95, 2.95)
        axes[density_index].tick_params(axis="x", colors="red")
        axes[density_index].spines["top"].set_edgecolor("red")
        axes[density_index].set_xticks([1.95, 2.45, 2.95])
        axes[density_index].set_ylim(common_ylim)

    # Plotting neutron log
    if neutron_col:
        ax5 = axes[density_index].twiny()
        ax5.plot(
            samplenphi[neutron_col],
            samplenphi["DEPT"],
            color="#AAFF00",
            label="sample_neu",
            alpha=0.6,
            linewidth=5,
        )
        ax5.plot(neutron_col, "DEPT", data=df, color="blue", linewidth=0.8)
        ax5.set_xlabel(axis_titles["neutron"])
        ax5.xaxis.label.set_color("blue")
        ax5.set_xlim(0.6, 0)
        ax5.set_ylim(common_ylim)
        ax5.tick_params(axis="x", colors="blue")
        ax5.spines["top"].set_position(("axes", 1.0200001))
        ax5.spines["top"].set_visible(True)
        ax5.spines["top"].set_edgecolor("blue")
        ax5.set_xticks([0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0])

    # Light fluid shading
    nphi_display = ax5.transData.transform(np.c_[df[neutron_col], df["DEPT"]])
    nphi_data = axes[density_index].transData.inverted().transform(nphi_display)
    axes[density_index].fill_betweenx(
        df["DEPT"],
        df[density_col],
        nphi_data[:, 0],
        where=(df[density_col] < nphi_data[:, 0]),
        color="yellow",
        alpha=0.3,
    )

    # Light fluid label
    rect = patches.Rectangle(
        (0, 1.04),
        1.0,
        0.015,
        transform=ax5.transAxes,
        color="yellow",
        alpha=0.3,
        clip_on=False,
    )
    ax5.add_patch(rect)
    ax5.text(
        0.5,
        1.045,
        "Light Fluid",
        transform=ax5.transAxes,
        fontsize=10,
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
    )

    # Plotting sonic log
    sonic_index = 3 + num_corr_plots
    if dtc_col:
        axes[sonic_index].plot(
            sampledtc[dtc_col],
            sampledtc["DEPT"],
            color="#00FFFF",
            label="sample_dt",
            alpha=0.6,
            linewidth=5,
        )
        axes[sonic_index].plot(dtc_col, "DEPT", data=df, color="purple", linewidth=1)
        axes[sonic_index].set_xlabel(axis_titles["dtc"])
        axes[sonic_index].xaxis.label.set_color("purple")
        axes[sonic_index].set_xlim(160, 60)
        axes[sonic_index].tick_params(axis="x", colors="purple")
        axes[sonic_index].spines["top"].set_edgecolor("purple")
        axes[sonic_index].set_ylim(common_ylim)
        axes[sonic_index].set_xticks([160, 140, 120, 100, 80, 60])

    for ax in axes:
        ax.grid(which="major", color="lightgrey", linestyle="-")
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

    return fig, corr_result


# modified with rock type names
def plot_rock_labels(
    df,
    mindepth,
    maxdepth,
    mnemonic_dict,
    rock_intervals,
    x_ranges,
    depth_ranges,
    mintick=50,
    maxtick=500,
):
    fig, ax = plt.subplots(figsize=(15, 20), sharey=True)
    fig.patch.set_visible(False)
    plt.axis("off")

    # Set up the plot axes
    ax1 = plt.subplot2grid((1, 5), (0, 0), rowspan=1, colspan=1)  # GR
    ax2 = plt.subplot2grid((1, 5), (0, 1), rowspan=1, colspan=1)  # RES
    ax3 = plt.subplot2grid((1, 5), (0, 2), rowspan=1, colspan=1)  # RHOB
    ax4 = plt.subplot2grid((1, 5), (0, 3), rowspan=1, colspan=1)  # SONIC
    ax5 = (
        ax3.twiny()
    )  # Twins the y-axis for the density track with the neutron track # NEU

    # Set common y-limits (Depth limits) for all subplots
    common_ylim = (mindepth, maxdepth)

    # Find columns for each log type
    gamma_col = find_column(df, "gamma")
    deepres_col = find_column(df, "deepres")
    rxo_col = find_column(df, "rxo")
    density_col = find_column(df, "density")
    dtc_col = find_column(df, "dtc")
    neutron_col = find_column(df, "neutron")
    caliper_col = find_column(df, "caliper")

    # Create a dictionary to store DataFrames for each sample
    sample_dfs = {}

    # Populate the dictionary with DataFrames based on depth ranges
    for i, (min_d, max_d, _, rock_type) in enumerate(depth_ranges):
        sample_name = f"sample_{i+1}"
        sample_df = df[(df["DEPT"] >= min_d) & (df["DEPT"] <= max_d)]
        sample_dfs[sample_name] = sample_df

    # Plot logs with sampled data highlighted
    if gamma_col and not df[gamma_col].empty:
        for i, (sample, (min_d, max_d, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax1.plot(
                sample[gamma_col],
                sample["DEPT"],
                color=color,
                label=f"sample_gr_{i+1}",
                alpha=0.6,
                linewidth=5,
            )
            ax1.plot(df[gamma_col], df["DEPT"], color="green", linewidth=1.5)
            #            # Annotate each rock type at the midpoint of its depth range
            #            ax1.annotate(
            #                rock_type,
            #                xy=(x_ranges["gamma"][1], (min_d + max_d) / 2),
            #                xytext=(5, 0),
            #                textcoords="offset points",
            #                ha="left",
            #                va="center",
            #                fontsize=8,
            #                color="black",
            #            )
            ax1.set_xlabel("Gamma")
            ax1.xaxis.label.set_color("green")
            ax1.set_xlim(x_ranges["gamma"])
            ax1.set_ylabel("Depth (ft)")
            ax1.tick_params(axis="x", colors="green")
            ax1.spines["top"].set_edgecolor("green")
            ax1.title.set_color("green")
            ax1.set_xticks(np.linspace(*x_ranges["gamma"], num=4))
            ax1.set_ylim(common_ylim)

    # Twin ax1 for plotting CALIPER_inches simultaneously as GR
    if caliper_col and not df[caliper_col].empty:
        ax1_twiny = ax1.twiny()
        ax1_twiny.plot(
            df[caliper_col], df["DEPT"], color="black", label="CALI", alpha=0.3
        )
        ax1_twiny.set_xlabel("CALI")
        ax1_twiny.xaxis.label.set_color("black")
        ax1_twiny.set_xlim(x_ranges["caliper"])
        ax1_twiny.tick_params(axis="x", colors="black")
        ax1_twiny.spines["top"].set_position(("axes", 1.02001))
        ax1_twiny.spines["top"].set_edgecolor("black")

    # Resistivity track
    if deepres_col and not df[deepres_col].empty:
        for i, (sample, (_, _, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax2.plot(
                sample[deepres_col],
                sample["DEPT"],
                color=color,
                label=f"sample_res_{i+1}",
                alpha=0.6,
                linewidth=4,
            )
            ax2.plot(df[deepres_col], df["DEPT"], color="red", linewidth=1.5)
            ax2.set_xlabel("Deep Resistivity (ohm.m)")
            ax2.set_xlim(x_ranges["deepres"])
            ax2.xaxis.label.set_color("red")
            ax2.tick_params(axis="x", colors="red")
            ax2.spines["top"].set_edgecolor("red")
            ax2.semilogx()
            ax2.set_ylim(common_ylim)
            ax2.grid(
                which="both", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
            )
            ax2.annotate(
                rock_type,
                xy=(
                    np.mean(x_ranges["deepres"]),
                    (min_d + max_d) / 2,
                ),  # Middle of resistivity track
                xytext=(0, 0),
                textcoords="offset points",
                ha="center",
                va="center",
                fontsize=6,  # Smaller font size
                color="black",
            )
    # Shallow resistivity
    if rxo_col and not df[rxo_col].empty:
        ax2_twiny1 = ax2.twiny()
        ax2_twiny1.set_xlabel("Shallow Resistivity (ohm.m)")
        ax2_twiny1.plot(df[rxo_col], df["DEPT"], color="green", linewidth=1.5)
        ax2_twiny1.set_xlim(x_ranges["shalres"])
        ax2_twiny1.xaxis.label.set_color("green")
        ax2_twiny1.tick_params(axis="x", colors="green")
        ax2_twiny1.spines["top"].set_position(("axes", 1.02001))
        ax2_twiny1.spines["top"].set_edgecolor("green")
        ax2_twiny1.semilogx()
        ax2_twiny1.set_ylim(common_ylim)

    # Density track
    if density_col and not df[density_col].empty:
        for i, (sample, (_, _, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax3.plot(
                sample[density_col],
                sample["DEPT"],
                color=color,
                label=f"sample_rhob_{i+1}",
                alpha=0.6,
                linewidth=5,
            )
            ax3.plot(df[density_col], df["DEPT"], color="red", linewidth=1.5)
            ax3.set_xlabel("Density (g/cc)")
            ax3.set_xlim(x_ranges["density"])
            ax3.xaxis.label.set_color("red")
            ax3.tick_params(axis="x", colors="red")
            ax3.spines["top"].set_edgecolor("red")
            ax3.set_xticks(np.linspace(*x_ranges["density"], num=3))
            ax3.set_ylim(common_ylim)

    # Sonic track
    if dtc_col and not df[dtc_col].empty:
        for i, (sample, (_, _, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax4.plot(
                sample[dtc_col],
                sample["DEPT"],
                color=color,
                label=f"sample_dtc_{i+1}",
                alpha=0.6,
                linewidth=5,
            )
            ax4.plot(df[dtc_col], df["DEPT"], color="purple", linewidth=0.5)
            ax4.set_xlabel("DTC (µs/ft)")
            ax4.set_xlim(x_ranges["dtc"])
            ax4.xaxis.label.set_color("purple")
            ax4.tick_params(axis="x", colors="purple")
            ax4.spines["top"].set_edgecolor("purple")
            ax4.set_ylim(common_ylim)
            ax4.set_xticks(np.linspace(*x_ranges["dtc"], num=5))
            ax4.set_xticklabels(np.linspace(*x_ranges["dtc"], num=5).astype(int))

    # Neutron track placed on top of density track
    if neutron_col:
        for i, (sample, (_, _, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax5.plot(
                sample[neutron_col],
                sample["DEPT"],
                color=color,
                label=f"sample_neutron_{i+1}",
                alpha=1,
                linewidth=5,
            )
            ax5.plot(df[neutron_col], df["DEPT"], color="blue", linewidth=1.5)
            ax5.set_xlabel("Neutron Porosity (dec)")
            ax5.xaxis.label.set_color("blue")
            ax5.set_xlim(x_ranges["neutron"])
            ax5.set_ylim(common_ylim)
            ax5.tick_params(axis="x", colors="blue")
            ax5.spines["top"].set_position(("axes", 1.0200001))
            ax5.spines["top"].set_visible(True)
            ax5.spines["top"].set_edgecolor("blue")
            ax5.set_xticks(np.linspace(*x_ranges["neutron"], num=7))

    # Highlight rock intervals with specified colors
    legend_handles = []
    for label, intervals, color in rock_intervals:
        mask = np.zeros_like(df["DEPT"], dtype=bool)
        for min_depth, max_depth in intervals:
            mask |= (df["DEPT"] >= min_depth) & (df["DEPT"] <= max_depth)
        if gamma_col:
            ax1.fill_betweenx(
                df["DEPT"], *x_ranges["gamma"], where=mask, color=color, alpha=0.2
            )
        if deepres_col:
            ax2.fill_betweenx(
                df["DEPT"], *x_ranges["deepres"], where=mask, color=color, alpha=0.2
            )
        if density_col:
            ax3.fill_betweenx(
                df["DEPT"], *x_ranges["density"], where=mask, color=color, alpha=0.2
            )
        if dtc_col:
            ax4.fill_betweenx(
                df["DEPT"], *x_ranges["dtc"], where=mask, color=color, alpha=0.2
            )

    # Add legend for rock types
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=len(rock_intervals),
        bbox_to_anchor=(0.5, 1.05),
        frameon=False,
    )

    # Steps needed to shade
    if density_col and neutron_col:
        nphi_display = ax5.transData.transform(np.c_[df[neutron_col], df["DEPT"]])
        nphi_data = ax3.transData.inverted().transform(nphi_display)
        ax3.fill_betweenx(
            df["DEPT"],
            df[density_col],
            nphi_data[:, 0],
            where=(df[density_col] < nphi_data[:, 0]),
            color="yellow",
            alpha=0.3,
        )

    # Add a rectangle with text above the NPHI label
    rect = patches.Rectangle(
        (0, 1.05),
        1.0,
        0.005,
        transform=ax5.transAxes,
        color="yellow",
        alpha=0.3,
        clip_on=False,
    )
    ax5.add_patch(rect)
    ax5.text(
        0.6,
        1.05,
        "Light Fluid",
        transform=ax5.transAxes,
        fontsize=10,
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
    )

    # Remove y-axis tick labels for all axes except ax1
    for ax in [ax3, ax2, ax4, ax5]:
        ax.set_yticklabels([])

    # Common functions for setting up the plot
    for ax in [ax1, ax2, ax3, ax4]:
        ax.grid(which="major", color="lightgrey", linestyle="-")
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

    # List of all resistivity-related axes
    resistivity_axes = [ax2]

    # Set specific x-ticks and add gridlines for all resistivity-related axes
    resistivity_ticks = [0.2, 2, 20, 200]
    for ax in resistivity_axes:
        ax.set_xticks(resistivity_ticks)
        ax.set_xticklabels(resistivity_ticks)
        ax.grid(
            which="major", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )

    # List of all axes including twinned axes
    all_axes = [ax1, ax2, ax3, ax4]

    # Invert the y-axis for all axes
    for ax in all_axes:
        ax.yaxis.set_minor_locator(MultipleLocator(mintick))
        ax.yaxis.set_major_locator(MultipleLocator(maxtick))
        ax.grid(
            which="minor", axis="y", color="lightgrey", linestyle="-", linewidth=0.5
        )
        ax.grid(
            which="major", axis="y", color="lightgrey", linestyle="-", linewidth=1.5
        )
        ax.tick_params(axis="y", which="minor", labelleft=False)
        ax.invert_yaxis()

    # Adjust layout
    plt.tight_layout(pad=2.0)
    return fig, sample_dfs


# Function that categorizes lithology based on gamma ray values
def categorize_intervals_from_df(df, gamma_col="GR"):
    # Define gamma ray thresholds for each rock type, excluding Carbonate
    thresholds = {
        "Clean Sandstone": (0, 40),  # Example threshold
        "Shaly Sandstone": (40, 100),
        "Shale": (100, 200),
    }

    # Initialize rock intervals
    rock_intervals = {"Clean Sandstone": [], "Shaly Sandstone": [], "Shale": []}

    # Iterate over the DataFrame rows
    for index, row in df.iterrows():
        gamma_value = row[gamma_col]
        depth_interval = (row["DEPT"], row["DEPT"])  # Assuming these columns exist

        # Determine the rock type based on gamma ray value
        for rock_type, (min_val, max_val) in thresholds.items():
            if min_val < gamma_value <= max_val:
                rock_intervals[rock_type].append(depth_interval)
                break

    # Convert to the desired format with colors, excluding Carbonate
    formatted_intervals = [
        ("Clean Sandstone", rock_intervals["Clean Sandstone"], "yellow"),
        ("Shaly Sandstone", rock_intervals["Shaly Sandstone"], "orange"),
        ("Shale", rock_intervals["Shale"], "brown"),
    ]

    return formatted_intervals


# Function that plots the rock labels automatically
def plot_rock_labels_auto(
    df,
    mindepth,
    maxdepth,
    mnemonic_dict,
    rock_intervals,
    x_ranges,
    depth_ranges,
    mintick=50,
    maxtick=500,
    wspace=0.3,dim1=15,dim2=20
):
    fig, ax = plt.subplots(figsize=(dim1, dim2), sharey=True)
    fig.patch.set_visible(False)
    plt.axis("off")

    # Set up the plot axes
    ax1 = plt.subplot2grid((1, 5), (0, 0), rowspan=1, colspan=1)  # GR
    ax2 = plt.subplot2grid((1, 5), (0, 1), rowspan=1, colspan=1)  # RES
    ax3 = plt.subplot2grid((1, 5), (0, 2), rowspan=1, colspan=1)  # RHOB
    ax5 = (
        ax3.twiny()
    )  # Twins the y-axis for the density track with the neutron track # NEU

    # Adjust subplot spacing
    plt.subplots_adjust(
        left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=wspace, hspace=0.1
    )

    # Set common y-limits (Depth limits) for all subplots
    common_ylim = (mindepth, maxdepth)

    # Find columns for each log type
    gamma_col = find_column(df, "gamma")
    deepres_col = find_column(df, "deepres")
    rxo_col = find_column(df, "rxo")
    density_col = find_column(df, "density")
    dtc_col = find_column(df, "dtc")
    neutron_col = find_column(df, "neutron")
    caliper_col = find_column(df, "caliper")
    pe_col = find_column(df, "pe")
    sp_col = find_column(df, "sp")

    # Create a dictionary to store DataFrames for each sample
    sample_dfs = {}

    # Populate the dictionary with DataFrames based on depth ranges
    for i, (min_d, max_d, color, rock_type) in enumerate(depth_ranges):
        sample_name = f"sample_{i+1}"
        sample_df = df[(df["DEPT"] >= min_d) & (df["DEPT"] <= max_d)]
        sample_dfs[sample_name] = sample_df

    # Plot logs with sampled data highlighted
    if gamma_col and not df[gamma_col].empty:
        for i, (sample, (min_d, max_d, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax1.plot(
                sample[gamma_col],
                sample["DEPT"],
                color=color,
                label=f"sample_gr_{i+1}",
                alpha=0.6,
                linewidth=5,
            )
            ax1.plot(df[gamma_col], df["DEPT"], color="green", linewidth=1.0)
    #            ax1.annotate(
    #                rock_type,
    #                xy=(
    #                    x_ranges["gamma"][0]
    #                    + 0.5 * (x_ranges["gamma"][1] - x_ranges["gamma"][0]),
    #                    min_d,
    #                ),
    #                xytext=(1, 0),
    #                textcoords="offset points",
    #                ha="left",
    #                va="center",
    #                fontsize=12,
    #                color="black",
    #                zorder=20,
    #            )

    ax1.set_xlabel("Gamma")
    ax1.xaxis.label.set_color("green")
    ax1.set_xlim(x_ranges["gamma"])
    ax1.set_ylabel("Depth (ft)")
    ax1.tick_params(axis="x", colors="green")
    ax1.spines["top"].set_edgecolor("green")
    ax1.title.set_color("green")
    ax1.set_xticks(np.linspace(*x_ranges["gamma"], num=4))
    ax1.set_ylim(common_ylim)

    # Twin ax1 for plotting CALIPER_inches simultaneously as GR
    if caliper_col and not df[caliper_col].empty:
        ax1_twiny = ax1.twiny()
        ax1_twiny.plot(
            df[caliper_col], df["DEPT"], color="black", label="CALI", alpha=0.3
        )
        ax1_twiny.set_xlabel("CALI")
        ax1_twiny.xaxis.label.set_color("black")
        ax1_twiny.set_xlim(x_ranges["caliper"])
        ax1_twiny.tick_params(axis="x", colors="black")
        ax1_twiny.spines["top"].set_position(("axes", 1.02001))
        ax1_twiny.spines["top"].set_edgecolor("black")

    # SP log on a twinned axis of the gamma track (ax1)
    if sp_col and not df[sp_col].empty:
        ax1_twiny_sp = ax1.twiny()
        ax1_twiny_sp.plot(
            df[sp_col], df["DEPT"], color="orange", linewidth=1.0, label="SP"
        )
        ax1_twiny_sp.set_xlabel("SP")
        ax1_twiny_sp.xaxis.label.set_color("orange")
        ax1_twiny_sp.set_xlim(x_ranges["sp"])
        ax1_twiny_sp.tick_params(axis="x", colors="orange")
        ax1_twiny_sp.spines["top"].set_position(("axes", 1.04))
        ax1_twiny_sp.spines["top"].set_edgecolor("orange")

    # Resistivity track
    if deepres_col and not df[deepres_col].empty:
        for i, (sample, (min_d, max_d, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax2.plot(
                sample[deepres_col],
                sample["DEPT"],
                color=color,
                label=f"sample_res_{i+1}",
                alpha=0.6,
                linewidth=4,
            )
            ax2.annotate(
                rock_type,
                xy=(
                    x_ranges["deepres"][0],
                    # + 0.5 * (x_ranges["deepres"][1] - x_ranges["deepres"][0]),
                    min_d,
                ),
                xytext=(1, 0),
                #            xy=(
                #                x_ranges["deepres"][1],
                #                (min_d + max_d) / 2,
                #            ),  # Middle of resistivity track
                #            xytext=(5, 0),
                textcoords="offset points",
                ha="center",
                va="center",
                fontsize=18,
                color="black",
            )
            ax2.plot(df[deepres_col], df["DEPT"], color="red", linewidth=1.0)
        ax2.set_xlabel("Deep Resistivity (ohm.m)")
        ax2.set_xlim(x_ranges["deepres"])
        ax2.xaxis.label.set_color("red")
        ax2.tick_params(axis="x", colors="red")
        ax2.spines["top"].set_edgecolor("red")
        ax2.semilogx()
        ax2.set_ylim(common_ylim)
        ax2.grid(
            which="both", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )
    # Shallow resistivity
    if rxo_col and not df[rxo_col].empty:
        ax2_twiny1 = ax2.twiny()
        ax2_twiny1.set_xlabel("Shallow Resistivity (ohm.m)")
        ax2_twiny1.plot(df[rxo_col], df["DEPT"], color="green", linewidth=1.0)
        ax2_twiny1.set_xlim(x_ranges["shalres"])
        ax2_twiny1.xaxis.label.set_color("green")
        ax2_twiny1.tick_params(axis="x", colors="green")
        ax2_twiny1.spines["top"].set_position(("axes", 1.02001))
        ax2_twiny1.spines["top"].set_edgecolor("green")
        ax2_twiny1.semilogx()
        ax2_twiny1.set_ylim(common_ylim)

    # Density track
    if density_col and not df[density_col].empty:
        for i, (sample, (_, _, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax3.plot(
                sample[density_col],
                sample["DEPT"],
                color=color,
                label=f"sample_rhob_{i+1}",
                alpha=0.6,
                linewidth=5,
            )
            ax3.plot(df[density_col], df["DEPT"], color="red", linewidth=1.0)
        ax3.set_xlabel("Density (g/cc)")
        ax3.set_xlim(x_ranges["density"])
        ax3.xaxis.label.set_color("red")
        ax3.tick_params(axis="x", colors="red")
        ax3.spines["top"].set_edgecolor("red")
        ax3.set_xticks(np.linspace(*x_ranges["density"], num=3))
        ax3.set_ylim(common_ylim)

    # PE curve on a twinned axis of the density track (ax3)
    if pe_col and not df[pe_col].empty:
        ax3_twiny_pe = ax3.twiny()
        ax3_twiny_pe.plot(
            df[pe_col], df["DEPT"], color="purple", linewidth=1.5, label="PE"
        )
        ax3_twiny_pe.set_xlabel("PE")
        ax3_twiny_pe.xaxis.label.set_color("purple")
        ax3_twiny_pe.set_xlim(x_ranges["pe"])
        ax3_twiny_pe.tick_params(axis="x", colors="purple")
        ax3_twiny_pe.spines["top"].set_position(("axes", 1.03))
        ax3_twiny_pe.spines["top"].set_edgecolor("purple")

    # Neutron track placed on top of density track
    if neutron_col:
        for i, (sample, (_, _, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax5.plot(
                sample[neutron_col],
                sample["DEPT"],
                color=color,
                label=f"sample_neutron_{i+1}",
                alpha=1,
                linewidth=5,
            )
            ax5.plot(df[neutron_col], df["DEPT"], color="blue", linewidth=1.0)
        ax5.set_xlabel("Neutron Porosity (dec)")
        ax5.xaxis.label.set_color("blue")
        ax5.set_xlim(x_ranges["neutron"])
        ax5.set_ylim(common_ylim)
        ax5.tick_params(axis="x", colors="blue")
        ax5.spines["top"].set_position(("axes", 1.015))
        ax5.spines["top"].set_visible(True)
        ax5.spines["top"].set_edgecolor("blue")
        ax5.set_xticks(np.linspace(*x_ranges["neutron"], num=7))
        ax5.grid(which="major", axis="x", color="lightgrey", linestyle="-", linewidth=0.5)

    # Highlight concatenated depth ranges with specified colors
    for i, (min_depth, max_depth, color, rock_type) in enumerate(depth_ranges):
        mask = (df["DEPT"] >= min_depth) & (df["DEPT"] <= max_depth)
        if gamma_col:
            ax1.fill_betweenx(
                df["DEPT"], *x_ranges["gamma"], where=mask, color=color, alpha=0.4
            )
        if deepres_col:
            ax2.fill_betweenx(
                df["DEPT"], *x_ranges["deepres"], where=mask, color=color, alpha=0.4
            )
        if density_col:
            ax3.fill_betweenx(
                df["DEPT"], *x_ranges["density"], where=mask, color=color, alpha=0.4
            )

    # Steps needed to shade
    if density_col and neutron_col:
        nphi_display = ax5.transData.transform(np.c_[df[neutron_col], df["DEPT"]])
        nphi_data = ax3.transData.inverted().transform(nphi_display)
        ax3.fill_betweenx(
            df["DEPT"],
            df[density_col],
            nphi_data[:, 0],
            where=(df[density_col] < nphi_data[:, 0]),
            color="yellow",
            alpha=0.3,
        )

    # Add a rectangle with text above the NPHI label
    rect = patches.Rectangle(
        (0, 1.05),
        1.0,
        0.005,
        transform=ax5.transAxes,
        color="yellow",
        alpha=0.3,
        clip_on=False,
    )
    ax5.add_patch(rect)
    ax5.text(
        0.6,
        1.05,
        "Light Fluid",
        transform=ax5.transAxes,
        fontsize=10,
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
    )

    # Remove y-axis tick labels for all axes except ax1
    for ax in [ax3, ax2, ax5]:
        ax.set_yticklabels([])

    # Common functions for setting up the plot
    for ax in [ax1, ax2, ax3]:
        ax.grid(which="major", color="lightgrey", linestyle="-")
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

    # List of all resistivity-related axes
    resistivity_axes = [ax2]

    # Set specific x-ticks and add gridlines for all resistivity-related axes
    #    resistivity_ticks = [0.2, 2, 20]
    #    resistivity_ticks = np.logspace(
    #        np.log10(x_ranges["deepres"][0]), np.log10(x_ranges["deepres"][1]), num=5
    #    )
    resistivity_ticks = [
        10**i
        for i in range(
            int(np.floor(np.log10(x_ranges["deepres"][0]))),
            int(np.ceil(np.log10(x_ranges["deepres"][1]))) + 1,
        )
    ]
    for ax in resistivity_axes:
        ax.set_xticks(resistivity_ticks)
        ax.set_xticklabels(resistivity_ticks)
        ax.set_xticklabels([str(tick) for tick in resistivity_ticks])  # Force decimal format
        ax.grid(
            which="major", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )

    # List of all axes including twinned axes
    all_axes = [ax1, ax2, ax3]

    # Invert the y-axis for all axes
    for ax in all_axes:
        ax.yaxis.set_minor_locator(MultipleLocator(mintick))
        ax.yaxis.set_major_locator(MultipleLocator(maxtick))
        ax.grid(
            which="minor", axis="y", color="lightgrey", linestyle="-", linewidth=0.5
        )
        ax.grid(
            which="major", axis="y", color="lightgrey", linestyle="-", linewidth=1.5
        )
        ax.tick_params(axis="y", which="minor", labelleft=False)
        ax.invert_yaxis()

    # Add an invisible axis that spans the entire figure
    full_width_ax = fig.add_axes([0, 0, 1, 1], zorder=-1)
    full_width_ax.set_xlim(0, 1)
    full_width_ax.set_ylim(mindepth, maxdepth)
    full_width_ax.axis("off")  # Hide the axis

    # Add horizontal lines for the top of each rock type
    for min_d, max_d, _, rock_type in depth_ranges:
        for ax in [ax1, ax2, ax3, ax5]:  # Loop through all axes
            ax.axhline(
                y=min_d, color="blue", linestyle="--", linewidth=0.1, zorder=10
            )  # Top
            ax.axhline(
                y=max_d, color="blue", linestyle="--", linewidth=0.1, zorder=10
            )  # Bottom

    return fig, sample_dfs



def plot_rock_labels_Int(
    df,
    mindepth,
    maxdepth,
    mnemonic_dict,
    rock_intervals,
    x_ranges,
    depth_ranges,
    mintick=50,
    maxtick=500,
):
    fig, ax = plt.subplots(figsize=(15, 30), sharey=True)
    fig.patch.set_visible(False)
    plt.axis("off")

    # Set up the plot axes
    ax1 = plt.subplot2grid((1, 5), (0, 0), rowspan=1, colspan=1)  # GR
    ax2 = plt.subplot2grid((1, 5), (0, 1), rowspan=1, colspan=1)  # RES
    ax3 = plt.subplot2grid((1, 5), (0, 2), rowspan=1, colspan=1)  # RHOB
    ax5 = (
        ax3.twiny()
    )  # Twins the y-axis for the density track with the neutron track # NEU
    ax6 = plt.subplot2grid((1, 5), (0, 3), rowspan=1, colspan=1)  # Clay volume
    ax7 = plt.subplot2grid((1, 5), (0, 4), rowspan=1, colspan=1)  # Porosity and Fluids

    # Adjust subplot spacing
    plt.subplots_adjust(
        left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.1, hspace=0.1
    )

    # Set common y-limits (Depth limits) for all subplots
    common_ylim = (mindepth, maxdepth)

    # Find columns for each log type
    gamma_col = find_column(df, "gamma")
    deepres_col = find_column(df, "deepres")
    rxo_col = find_column(df, "rxo")
    density_col = "Phid_ShCorr_hc"  # find_column(df, "density")
    dtc_col = find_column(df, "dtc")
    neutron_col = "TNPH_ShCorr_hc"  # find_column(df, "neutron")
    caliper_col = find_column(df, "caliper")
    pe_col = find_column(df, "pe")
    sp_col = find_column(df, "sp")

    # Create a dictionary to store DataFrames for each sample
    sample_dfs = {}

    # Populate the dictionary with DataFrames based on depth ranges
    for i, (min_d, max_d, color, rock_type) in enumerate(depth_ranges):
        sample_name = f"sample_{i+1}"
        sample_df = df[(df["DEPT"] >= min_d) & (df["DEPT"] <= max_d)]
        sample_dfs[sample_name] = sample_df

    # Plot logs with sampled data highlighted
    if gamma_col and not df[gamma_col].empty:
        for i, (sample, (min_d, max_d, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax1.plot(
                sample[gamma_col],
                sample["DEPT"],
                color=color,
                label=f"sample_gr_{i+1}",
                alpha=0.6,
                linewidth=5,
            )
            ax1.plot(df[gamma_col], df["DEPT"], color="green", linewidth=1.0)

    ax1.set_xlabel("Gamma")
    ax1.xaxis.label.set_color("green")
    ax1.set_xlim(x_ranges["gamma"])
    ax1.set_ylabel("Depth (ft)")
    ax1.tick_params(axis="x", colors="green")
    ax1.spines["top"].set_edgecolor("green")
    ax1.title.set_color("green")
    ax1.set_xticks(np.linspace(*x_ranges["gamma"], num=4))
    ax1.set_ylim(common_ylim)

    # Twin ax1 for plotting CALIPER_inches simultaneously as GR
    if caliper_col and not df[caliper_col].empty:
        ax1_twiny = ax1.twiny()
        ax1_twiny.plot(
            df[caliper_col], df["DEPT"], color="black", label="CALI", alpha=0.3
        )
        ax1_twiny.set_xlabel("CALI")
        ax1_twiny.xaxis.label.set_color("black")
        ax1_twiny.set_xlim(x_ranges["caliper"])
        ax1_twiny.tick_params(axis="x", colors="black")
        ax1_twiny.spines["top"].set_position(("axes", 1.02001))
        ax1_twiny.spines["top"].set_edgecolor("black")

    # SP log on a twinned axis of the gamma track (ax1)
    if sp_col and not df[sp_col].empty:
        ax1_twiny_sp = ax1.twiny()
        ax1_twiny_sp.plot(
            df[sp_col], df["DEPT"], color="orange", linewidth=1.0, label="SP"
        )
        ax1_twiny_sp.set_xlabel("SP")
        ax1_twiny_sp.xaxis.label.set_color("orange")
        ax1_twiny_sp.set_xlim(x_ranges["sp"])
        ax1_twiny_sp.tick_params(axis="x", colors="orange")
        ax1_twiny_sp.spines["top"].set_position(("axes", 1.04))
        ax1_twiny_sp.spines["top"].set_edgecolor("orange")

    # Resistivity track
    if deepres_col and not df[deepres_col].empty:
        for i, (sample, (min_d, max_d, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax2.plot(
                sample[deepres_col],
                sample["DEPT"],
                color=color,
                label=f"sample_res_{i+1}",
                alpha=0.6,
                linewidth=4,
            )
            ax2.annotate(
                rock_type,
                xy=(
                    x_ranges["deepres"][0],
                    # + 0.5 * (x_ranges["deepres"][1] - x_ranges["deepres"][0]),
                    min_d,
                ),
                xytext=(1, 0),
                textcoords="offset points",
                ha="center",
                va="center",
                fontsize=18,
                color="black",
            )
            ax2.plot(df[deepres_col], df["DEPT"], color="red", linewidth=1.0)
        ax2.set_xlabel("Deep Resistivity (ohm.m)")
        ax2.set_xlim(x_ranges["deepres"])
        ax2.xaxis.label.set_color("red")
        ax2.tick_params(axis="x", colors="red")
        ax2.spines["top"].set_edgecolor("red")
        ax2.semilogx()
        ax2.set_ylim(common_ylim)
        ax2.grid(
            which="both", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )
    # Shallow resistivity
    if rxo_col and not df[rxo_col].empty:
        ax2_twiny1 = ax2.twiny()
        ax2_twiny1.set_xlabel("Shallow Resistivity (ohm.m)")
        ax2_twiny1.plot(df[rxo_col], df["DEPT"], color="green", linewidth=1.0)
        ax2_twiny1.set_xlim(x_ranges["shalres"])
        ax2_twiny1.xaxis.label.set_color("green")
        ax2_twiny1.tick_params(axis="x", colors="green")
        ax2_twiny1.spines["top"].set_position(("axes", 1.02001))
        ax2_twiny1.spines["top"].set_edgecolor("green")
        ax2_twiny1.semilogx()
        ax2_twiny1.set_ylim(common_ylim)

    # Density track
    if density_col and not df[density_col].empty:

        ax3.plot(df["Phid_ShCorr_hc"], df["DEPT"], color="red", linewidth=1.0)
        ax3.set_xlabel("Corrected Density Porosity (dec )")
        #        ax3.set_xlim(x_ranges["density"])
        ax3.set_xlim(x_ranges["neutron"])

        ax3.xaxis.label.set_color("red")
        ax3.tick_params(axis="x", colors="red")
        ax3.spines["top"].set_edgecolor("red")
        ax3.set_xticks(np.linspace(*x_ranges["neutron"], num=7))
        # ax3.set_xticks(np.linspace(*x_ranges["density"], num=3))
        ax3.set_ylim(common_ylim)

    # PE curve on a twinned axis of the density track (ax3)
    if pe_col and not df[pe_col].empty:
        ax3_twiny_pe = ax3.twiny()
        ax3_twiny_pe.plot(
            df[pe_col], df["DEPT"], color="purple", linewidth=1.5, label="PE"
        )
        ax3_twiny_pe.set_xlabel("PE")
        ax3_twiny_pe.xaxis.label.set_color("purple")
        ax3_twiny_pe.set_xlim(x_ranges["pe"])
        ax3_twiny_pe.tick_params(axis="x", colors="purple")
        ax3_twiny_pe.spines["top"].set_position(("axes", 1.03))
        ax3_twiny_pe.spines["top"].set_edgecolor("purple")

    # Neutron track placed on top of density track
    if neutron_col:
        ax5.plot(df["TNPH_ShCorr_hc"], df["DEPT"], color="blue", linewidth=1.0)
        ax5.set_xlabel("Corrected Neutron Porosity (dec)")
        ax5.xaxis.label.set_color("blue")
        ax5.set_xlim(x_ranges["neutron"])
        ax5.set_ylim(common_ylim)
        ax5.tick_params(axis="x", colors="blue")
        ax5.spines["top"].set_position(("axes", 1.015))
        ax5.spines["top"].set_visible(True)
        ax5.spines["top"].set_edgecolor("blue")
        ax5.set_xticks(np.linspace(*x_ranges["neutron"], num=7))

    # Highlight concatenated depth ranges with specified colors
    for i, (min_depth, max_depth, color, rock_type) in enumerate(depth_ranges):
        mask = (df["DEPT"] >= min_depth) & (df["DEPT"] <= max_depth)
        if gamma_col:
            ax1.fill_betweenx(
                df["DEPT"], *x_ranges["gamma"], where=mask, color=color, alpha=0.4
            )
        if deepres_col:
            ax2.fill_betweenx(
                df["DEPT"], *x_ranges["deepres"], where=mask, color=color, alpha=0.4
            )
        if density_col:
            ax3.fill_betweenx(
                df["DEPT"], *x_ranges["density"], where=mask, color=color, alpha=0.4
            )

    # Steps needed to shade between density and neutron
    if density_col and neutron_col:
        nphi_display = ax5.transData.transform(np.c_[df[neutron_col], df["DEPT"]])
        nphi_data = ax3.transData.inverted().transform(nphi_display)
        ax3.fill_betweenx(
            df["DEPT"],
            df["Phid_ShCorr_hc"],
            nphi_data[:, 0],
            where=(df[density_col] > nphi_data[:, 0]),  # Changed from < to >
            color="yellow",
            alpha=0.3,
        )
    # Add a rectangle with text above the NPHI label
    rect = patches.Rectangle(
        (0, 1.05),
        1.0,
        0.02,
        transform=ax5.transAxes,
        color="yellow",
        alpha=0.3,
        clip_on=False,
    )
    ax5.add_patch(rect)
    ax5.text(
        0.5,
        1.06,
        "Light Fluid",
        transform=ax5.transAxes,
        fontsize=10,
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
    )

    # Porosity track
    if not df["Phis_hc"].empty:
        ax6.plot(df["Phis_hc"], df["DEPT"], color="red", linewidth=1.0)
        ax6.set_xlabel("Phi_SS (dec)")
        ax6.set_xlim(x_ranges["neutron"])
        ax6.xaxis.label.set_color("red")
        ax6.tick_params(axis="x", colors="red")

        # Set spine position for Phi_SS (at top)
        ax6.spines["top"].set_position(("axes", 1.0))
        ax6.spines["top"].set_visible(True)
        ax6.spines["top"].set_edgecolor("red")

        # Force ticks and labels to top
        ax6.xaxis.set_ticks_position("top")
        ax6.xaxis.set_label_position("top")

        ax6.set_xticks(np.linspace(*x_ranges["neutron"], num=7))
        ax6.set_ylim(common_ylim)

        # Invert y-axis after setting tick positions
        # ax6.invert_yaxis()

    # Position HCPV spine slightly above
    if not df["HCPV"].empty:
        ax6_twiny1 = ax6.twiny()
        ax6_twiny1.set_xlabel("HCPV (dec)")
        ax6_twiny1.plot(df["HCPV"], df["DEPT"], color="green", linewidth=1.0)
        ax6_twiny1.set_xlim(x_ranges["neutron"])
        ax6_twiny1.xaxis.label.set_color("green")
        ax6_twiny1.tick_params(axis="x", colors="green")
        ax6_twiny1.set_xticks(np.linspace(*x_ranges["neutron"], num=7))

        ax6_twiny1.spines["top"].set_position(("axes", 1.02))  # Slightly above
        ax6_twiny1.spines["top"].set_edgecolor("green")
        # ax6_twiny1.semilogx()
        ax6_twiny1.set_ylim(common_ylim)

    # Steps needed to shade between Phi_SS and HCPV
    if not df["Phis_hc"].empty and not df["HCPV"].empty:
        hcpv_display = ax6_twiny1.transData.transform(np.c_[df["HCPV"], df["DEPT"]])
        hcpv_data = ax6.transData.inverted().transform(hcpv_display)
        ax6.fill_betweenx(
            df["DEPT"],
            df["Phis_hc"],
            hcpv_data[:, 0],
            where=(df["Phis_hc"] > hcpv_data[:, 0]),  # Change this condition
            color="lightblue",
            alpha=0.3,
        )

    # Sonic log on ax7
    if dtc_col and not df[dtc_col].empty:
        ax7.plot(df[dtc_col], df["DEPT"], color="purple", linewidth=1.0)
        ax7.set_xlabel("Sonic (µs/ft)")
        ax7.xaxis.label.set_color("purple")
        ax7.set_xlim(x_ranges["dtc"])  # Define the x-range for the sonic log
        ax7.tick_params(axis="x", colors="purple")
        ax7.xaxis.set_ticks_position("top")
        ax7.xaxis.set_label_position("top")
        ax7.set_xticks(np.linspace(*x_ranges["dtc"], num=5))
        ax7.set_xticklabels(
            [f"{int(tick)}" for tick in ax7.get_xticks()]
        )  # Format as integers

        ax7.set_ylim(common_ylim)

    # Remove y-axis tick labels for all axes except ax1
    for ax in [ax3, ax2, ax5, ax6, ax7]:
        ax.set_yticklabels([])

    # Common functions for setting up the plot
    # X gridlines
    for ax in [ax1, ax2, ax3, ax6, ax7]:
        ax.grid(which="major", color="lightgrey", linestyle="-")
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

    # List of all resistivity-related axes
    resistivity_axes = [ax2, ax2_twiny1]

    resistivity_ticks = [
        10**i
        for i in range(
            int(np.floor(np.log10(x_ranges["deepres"][0]))),
            int(np.ceil(np.log10(x_ranges["deepres"][1]))) + 1,
        )
    ]
    for ax in resistivity_axes:
        ax.set_xticks(resistivity_ticks)
        ax.set_xticklabels(resistivity_ticks)
        ax.grid(
            which="major", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )

    # List of all axes including twinned axes
    all_axes = [ax1, ax2, ax3, ax6, ax7]

    # Invert the y-axis for all axes
    for ax in all_axes:
        ax.yaxis.set_minor_locator(MultipleLocator(mintick))
        ax.yaxis.set_major_locator(MultipleLocator(maxtick))
        ax.grid(
            which="minor", axis="y", color="lightgrey", linestyle="-", linewidth=0.5
        )
        ax.grid(
            which="major", axis="y", color="lightgrey", linestyle="-", linewidth=1.5
        )
        ax.tick_params(axis="y", which="minor", labelleft=False)
        ax.invert_yaxis()
    # Add a horizontal line at 8555 depth across all subplots
    for ax in [ax1, ax2, ax3, ax5, ax6, ax7]:
        ax.axhline(y=8555, color="black", linestyle="-", linewidth=1.0)

    # Add an invisible axis that spans the entire figure
    full_width_ax = fig.add_axes([0, 0, 1, 1], zorder=-1)
    full_width_ax.set_xlim(0, 1)
    full_width_ax.set_ylim(mindepth, maxdepth)
    full_width_ax.axis("off")  # Hide the axis

    # Add horizontal lines for the top of each rock type
    for min_d, max_d, _, rock_type in depth_ranges:
        for ax in [ax1, ax2, ax3, ax5, ax6, ax7]:  # Loop through all axes
            ax.axhline(
                y=min_d, color="blue", linestyle="--", linewidth=0.1, zorder=10
            )  # Top
            ax.axhline(
                y=max_d, color="blue", linestyle="--", linewidth=0.1, zorder=10
            )  # Bottom

    return fig, sample_dfs


# To define dimensions of plot from input
def plot_rock_labels_auto_dim(
    df,
    mindepth,
    maxdepth,
    mnemonic_dict,
    rock_intervals,
    x_ranges,
    depth_ranges,
    mintick=50,
    maxtick=500,
    dim1=15,dim2=20
):
    fig, ax = plt.subplots(figsize=(dim1, dim2), sharey=True)
    fig.patch.set_visible(False)
    plt.axis("off")

    # Set up the plot axes

    ax1 = plt.subplot2grid((1, 2), (0, 0), rowspan=1, colspan=1)  # GR
    ax2 = plt.subplot2grid((1, 2), (0, 1), rowspan=1, colspan=1)  # RES

    # ax1 = plt.subplot2grid((1, 5), (0, 0), rowspan=1, colspan=1)  # GR
    # ax2 = plt.subplot2grid((1, 5), (0, 1), rowspan=1, colspan=1)  # RES
    # ax3 = plt.subplot2grid((1, 5), (0, 2), rowspan=1, colspan=1)  # RHOB
    # ax5 = (
    #     ax3.twiny()
    # )  # Twins the y-axis for the density track with the neutron track # NEU

    # Adjust subplot spacing
    plt.subplots_adjust(
        left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.3, hspace=0.1
    )

    # Set common y-limits (Depth limits) for all subplots
    common_ylim = (mindepth, maxdepth)

    # Find columns for each log type
    gamma_col = find_column(df, "gamma")
    deepres_col = find_column(df, "deepres")
    rxo_col = find_column(df, "rxo")
    density_col = find_column(df, "density")
    dtc_col = find_column(df, "dtc")
    neutron_col = find_column(df, "neutron")
    caliper_col = find_column(df, "caliper")
    pe_col = find_column(df, "pe")
    sp_col = find_column(df, "sp")

    # Create a dictionary to store DataFrames for each sample
    sample_dfs = {}

    # Populate the dictionary with DataFrames based on depth ranges
    for i, (min_d, max_d, color, rock_type) in enumerate(depth_ranges):
        sample_name = f"sample_{i+1}"
        sample_df = df[(df["DEPT"] >= min_d) & (df["DEPT"] <= max_d)]
        sample_dfs[sample_name] = sample_df

    # Plot logs with sampled data highlighted
    if gamma_col and not df[gamma_col].empty:
        for i, (sample, (min_d, max_d, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax1.plot(
                sample[gamma_col],
                sample["DEPT"],
                color=color,
                label=f"sample_gr_{i+1}",
                alpha=0.6,
                linewidth=5,
            )
            ax1.plot(df[gamma_col], df["DEPT"], color="green", linewidth=1.0)


    ax1.set_xlabel("Gamma")
    ax1.xaxis.label.set_color("green")
    ax1.set_xlim(x_ranges["gamma"])
    ax1.set_ylabel("Depth (ft)")
    ax1.tick_params(axis="x", colors="green")
    ax1.spines["top"].set_edgecolor("green")
    ax1.title.set_color("green")
    ax1.set_xticks(np.linspace(*x_ranges["gamma"], num=4))
    ax1.set_ylim(common_ylim)

    # Twin ax1 for plotting CALIPER_inches simultaneously as GR
    if caliper_col and not df[caliper_col].empty:
        ax1_twiny = ax1.twiny()
        ax1_twiny.plot(
            df[caliper_col], df["DEPT"], color="black", label="CALI", alpha=0.3
        )
        ax1_twiny.set_xlabel("CALI")
        ax1_twiny.xaxis.label.set_color("black")
        ax1_twiny.set_xlim(x_ranges["caliper"])
        ax1_twiny.tick_params(axis="x", colors="black")
        ax1_twiny.spines["top"].set_position(("axes", 1.02001))
        ax1_twiny.spines["top"].set_edgecolor("black")

    # SP log on a twinned axis of the gamma track (ax1)
    if sp_col and not df[sp_col].empty:
        ax1_twiny_sp = ax1.twiny()
        ax1_twiny_sp.plot(
            df[sp_col], df["DEPT"], color="orange", linewidth=1.0, label="SP"
        )
        ax1_twiny_sp.set_xlabel("SP")
        ax1_twiny_sp.xaxis.label.set_color("orange")
        ax1_twiny_sp.set_xlim(x_ranges["sp"])
        ax1_twiny_sp.tick_params(axis="x", colors="orange")
        ax1_twiny_sp.spines["top"].set_position(("axes", 1.04))
        ax1_twiny_sp.spines["top"].set_edgecolor("orange")

    # Resistivity track
    if deepres_col and not df[deepres_col].empty:
        for i, (sample, (min_d, max_d, color, rock_type)) in enumerate(
            zip(sample_dfs.values(), depth_ranges)
        ):
            ax2.plot(
                sample[deepres_col],
                sample["DEPT"],
                color=color,
                label=f"sample_res_{i+1}",
                alpha=0.6,
                linewidth=4,
            )
            ax2.annotate(
                rock_type,
                xy=(
                    x_ranges["deepres"][0],
                    # + 0.5 * (x_ranges["deepres"][1] - x_ranges["deepres"][0]),
                    min_d,
                ),
                xytext=(1, 0),
                #            xy=(
                #                x_ranges["deepres"][1],
                #                (min_d + max_d) / 2,
                #            ),  # Middle of resistivity track
                #            xytext=(5, 0),
                textcoords="offset points",
                ha="center",
                va="center",
                fontsize=28,
                color="black",
            )
            ax2.plot(df[deepres_col], df["DEPT"], color="red", linewidth=1.0)
        ax2.set_xlabel("Deep Resistivity (ohm.m)")
        ax2.set_xlim(x_ranges["deepres"])
        ax2.xaxis.label.set_color("red")
        ax2.tick_params(axis="x", colors="red")
        ax2.spines["top"].set_edgecolor("red")
        ax2.semilogx()
        ax2.set_ylim(common_ylim)
        ax2.grid(
            which="both", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )
    # Shallow resistivity
    if rxo_col and not df[rxo_col].empty:
        ax2_twiny1 = ax2.twiny()
        ax2_twiny1.set_xlabel("Shallow Resistivity (ohm.m)")
        ax2_twiny1.plot(df[rxo_col], df["DEPT"], color="green", linewidth=1.0)
        ax2_twiny1.set_xlim(x_ranges["shalres"])
        ax2_twiny1.xaxis.label.set_color("green")
        ax2_twiny1.tick_params(axis="x", colors="green")
        ax2_twiny1.spines["top"].set_position(("axes", 1.06001))
        ax2_twiny1.spines["top"].set_edgecolor("green")
        ax2_twiny1.semilogx()
        ax2_twiny1.set_ylim(common_ylim)

   
    # Highlight concatenated depth ranges with specified colors
    for i, (min_depth, max_depth, color, rock_type) in enumerate(depth_ranges):
        mask = (df["DEPT"] >= min_depth) & (df["DEPT"] <= max_depth)
        if gamma_col:
            ax1.fill_betweenx(
                df["DEPT"], *x_ranges["gamma"], where=mask, color=color, alpha=0.4
            )
        if deepres_col:
            ax2.fill_betweenx(
                df["DEPT"], *x_ranges["deepres"], where=mask, color=color, alpha=0.4
            )
    

    # Remove y-axis tick labels for all axes except ax1
    for ax in [ax2]:
        ax.set_yticklabels([])

    # Common functions for setting up the plot
    for ax in [ax1, ax2]:#, ax3]:
        ax.grid(which="major", color="lightgrey", linestyle="-")
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

    # List of all resistivity-related axes
    resistivity_axes = [ax2]

    resistivity_ticks = [
        10**i
        for i in range(
            int(np.floor(np.log10(x_ranges["deepres"][0]))),
            int(np.ceil(np.log10(x_ranges["deepres"][1]))) + 1,
        )
    ]
    for ax in resistivity_axes:
        ax.set_xticks(resistivity_ticks)
        ax.set_xticklabels(resistivity_ticks)
        ax.grid(
            which="major", axis="x", color="lightgrey", linestyle="-", linewidth=0.5
        )

    # List of all axes including twinned axes
    all_axes = [ax1, ax2]

    # Invert the y-axis for all axes
    for ax in all_axes:
        ax.yaxis.set_minor_locator(MultipleLocator(mintick))
        ax.yaxis.set_major_locator(MultipleLocator(maxtick))
        ax.grid(
            which="minor", axis="y", color="lightgrey", linestyle="-", linewidth=0.5
        )
        ax.grid(
            which="major", axis="y", color="lightgrey", linestyle="-", linewidth=1.5
        )
        ax.tick_params(axis="y", which="minor", labelleft=False)
        ax.invert_yaxis()

    # Add an invisible axis that spans the entire figure
    full_width_ax = fig.add_axes([0, 0, 1, 1], zorder=-1)
    full_width_ax.set_xlim(0, 1)
    full_width_ax.set_ylim(mindepth, maxdepth)
    full_width_ax.axis("off")  # Hide the axis

    # Add horizontal lines for the top of each rock type
    for min_d, max_d, _, rock_type in depth_ranges:
        for ax in [ax1, ax2]:#, ax3, ax5]:  # Loop through all axes
            ax.axhline(
                y=min_d, color="blue", linestyle="--", linewidth=0.1, zorder=10
            )  # Top
            ax.axhline(
                y=max_d, color="blue", linestyle="--", linewidth=0.1, zorder=10
            )  # Bottom

    return fig, sample_dfs


# To plot histograms of matched zones
def plot_matching_zones_histograms_dynamic(df1, filtered_ranges1, df2, filtered_ranges2,
                                         figsize=(12, 10), bins=30, alpha1=0.7, alpha2=0.5,
                                         use_ranks=False):
    """
    Create overlapping histograms for zones in a dynamic grid with 2 columns per row.
    Only matches zones with the same size factor.
    
    Parameters:
    df1: First DataFrame with DEPT and GR columns
    filtered_ranges1: List of tuples for df1 (min_depth, max_depth, color, zone_name)
    df2: Second DataFrame with DEPT and GR columns
    filtered_ranges2: List of tuples for df2 (min_depth, max_depth, color, zone_name)
    figsize: Figure size tuple
    bins: Number of bins for histograms
    alpha1, alpha2: Transparency values for the two datasets
    use_ranks: Boolean, if True applies rank transformation to GR values
    
    Returns:
    fig: matplotlib figure object
    axes: array of subplot axes
    filtered_data1, filtered_data2: dictionaries of filtered dataframes for matching zones
    """
    
    def extract_zone_info(zone_name):
        """
        Extract zone type and size factor from zone name.
        E.g., 'LST_8_0.5_0.5' -> ('LST_8', '0.5')
        E.g., 'LST_8_0.5' -> ('LST_8', '0.5')
        E.g., 'LST_4_1.0_2.0' -> ('LST_4', '2.0')  # Uses the last factor
        """
        parts = zone_name.split('_')
        if len(parts) >= 3:
            zone_type = f"{parts[0]}_{parts[1]}"  # LST_number
            if len(parts) == 4:  # Format: LST_8_0.5_0.5
                size_factor = parts[3]  # Use the last factor
            else:  # Format: LST_8_0.5
                size_factor = parts[2]  # Use the third part
            return zone_type, size_factor
        return zone_name, "unknown"

    def create_match_key(zone_name):
        """
        Create a matching key based on zone type and size factor.
        """
        zone_type, size_factor = extract_zone_info(zone_name)
        return f"{zone_type}_{size_factor}"

    # Create dictionaries with match keys
    ranges1_dict = {}
    ranges2_dict = {}

    # Process dataset 1 ranges
    for min_d, max_d, color, zone_name in filtered_ranges1:
        match_key = create_match_key(zone_name)
        ranges1_dict[match_key] = (min_d, max_d, color, zone_name)

    # Process dataset 2 ranges
    for min_d, max_d, color, zone_name in filtered_ranges2:
        match_key = create_match_key(zone_name)
        ranges2_dict[match_key] = (min_d, max_d, color, zone_name)

    # Find zones that match by type and size factor
    common_zones = sorted(list(set(ranges1_dict.keys()) & set(ranges2_dict.keys())))
    
    if not common_zones:
        print("No matching zone names found with same size factors")
        print(f"Dataset 1 zone keys: {list(ranges1_dict.keys())}")
        print(f"Dataset 2 zone keys: {list(ranges2_dict.keys())}")
        return None, None, {}, {}

    print(f"Matching zones found: {common_zones}")
    print(f"Total number of zones: {len(common_zones)}")
    print(f"Ranks: {'Enabled' if use_ranks else 'Disabled'}")

    # Calculate dynamic grid size - 2 columns per row
    n_zones = len(common_zones)
    n_cols = 2
    n_rows = math.ceil(n_zones / n_cols)
    
    print(f"Creating {n_rows}x{n_cols} grid for {n_zones} zones")

    # Adjust figure size based on number of rows
    dynamic_figsize = (figsize[0], figsize[1] * (n_rows / 2))  # Scale height with rows
    
    # Create dynamic subplot grid
    fig, axes = plt.subplots(n_rows, n_cols, figsize=dynamic_figsize)
    
    # Handle case where we have only one row or one subplot
    if n_rows == 1 and n_cols == 1:
        axes = np.array([axes])  # Make it iterable
    elif n_rows == 1:
        axes = axes.reshape(1, -1)  # Ensure 2D array
    elif n_cols == 1:
        axes = axes.reshape(-1, 1)  # Ensure 2D array

    # Dictionaries to store filtered data
    filtered_data1 = {}
    filtered_data2 = {}

    # Process each matching zone
    for i, match_key in enumerate(common_zones):
        # Calculate row and column indices
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col]

        # Get range information for both datasets
        min_d1, max_d1, color1, original_name1 = ranges1_dict[match_key]
        min_d2, max_d2, color2, original_name2 = ranges2_dict[match_key]

        # Filter data from first dataset
        mask1 = (df1['DEPT'] >= min_d1) & (df1['DEPT'] <= max_d1)
        filtered_df1 = df1[mask1].copy()
        filtered_data1[match_key] = filtered_df1

        # Filter data from second dataset
        mask2 = (df2['DEPT'] >= min_d2) & (df2['DEPT'] <= max_d2)
        filtered_df2 = df2[mask2].copy()
        filtered_data2[match_key] = filtered_df2

        # Extract GR values for this zone only
        gr_values1_raw = pd.Series(dtype=float)
        gr_values2_raw = pd.Series(dtype=float)
        
        if not filtered_df1.empty and 'GR' in filtered_df1.columns:
            gr_values1_raw = filtered_df1['GR'].dropna()
        if not filtered_df2.empty and 'GR' in filtered_df2.columns:
            gr_values2_raw = filtered_df2['GR'].dropna()

        # Apply transformation based on option
        if use_ranks:
            # Apply rank transformation only (no normalization)
            gr_values1_plot = pd.Series(rankdata(gr_values1_raw, method='average')) if len(gr_values1_raw) > 0 else pd.Series(dtype=float)
            gr_values2_plot = pd.Series(rankdata(gr_values2_raw, method='average')) if len(gr_values2_raw) > 0 else pd.Series(dtype=float)
            
            # Determine bin range for rank data
            all_ranks = pd.concat([gr_values1_plot, gr_values2_plot], ignore_index=True)
            if len(all_ranks) > 0:
                bin_edges = np.linspace(all_ranks.min(), all_ranks.max(), bins + 1)
            else:
                bin_edges = bins
            xlabel = 'GR Ranks'
            title_suffix = ' (Ranked)'
        else:
            # Use raw GR values
            gr_values1_plot = gr_values1_raw
            gr_values2_plot = gr_values2_raw
            
            # Determine common bin range for both datasets
            all_values = pd.concat([gr_values1_raw, gr_values2_raw], ignore_index=True)
            if len(all_values) > 0:
                bin_range = (all_values.min(), all_values.max())
                bin_edges = np.linspace(bin_range[0], bin_range[1], bins + 1)
            else:
                bin_edges = bins
            xlabel = 'Gamma Ray (API)'
            title_suffix = ''

        # Plot histograms
        has_data = False
        if len(gr_values1_plot) > 0:
            ax.hist(gr_values1_plot, bins=bin_edges, alpha=alpha1, color='blue',
                   label=f'Original Pattern', edgecolor='darkblue', linewidth=0.5)
            has_data = True
            
        if len(gr_values2_plot) > 0:
            ax.hist(gr_values2_plot, bins=bin_edges, alpha=alpha2, color='red',
                   label=f'Offset Pattern', edgecolor='darkred', linewidth=0.5)
            has_data = True

        # Add statistics text box
        if has_data:
            stats_text = ""
            if len(gr_values1_plot) > 0:
                stats_text += f"Original ({original_name1}):\n"
                if use_ranks:
                    stats_text += f"  Raw GR: μ={gr_values1_raw.mean():.1f}, σ={gr_values1_raw.std():.1f}\n"
                    stats_text += f"  Ranks: μ={gr_values1_plot.mean():.1f}, σ={gr_values1_plot.std():.1f}\n"
                else:
                    stats_text += f"  GR: μ={gr_values1_raw.mean():.1f}, σ={gr_values1_raw.std():.1f}\n"
                    
            if len(gr_values2_plot) > 0:
                stats_text += f"Offset well ({original_name2}):\n"
                if use_ranks:
                    stats_text += f"  Raw GR: μ={gr_values2_raw.mean():.1f}, σ={gr_values2_raw.std():.1f}\n"
                    stats_text += f"  Ranks: μ={gr_values2_plot.mean():.1f}, σ={gr_values2_plot.std():.1f}"
                else:
                    stats_text += f"  GR: μ={gr_values2_raw.mean():.1f}, σ={gr_values2_raw.std():.1f}"
                    
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=8,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        else:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                   ha='center', va='center', fontsize=12)

        # Set labels and title
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'{match_key}{title_suffix}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Add legend if there's data
        if has_data:
            ax.legend(loc='upper right', fontsize=8)

        # Print zone information with size factor
        zone_type1, size_factor1 = extract_zone_info(original_name1)
        zone_type2, size_factor2 = extract_zone_info(original_name2)
        print(f"\n{match_key}:")
        print(f"  Original template ({original_name1}) - Factor: {size_factor1}: {min_d1:.1f}-{max_d1:.1f} ft ")
        if len(gr_values1_raw) > 0:
            print(f"    Raw GR range: {gr_values1_raw.min():.1f} - {gr_values1_raw.max():.1f}")
        print(f"  Offset well ({original_name2}) - Factor: {size_factor2}: {min_d2:.1f}-{max_d2:.1f} ft ")
        if len(gr_values2_raw) > 0:
            print(f"    Raw GR range: {gr_values2_raw.min():.1f} - {gr_values2_raw.max():.1f}")

    # Hide unused subplots if the last row is not completely filled
    total_subplots = n_rows * n_cols
    for j in range(n_zones, total_subplots):
        row = j // n_cols
        col = j % n_cols
        axes[row, col].set_visible(False)

    # Add overall title based on transformation option
    if use_ranks:
        main_title = 'Same Size Factor Ranked GR Histograms'
    else:
        main_title = 'Same Size Factor GR Histograms Comparison'
        
    fig.suptitle(main_title, fontsize=14, fontweight='bold', y=0.95)

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)

    return fig, axes, filtered_data1, filtered_data2

## Example usage with the updated function
#fig1, axes1, data1_raw, data2_raw = plot_matching_zones_histograms_dynamic(
#    df2, filtered_ranges2, df, filtered_ranges,
#    figsize=(12, 10), bins=25, use_ranks=False
#)
#plt.show()
#
