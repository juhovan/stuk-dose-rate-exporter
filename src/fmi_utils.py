from urllib.error import URLError
from urllib.request import urlopen
import socket
import time

gml_namespace = "http://www.opengis.net/gml/3.2"
gmlcov_namespace ="http://www.opengis.net/gmlcov/1.0"
swe_ns = "http://www.opengis.net/swe/2.0"
wfs_ns = "http://www.opengis.net/wfs/2.0"

fmi_request_datetime_format = "YYYY-MM-DDThh:mm:ss"

request_templates = {
    "dose_rates": ("https://opendata.fmi.fi/wfs/eng?"
                    "request=GetFeature&storedquery_id=stuk::observations::"
                    "external-radiation::multipointcoverage")
}

geojson_template = {
    "type": "FeatureCollection",
    "name": "stuk_open_data_dose_rates",
    "crs": { "type": "name", "properties":
            { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": []
}

def wfs_request(results_type):
    """
    Performs a WFS request to the FMI open data API.

    :param results_type: type of data to get
    :return: dataset as a string
    """
    url = request_templates[results_type]
    response = None

    try:
        with urlopen(url, timeout=50) as connection:
            response = connection.read()
    except (URLError, ConnectionError, socket.timeout):
        pass

    return response
