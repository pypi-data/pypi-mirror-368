# Copyright 2025 West University of Timisoara
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io

import click
import geopandas as gpd
from geopandas import GeoDataFrame
from owslib.etree import etree
from owslib.fes import PropertyIsEqualTo, OgcExpression
from owslib.wfs import WebFeatureService
from rich.table import Table

from eocube.cli import console

COUNTY_TABLE = "geospatial:ro_judete_poligon"
UAT_TABLE = "geospatial:ro_uat_poligon"


__ascii_art_availble = False


def _ascii_art_availble():
    try:
        import matplotlib.pyplot as plt
        import ascii_magic

        __ascii_art_availble = True
    except ImportError:
        __ascii_art_availble = False
    return __ascii_art_availble


def print_table(table):
    console.print(table)


def print_gdf(gdf):
    import matplotlib.pyplot as plt
    import ascii_magic

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    gdf.plot(ax=ax)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    ascii_art = ascii_magic.from_image(buf)
    ascii_art.to_terminal()


class UAT(object):

    def __init__(
        self,
        endpoint: str = "http://www.geo-spatial.org/geoserver/ows",
        epsg: int = 4326,
    ):
        self._ows_endpoint = endpoint
        self._wfs11 = WebFeatureService(url=self._ows_endpoint, version="1.1.0")
        self._epsg = epsg

    def get_feature(
        self, feature: str, filter: OgcExpression, epsg: int = None
    ) -> GeoDataFrame:
        """Get features matching the filter. Return in specified EPSG

        :param feature: What WFS feature to query
        :param filter: The WFS filter to apply
        :param epsg: the projection the results should be
        :return: Dataframe with the result
        """
        epsg_ = epsg if epsg is not None else self._epsg
        filterxml = etree.tostring(filter.toXML(), encoding="unicode")
        response = self._wfs11.getfeature(
            feature,
            filter=filterxml,
            outputFormat="json",
            srsname=f"urn:x-ogc:def:crs:EPSG:{epsg_}",
        )
        data = gpd.GeoDataFrame.from_file(response)
        if data.empty:
            return None
        # minx, miny, maxx, maxy = data.unary_union.envelope.bounds
        return data  # , (minx, miny, maxx, maxy)


def get_administrative_unit_by_code(siruta_code: int, epsg: int = 4326) -> GeoDataFrame:
    """Query the Geo-Spatial.org service for a Romanian administrative unit by SIRUTA Code

    :param siruta_code: Siruta code of the administrative unit
    :param epsg: The EPSG of the results
    :return: GeoDataFrame with the matches
    """
    uat = UAT(epsg=epsg)
    wfs_filter = PropertyIsEqualTo(propertyname="natcode", literal=f"{siruta_code}")
    return uat.get_feature(UAT_TABLE, filter=wfs_filter)


def get_administrative_unit_by_name(
    name: str, matchcase=False, epsg: int = 4326
) -> GeoDataFrame:
    """Query the Geo-Spatial.org service for a Romanian administrative unit by name

    :param name: Name of the administrative unit
    :param matchcase: Whether to match the case
    :param epsg: The EPSG of the results
    :return: GeoDataFrame with the matches
    """
    uat = UAT(epsg=epsg)
    wfs_filter = PropertyIsEqualTo(
        propertyname="name", literal=f"{name}", matchcase=matchcase
    )
    return uat.get_feature(UAT_TABLE, filter=wfs_filter)


def get_county_by_mnemonic(county_mnemonic: str, epsg: int = 4326) -> GeoDataFrame:
    """Query the Geo-Spatial.org service for a Romanian county

    :param county_mnemonic: Mnemonic code of the county
    :param epsg: The EPSG of the results
    :return: GeoDataFrame with the matches
    """
    uat = UAT(epsg=epsg)
    wfs_filter = PropertyIsEqualTo(
        propertyname="mnemonic", literal=f"{county_mnemonic}"
    )
    return uat.get_feature(COUNTY_TABLE, filter=wfs_filter)


def get_county_by_name(name: str, epsg: int = 4326) -> GeoDataFrame:
    """Query the Geo-Spatial.org service for a Romanian county

    :param name: County Name
    :param epsg: The EPSG of the results
    :return: GeoDataFrame with the matches
    """
    uat = UAT(epsg=epsg)
    wfs_filter = PropertyIsEqualTo(propertyname="name", literal=f"{name}")
    return uat.get_feature(COUNTY_TABLE, filter=wfs_filter)


def uat_gdf_to_table(gdf, title):
    result_table = Table(title=f"Geo-Spatial.org -- {title}")
    result_table.add_column("Name", justify="left")
    result_table.add_column("natLevName", justify="left")
    result_table.add_column("countyCode", justify="left")
    result_table.add_column("county", justify="left")
    result_table.add_column("countyMn", justify="left")
    result_table.add_column("regionId", justify="left")
    result_table.add_column("regionCode", justify="left")
    result_table.add_column("region", justify="left")
    result_table.add_column("pop2011", justify="left")
    result_table.add_column("pop2012", justify="left")
    result_table.add_column("pop2013", justify="left")
    result_table.add_column("pop2014", justify="left")
    result_table.add_column("pop2015", justify="left")
    result_table.add_column("pop2020", justify="left")
    result_table.add_column("Area", justify="left")
    result_table.add_column("Centroid", justify="left")
    for _, row in gdf.head(10).iterrows():
        result_table.add_row(
            row["name"],
            row["natLevName"],
            f"{row["countyCode"]}",
            row["county"],
            row["countyMn"],
            f"{row['regionId']}",
            f"{row['regionCode']}",
            row["region"],
            f"{int(row['pop2011']):,}",
            f"{int(row['pop2012']):,}",
            f"{int(row['pop2013']):,}",
            f"{int(row['pop2014']):,}",
            f"{int(row['pop2015']):,}",
            f"{int(row['pop2020']):,}",
            f"{row['geometry'].area:.2f}",
            str(row["geometry"].centroid),
        )
    return result_table


