# GMaps Image Fetcher

Simple tool to download image tiles from Google Maps via the Static-Maps API

![preview image](preview.PNG)

## How it works

* Give the tool two sets of latitudes and longitudes for the north-west and south-east of the area you wish to download
the imagery from
* The tool calculates how many individual image tiles it needs to get from Google's Static-Maps API and begins to
download them
* All image tiles are stitched together and a preview showed onscreen
* The image is also saved to a file

## Installation

### Prerequisites

* A GOOGLE_MAPS_API_KEY is required as per the T&Cs of Google's Static-Maps API (plenty of tutorials online showing you
how to generate this, Google it)

### Existing Python environment

If you wish to download this into an existing Python environment you can us pip to install the tool like so:

```bash
pip install git+https://github.com/joseph-holland/gmaps-image-fetcher.git

pip install -r requirements.txt
```

### Windows executable

If on Windows platform I've compiled a release of the tool into an exe using [PyInstaller](https://www.pyinstaller.org/)

Just download the latest release from the
[Release section](https://github.com/joseph-holland/gmaps-image-fetcher/releases) of the repo

## Running

1. Set your GOOGLE_MAPS_API_KEY environment variable

    Windows
    ```bash
    set GOOGLE_MAPS_API_KEY=AIzaS.............
    ```
    
    Linux
    ```bash
    export GOOGLE_MAPS_API_KEY=AIzaS.............
    ```
    
2. Run the tool and give it the NW lat/lon and SE lat/lon as well as a zoom level (1= world, 20=buildings)

    ```bash
    gmaps-image-fetcher.py -nw 53.369745 -6.348743 -se 53.348326 -6.296656 -z 16
    ```

3. The tool will calculate how many image tiles it will need to retrieve and prompt if you wish to continue

    ```bash
    Retrieve 15 image tiles from Google static-maps API
    Do you want to continue y/n: y
    ```

4. It will then download the image tiles, stitch them together, show the image onscreen and save to the local directory

    ![satellite sample](satellite_sample.PNG)