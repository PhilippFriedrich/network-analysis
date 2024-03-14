#!/usr/bin/env python
# -*- coding: utf-8 -*-
# raster_analyzer.py

"""Methods for raster handling and population implementation"""

import rasterio
from rasterio.sample import sample_gen
import geopandas as gpd


class RasterAnalyzer:
    """Raster Class Definition"""

    def __init__(self, filepath: str):
        """
        Defines a raster based on filepath
        :param filepath: Path to raster file
        """
        assert isinstance(filepath, str), "filepath must be of type str."

        self.filepath = filepath
        self.dataset = None


    def open(self):
        """
        Opens raster from source
        :return: rasterio raster file
        """

        self.dataset = rasterio.open(self.filepath)
        return self.dataset
    

    def clip_to_polygon(self, poly: gpd.GeoDataFrame, outfilepath: str):
        """
        Clips raster to geopandas polygon
        :param city_poly: Polygon to mask the raster with
        :return: Clipped raster
        """

        try:
            clipped_raster, transform = rasterio.mask(self.dataset, poly.geometry, crop=True)

            # Get metadata from the original raster
            meta = self.dataset.meta.copy()
            meta.update({
                "driver": "GTiff",
                "height": clipped_raster.shape[1],
                "width": clipped_raster.shape[2],
                "transform": transform
            })

            # Write the clipped raster to a new GeoTIFF file
            with rasterio.open(outfilepath, "w", **meta) as dest:
                dest.write(clipped_raster)
            
            # Close the raster datasets
            dest.close()

            # Open the clipped raster
            clipped_raster = rasterio.open(outfilepath)

            return clipped_raster
        
        except Exception as e:
            print(f"Error clipping the raster: {str(e)}")


    # Write method to sample raster values at certain point coordinates
    def get_point_values(self, sample_points: gpd.GeoDataFrame):
        """
        Samples random points on raster 
        :param raster_points: Point coordinates as geodataframe to sample raster values
        :return: Geodataframe containing the sampled points
        """

        print("Starting to sample point values..")

        # Sample raster at given point coordinates
        sampled_values = list(sample_gen(self.dataset, zip(sample_points.geometry.x, sample_points.geometry.y)))

        # Add the sampled values to the GeoDataFrame
        sample_points["raster_value"] = [val[0] for val in sampled_values]
        
        # Remove points outside of built up area
        sample_points = sample_points[sample_points["raster_value"] > 0]

        print("Done. Point values sampled.")

        return sample_points

    
    # Write method that selects points weighted by raster values
    def get_weighted_points(self, points_with_values: gpd.GeoDataFrame, num_points: int = 1000):
        """
        Selected points based on previously extracted raster values
        :param points_with_values: Geodataframe containing the points with the raster values
        :param num_points: Number of points to select (default=10000)
        :return: Geodataframe of selected points
        """

        print("Starting to choose random points weighted with point values..")

        # Extract weights from the "value" column
        weights = points_with_values["raster_value"] / points_with_values["raster_value"].sum()

        selected_points = points_with_values.sample(n=num_points, weights=weights, replace=True, random_state=42)

        print("Done. Weighted points selected.")

        return selected_points







