import geopandas as gpd

from libadalina_core.sedona_utils import DEFAULT_EPSG


def geopackage_to_dataframe(path: str, layer: str) -> gpd.GeoDataFrame:
    """
    Read a GeoPackage file into a GeoDataFrame.

    Geometry is automatically converted in libadalina default EPSG `DEFAULT_EPSG`.

    :param path: The path to the GeoPackage file.
    :param layer: The layer name of the GeoPackage.
    :return: A GeoDataFrame containing the data from the specified layer.
    """
    gdf = gpd.read_file(path, layer=layer)
    gdf.to_crs(epsg=DEFAULT_EPSG.value, inplace=True)
    return gdf