from enum import Enum
from dataclasses import dataclass
from .commons import DataFrame
from sedona.sql import ST_Area, ST_Intersection, ST_Union, ST_Buffer, ST_GeometryType, ST_Dump
from libadalina_core.sedona_utils import to_spark_dataframe, DEFAULT_EPSG
import pyspark.sql.functions as func
import pyspark.sql as ps

def polygonize(df: DataFrame, radius_meters: float) -> ps.DataFrame:
    """
    Transform lines and points into polygons by buffering them with a given radius.

    Each line (or multi-line) is transformed into a polygon by buffering it on both sides,
    while points are buffered to create a circular area around them.

    Geometries are implicitly converted to :py:DEFAULT_EPSG.

    :param df: The input DataFrame containing geometries.
    :param radius_meters: The radius in meters to use for buffering points and lines.
    :return: A Spark DataFrame with a new column 'polygonized_geometry' containing the buffered geometries.

    """
    table = to_spark_dataframe(df)
    return table.select("*", func
                        .when(ST_GeometryType(table.geometry).like('%Point%'),
                              ST_Buffer(func.col('geometry'), radius_meters, func.lit(True)))
                        .when(ST_GeometryType(func.col('geometry')).like('%LineString%'),
                              ST_Union(
                                  ST_Buffer(func.col('geometry'), radius_meters, func.lit(True),
                                            parameters=func.lit('endcap=flat side=left')),
                                  ST_Buffer(func.col('geometry'), radius_meters, func.lit(True),
                                            parameters=func.lit('endcap=flat side=right'))
                              ))
                        .otherwise(table.geometry)
                        .alias('polygonized_geometry')
                        )


def explode_multi_geometry(df: DataFrame) -> ps.DataFrame:
    table = to_spark_dataframe(df)

    return table.select("*", func
                        .when(df.geometry.isNull(), func.array())
                        .when(ST_GeometryType(df.geometry).like('%Multi%'),
                              func.explode(ST_Dump(df.geometry)))
                        .otherwise(df.geometry)
                        )


class AggregationType(Enum):
    COUNT = 'count'
    SUM = 'sum'
    AVG = 'avg'
    MIN = 'min'
    MAX = 'max'

    def to_spark_func(self):
        if self == AggregationType.COUNT:
            return func.count
        elif self == AggregationType.SUM:
            return func.sum
        elif self == AggregationType.AVG:
            return func.avg
        elif self == AggregationType.MIN:
            return func.min
        elif self == AggregationType.MAX:
            return func.max
        return func.count  # Default to count if none matched

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

@dataclass
class AggregationFunction:
    column: str
    aggregation_type: AggregationType
    alias: str | None = None
    proportional: str | None = None

def spatial_aggregation(table: DataFrame, aggregate_functions: list[AggregationFunction]) -> ps.DataFrame:
    table = to_spark_dataframe(table)

    columns_to_aggregate = [c.column for c in aggregate_functions]
    projection_of_not_aggregated_columns = (
        func.first(c).alias(c) for c in table.columns if c != 'geometry' and c not in columns_to_aggregate
    )

    columns_with_no_proportional_aggregation = [c for c in aggregate_functions if c.proportional is None]
    columns_with_proportional_aggregation = [c for c in aggregate_functions if c.proportional is not None]

    projection_of_aggregated_columns = (
        agg_func.aggregation_type.to_spark_func()(func.col(agg_func.column)).alias(
            f"{agg_func.aggregation_type.value}({agg_func.column})" if agg_func.alias is None else agg_func.alias
        ) for agg_func in columns_with_no_proportional_aggregation if agg_func.column in table.columns
    )

    projection_of_proportional_aggregated_columns = (
        agg_func.aggregation_type.to_spark_func()(func.col(agg_func.column) * ST_Area(ST_Intersection(func.col('geometry'), func.col(agg_func.proportional))) / ST_Area(func.col(agg_func.proportional))).alias(
            f"{agg_func.aggregation_type.value}({agg_func.column})" if agg_func.alias is None else agg_func.alias
        ) for agg_func in columns_with_proportional_aggregation if agg_func.column in table.columns
    )

    # Group by geometry and aggregate other columns
    aggregated = (table
                  .groupby(table.geometry)
                    .agg(
                        # from the columns for which is not specified an aggregation function, take the first value
                        *projection_of_not_aggregated_columns,
                        # apply the aggregation functions to the other columns
                        *projection_of_aggregated_columns,
                        *projection_of_proportional_aggregated_columns
                    ))

    return aggregated