from copy import deepcopy
from datetime import datetime, timedelta
from xml.etree import ElementTree
import json
import logging
import math
import os
import sys
import time

import fmi_utils

def get_data():
    """
    Downloads, parses, and writes dose rate data.
    """
    data = download_data()

    logging.info("Generating metrics")
    invalidDatasets = 0
    for dataset in data:
        try:
            parsed_data = parse_data(dataset)
            return parsed_data
        except InvalidDatasetError:
            invalidDatasets += 1

    if invalidDatasets > 0:
        logging.info("{0} invalid datasets were skipped".format(invalidDatasets))

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
        sys.exit(1)

    return data

def parse_data(data):
    """
    Parses the argument dose rate data into a list of metrics.

    :param data: raw dose rate data from the FMI open data API.
    :return: list of metrics
    """
    if data is None:
        raise InvalidDatasetError

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
    values = []
    try:
        value_lines = wfs_response.findall('.//{%s}doubleOrNilReasonTupleList' \
                                            % fmi_utils.gml_namespace)[0].text.split("\n")[1:-1]
    except IndexError:
        raise InvalidDatasetError("Dataset contains no features.")

    for line in value_lines:
        value = float(line.strip().split()[0])
        values.append(value)

    # check if all values are NaNs
    if all ( math.isnan(value) for value in values ):
        raise InvalidDatasetError("Dataset values are all NaN")

    # Construct features.
    position_lines =  wfs_response.findall('.//{%s}positions' \
                                            % fmi_utils.gmlcov_namespace)[0].text.split("\n")[1:-1]

    result = []
    dataset_timestamp = None
    for i, line in enumerate(position_lines):
        if math.isnan(values[i]):
            continue

        line = line.split()
        coords = line[0] + " " + line[1]
        lat = line[0]
        lon = line[1]
        timestamp = datetime.utcfromtimestamp(int(line[2]))

        # Some datasets contain duplicate entries for sites where the timestamp
        # of one of the entries differs by e.g. a minute.
        # Entries that don't match the dataset's timestamp are skipped.
        # The dataset's timestamp is set to the timestamp of the first entry.
        if dataset_timestamp is None:
            dataset_timestamp = timestamp
        elif timestamp != dataset_timestamp:
            continue

        result.append("dose_rate{{site=\"{site}\",lat=\"{lat}\",lon=\"{lon}\"}} {doserate}".format(
            site=locations[coords]["site"], lat=lat, lon=lon, doserate=values[i]))

    return result

class InvalidDatasetError(Exception):
    """
    A custom exception type for when a dataset retrieved from
    FMI's API is considered invalid (e.g. it contains no features).
    """
    pass


if __name__ == "__main__":
    get_data()
