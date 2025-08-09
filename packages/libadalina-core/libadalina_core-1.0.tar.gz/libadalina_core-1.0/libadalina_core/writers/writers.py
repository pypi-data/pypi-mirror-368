import pandas as pd
import geopandas as gpd
import pyspark.sql as ps
from libadalina_core.sedona_utils.coordinate_formats import DEFAULT_EPSG

def dataframe_to_geopackage(df: pd.DataFrame | gpd.GeoDataFrame | ps.DataFrame, path: str):
    """
    Write a DataFrame to a GeoPackage file.
    DataFrame geometry is assumed to be in libadalina default EPSG `DEFAULT_EPSG`

    :param df: The DataFrame to write, which can be a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame.
    :param path: The path to the GeoPackage file where the DataFrame will be saved.
    """
    if isinstance(df, ps.DataFrame):
        df = gpd.GeoDataFrame(df.toPandas(), geometry = 'geometry', crs = DEFAULT_EPSG.value)
    elif isinstance(df,  pd.DataFrame):
        df = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG.value)
    elif isinstance(df, gpd.GeoDataFrame):
        pass # already a GeoDataFrame
    else:
        raise TypeError(f"Unsupported type {type(df)}. Expected pandas DataFrame, geopandas GeoDataFrame, or spark DataFrame.")
    df.to_file(path, layer='dataframe', driver="GPKG")