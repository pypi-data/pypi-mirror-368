import os
import requests
from tqdm import tqdm
from loguru import logger
from datetime import datetime
from izisat.misc.utils import Utils
from izisat.misc.files import Files
from izisat.misc.dates import Dates


class Connections:
    def __init__(self):
        pass
    
    
    def access_token(self, username: str, password: str) -> str:
        """
        Obtain an access token for accessing the Sentinel API.

        Parameters:
        -----------
        username: str
            The username for authentication.
        password: str
            The password for authentication.

        Returns:
        --------
        access_token, refresh_token, dt_now: Tuple[str, str, datetime]
            A tuple containing the access token, refresh token, and the current datetime when the tokens were obtained.
        """
        logger.info("Trying to establish connection with Copernicus API.")
        data = {
            "client_id": "cdse-public",
            "username": username,
            "password": password,
            "grant_type": "password",
            
            }
        try:
            r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
            )
            dt_now = datetime.now()
            r.raise_for_status()
        except Exception as e:
            raise Exception(
                f"Keycloak token creation failed. Response from the server was: {r.json()}"
                )
            
        logger.success("Connection estalished")
        access_token = r.json()["access_token"]
        refresh_token = r.json()["refresh_token"]
        return access_token, refresh_token, dt_now

    def refresh_access_token(self, refresh_token: str):
        """
        Refresh the access token using the provided refresh token.

        Parameters:
        -----------
        refresh_token : str
            The refresh token obtained during the initial authentication process.

        Returns:
        --------
        r.json()["access_token"], dt_now: Tuple[str, datetime]
        A tuple containing the new access token and the current datetime when the refresh was performed.
    """
        data = {
            "client_id": "cdse-public",
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            r = requests.post(
                "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                data=data,
            )
            dt_now = datetime.now()
            r.raise_for_status()
        except Exception as e:
            raise Exception(
                f"Access token refresh failed. Reponse from the server was: {r.json()}"
            )

        return r.json()["access_token"], dt_now

    def retrieve_sent_prod_from_query(self, params):
        """
        Retrieve Sentinel products from a specified query.

        Parameters:
        -----------
        params: str
            The query parameters to be appended to the URL.

        Returns:
        ---------
        response.json()['value']: list
            List of Sentinel products, each represented as a dictionary.
        None 
            if no products are found.
        """
        logger.info("Searching Sentinel products...")
        url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
        url_complet  = url + params
        response = requests.get(url_complet)
        if response.status_code == 200:
            if not response.json()['value']:
                logger.warning("There is no Sentinel data available with this parameters.")
                return None
            
            for product in response.json()['value']:
                if product['Online']:
                    product_name = response.json()['value']
                    logger.success(f"Found successfully {len(product_name)} products!")
                    return response.json()['value'] 
        else:
            # If status code is not 200, raise an exception to trigger the retry mechanism
            response.raise_for_status()
            

    def retrieve_bands_for_resolution(self, session, headers, response, resolution, band_list, url_index):
        """
        Retrieve links for bands at a specific resolution for Sentinel 2 type L2A.

        Parameters:
        -----------
        session: requests.Session
            The active session for making HTTP requests.
        headers: dict
            The headers to include in the HTTP request.
        response: requests.Response
            The response object containing information about the product.
        resolution: str
            The resolution category ('10m', '20m', '60m').
        band_list: list
            List of bands to retrieve links for.
        url_index: int
            The index in the response JSON where the URL for bands is located.

        Returns:
        --------
        url_bands_resolution: list
            List of lists containing band names and their corresponding URLs.
            
        Example:
        --------
        session = requests.Session()
        headers = {'Authorization': 'Bearer YOUR_ACCESS_TOKEN'}
        response = session.get("https://example.com/api/products/1234")
        resolution = "10m"
        band_list = ["band1", "band2"]
        url_index = 0

        bands_links = retrieve_bands_for_resolution(session, headers, response, resolution, band_list, url_index)

        """
        url_resolution = response.json()["result"][url_index]["Nodes"]["uri"]
        response_resolution = session.get(url_resolution, headers=headers, stream=True)
        url_bands_resolution = []

        for band in band_list:
            url_bands = response_resolution.json()["result"]
            for product in url_bands:
                # Ensure the band name contains the resolution string (e.g., "10m", "20m")
                # and the specific band (e.g., "B02")
                if f"_{resolution}" in product["Name"] and band in product["Name"]:
                    item_to_append = [product["Name"], product["Nodes"]["uri"]]
                    url_bands_resolution.append(item_to_append)
        
        logger.success(f"Links successfully retrieved for bands {band_list} in resolution {resolution}")        
        return url_bands_resolution


          
        
    def get_links_l1c_product(self, access_token, product_id, bands):
        """
        Retrieve links for bands in a Level-1C (L1C) product.

        Parameters:
        -----------
        access_token: str
            The access token for authentication.
        product_id: str
            The ID of the Sentinel product.
        bands: list
            List of bands to retrieve links for.

        Returns:
        --------
        url_l1c_bands: list
            List of lists containing band names and their corresponding URLs.

        Example:
        --------
        access_token = "YOUR_ACCESS_TOKEN"
        product_id = "1234567890"
        bands = ["band1", "band2"]

        l1c_bands_links = get_links_l1c_product(access_token, product_id, bands)
        """
        url_l1c_bands = {}
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({product_id})/Nodes"

        try:
            logger.info("Starting connection to search for band links...")
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, headers=headers, stream=True)
            
            #### Trying to download specific bands #########################
            #### Trying to download specific bands #########################
            url_1 = response.json()['result'][0]["Nodes"]['uri']
            response_1 = session.get(url_1, headers=headers, stream=True)
            url_2 = next(item['Nodes']['uri'] for item in response_1.json().get('result', []) if item.get('Id') == 'GRANULE')
            response_2 = session.get(url_2, headers=headers, stream=True)
            url_3 = response_2.json()["result"][0]["Nodes"]["uri"]
            response_3 = session.get(url_3, headers=headers, stream=True)
            url_4 = next(item['Nodes']['uri'] for item in response_3.json().get('result', []) if item.get('Id') == 'IMG_DATA')
            response_4 = session.get(url_4, headers=headers, stream=True)
            products = response_4.json()["result"]
            for product in products:
                for resolution, band_list in bands.items():
                    for band in band_list:
                        if band in product["Name"]:
                            itens_to_append = [product["Name"], product["Nodes"]["uri"]]
                            url_l1c_bands[resolution] = itens_to_append
                            break
            logger.success(f"Links for bands {bands} successfully retrieved")
            
            return url_l1c_bands

        except Exception as e:
            raise requests.exceptions.RequestException(e)
        
        
        
        
    def get_links_l2a_product(self, access_token, product_id, bands):
        """
        Retrieve links for bands in a Level-2A (L2A) product.

        Parameters:
        -----------
        access_token: str
            The access token for authentication.
        product_id: str
            The ID of the Sentinel product.
        bands: dict
            Dictionary mapping resolutions to lists of bands.

        Returns:
        --------
        resolution_links: dict
            Dictionary containing resolution-wise lists of band names and their corresponding URLs.
            
        Example:
        --------
        access_token = "YOUR_ACCESS_TOKEN"
        product_id = "1234567890"
        bands = {"10m": ["band1", "band2"], "20m": ["band3", "band4"]}

        l2a_links = get_links_l2a_product(access_token, product_id, bands)
        """
        resolution_links = {}
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({product_id})/Nodes"

        try:
            logger.info("Starting connection to search for band links...")
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, headers=headers, stream=True)
            
            #### Trying to download specific bands #########################
            url_1 = response.json()['result'][0]["Nodes"]['uri']
            response_1 = session.get(url_1, headers=headers, stream=True)
            url_2 = next(item['Nodes']['uri'] for item in response_1.json().get('result', []) if item.get('Id') == 'GRANULE')
            response_2 = session.get(url_2, headers=headers, stream=True)
            url_3 = response_2.json()["result"][0]["Nodes"]["uri"]
            response_3 = session.get(url_3, headers=headers, stream=True)
            url_4 = next(item['Nodes']['uri'] for item in response_3.json().get('result', []) if item.get('Id') == 'IMG_DATA')
            response_4 = session.get(url_4, headers=headers, stream=True)
            
            # Mapping resolution to url_index
            resolution_to_url_index = {'10m': 0,
                                        '20m': 1,
                                        '60m': 2
                                        }
            
            for resolution, band_list in bands.items():
                logger.info(f"Searching links for resolution {resolution}...")
                url_index = resolution_to_url_index.get(resolution, -1)
    
                if url_index != -1:
                    resolution_links[resolution] = self.retrieve_bands_for_resolution(
                        session, headers, response_4, resolution, band_list, url_index)
                else:
                    # Handle the case when resolution is not found in the mapping
                    logger.warning(f"Resolution {resolution} not mapped to a valid url_index.")

        except Exception as e:
            raise requests.exceptions.RequestException(e)

        return resolution_links
            

        
    def retrieve_bands_links(self, access_token, products_info, bands_dict):
        """
        Retrieve links for bands in Sentinel products.

        Parameters:
        -----------
        access_token: str
            The access token for authentication.
        products_info: list
            List of lists containing information about Sentinel products.
        bands_dict: dict
            Dictionary mapping product types to dictionaries of resolutions and their corresponding bands.

        Returns:
        --------
        all_links: dict
            Dictionary containing links for bands in Sentinel products.
            The structure is {product_name: {product_type: {resolution: [(band_name, band_link), ...], ...}, ...}, ...}.

        Example:
        --------
        access_token = "YOUR_ACCESS_TOKEN"
        products_info = [
            ["product_id_1", "product_name_1", "path_1", "date_1", "tile_1", "platform_1", "L1C"],
            ["product_id_2", "product_name_2", "path_2", "date_2", "tile_2", "platform_2", "L2A"],
            ]
        bands_dict = {
            "L1C": ["band1", "band2"],
            "L2A": {"10m": ["band3", "band4"], "20m": ["band5", "band6"]},
            }

        links = retrieve_bands_links(access_token, products_info, bands_dict)
        """
        all_links = {}

        for product_info in products_info:
            product_id = product_info[0]
            product_type = product_info[6]
            product_name = product_info[1]
            product_name = product_name.replace(".SAFE", "")
            logger.info(f"Getting bands links for: {product_name}")
            
            if product_type == "L1C":
                logger.info(f"{product_name} is type {product_type}...")
                l1c_bands = bands_dict["L1C"]
                links_l1c = self.get_links_l1c_product(access_token, product_id, l1c_bands)
                all_links.setdefault(product_name, {}).setdefault("L1C", links_l1c)
            elif product_type == "L2A":
                logger.info(f"{product_name} is type {product_type}...")
                l2a_bands = bands_dict["L2A"]
                links_l2a = self.get_links_l2a_product(access_token, product_id, l2a_bands)
                
                all_links.setdefault(product_name, {}).setdefault("L2A", links_l2a)
        
        return all_links
    

            
    def download(self, access_token, url, output_path, product_name, name):
        """
        Download data from a specified URL using an access token.

        Parameters:
        -----------
        access_token: str
            The access token obtained from the Sentinel API for authentication.
        url: str
            The URL of the data to be downloaded.
        output_path: str
            The local path where the downloaded data will be saved.
        product_name: str
            The name of the Sentinel product associated with the data.
        name: str
            The name or identifier for the downloaded data.

        Returns:
        --------
        None
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            logger.info("Starting connection to download data...")
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, headers=headers, stream=True)
            
            if response.status_code == 200:
                logger.success("Connection estabilished!")
                logger.info(f"Starting download of: {name}")
                # Get the file size from the 'Content-Length' header of the response
                total_size = int(response.headers.get('Content-Length', 0))

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # Open a file for writing in binary mode
                with open(output_path, "wb") as file, tqdm(desc="Downloading", total=total_size, unit="B", unit_scale=True, unit_divisor=1024, ) as bar:
                    # Iterate over the content in chunks (chunk_size=8192 bytes)
                    for chunk in response.iter_content(chunk_size=8192):
                        # Check if the chunk is not empty
                        if chunk:
                            # Write the chunk to the file
                            file.write(chunk)
                            # Update the progress bar with the size of the current chunk
                            bar.update(len(chunk))
                logger.success(f"Data {name} successfuly downloaded for product {product_name}")
            else:
                # If the response status code is not 200, raise an exception
                response.raise_for_status()
        except Exception as e:
            raise requests.exceptions.RequestException(e)
        
    def download_bands(self, access_token, products_info, bands_links, base_dir, dt_access_token, refresh_token, tile):
        """
        Download bands for Sentinel products based on the provided links.

        Parameters:
        -----------
        access_token: str
            The access token obtained from the Sentinel API for authentication.
        products_info: List[List]
            List of lists containing information about Sentinel products.
        bands_links: Dict[str, Any]
            Dictionary containing links to bands for each Sentinel product.
        base_dir: str
            The base directory where the downloaded bands will be saved.

        Returns:
        --------
        None
        """
        
        utils = Utils()
        files = Files()
        dates = Dates()
        for product_info in products_info:                   
            product_id = product_info[0]
            product_type = product_info[6]
            product_name = product_info[1]
            product_date = product_info[3]
            product_platform = product_info[5]
            product_tile = product_info[4]
            product_name = product_name.replace(".SAFE", "")
            logger.info(f"Starting download process for product {product_name}")
        
            
            if tile == product_tile:
                if product_name in bands_links:
                    if "MSIL1C" in product_name:
                        product = bands_links[product_name]
                        key = next(iter(product))
                        # Access the nested lists
                        products_link_lists = product[key]
                        for nested_list in products_link_lists:
                            name, link = nested_list
                            link_mod = utils.modify_string(link)
                            filepath = files.check_file_exist(base_dir, product_platform, product_date, product_tile, product_type, name)
                            logger.info(f"Starting download process for band {name}")
                            if filepath[0] == True:
                                logger.warning(f"Band {name} Already downloaded")
                            else:
                                dt_now = datetime.now()
                                expired = dates.is_token_expired(dt_access_token, dt_now)
            
                                if expired:
                                    access_token, dt_access_token = self.refresh_access_token(refresh_token)   
                                logger.info("Data has not been downloaded. Starting data downloaded...")  
                                self.download(access_token, link_mod, filepath[1], product_name, name)
                                    
                    elif "MSIL2A" in product_name:
                        product = bands_links[product_name]
                        key = next(iter(product))
                        # Access the nested lists
                        products_link_lists = product[key]
                        for resolution, bands_links_list in products_link_lists.items():
                            for band in bands_links_list:
                                name = band[0]
                                link = band[1]
                                link_mod = utils.modify_string(link)
                                filepath = files.check_file_exist(base_dir, product_platform, product_date, product_tile, product_type, name, resolution)

                                logger.info(f"Starting download process for band {name}")
                                if filepath[0] == True:
                                    logger.warning(f"Band {name} Already downloaded")
                                else:
                                    logger.info("Data has not been downloaded. Starting data downloaded...")
                                    dt_now = datetime.now()
                                    expired = dates.is_token_expired(dt_access_token, dt_now)
            
                                    if expired:
                                        access_token, dt_access_token = self.refresh_access_token(refresh_token)  
                                    self.download(access_token, link_mod, filepath[1], product_name, name)
                                    
            elif tile == None:
               if product_name in bands_links:
                    if "MSIL1C" in product_name:
                        product = bands_links[product_name]
                        key = next(iter(product))
                        # Access the nested lists
                        products_link_lists = product[key]
                        for resolution, bands_links_list in products_link_lists.items():
                            for band in [bands_links_list]:
                                name = band[0]
                                link = band[1]
                                link_mod = utils.modify_string(link)
                                filepath = files.check_file_exist(base_dir, product_platform, product_date, product_tile, product_type, name, resolution)

                                logger.info(f"Starting download process for band {name}")
                                if filepath[0] == True:
                                    logger.warning(f"Band {name} Already downloaded")
                                else:
                                    logger.info("Data has not been downloaded. Starting data downloaded...")
                                    dt_now = datetime.now()
                                    expired = dates.is_token_expired(dt_access_token, dt_now)
            
                                    if expired:
                                        access_token, dt_access_token = self.refresh_access_token(refresh_token)  
                                    self.download(access_token, link_mod, filepath[1], product_name, name)
                                    
                    elif "MSIL2A" in product_name:
                        product = bands_links[product_name]
                        key = next(iter(product))
                        # Access the nested lists
                        products_link_lists = product[key]
                        for resolution, bands_links_list in products_link_lists.items():
                            for band in bands_links_list:
                                name = band[0]
                                link = band[1]
                                link_mod = utils.modify_string(link)
                                filepath = files.check_file_exist(base_dir, product_platform, product_date, product_tile, product_type, name, resolution)

                                logger.info(f"Starting download process for band {name}")
                                if filepath[0] == True:
                                    logger.warning(f"Band {name} Already downloaded")
                                else:
                                    logger.info("Data has not been downloaded. Starting data downloaded...")
                                    dt_now = datetime.now()
                                    expired = dates.is_token_expired(dt_access_token, dt_now)
            
                                    if expired:
                                        access_token, dt_access_token = self.refresh_access_token(refresh_token)  
                                    self.download(access_token, link_mod, filepath[1], product_name, name)
            else:
                logger.warning("Tile not selected to download")                  

               