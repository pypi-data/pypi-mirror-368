import signal_petrophysics.utils.mnemonics as mnm
from signal_petrophysics.utils.mnemonics import (
    gamma_names,
    sp_names,
    caliper_names,
    deepres_names,
    rxo_names,
    density_names,
    density_correction_names,
    neutron_names,
    dtc_names,
    dts_names,
    pe_names,
)
import os
import pathlib
import pandas as pd
import lasio
from os.path import join
from sys import stdout




# Function that create the mnemonic dictionary
def create_mnemonic_dict(
    gamma_names,
    sp_names,
    caliper_names,
    deepres_names,
    rxo_names,
    density_names,
    density_correction_names,
    neutron_names,
    dtc_names,
    dts_names,
    pe_names,
):
    """
    Function that create the mnemonic dictionary with the mnemonics per log type in the utils module
    """

    mnemonic_dict = {
        "gamma": gamma_names,
        "sp": sp_names,
        "caliper": caliper_names,
        "deepres": deepres_names,
        "rxo": rxo_names,
        "density": density_names,
        "density_correction": density_correction_names,
        "neutron": neutron_names,
        "dtc": dtc_names,
        "dts": dts_names,
        "pe": pe_names,
    }
    return mnemonic_dict




# Function that reads in and parses the las files in a directory with them already classified and renames GR curves to "GR"
def field_las_read(dir):
    well_logs_by_folder = {}
    directories = [dir]

    for current_dir in directories[:]:  # Iterate over a copy of the list
        items = os.listdir(current_dir)
        for item in items:
            item_path = join(current_dir, item)
            if os.path.isdir(item_path):
                directories.append(item_path)  # Add new directories to the list
                subfolder_name = os.path.basename(item_path)
                well_logs_by_folder[subfolder_name] = {}
                for file_name in os.listdir(item_path):
                    if file_name.endswith(".las"):
                        file_path = os.path.join(item_path, file_name)
                        try:
                            las_data = lasio.read(file_path)
                            df = las_data.df()
                            df.index = df.index.astype(float)
                            df.dropna(inplace=True)

                            # Extract well name from the header
                            well_name = las_data.well.WELL.value.strip()
                            print(f"Processing well: {well_name}")

                            for curve in las_data.curves:
                                mnemonic_lower = curve.mnemonic.lower()
                                if mnemonic_lower in gamma_names:
                                    df.rename(
                                        columns={curve.mnemonic: "GR"}, inplace=True
                                    )
                                    break
                            well_logs_by_folder[subfolder_name][well_name] = df
                        except lasio.exceptions.LASHeaderError:
                            print(f"Warning: {file_name} needs revision")
                        except Exception as e:
                            print(f"Error processing {file_name}: {str(e)}")
    return well_logs_by_folder

# Function that reads in and parses the las files of offset wells without dropping nan values rows
def field_las_read_offset(dir):
    well_logs_by_folder = {}
    directories = [dir]

    for current_dir in directories[:]:  # Iterate over a copy of the list
        items = os.listdir(current_dir)
        for item in items:
            item_path = join(current_dir, item)
            if os.path.isdir(item_path):
                directories.append(item_path)  # Add new directories to the list
                subfolder_name = os.path.basename(item_path)
                well_logs_by_folder[subfolder_name] = {}
                for file_name in os.listdir(item_path):
                    if file_name.endswith(".las"):
                        file_path = os.path.join(item_path, file_name)
                        try:
                            las_data = lasio.read(file_path)
                            df = las_data.df()
                            df.index = df.index.astype(float)
                            #df.dropna(inplace=True)

                            # Extract well name from the header
                            well_name = las_data.well.WELL.value.strip()
                            print(f"Processing well: {well_name}")

                            for curve in las_data.curves:
                                mnemonic_lower = curve.mnemonic.lower()
                                if mnemonic_lower in gamma_names:
                                    df.rename(
                                        columns={curve.mnemonic: "GR"}, inplace=True
                                    )
                                    break
                            well_logs_by_folder[subfolder_name][well_name] = df
                        except lasio.exceptions.LASHeaderError:
                            print(f"Warning: {file_name} needs revision")
                        except Exception as e:
                            print(f"Error processing {file_name}: {str(e)}")
    return well_logs_by_folder

