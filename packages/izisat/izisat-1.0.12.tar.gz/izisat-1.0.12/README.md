# izisat

`izisat` is a Python library designed to facilitate the automated download of Sentinel-2 satellite imagery bands from the Copernicus Open Access Hub (previously SciHub). It provides functionalities to connect to the Copernicus API, construct queries based on geographical footprints and time ranges, retrieve product information, and download specified bands to a local directory structure.

## Features

*   **API Connection:** Securely connect to the Copernicus Open Access Hub using provided credentials.
*   **Query Construction:** Build complex queries for Sentinel-2 products based on:
    *   Geographical footprint (WKT format)
    *   Start and End Dates
    *   Cloud Cover Percentage
    *   Product Type (e.g., L2A)
    *   Platform Name (e.g., SENTINEL-2)
*   **Product Retrieval:** Fetch a list of available Sentinel-2 products matching the constructed query.
*   **Automated Folder Creation:** Organize downloaded bands into a structured directory based on product information (e.g., `auxiliary/Sentinel-2/YYYY/MM/DD/TILE/L2A/RESOLUTION/`).
*   **Band Downloading:** Download specific Sentinel-2 bands (e.g., B02, B03, B04, B08) for retrieved products.

## Installation

*(Placeholder: Add installation instructions here, e.g., using pip and a `requirements.txt` or `pyproject.toml`)*

## Usage

The `IZISentinel` class is the main entry point for interacting with the library. Below is an example demonstrating how to use `izisat` to download Sentinel-2 bands.

```python
import geopandas as gpd
from datetime import datetime, timedelta
from izisat.izisentinel import IZISentinel

# Configuration
DOWNLOAD_FOLDER = '/home/ppz/Documentos/coding/izisat/auxiliary' # Adjust as needed
MAX_CLOUD_COVER = 99
BANDS_DICT = {"L2A":{"10m": ["B02", "B03","B04", "B08"]}} # Specify bands and resolutions
PLATFORM_NAME = "SENTINEL-2"
SATELLITE_TYPE = 'L2A' # Level 2A products (bottom-of-atmosphere corrected)
COPERNICUS_USER='your_copernicus_username' # Replace with your Copernicus username
COPERNICUS_PASSWD='your_copernicus_password' # Replace with your Copernicus password

# Define date range
today = datetime.now().strftime('%Y-%m-%d')
one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

# Initialize the downloader
downloader = IZISentinel(output_base_path=DOWNLOAD_FOLDER)

# 1. Connect to Copernicus API
access_token, refresh_token, dt_access_token = downloader.connect_to_api(
    username=COPERNICUS_USER,
    password=COPERNICUS_PASSWD
)

# 2. Load geographical footprint (example using a GeoJSON file)
# Replace 'path/to/your/farm.geojson' with the actual path to your GeoJSON file
# The GeoJSON should contain a polygon representing your area of interest.
try:
    farm = gpd.read_file('/home/ppz/Documentos/coding/forestry_monitor/data/vectors/farms/farms.geojson')
    footprint = farm.iloc[0].geometry.wkt # Assuming the first feature's geometry is the desired footprint
except Exception as e:
    print(f"Error loading GeoJSON or extracting footprint: {e}")
    print("Please ensure 'forestry_monitor/data/vectors/farms/farms.geojson' exists and is valid, or provide a WKT string directly.")
    footprint = "POLYGON ((<lon1> <lat1>, <lon2> <lat2>, ...))" # Example placeholder for direct WKT

# 3. Construct the query
query = downloader.construct_query(
    footprint=footprint,
    end_date=today,
    start_date=one_week_ago,
    cloud_cover_percentage=MAX_CLOUD_COVER,
    type=SATELLITE_TYPE,
    platform_name=PLATFORM_NAME
)

# 4. Retrieve products
products = downloader.products_from_sentinel_2(query)

# 5. Download specified bands
if products:
    images_downloaded = downloader.download_sentinel2_bands(
        access_token,
        products,
        BANDS_DICT,
        dt_access_token,
        refresh_token,
        tile=None # Specify a tile if you want to filter by tile, otherwise None
    )
    print(f"Downloaded images info: {images_downloaded}")
else:
    print("No products found for the given query.")
```

## Dependencies

The core dependencies for `izisat` include:

*   `loguru`: For logging.
*   `geopandas`: For handling geographical data (used in the example for footprint).
*   `datetime`: For date and time operations.

*(Note: Specific versions and other implicit dependencies from `izisat.misc` modules would be listed in `pyproject.toml` or `requirements.txt`)*

## Project Structure

```
.
├── auxiliary/
│   └── Sentinel-2/  # Default download location for Sentinel-2 bands
├── src/
│   └── izisat/
│       ├── __init__.py
│       ├── izisentinel.py  # Main class for Sentinel-2 band downloading
│       └── misc/
│           ├── __init__.py
│           ├── connections.py # Handles API connections to Copernicus
│           ├── dates.py       # Utility functions for date handling
│           ├── files.py       # Utility functions for file and directory operations
│           └── utils.py       # General utility functions (e.g., query construction, product info retrieval)
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

## How to Contribute

We welcome contributions to `izisat`! If you'd like to contribute, please follow these guidelines:

1.  **Reporting Bugs:** If you find a bug, please open an issue on the GitHub repository. Provide a clear and concise description of the bug, steps to reproduce it, and expected behavior.
2.  **Suggesting Features:** For new features or enhancements, open an issue to discuss your ideas.
3.  **Submitting Pull Requests:**
    *   Fork the repository and create a new branch for your changes.
    *   Ensure your code adheres to the project's coding style.
    *   Write clear and concise commit messages.
    *   Include tests for new features or bug fixes.
    *   Submit a pull request with a detailed description of your changes.

Thank you for your contributions!