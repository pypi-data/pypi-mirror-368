from libadalina_core.readers.geopackage import geopackage_to_dataframe
import pathlib
import pandas as pd

from libadalina_core.spatial_operators.multi_table_operators import spatial_join, JoinType, spatial_aggregation, AggregationType, \
    AggregationFunction

if __name__ == "__main__":
    """Example of how to use libadalina to find the total amount of the population living in specific provinces in Italy."""

    # Set pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 100)

    population = geopackage_to_dataframe(
        str(pathlib.Path(__file__).parent.parent / "tests" / "samples" / "population-north-italy" / "nord-italia.gpkg"),
        "census2021"
    )[['T', 'geometry']]

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

    # join with population table to get the population of these provinces
    result = spatial_aggregation(
        spatial_join(filtered_regions, population, join_type=JoinType.LEFT)
              # join operator renames the geometries adding suffixes _left and _right to avoid conflicts
              .withColumnRenamed('geometry_left', 'geometry'),
        aggregate_functions=[
            AggregationFunction("T", AggregationType.SUM, 'population', proportional='geometry_right'),
    ])
    result.show(truncate=False)

