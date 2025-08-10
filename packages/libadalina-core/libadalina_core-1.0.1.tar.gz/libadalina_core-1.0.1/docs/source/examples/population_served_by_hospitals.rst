Population Served by Hospitals
==============================

This example demonstrates how to calculate the population served by hospitals in different provinces of Italy.

.. literalinclude:: ../../../examples/example_population_served_by_hospitals.py
   :language: python
   :linenos:
   :caption: Example: Calculating population served by hospitals

Example Explanation
-------------------

This example shows how to:

1. Load geospatial data from GeoPackage files using ``geopackage_to_dataframe``
2. Filter data to select specific provinces in Northern Italy
3. Create buffer zones around hospitals using ``polygonize``
4. Perform a spatial join between hospital buffer zones and population data using ``spatial_join``
5. Aggregate population data by hospital using ``spatial_aggregation``

The example demonstrates the use of the following libadalina-core features:

* Reading geospatial data
* Filtering data based on attributes
* Creating buffer zones around geometries
* Spatial joins
* Spatial aggregations with proportional calculations
* Handling of complex spatial relationships
