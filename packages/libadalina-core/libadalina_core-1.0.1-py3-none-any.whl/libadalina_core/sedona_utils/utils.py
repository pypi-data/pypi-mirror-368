import pandas as pd
import geopandas as gpd
import pyspark.sql as ps
from sedona.sql import ST_BestSRID, ST_SetSRID, ST_Transform, ST_SRID
import sedona.sql.st_functions as func
from shapely.io import from_wkt
from functools import wraps
from .coordinate_formats import EPSGFormats, DEFAULT_EPSG
from libadalina_core.sedona_configuration.sedona_configuration import get_sedona_context

def to_default_epsg(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        if isinstance(result, ps.DataFrame) and 'geometry' in result.columns:
            result = result.withColumn('geometry', ST_Transform(result.geometry, func.lit(f'EPSG:{DEFAULT_EPSG.value}')))
        return result

    return wrapper

@to_default_epsg
def to_spark_dataframe(df: pd.DataFrame | gpd.GeoDataFrame | ps.DataFrame, epsg_format: EPSGFormats | None = None) -> ps.DataFrame:
    """
    Covert a pandas DataFrame or a GeoPandas GeoDataFrame to a Spark DataFrame.
    If the input is already a Spark DataFrame, it will be returned as is.

    This function is useful for converting data to a format suitable for processing with Apache Sedona,
    however, each function of libadalina already converts the input DataFrame to a Spark DataFrame before processing.

    :param df: The DataFrame to convert, which can be a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame.
    :param epsg_format: The EPSG format to use for converting the pandas DataFrame. If None is provided and the
        geometry is missing the EPSG format, libadalina will try to infer the best fitting format.
    :return: A Spark DataFrame.
    """
    if isinstance(df, ps.DataFrame):
        if 'geometry' not in df.columns:
            raise TypeError(f"Unsupported DataFrame: missing `geometry` column.")
        return df # nothing to do here
    sedona = get_sedona_context()
    if isinstance(df, gpd.GeoDataFrame):
        if 'geometry' not in df.columns:
            raise TypeError(f"Unsupported DataFrame: missing `geometry` column.")
        return sedona.createDataFrame(df)
    if isinstance(df, pd.DataFrame):
        if 'geometry' not in df.columns:
            raise TypeError(f"Unsupported DataFrame: missing `geometry` column.")
        df.loc[:, 'geometry'] = df['geometry'].apply(from_wkt)
        df = sedona.createDataFrame(gpd.GeoDataFrame(df, geometry='geometry'))
        df.select(ST_SRID(df.geometry)).show()
        if epsg_format is None:
            df = df.withColumn('geometry', ST_SetSRID(df.geometry, ST_BestSRID(df.geometry)))
        else:
            df = df.withColumn('geometry', ST_SetSRID(df.geometry, func.lit(epsg_format.value)))
        return df
    raise TypeError(f"Unsupported type {type(df)}. Expected pandas, geopandas, or spark DataFrame.")

