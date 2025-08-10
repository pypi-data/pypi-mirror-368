pip install libadalina-core # install libadalina-core

from ameliadp_sql_toolkit import GrinsAmeliaSQLToolkit # import amelia package to read from their datasets
amelia_sql_toolkit = GrinsAmeliaSQLToolkit()
milan_osm = amelia_sql_toolkit.read_data(table_name='gis_osm_roads_free_1') # read a dataset

# select interesting columns and fill NaNs
milan_osm = milan_osm[['geometry', 'name']]
milan_osm.loc[:, 'name'] = milan_osm['name'].fillna('')

milan_osm

from libadalina_core.sedona_utils import to_spark_dataframe, EPSGFormats
from libadalina_core.spatial_operators import polygonize

# load dataframe into Apache Sedona
df = to_spark_dataframe(milan_osm, EPSGFormats.EPSG4326)
# Transform lines and points into polygons
df = polygonize(df, 100)

df
