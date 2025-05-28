#!/usr/bin/env python
"""
Stitch together Google Maps images from lat, long coordinates

Based on work by enigmaticPhysicist, heltonbiker and BenElgar on StackExchange
https://stackoverflow.com/questions/7490491/capture-embedded-google-map-image-with-python-without-using-a-browser

Changes:
* Ability to set GOOGLE_MAPS_API_KEY as environment variable
* Added command-line options for NW and SE Lat/Lons and zoom level
* Added option to quit/continue (if the amoutn of images to be downloaded was too great)
* Ability to save images
* Added logging
* Dramatically simplified the maths.
* Set a more reasonable default logo cutoff.
* Added global constants for logo cutoff and max image size.
* Translated a couple presumably Portuguese variable names to English.
* Updated for Python 3
* Added Google Maps API key (compliance with T&C, although can set to None)
* Handle http request exceptions
"""

import argparse
import logging
import sys
from io import BytesIO
from os import environ

import requests
from PIL import Image
from math import log, exp, tan, atan, ceil
from datetime import datetime
from gmaps_image_fetcher.main import main

__version__ = "0.3.2"

# circumference/radius
tau = 6.283185307179586
# One degree in radians, i.e. in the units the machine uses to store angle,
# which is always radians. For converting to and from degrees. See code for
# usage demonstration.
DEGREE = tau / 360

ZOOM_OFFSET = 8

# Max width or height of a single image grabbed from Google.
MAXSIZE = 600
# For cutting off the logos at the bottom of each of the grabbed images.  The
# logo height in pixels is assumed to be less than this amount.
LOGO_CUTOFF = 32

logger = None  # Global logger, will be set in main


def latlon_to_pixels(lat, lon, zoom):
    mx = lon
    my = log(tan((lat + tau / 4) / 2))
    res = 2 ** (zoom + ZOOM_OFFSET) / tau
    px = mx * res
    py = my * res
    return px, py


def pixels_to_latlon(px, py, zoom):
    res = 2 ** (zoom + ZOOM_OFFSET) / tau
    mx = px / res
    my = py / res
    lon = mx
    lat = 2 * atan(exp(my)) - tau / 4
    return lat, lon


def get_maps_image(nw_lat_long, se_lat_long, zoom=18, scale=1):
    global logger
    try:
        GOOGLE_MAPS_API_KEY = environ['GOOGLE_MAPS_API_KEY']  # set to 'your_API_key'
    except KeyError as e:
        if logger:
            logger.error("Please set your GOOGLE_MAPS_API_KEY environment variable")
        else:
            print("Please set your GOOGLE_MAPS_API_KEY environment variable")
        sys.exit(1)

    # Unpack lats/lons
    ullat, ullon = nw_lat_long
    lrlat, lrlon = se_lat_long

    # convert all these coordinates to pixels
    ulx, uly = latlon_to_pixels(ullat, ullon, zoom)
    lrx, lry = latlon_to_pixels(lrlat, lrlon, zoom)

    dx, dy = lrx - ulx, uly - lry  # Calculate total pixel dimensions of final image
    cols, rows = ceil(dx / (MAXSIZE * scale)), ceil(dy / (MAXSIZE * scale))  # Calculate rows and columns

    logger.debug("GOOGLE_MAPS_API_KEY: {}".format(GOOGLE_MAPS_API_KEY))

    print("Retrieve {} image tiles from Google static-maps API".format(cols * rows))
    user_input = input("Do you want to continue y/n: ")
    if user_input.lower() == 'n':
        sys.exit(0)
    else:
        # calculate pixel dimensions of each small image
        width = ceil(dx / cols)
        height = ceil(dy / rows)
        heightplus = height + LOGO_CUTOFF * scale

        # assemble the image from stitched
        final = Image.new('RGB', (int(dx), int(dy)))
        for x in range(cols):
            for y in range(rows):
                dxn = width * (0.5 + x)
                dyn = height * (0.5 + y)
                latn, lonn = pixels_to_latlon(
                    ulx + dxn, uly - dyn - (LOGO_CUTOFF * scale) / 2, zoom)
                position = ','.join((str(latn / DEGREE), str(lonn / DEGREE)))
                logger.info("Getting image tile from column {0} row {1} for position {2}".format(x, y, position))
                urlparams = {
                    'center': position,
                    'zoom': str(zoom),
                    'size': '%dx%d' % (int(width), int(heightplus)),
                    'maptype': 'satellite',
                    'sensor': 'false',
                    'scale': scale
                }
                logger.debug("urlparams: {}".format(urlparams))
                if GOOGLE_MAPS_API_KEY is not None:
                    urlparams['key'] = GOOGLE_MAPS_API_KEY

                url = 'http://maps.google.com/maps/api/staticmap'
                try:
                    response = requests.get(url, params=urlparams)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(e)
                    sys.exit(1)

                im = Image.open(BytesIO(response.content))
                final.paste(im, (int(x * width), int(y * height)))

        return final


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Prevent logging from propagating to the root logger
        logger.propagate = 0
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
    return logger


def main():
    # Configure command-line options
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('-d', '--debug', help='Enable debug output', action='store_true')
    parser.add_argument('-l', '--logfile', help='Logfile to write', nargs=1)
    parser.add_argument('-nw', '--northwest', help='NW Lat/Lon', nargs=2)
    parser.add_argument('-se', '--southeast', help='SE Lat/Lon', nargs=2)
    parser.add_argument('-z', '--zoom', help='Zoom level from 1 (world) to 20+ (buildings), default is 18', nargs=1)
    parser.add_argument('--scale', help='Scale factor for Google Maps API (1 or 2)', type=int, choices=[1,2], default=1)
    options = parser.parse_args()

    # Configure logging
    global logger
    logger = get_logger(__name__)
    logger.setLevel(logging.INFO)
    if options.logfile:
        fh = logging.FileHandler(str(options.logfile[0]))
        logger.addHandler(fh)
    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Command-line options: {}".format(options))

    nw_lat_long = (float(options.northwest[0]) * DEGREE, float(options.northwest[1]) * DEGREE)
    se_lat_long = (float(options.southeast[0]) * DEGREE, float(options.southeast[1]) * DEGREE)

    # Get satellite image
    result = get_maps_image(
        nw_lat_long, se_lat_long, zoom=int(options.zoom[0]), scale=options.scale
    )
    result.show()  # Show onscreen
    result.save("satellite_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".bmp")  # Save image


if __name__ == "__main__":
    main()
