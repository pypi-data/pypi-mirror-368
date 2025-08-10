from libadalina_core.readers.geopackage import geopackage_to_dataframe
import pathlib
import pandas as pd

from libadalina_core.spatial_operators.multi_table_operators import spatial_join, JoinType, spatial_aggregation, AggregationType, \
    AggregationFunction

if __name__ == "__main__":
    """Example of how to use libadalina to find hospitals in specific provinces in Italy and aggregate their data."""

    # Set pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 100)

    hospitals = geopackage_to_dataframe(
        str(pathlib.Path(__file__).parent.parent / "tests" / "samples" / "healthcare" / "EU_healthcare.gpkg"),
        "EU"
    )[["hospital_name", "geometry", "city", "cap_beds"]]

    regions = geopackage_to_dataframe(
        str(pathlib.Path(__file__).parent.parent / "tests" / "samples" / "regions" / "NUTS_RG_20M_2024_4326.gpkg"),
        "NUTS_RG_20M_2024_4326.gpkg"
    )[["LEVL_CODE", "NUTS_NAME", "CNTR_CODE", "geometry"]]

    # select province of Milan and Cremona
    filtered_regions = regions[
        (regions['LEVL_CODE'] == 3) &
        (regions['CNTR_CODE'] == "IT") &
        (regions['NUTS_NAME'].str.contains('Milano|Cremona', case=False))
    ]

    # join with hospitals table to get hospitals in these provinces
    result = (spatial_join(filtered_regions, hospitals, join_type=JoinType.LEFT)
              # join operator renames the geometries adding suffixes _left and _right to avoid conflicts
              .withColumnRenamed('geometry_left', 'geometry'))
    result.show(truncate=False)

    # get the number of hospitals in each province along with the total and average number of beds
    result = spatial_aggregation(result, aggregate_functions=[
        AggregationFunction("hospital_name", AggregationType.COUNT, 'hospitals'),
        AggregationFunction("cap_beds", AggregationType.SUM, 'total_beds'),
        AggregationFunction("cap_beds", AggregationType.AVG, 'average_beds'),
    ])
    result.show(truncate=False)