def county_gdf_to_table(gdf, title):
    result_table = Table(title=f"Geo-Spatial.org -- {title}")
    result_table.add_column("Name", justify="left")
    result_table.add_column("Mnemonic", justify="left")
    result_table.add_column("Region", justify="left")
    result_table.add_column("Pop. 1948", justify="left")
    result_table.add_column("Pop. 1956", justify="left")
    result_table.add_column("Pop. 1966", justify="left")
    result_table.add_column("Pop. 1977", justify="left")
    result_table.add_column("Pop. 1992", justify="left")
    result_table.add_column("Pop. 2002", justify="left")
    result_table.add_column("Pop. 2011", justify="left")
    result_table.add_column("Area", justify="left")
    result_table.add_column("Centroid", justify="left")
    for _, row in gdf.head(10).iterrows():
        result_table.add_row(
            row["name"],
            row["mnemonic"],
            row["region"],
            f"{int(row['pop1948']):,}",
            f"{int(row['pop1956']):,}",
            f"{int(row['pop1966']):,}",
            f"{int(row['pop1977']):,}",
            f"{int(row['pop1992']):,}",
            f"{int(row['pop2002']):,}",
            f"{int(row['pop2011']):,}",
            f"{row['geometry'].area:.2f}",
            str(row["geometry"].centroid),
        )
    return result_table


@click.command("get-county-by-name")
@click.option("--name", prompt="Name of County", help="County Name")
@click.option("--epsg", default=3844, help="EPSG of the results")
@click.option(
    "--ascii-art",
    is_flag=True,
    default=False,
    help="Prin ascii art of the map, if available.",
)
@click.option(
    "--output", default=None, help="Destination of the output saved as GeoJSON"
)
def get_county_by_name_cli(name: str, output, epsg: int = 3844, ascii_art=False):
    """Retrieves the county by name"""
    result = get_county_by_name(name, epsg=epsg)
    if result is None:
        click.echo("County not found")
        return
    if output is not None:
        result.to_file(output, driver="GeoJSON")
    else:
        if ascii_art and _ascii_art_availble():
            print_gdf(result)
        else:
            print_table(county_gdf_to_table(result, f"Counties by Name ({name})"))

    return result


@click.command("get-county-by-mnemonic")
@click.option("--name", prompt="County Mnemonic", help="County Mnemonic. Eg. TM")
@click.option("--epsg", default=3844, help="EPSG of the results")
@click.option(
    "--ascii-art",
    is_flag=True,
    default=False,
    help="Prin ascii art of the map, if available.",
)
@click.option(
    "--output", default=None, help="Destination of the output saved as GeoJSON"
)
def get_county_by_mnemonic_cli(
    name: str, output: str, epsg: int = 3844, ascii_art=False
):
    """Retrieves the county by mnemonic"""
    result = get_county_by_mnemonic(name, epsg=epsg)
    if result is None:
        click.echo("County not found")
        return
    if output is not None:
        result.to_file(output, driver="GeoJSON")
    else:
        if ascii_art and _ascii_art_availble():
            print_gdf(result)
        else:
            print_table(county_gdf_to_table(result, f"Counties by Mnemonic ({name})"))
    return result


@click.command("get-administrative-unit-by-name")
@click.option(
    "--name", prompt="Name of administrative unit", help="Administrative unit name"
)
@click.option("--epsg", default=3844, help="EPSG of the results")
@click.option(
    "--ascii-art",
    is_flag=True,
    default=False,
    help="Prin ascii art of the map, if available.",
)
@click.option(
    "--output", default=None, help="Destination of the output saved as GeoJSON"
)
def get_administrative_unit_by_name_cli(
    name: str, output=str, matchcase=False, epsg: int = 4326, ascii_art=False
):
    """Retrieves the administrative unit by name"""
    result = get_administrative_unit_by_name(name, epsg=epsg, matchcase=matchcase)
    if result is None:
        click.echo("Administrative Unit not found")
        return
    if output is not None:
        result.to_file(output, driver="GeoJSON")
    else:
        if ascii_art and _ascii_art_availble():
            print_gdf(result)
        else:
            print_table(uat_gdf_to_table(result, f"Counties by Name ({name})"))
    return result


@click.command("get-administrative-unit-by-code")
@click.option(
    "--code",
    prompt="Administrative unit code",
    help="SIRUTA Code of the administrative unit",
)
@click.option("--epsg", default=3844, help="EPSG of the results")
@click.option(
    "--ascii-art",
    is_flag=True,
    default=False,
    help="Prin ascii art of the map, if available.",
)
@click.option(
    "--output", default=None, help="Destination of the output saved as GeoJSON"
)
def get_administrative_unit_by_code_cli(
    code: int, output, epsg: int = 4326, ascii_art=False
):
    """Uses the SIRUTA Code to retrieve the administrative unit"""
    result = get_administrative_unit_by_code(siruta_code=code, epsg=epsg)
    if result is None:
        click.echo("Administrative Unit not found")
        return
    if output is not None:
        result.to_file(output, driver="GeoJSON")
    else:
        if ascii_art and _ascii_art_availble():
            print_gdf(result)
        else:
            print_table(uat_gdf_to_table(result, f"Counties by SIRUTA ({code})"))
    return result
