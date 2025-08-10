import pandas as pd
import geopandas as gpd
import pyspark.sql as ps

DataFrame = pd.DataFrame | gpd.GeoDataFrame | ps.DataFrame
