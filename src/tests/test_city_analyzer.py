#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_city_analyzer.py

"""Unit tests for city_analyzer.py"""

import unittest
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point
import sys

sys.path.append("../betweenness_centrality")
from city_analyzer import CityAnalyzer 


# Implement a Test Class for Unit Tests
class TestCityAnalyzer(unittest.TestCase):

    def setUp(self):
        # Create a CityAnalyzer instance for testing
        self.city_analyzer = CityAnalyzer(city_name="Heidelberg, Germany")


    # Check if initial input is passed correctly
    def test_get_name(self):
        self.assertEqual(self.city_analyzer.get_name(), "Heidelberg, Germany")


    # Check if polygon is GeoDataframe and contains geometry column
    def test_get_poly(self):
        city_poly = self.city_analyzer.get_poly()
        self.assertIsInstance(city_poly, gpd.GeoDataFrame)
        self.assertTrue('geometry' in city_poly.columns)


    # Check get_points() method
    def test_get_points(self):
        city_poly = self.city_analyzer.get_poly()
        city_points = self.city_analyzer.get_points(city_poly, num_points=10)

        # Check data type
        self.assertIsInstance(city_points, gpd.GeoDataFrame)

        # Check correct number of points
        self.assertEqual(len(city_points), 10)

        # Check if points contain geometry column
        self.assertTrue("geometry" in city_points.columns)


    # Check data type of graph
    def test_get_graph(self):
        city_graph = self.city_analyzer.get_graph()
        self.assertIsInstance(city_graph, nx.MultiDiGraph)


    # Check get_routes() method
    def test_get_routes(self):
        city_poly = self.city_analyzer.get_poly()
        city_points = self.city_analyzer.get_points(city_poly, num_points=10)
        city_routes = self.city_analyzer.get_routes(city_points, num_routes=5)

        # Check for correct data type
        self.assertIsInstance(city_routes, gpd.GeoDataFrame)

        # Check for geometry column
        self.assertTrue("geometry" in city_routes.columns)

        # Check for city_routes length not possible because each route consists of more than one edge.
        # The city_routes GeoDataframe will therefore be longer than the input num_routes.
        

    # Check get_geocentrality() method
    def test_get_geocentrality(self):
        city_poly = self.city_analyzer.get_poly()
        city_points = self.city_analyzer.get_points(city_poly, num_points=10)
        city_routes = self.city_analyzer.get_routes(city_points, num_routes=5)
        geocentrality_gdf = self.city_analyzer.get_geocentrality(city_routes)

        # Check for correct data type
        self.assertIsInstance(geocentrality_gdf, gpd.GeoDataFrame)

        # Check for geometry column
        self.assertTrue("geometry" in geocentrality_gdf.columns)
    
        # Check for centrality column
        self.assertTrue("centrality" in geocentrality_gdf.columns)


    # Check get_netcentrality() method
    def test_get_netcentrality(self):
        city_netcentrality_gdf = self.city_analyzer.get_netcentrality()

        # Check for correct data type
        self.assertIsInstance(city_netcentrality_gdf, gpd.GeoDataFrame)

        # Check for geometry column
        self.assertTrue("geometry" in city_netcentrality_gdf.columns)
        
        # Check for centrality column
        self.assertTrue("centrality" in city_netcentrality_gdf.columns)


if __name__ == "__main__":
    unittest.main()