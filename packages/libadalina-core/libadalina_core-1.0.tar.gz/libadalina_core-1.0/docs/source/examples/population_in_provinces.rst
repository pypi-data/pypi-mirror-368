Population in Provinces
=======================

This example demonstrates how to calculate population statistics for provinces in Italy.

.. literalinclude:: ../../../libadalina_core/examples/example_population_in_provinces.py
   :language: python
   :linenos:
   :caption: Example: Calculating population statistics for provinces

Example Explanation
-------------------

This example shows how to:

1. Load geospatial data from GeoPackage files using ``geopackage_to_dataframe``
2. Filter data to select specific provinces in Northern Italy
3. Perform a spatial join between provinces and population data using ``spatial_join``
4. Aggregate population data by province using ``spatial_aggregation``

The example demonstrates the use of the following libadalina-core features:

* Reading geospatial data
* Filtering data based on attributes
* Spatial joins
* Spatial aggregations with sum aggregation function
