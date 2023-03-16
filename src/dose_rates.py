from datetime import datetime
from xml.etree import ElementTree
import math
import logging

import fmi_utils
from prometheus_client import Gauge

# Create a Prometheus Gauge metric
dose_rate_gauge = Gauge('dose_rate', 'Dose rate', ['site', 'lat', 'lon'])


class DownloadError(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class EmptyDatasetError(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class AllNaNValuesError(Exception):
    def __init__(self, message=None):
        super().__init__(message)


def update_data():
    """
    Downloads, parses, and updates dose rate data.
    """
    try:
        data = download_data()
    except DownloadError:
        logging.warning("DownloadError: Could not update data due to download failure")
        return

    logging.info("Updating metrics")
    invalid_datasets = 0
    for dataset in data:
        try:
            parse_data(dataset)
        except (EmptyDatasetError, AllNaNValuesError) as e:
            logging.warning(f"Error parsing dataset: {e}")
            invalid_datasets += 1

    if invalid_datasets > 0:
        logging.info(f"{invalid_datasets} invalid datasets were skipped")


def download_data():
    """
    Performs a WFS request for dose rate data from the FMI open data API.
    If no timespan is provided when running the program, the function
    fetches the most recent measurements.
    :return: array of HTTPResponse objects
    """
    data = []

    logging.info("Downloading dataset")
    dataset = fmi_utils.wfs_request("dose_rates")
    if dataset is not None:
        data.append(dataset)
    else:
        logging.warning("Failed to download dataset")
        raise DownloadError("Failed to download dataset")

    return data


def parse_data(data):
    """
    Parses the argument dose rate data into a list of metrics.
    :param data: raw dose rate data from the FMI open data API.
    :return: None
    """
    if data is None:
        raise EmptyDatasetError("Dataset is empty")

    wfs_response = ElementTree.fromstring(data)
    gml_points = wfs_response.findall('.//{%s}Point' % fmi_utils.gml_namespace)

    # Read locations.
    locations = {}
    for n, point in enumerate(gml_points):
        identifier = point.attrib['{%s}id' % fmi_utils.gml_namespace].split("-")[-1]
        name = point.findall('{%s}name' % fmi_utils.gml_namespace)[0].text
        position = point.findall('{%s}pos' % fmi_utils.gml_namespace)[0].text.strip()
        longitude = float(position.split()[1])
        latitude = float(position.split()[0])
        locations[position] = {
            "site": name,
            "longitude": longitude,
            "latitude": latitude,
            "id": identifier
        }

    # Read values.
    value_elements = wfs_response.findall('.//{%s}doubleOrNilReasonTupleList' \
                                          % fmi_utils.gml_namespace)[0]

    # Construct features.
    position_elements = wfs_response.findall('.//{%s}positions' \
                                             % fmi_utils.gmlcov_namespace)[0]

    value_lines = value_elements.text.split("\n")[1:-1]
    position_lines = position_elements.text.split("\n")[1:-1]

    for value_line, position_line in zip(value_lines, position_lines):
        value = float(value_line.strip().split()[0])
        position_line = position_line.split()
        coords = position_line[0] + " " + position_line[1]
        lat = position_line[0]
        lon = position_line[1]

        if math.isnan(value):
            continue

        dose_rate_gauge.labels(
            site=locations[coords]["site"],
            lat=str(locations[coords]["latitude"]),
            lon=str(locations[coords]["longitude"])
        ).set(value)
