import os
from loguru import logger
from datetime import datetime


class Files:
    def __init__(self):
        pass
    
    
    def save_path_sentinel2_data(self, dir_out, etc, date, type, tile, band=None):
        """
        Generate a directory path for Sentinel-2 data and create it if it doesn't exist.

        Parameters:
        ------------
        dir_out: str
            The base output directory.
        date: str
            The date in the format '%Y-%m-%dT%H:%M:%S.%fZ'.
        etc: str
            Additional information for the directory path.
        tile: str
            The tile information for the directory path.
        band: str, optional
            The band information for the directory path.

        Returns:
        ----------
        str 
            The path of the generated or existing directory.
        """
        dt_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Format the datetime object as 'YYYY/MM/DD'
        date = dt_object.strftime('%Y/%m/%d')

        if band is not None:
            directory = os.path.join(dir_out, etc, date, type, tile, band)
        else:
            directory = os.path.join(dir_out, etc, date, type, tile)

        if os.path.exists(directory):
            logger.warning(f"Directory {directory} already exists.")
            return directory
        else:
            os.makedirs(directory, exist_ok=True)
            logger.success(f"Directory {directory} created!")
            return directory
        
        
    def create_output_folders(self, output_base_path, products_info, bands_dict):
        """
        Create, if necessary, folders to save the downloaded bands.

        Parameters:
        -----------
        output_base_path: str
            The base path where the output folders will be created.
        products_info: list
            A list of product information, where each item contains:
            [product_id, product_name, product_path, product_origin_date, product_tile, product_platform_name, product_type]
        bands_dict: dict
            A dictionary containing information about bands for different product types and resolutions.

        Returns:
        --------
        created_directories: list
            A list of paths to the created output directories.
        """
        logger.info("Creating, if necessary, folders to save the downloaded bands...")
        created_directories = []
        for product_info in products_info:
            product_type = product_info[6]
            product_tile = product_info[4]
            product_date = product_info[3]
            product_plataform = product_info[5]
            if product_type == "L1C":
                directory_path = self.save_path_sentinel2_data(output_base_path, product_plataform, product_date, product_tile, product_type)
                created_directories.append(directory_path)
            elif product_type == "L2A":
                for resolution, _ in bands_dict.items():
                    if resolution == "L1C":
                        pass
                    else:
                        l2a_dict = bands_dict.get("L2A", {})
                        for resolution_key in l2a_dict:
                            directory_path = self.save_path_sentinel2_data(output_base_path, product_plataform, product_date, product_tile, product_type, resolution_key)
                            created_directories.append(directory_path)

        return created_directories


    def check_file_exist(self, base_dir, etc, date, tile, type, filename, resolution = None):
        """
        Check if a file exists based on the specified parameters.

        Parameters:
        -----------
        base_dir: str
            The base directory where the file is expected to exist.
        etc: str
            Additional subdirectory for categorization (e.g., product platform or other metadata).
        date: str
            The date of the product in 'YYYY-MM-DDTHH:MM:SS.sssZ' format.
        tile: str
            The tile identifier associated with the product.
        type: str
            The type of the product (e.g., 'L1C', 'L2A').
        filename: str
            The name of the file to check.
        resolution: str, optional
            The resolution category (e.g., 'resolution10m', 'resolution20m').
            If provided, the file path will include this resolution subdirectory.

        Returns:
        --------
        exists: bool
            True if the file exists, False otherwise.
        file_path: str
            The full path to the checked file.

        """
        date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Format datetime object as 'YYYY/MM/DD'
        date = date_obj.strftime('%Y/%m/%d')
        
        if resolution is None:
            file = os.path.join(base_dir, etc, date, tile, type, filename)
            return os.path.exists(file), file
        else:
            file = os.path.join(base_dir, etc, date, tile, type, resolution, filename)
            return os.path.exists(file), file
    
                    
    