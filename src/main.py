#!/usr/bin/env python
# -*- coding: utf-8 -*-
# raster_analyzer.py

"""Main Program Execution File to Calculate Betweenness Centrality"""


from betweenness_centrality.city_analyzer import CityAnalyzer
from betweenness_centrality.raster_analyzer import RasterAnalyzer
import betweenness_centrality.file_handler as file_handler


def main():
    """
    Main function to process command line arguments and execute the specified analysis.
    """

    city, method, type, num_routes = file_handler.check_input_arguments()
    num_points = num_routes * 2
    num_points_raster = num_points * 4

    # Define raster path
    raster_path = "../data/GHS_POP_WGS84.tif"

    # Create output folders if not exist
    folder_name = "../output"
    subfolder_name = f"../output/{city}_{method}_{type}_{num_routes}"
    
    file_handler.create_output_folder(folder_name)
    file_handler.create_output_folder(subfolder_name)

    # Method geographical
    if method == "geographical":
        header = f"Geographical, route type: {type}"
        study_area = CityAnalyzer(city)
        area_poly = study_area.get_poly()
        area_points = study_area.get_points(area_poly, num_points)
        area_routes = study_area.get_routes(area_points, num_routes, type)
        centrality_gdf = study_area.get_geocentrality(area_routes)

        # Plot and save Centrality as image and geopackage
        file_handler.plot_centrality(centrality_gdf, header, f"{subfolder_name}/{city}_{method}_{type}_{num_routes}.png")
        file_handler.gdf_to_gpkg(centrality_gdf, f"{subfolder_name}/{city}_{method}_{type}_{num_routes}.gpkg")

    # Method geographicalPop
    elif method == "geographicalPop":
        header = f"GeographicalPop, route type: {type}"
        study_area = CityAnalyzer(city)
        raster = RasterAnalyzer(raster_path)
        raster.open()
        area_poly = study_area.get_poly()
        area_points = study_area.get_points(area_poly, num_points_raster)
        raster_points = raster.get_point_values(area_points)
        raster_points_weighted = raster.get_weighted_points(raster_points, num_points)
        area_routes = study_area.get_routes(raster_points_weighted, num_routes, type)
        centrality_gdf = study_area.get_geocentrality(area_routes)

        # Plot and save Centrality as image and geopackage
        file_handler.plot_centrality(centrality_gdf, header, f"{subfolder_name}/{city}_{method}_{type}_{num_routes}.png")
        file_handler.gdf_to_gpkg(centrality_gdf, f"{subfolder_name}/{city}_{method}_{type}_{num_routes}.gpkg")

    # Method networkx
    elif method == "networkx":
        header = f"NetworkX, route type: {type}"
        study_area = CityAnalyzer(city)
        centrality_gdf = study_area.get_netcentrality(type)

        # Plot and save Centrality as image and geopackage
        file_handler.plot_centrality(centrality_gdf, header, f"{subfolder_name}/{city}_{method}_{type}_{num_routes}.png")
        file_handler.gdf_to_gpkg(centrality_gdf, f"{subfolder_name}/{city}_{method}_{type}_{num_routes}.gpkg")

    else:
        print("Wrong method selected.")


if __name__ == "__main__":
    main()