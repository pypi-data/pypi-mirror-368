import pandas as pd
import pathlib

from libadalina_core.sedona_utils import to_spark_dataframe, EPSGFormats
from spatial_operators import polygonize

if __name__ == "__main__":
    """Example of reading a pandas DataFrame, converting it to a Spark DataFrame, and polygonizing its geometry."""

    # Read a CSV file into a pandas DataFrame
    df = pd.read_csv(
        pathlib.Path(__file__).parent.parent / "tests" / "samples" / "milano" / "gis_osm_roads_free_1.csv",
        sep=',', quotechar='"', dtype={'name': 'string', 'ref': 'string'},
    )
    # Fill NaN values
    df.loc[:, 'name'] = df['name'].fillna('')
    df.loc[:, 'ref'] = df['ref'].fillna('')

    # Convert the pandas DataFrame into a Spark DataFrame setting the EPSG format of the geometry
    df = to_spark_dataframe(df, EPSGFormats.EPSG4326)
    # Transform lines and points into polygons
    df = polygonize(df, 100)

    df.show()