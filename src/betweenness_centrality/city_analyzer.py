#!/usr/bin/env python
# -*- coding: utf-8 -*-
# city_analyzer.py

'''A CityAnalyzer Class Definition'''

import os
import argparse
import osmnx as ox
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import warnings
from shapely.geometry import Point
import matplotlib.pyplot as plt
ox.config(use_cache=True, log_console=True)


class CityAnalyzer:
    '''User defined City Class'''

    def __init__(
        self, 
        city_name: str ='Heidelberg, Germany', 
        city_graph: nx.MultiDiGraph = None
    ):
        '''
        Defines a city based on user input
        :param city_name: Name of the city
        :param city_graph: Graph network of the city (optional)
        '''
        assert isinstance(city_name, str), 'number_steps must be of type str.'

        self.city_name = city_name
        self.city_graph = city_graph

        # If a graph is not provided, retrieve it using osmnx
        if self.city_graph is None:
            self.city_graph = self.get_graph()


    # Write method to get information about the city
    def get_name(self):
        '''
        Returns the name of the city
        :return: City name'''
        return self.city_name


    # Write method to download city polygon from OSM
    def get_poly(self):
        '''
        Retrieves the administrative city boundaries from OSM using osmnx package,
        returns meaningfull error massages if an error occures
        :return: Polygon of the city as geodataframe
        '''

        print("Starting download request of city polygon..")

        try:
            # Get polygon of the city using OSMnx
            poly = ox.geocode_to_gdf(self.city_name)

            # Shorten column names to less than 10 characters
            poly.columns = poly.columns.map(lambda x: x[:10])

        except ox._errors.InsufficientResponseError:
            print(f"No results found for the query '{self.city_name}'. Please check the input.")

        except Exception as e:
            print(f"Error retrieving city boundaries for '{self.city_name}': {str(e)}.")
        
        print("Done. City polygon successfully downloaded.")
        return poly


    # Write method to generate random points within city boundaries
    def get_points(
        self, 
        city_poly: gpd.GeoDataFrame, 
        num_points: int = 1000
    ):
        '''
        Generates a certain amount of random points within the city boundaries,
        default value is 1000
        :param city_poly: Polygon of the city as geodataframe
        :param num_points: Number of points to sample within the boundaries (default=10000)
        :return: Geodataframe containing the sampled points
        '''
        
        print("Start sampling random points within the city boundaries..")

        # Create a Shapely geometry object for the city boundaries
        city_geom = city_poly['geometry'].iloc[0]

        # Generate random points within the non-rectangular bounds of the city
        points_within_city = []
        while len(points_within_city) < int(num_points):
            lon = np.random.uniform(city_poly.bounds.minx.values[0], city_poly.bounds.maxx.values[0])
            lat = np.random.uniform(city_poly.bounds.miny.values[0], city_poly.bounds.maxy.values[0])
            point = Point(lon, lat)
            if point.within(city_geom):
                points_within_city.append(point)

        # Create a GeoDataFrame with random points
        gdf = gpd.GeoDataFrame(geometry=points_within_city)

        print("Done. Sampled random points within the city boundaries.")
        return gdf


    # Write method to get graph network of the city
    def get_graph(self):
        '''
        Retrieves OSM graph network for the city using osmnx package
        :return: Graph network of the city containing travel times
        '''

        # Get graph from place using osmnx
        city_graph = ox.graph_from_place(self.city_name, network_type='drive')

        # Define travel speeds
        hwy_speeds = {"motorway": 100,
              "motorway_link": 60,
              "motorroad": 90,
              "trunk": 85,
              "trunk_link": 60,
              "primary": 65,
              "primary_link": 50,
              "secondary": 60,
              "secondary_link": 50,
              "tertiary": 50,
              "tertiary_link": 40,
              "unclassified": 30,
              "residential": 30,
              "living_street": 10,
              "service": 20,
              "road": 20,
              "track": 15}
        
        # Create graph with speeds
        graph_with_speeds = ox.add_edge_speeds(city_graph, hwy_speeds)

        # Create graph with travel times
        graph_with_travel_times = ox.add_edge_travel_times(graph_with_speeds)

        return graph_with_travel_times


    # Write method that computes random routes within the city
    def get_routes(
        self, 
        city_points: gpd.GeoDataFrame, 
        num_routes: int = 100, 
        method: str = 'length'
    ):
        '''
        Computes random routes within the city based on input city point coordinates
        :param city_points: Points within the city as geodataframe
        :param num_routes: Number of routes to compute (default: 1000)
        :param method: Computing method for routes ('length' or 'travel_time')
        :return: City routes as geodataframe
        '''

        print("Starting to generate random routed out of given points..")

        routes_gdf = gpd.GeoDataFrame()
        count = 0

        total_edges = 0
        for i in range(0, num_routes):
            # Selct two points of the city points
            sample_points = city_points.sample(2)

            # Get nearest nodes 
            origin_node = ox.nearest_nodes(self.city_graph, sample_points['geometry'].iloc[0].x, sample_points['geometry'].iloc[0].y)
            destination_node = ox.nearest_nodes(self.city_graph, sample_points['geometry'].iloc[1].x, sample_points['geometry'].iloc[1].y)

            # Get shortes route between nodes
            random_route = ox.shortest_path(self.city_graph, origin_node, destination_node, weight=method)

            # Repeat if origin and destination node are equal or no route was found
            while origin_node == destination_node or not random_route:
                sample_points = city_points.sample(2)
                origin_node = ox.nearest_nodes(self.city_graph, sample_points['geometry'].iloc[0].x, sample_points['geometry'].iloc[0].y)
                destination_node = ox.nearest_nodes(self.city_graph, sample_points['geometry'].iloc[1].x,
                                                sample_points['geometry'].iloc[1].y)
                random_route = ox.shortest_path(self.city_graph, origin_node, destination_node, weight=method)

            total_edges_in_route = len(random_route) - 1  
            total_edges += total_edges_in_route

            # Convert route to geodataframe and concat it to overall routes geodataframe
            route_gdf = ox.utils_graph.route_to_gdf(self.city_graph, random_route, weight=method)
            routes_gdf = pd.concat([routes_gdf, route_gdf])
            count += 1
            print("--------------------------------------------")
            print("Loading.. done: " + str(count) + " from "+ str(num_routes) + " requested routes generated. Please wait..")
            print("--------------------------------------------")
        
        print("Done. All routes generated.")

        return routes_gdf

    
    # Write function that computes geographical centrality
    def get_geocentrality(self, city_routes: gpd.GeoDataFrame):
        '''
        Calculates betweeness centrality based on given routes using a geographical approach
        :param city_routes: Geodataframe containing different computed routes of a city
        :return: Geodataframe containing osmid, geometry and centrality of the streets
        '''

        print("Starting to compute betweenness centrality based on geographical approach.. Please wait..")

        # Delete all columns except 'geometry' and 'osmid'
        geocentrality_gdf = city_routes[['geometry', 'osmid']].copy()

        # Clean 'osmid' column
        geocentrality_gdf['osmid'] = geocentrality_gdf['osmid'].apply(lambda x: x[0] if isinstance(x, list) else x)

        # Convert 'osmid' to integer
        geocentrality_gdf['osmid'] = geocentrality_gdf['osmid'].astype(int)

        # Count 'osmid' as value for betweenness centrality
        count_osmid = geocentrality_gdf['osmid'].value_counts()

        # Create new column 'centrality'
        geocentrality_gdf['centrality'] = geocentrality_gdf['osmid'].map(count_osmid) / len(city_routes)

        try:
            print("Start dissolving Process...")

            # Dissolve geometries based on centrality values
            dissolved_geocentrality_gdf = geocentrality_gdf.dissolve(by='centrality', aggfunc='first')
            dissolved_geocentrality_gdf = dissolved_geocentrality_gdf.reset_index()

            print("Dissolve process finished.")
            print("Processing done.. networkx betweenness centrality computed.")

            return dissolved_geocentrality_gdf
        
        except Exception as e:
            print(f"Error during dissolve process: {str(e)}")
    

    # Write function that calcultes betweenness centrality based on NetworkX
    def get_netcentrality(self, method: str = 'length'):
        '''
        Calculates betweenes centrality based on NetworkX
        return: Geodataframe containing osmid, geometry and centrality of the streets 
        '''

        print("Starting to compute networkx betweenness centrality.. Please wait..")

        # Calculate betweenness centrality using NetworkX
        betweenness_centrality = nx.edge_betweenness_centrality(self.city_graph, weight=method)

        # Convert the values in betweenness_centrality into a pandas.Dataframe
        netcentrality_df = pd.DataFrame(index=betweenness_centrality.keys(), data=betweenness_centrality.values())

        # Name the two index columns of the centrality_df 'u' and 'v'
        netcentrality_df.reset_index(inplace=True)
        netcentrality_df.columns = ['u', 'v', 'key', 'centrality']
        netcentrality_df = netcentrality_df.set_index(['u', 'v', 'key'])

        # Converting the graph to a geopandas.GeoDataFrame
        nodes_df, edges_df = ox.graph_to_gdfs(self.city_graph)

        # Join the centrality_df with the edges_df
        netcentrality_gdf = netcentrality_df.join(edges_df[['osmid', 'geometry']])
        netcentrality_gdf = gpd.GeoDataFrame(netcentrality_gdf, crs=4326)

        # Convert column lists into strings for saving 
        netcentrality_gdf['osmid'] = netcentrality_gdf['osmid'].astype(str)

        print("Processing done.. networkx betweenness centrality computed.")

        return netcentrality_gdf