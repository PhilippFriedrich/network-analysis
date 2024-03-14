#!/usr/bin/env python
# -*- coding: utf-8 -*-
# file_handler.py

"""Functions for Geodataframe handling"""

import geopandas as gpd
import matplotlib.pyplot as plt
import os
import sys


# Function to create new output folder
def create_output_folder(folder_name: str):
    """
    Creates a new output folder if it doesn't exist
    :param folder_name: Name of the folder that shall be created
    """
    
    # Create a new folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    else:
        print(f"Folder '{folder_name}' already exists.")


# Function to check input arguments
def check_input_arguments():
    """
    Checks if provided command-line arguments are valid
    """

    # Ensure that the correct number of command-line arguments are provided
    if len(sys.argv) != 5:
        print("Usage: python script.py arg1 arg2 arg3 arg4")
        print("Please provide four arguments.")
        sys.exit(1)  # Exit with a non-zero status code to indicate an error

    # Extract command-line arguments
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]
    arg4 = sys.argv[4]

    def is_integer(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    if not isinstance(arg1, str):
        print("Error. arg1 must be of type string.")
        sys.exit(1)

    elif not (isinstance(arg2, str) and arg2 in ["geographical", "geographicalPop", "networkx"]):
        print("Error. arg2 must be of type string and in [geographical, geographicalPop, networkx]")
        sys.exit(1)

    elif not (isinstance(arg3, str) and arg3 in ["length", "travel_time"]):
        print("Error. arg3 must be of type string and in [length, travel_time]")
        sys.exit(1)

    elif not is_integer(arg4):
        print("Error. arg4 must be a number.")
        sys.exit(1)

    else:
        print("System Arguments correct. Start processing..")

    return arg1, arg2, arg3, int(arg4)


# Function to plot centrality geodataframe
def plot_centrality(centrality_gdf: gpd.GeoDataFrame, title: str, filepath: str):
    """
    Plots geodataframe, visualizes betweenness centrality and saves imag as PNG
    :param centrality_gdf: Geodataframe containing centrality values
    :param method: Method used for analysis
    :param filepath: Path to store the file
    """

    # Create plot
    centrality_gdf.plot(column="centrality", legend=True, cmap="magma_r", figsize=(15, 10))
    plt.title(title)

    # Safe plot as PNG
    png_filename_result = filepath
    plt.savefig(png_filename_result, format="png")
    
    # Show plot
    plt.show()


# Function to save geodataframe as geopackage 
def gdf_to_gpkg(centrality_gdf: gpd.GeoDataFrame, filepath: str):
    """
    Stores geodataframe as geopackage
    :param centrality_gdf: Geodataframe containing centrality values
    :param filepath: Path to store the file
    """

    # Define filepath
    geopackage_filename_result = filepath

    # Store Geodataframe as GeoPackage
    centrality_gdf.to_file(geopackage_filename_result, driver="GPKG")


