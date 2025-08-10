Hospitals in Provinces
=======================

This example demonstrates how to find hospitals in specific provinces in Italy and aggregate their data.

.. literalinclude:: ../../../examples/example_hospitals_in_provinces.py
   :language: python
   :linenos:
   :caption: Example: Finding hospitals in provinces and aggregating data

Example Explanation
-------------------

This example shows how to:

1. Load geospatial data from GeoPackage files using ``geopackage_to_dataframe``
2. Filter data to select specific provinces (Milan and Cremona)
3. Perform a spatial join between provinces and hospitals using ``spatial_join``
4. Aggregate data to count hospitals and calculate total and average beds using ``spatial_aggregation``

The example demonstrates the use of the following libadalina-core features:

* Reading geospatial data
* Spatial joins
* Spatial aggregations with different aggregation functions
