
from typing import Optional
from izisat.misc.raster_processing import RasterProcessing        
from izisat.misc.connections import Connections
from izisat.misc.utils import Utils
from izisat.misc.files import Files
from loguru import logger
import geopandas as gpd
from datetime import datetime, timedelta
from shapely.geometry import box
import os
from dataclasses import dataclass
from typing import List, Dict, Union, Literal, Any
import numpy as np
from collections import defaultdict
from izisat.misc.dto import CompositeRaster, RasterBand

@dataclass
class CompositeData:
    rgb: Optional[str] = None
    ndvi: Optional[str] = None
    evi: Optional[str] = None
    cir: Optional[str] = None
    cloud_mask: Optional[str] = None

class IZISentinel:
    def __init__(self, output_base_path, username, password):
        """Initializes the Sentinel2_Band_Downloader instance."""
        self.output_base_path = output_base_path
        self.access_token, self.refresh_token, self.dt_access_token = self.connect_to_api(username, password)
        
    def connect_to_api(self, username, password):
        """Connects to the Sentinel API and obtains an access token."""
        connections = Connections()
        access_token, refresh_token, dt_access_token = connections.access_token(username, password)
        return access_token, refresh_token, dt_access_token
                                      
    def construct_query(self, geodataframe, end_date, cloud_cover_percentage, type, platform_name):
        """Constructs a query for retrieving Sentinel-2 products based on specified parameters."""
        utils = Utils()
        start_date = (end_date - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        projected_gdf = geodataframe.to_crs(geodataframe.estimate_utm_crs('SIRGAS 2000'))
        geodataframe = projected_gdf.buffer(1000)
        geodataframe = geodataframe.to_crs(4674)
        minx, miny, maxx, maxy = geodataframe.total_bounds
        bbox_geom = box(minx, miny, maxx, maxy)
        bbox_gdf = gpd.GeoDataFrame(geometry=[bbox_geom], crs=geodataframe.crs)
        footprint = bbox_gdf.iloc[0].geometry.wkt
        query = utils.construct_query_for_sentinel2_products(footprint, start_date, end_date, cloud_cover_percentage, type, platform_name)
        return query
        
    def products_from_sentinel_2(self, params):
        """Retrieves Sentinel-2 products based on the provided query parameters."""
        connections = Connections()
        products = connections.retrieve_sent_prod_from_query(params)
        return products
    
    def get_products_info(self, products):
        """Retrieves information about Sentinel-2 products."""
        utils = Utils()
        products_info = utils.retrieve_products_info(products)
        return products_info
    
    def output_folder(self, products_info, bands_dict):
        """Creates output folders to save downloaded bands."""
        files = Files()
        directory_paths = files.create_output_folders(self.output_base_path, products_info, bands_dict)
        return directory_paths
    
    def get_bands_links(self, products_info, bands_dict):
        """Retrieves links to bands for Sentinel-2 products."""
        connections = Connections()
        bands_links = connections.retrieve_bands_links(self.access_token, products_info, bands_dict)
        return bands_links
    
    def download_band(self, products_info, bands_link, base_dir, tile):
        """Downloads bands for Sentinel-2 products based on the provided links."""
        connections = Connections()
        connections.download_bands(self.access_token, products_info, bands_link, base_dir, self.dt_access_token, self.refresh_token, tile)

    def download_sentinel2_bands(self, products, bands_dict, tile):
        """Orchestrates the download process for Sentinel-2 bands."""
        utils = Utils()
        if products is None:
            logger.warning("Stopping further execution.")
        else:
            products_info = self.get_products_info(products)
            self.output_folder(products_info, bands_dict)
            links = self.get_bands_links(products_info, bands_dict)
            products=self.download_band(products_info, links, self.output_base_path, tile)

            downloaded_dict = utils.generate_sentinel2_band_paths_nested_by_tile(self.output_base_path, products_info)
            return downloaded_dict

    def get_composite_data(self, gdf, downloaded_dict, output_rgb=None, output_ndvi=None, output_evi=None, output_cir=None, output_cloud=None, threshold=0.4, average_over=2, dilation_size=10) -> Dict[str, CompositeRaster]:
        raster_processing = RasterProcessing()
        first_key = next(iter(downloaded_dict))
        first_entry = downloaded_dict[first_key]
        if len(first_entry) == 1:
            band_paths = first_entry[0]
            cropped_bands: Dict[str, RasterBand] = raster_processing.get_cropped_bands_no_merge(gdf, band_paths)
        elif len(first_entry) > 1:
            cropped_bands: Dict[str, RasterBand] = raster_processing.get_cropped_bands_with_merge(gdf, first_entry)

        if output_rgb is not None:
            if not os.path.exists(output_rgb):
                os.makedirs(os.path.dirname(output_rgb), exist_ok=True)
                raster_processing.create_rgb(cropped_bands, output_rgb)
            else:
                logger.warning(f'Arquivo {output_rgb} já existe no diretório.')

        if output_ndvi is not None:
            if not os.path.exists(output_ndvi):
                os.makedirs(os.path.dirname(output_ndvi), exist_ok=True)
                raster_processing.create_ndvi(cropped_bands, output_ndvi)
            else:
                logger.warning(f'Arquivo {output_ndvi} já existe no diretório.')

        if output_evi is not None:
            if not os.path.exists(output_evi):
                os.makedirs(os.path.dirname(output_evi), exist_ok=True)
                raster_processing.create_evi(cropped_bands, output_evi)
            else:
                logger.warning(f'Arquivo {output_evi} já existe no diretório.')
        
        if output_cir is not None:
            if not os.path.exists(output_cir):
                os.makedirs(os.path.dirname(output_cir), exist_ok=True)
                raster_processing.create_cir(cropped_bands, output_cir)
            else:
                logger.warning(f'Arquivo {output_cir} já existe no diretório.')

        if output_cloud is not None:
            if not os.path.exists(output_cloud):
                raster_processing.create_cloud_mask(cropped_bands, output_cloud, threshold=threshold, average_over=average_over, dilation_size=dilation_size)
            else:
                logger.warning(f'Arquivo {output_cloud} já existe no diretório.')

    def get_satellite_image(self, geodataframe, end_date, cloud_cover_percentage, type='L2A', platform_name='SENTINEL-2', bands_dict={"L2A": {"10m": ["B02", "B03", "B04", "B08"],"20m": ["B05", "B06", "B07", "B8A", "B11", "B12"],"60m": ["B01", "B09", "B10"],"mask": ["datMask"]}, 'L1C':{'60m': ['B10']}}, output_rgb=None, output_ndvi=None, output_evi=None, output_cir=None, output_cloud=None, threshold=0.4, average_over=2, dilation_size=10):
        product_list = []
        for type in ['L2A', 'L1C']:
            query = self.construct_query(geodataframe, end_date, cloud_cover_percentage, type, platform_name)
            products = self.products_from_sentinel_2(query)
            product_list.extend(products)
        if not product_list:
            return
        downloaded_dict = self.download_sentinel2_bands(product_list, bands_dict, None)
        self.get_composite_data(geodataframe, downloaded_dict, output_rgb, output_ndvi, output_evi, output_cir, output_cloud, threshold=threshold, average_over=average_over, dilation_size=dilation_size)
        return CompositeData(
            rgb=output_rgb,
            ndvi=output_ndvi,
            evi=output_evi,
            cir=output_cir,
            cloud_mask=output_cloud
        )


if __name__ == '__main__':
    DOWNLOAD_FOLDER = '/home/ppz/Documentos/coding/izisat/auxiliary'
    MAX_CLOUD_COVER = 99
    BANDS_DICT = {"L2A": 
                  {"10m": ["B02", "B03", "B04", "B08"],
                   "20m": ["B05", "B06", "B07", "B8A", "B11", "B12"],
                   "60m": ["B01", "B09", "B10"],"mask": ["datMask"]}, 
                   'L1C':
                   {'60m': ['B10']}}
    PLATFORM_NAME = "SENTINEL-2"
    SATELLITE_TYPE = 'L1C'
    COPERNICUS_USER = 'anderson.stolfi22@gmail.com'
    COPERNICUS_PASSWD = '158695Ander!'



    downloader = IZISentinel(output_base_path=DOWNLOAD_FOLDER, username=COPERNICUS_USER, password=COPERNICUS_PASSWD)
    # gdf = gpd.read_file('/media/nvme1tb/enterprise_code/sentinela/auxiliary/FULL_20250709_VIEW.geojson')
   
    # gdf = gdf.dissolve(by='PROJETO').reset_index()
    # gdf = gdf[gdf['PROJETO'].isin(['Douradinho'])].copy()
    # gdf.to_file('teste.geojson', driver='GeoJSON')
    today = datetime(2025, 7, 26, 0, 0, 0)
    gdf = gpd.read_file('teste.geojson')

    logger.info(f'Baixando imagens do dia {today.strftime("%Y-%m-%d")}')

    # output_rgb = f'/home/ppz/Documentos/coding/izisat/auxiliary/raster_lake/rgb/teste_rgb_{today.strftime("%Y%m%d")}.tif'
    # output_ndvi = f'/home/ppz/Documentos/coding/izisat/auxiliary/raster_lake/ndvi/teste_ndvi_{today.strftime("%Y%m%d")}.tif'
    # output_cir = f'/home/ppz/Documentos/coding/izisat/auxiliary/raster_lake/cir/teste_cir_{today.strftime("%Y%m%d")}.tif'
    # output_evi = f'/home/ppz/Documentos/coding/izisat/auxiliary/raster_lake/evi/teste_evi_{today.strftime("%Y%m%d")}.tif'
    output_cloud = f'/home/ppz/Documentos/coding/izisat/auxiliary/raster_lake/cloud/teste_cloud_{today.strftime("%Y%m%d")}.tif'
    downloader.get_satellite_image(
                    geodataframe=gdf,
                    end_date=today,
                    cloud_cover_percentage=MAX_CLOUD_COVER,
                    type=SATELLITE_TYPE,
                    platform_name=PLATFORM_NAME,
                    bands_dict=BANDS_DICT,
                    # output_rgb=output_rgb,
                    # output_ndvi=output_ndvi,
                    # output_cir=output_cir,
                    # output_evi=output_evi,
                    output_cloud=output_cloud,
                    threshold=0.4,
                    average_over=4,
                    dilation_size=2
                )