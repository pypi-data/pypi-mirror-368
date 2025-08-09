import pandas as pd
import geopandas as gpd
import pyspark.sql as ps

from libadalina_core.sedona_configuration.sedona_configuration import get_sedona_context

def to_spark_dataframe(df: pd.DataFrame | gpd.GeoDataFrame | ps.DataFrame) -> ps.DataFrame:
    """
    Covert a pandas DataFrame or a GeoPandas GeoDataFrame to a Spark DataFrame.
    If the input is already a Spark DataFrame, it will be returned as is.

    This function is useful for converting data to a format suitable for processing with Apache Sedona,
    however, each function of libadalina already converts the input DataFrame to a Spark DataFrame before processing.

    :param df: The DataFrame to convert, which can be a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame.
    :return: A Spark DataFrame.
    """
    if isinstance(df, ps.DataFrame):
        return df
    sedona = get_sedona_context()
    if isinstance(df, gpd.GeoDataFrame):
        return sedona.createDataFrame(df)
    if isinstance(df, pd.DataFrame):
        return sedona.createDataFrame(df)
    if isinstance(df, ps.DataFrame):
        return df # nothing to do here
    raise TypeError(f"Unsupported type {type(df)}. Expected pandas, geopandas, or spark DataFrame.")