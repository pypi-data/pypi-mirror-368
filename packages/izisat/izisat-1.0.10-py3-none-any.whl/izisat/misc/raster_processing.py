import os
import rasterio
import rasterio.mask
from shapely import wkt
from shapely.geometry import mapping
from typing import Union, Optional, Tuple, Dict, List
from collections import defaultdict
from pathlib import Path
import geopandas as gpd
import numpy as np
from rasterio.crs import CRS
from rasterio.transform import from_origin
from rasterio.merge import merge
import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import reproject, Resampling, calculate_default_transform
import rasterio
from s2cloudless import S2PixelCloudDetector
from skimage.transform import resize
from izisat.misc.dto import RasterBand, CompositeRaster

BANDS_LIST = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"]
UTM_ZONES = {
            19:31979,
            20:31980,
            21:31981,
            22:31982,
            23:31983,
            24:31984,
            25:31985,
        }

class RasterProcessing:
    def __init__(self):
        pass

    def crop_band_by_footprint_wkt(self,
                                    jp2_path: str,
                                    footprint_wkt: str,
                                    output_path: str = None
                                ):
        """
        Crops a georeferenced JP2 image using a WKT footprint (MULTIPOLYGON).

        Args:
            jp2_path (str): Path to the .jp2 image (satellite band).
            footprint_wkt (str): WKT string of the footprint polygon (e.g. 'MULTIPOLYGON (...)').
            output_path (str, optional): Output .tif file path or directory. If None, nothing is saved.
            suffix (str): Suffix to append to the output file name if saving to a directory.

        Returns:
            dict: {
                "image": Cropped image as a NumPy array,
                "profile": Raster metadata dictionary,
                "output_name": Full output path if saved, else None
            }
        """
        # Convert WKT string to geometry
        geometry = [mapping(wkt.loads(footprint_wkt))]

        with rasterio.open(jp2_path) as src:
            cropped_image, transform = rasterio.mask.mask(src, geometry, crop=True)
            cropped_image = cropped_image.squeeze()
            profile = src.profile.copy()
            profile.update({
                "height": cropped_image.shape[0],
                "width": cropped_image.shape[1],
                "transform": transform,
                'driver': 'GTiff',
                'dtype': 'uint16',
                'compress': None,
                'tiled': False,
                'nodata': 0
            })
        if output_path is not None:
            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(cropped_image)
        return cropped_image, profile

    def ensure_array_in_epsg(self, array: np.ndarray, profile: dict, target_epsg: int):
        import numpy as np
        import rasterio
        from rasterio.io import MemoryFile
        from rasterio.warp import reproject, Resampling, calculate_default_transform
        from rasterio.transform import array_bounds
        """
        Garante que o array raster esteja no EPSG desejado. Se necessário, reprojeta.

        Parâmetros:
        - array: np.ndarray (2D)
        - profile: dict com as chaves: 'transform', 'crs', 'width', 'height'
        - target_epsg: int

        Retorna:
        - dst_array: np.ndarray reprojetado ou original
        - new_profile: dict atualizado
        """
        src_crs = profile.get("crs")
        dst_crs = rasterio.crs.CRS.from_epsg(target_epsg)

        if src_crs == dst_crs:
            new_profile = profile.copy()
            new_profile["crs"] = dst_crs
            return array, new_profile

        # Calcula os bounds a partir do transform
        bounds = array_bounds(profile["height"], profile["width"], profile["transform"])

        transform, width, height = calculate_default_transform(
            src_crs, dst_crs,
            profile["width"], profile["height"],
            *bounds
        )

        dst_array = np.empty((height, width), dtype=array.dtype)

        reproject(
            source=array,
            destination=dst_array,
            src_transform=profile["transform"],
            src_crs=src_crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest
        )

        new_profile = profile.copy()
        new_profile.update({
            "crs": dst_crs,
            "transform": transform,
            "width": width,
            "height": height
        })

        return dst_array, new_profile

    def get_cropped_bands_no_merge(self, gdf:gpd.GeoDataFrame, band_paths:Dict[str, str]) -> Dict[str, RasterBand]:
        cropped_bands = defaultdict(RasterBand)


        epsg = UTM_ZONES[int(os.path.basename(band_paths['B02']).split('_')[0][1:3])]
        gdf = gdf.to_crs(epsg)
        footprint_wkt = gdf.iloc[0].geometry.wkt
        
        for band in BANDS_LIST:
            path = band_paths.get(band)
            if path:
                cropped, profile = self.crop_band_by_footprint_wkt(path, footprint_wkt)
                cropped_bands[band] = RasterBand(
                    filepath=path,
                    valid=True,
                    array=cropped,
                    profile=profile
                )
        return cropped_bands

    def get_cropped_bands_with_merge(self, gdf: gpd.GeoDataFrame, band_dicts: list) -> Dict[str, RasterBand]:
        """
        Recorta e mescla múltiplas bandas de entrada organizadas como uma lista de dicionários.
        
        Parâmetros:
        - gdf: GeoDataFrame com a geometria para recorte.
        - band_dicts: lista de dicionários, cada um contendo os caminhos das bandas 'B02', 'B03', 'B04' e 'B08'.
        
        Retorna:
        - Tupla com arrays mesclados para cada banda: B02, B03, B04, B08 e o profile do merge.
        """        
        cropped_bands_by_type = {band: [] for band in BANDS_LIST}
        final_profile = None
        final_crs = gdf.estimate_utm_crs('SIRGAS 2000').to_epsg()

        # Recorta todas as bandas e armazena por tipo
        for band_paths in band_dicts:
            try:
                for band in BANDS_LIST:
                    path = band_paths.get(band)
                    if path:
                        epsg = UTM_ZONES[int(os.path.basename(path).split('_')[0][1:3])]
                        gdf = gdf.to_crs(epsg)
                        footprint_wkt = gdf.iloc[0].geometry.wkt
                        cropped, profile = self.crop_band_by_footprint_wkt(path, footprint_wkt)
                        cropped_bands_by_type[band].append((cropped, profile))
            except:
                pass

        merged_bands = []
        cropped_bands = defaultdict(RasterBand)
        for band in BANDS_LIST:
            datasets = []
            for cropped, profile in cropped_bands_by_type[band]:
                cropped_epsg, profile_epsg = self.ensure_array_in_epsg(cropped, profile, final_crs)
                profile_epsg.update({
                    'driver': 'GTiff',
                    'dtype': 'uint16',
                    'compress': None,
                    'tiled': False,
                    'nodata': 0
                })
                memfile = rasterio.io.MemoryFile()
                with memfile.open(**profile_epsg) as tmp:
                    tmp.write(cropped_epsg, 1)
                datasets.append(memfile.open())

            merged, out_transform = merge(datasets, method='first')
            merged_array = merged.squeeze()
            merged_bands.append(merged_array)
            profile = datasets[0].profile.copy()
            profile.update({
                "height": merged.shape[1],
                "width": merged.shape[2],
                "transform": out_transform,
                "count": 1,
                "nodata": datasets[0].nodata
            })
            cropped_bands[band] = RasterBand(
                filepath=path,
                valid=True,
                array=merged_array,
                profile=profile
            )
    
        return cropped_bands


    def create_rgb(self, cropped_bands, output_path=None) -> CompositeRaster:
        
        b02_array = cropped_bands.get('B02').array
        b03_array = cropped_bands.get('B03').array
        b04_array = cropped_bands.get('B04').array
        reference_profile = cropped_bands.get('B02').profile
        if not (b02_array.shape == b03_array.shape == b04_array.shape):
            raise ValueError("As bandas devem ter as mesmas dimensões")

        rgb_array = np.stack([b04_array, b03_array, b02_array], axis=0)

        profile = reference_profile.copy()
        profile.update({
            'count': 3,
            'dtype': rgb_array.dtype,
            'driver': 'GTiff'
        })

        if output_path:
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(rgb_array)

        composite_raster = CompositeRaster(
            composition='rgb',
            bands={
                'B02': cropped_bands.get('B02'),
                'B03': cropped_bands.get('B03'),
                'B04': cropped_bands.get('B04')
            },
            filepath=output_path,
            valid=True
        )
        return composite_raster

    
    def create_cir(self, cropped_bands, output_path=None) -> CompositeRaster:

        b08_array = cropped_bands.get('B08').array
        b04_array = cropped_bands.get('B04').array
        b03_array = cropped_bands.get('B03').array
        reference_profile = cropped_bands.get('B08').profile
        
        if not (b08_array.shape == b04_array.shape == b03_array.shape):
            raise ValueError("As bandas devem ter as mesmas dimensões")

        # Cria array CIR no formato (3, altura, largura)
        cir_array = np.stack([b08_array, b04_array, b03_array], axis=0)  # (R=NIR, G=Red, B=Green)

        # Atualiza o perfil para refletir 3 bandas
        profile = reference_profile.copy()
        profile.update({
            'count': 3,
            'dtype': cir_array.dtype,
            'driver': 'GTiff'
        })

        # Salva ou retorna
        if output_path:
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(cir_array)

        composite_raster = CompositeRaster(
            composition='cir',
            bands={
                'B08': cropped_bands.get('B08'),
                'B04': cropped_bands.get('B04'),
                'B03': cropped_bands.get('B03')
            },
            filepath=output_path,
            valid=True
        )
        return composite_raster


    def create_ndvi(self, cropped_bands, output_path=None):
        
        b04_array = cropped_bands.get('B04').array  # Red
        b08_array = cropped_bands.get('B08').array  # NIR
        reference_profile = cropped_bands.get('B08').profile

        # Verifica se as dimensões batem
        if b04_array.shape != b08_array.shape:
            raise ValueError("As bandas devem ter as mesmas dimensões")

        # Converte para float32 para evitar problemas de divisão inteira
        b04 = b04_array.astype('float32')
        b08 = b08_array.astype('float32')

        # NDVI = (NIR - Red) / (NIR + Red)
        denominator = b08 + b04
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (b08 - b04) / denominator
            ndvi[np.isnan(ndvi)] = -9999  # valor nodata

        # Atualiza o perfil
        profile = reference_profile.copy()
        profile.update({
            'count': 1,
            'dtype': 'float32',
            'driver': 'GTiff',
            'nodata': -9999
        })

        if output_path:
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(ndvi, 1)

        composite_raster = CompositeRaster(
            composition='ndvi',
            bands={
                'B04': cropped_bands.get('B04'),
                'B08': cropped_bands.get('B08')
            },
            filepath=output_path,
            valid=True
        )
        return composite_raster

    def create_evi(self, cropped_bands, output_path=None):

        b02_array = cropped_bands.get('B02').array  # Blue
        b04_array = cropped_bands.get('B04').array  # Red
        b08_array = cropped_bands.get('B08').array  # NIR
        reference_profile = cropped_bands.get('B08').profile

        # Verifica se as dimensões batem
        if not (b02_array.shape == b04_array.shape == b08_array.shape):
            raise ValueError("As bandas devem ter as mesmas dimensões")

        # Converte para float32
        b02 = b02_array.astype('float32') / 10000 # Blue
        b04 = b04_array.astype('float32') / 10000 # Red
        b08 = b08_array.astype('float32') / 10000  # NIR

        # Parâmetros do EVI
        G = 2.5
        C1 = 6.0
        C2 = 7.5
        L = 1.0

        # Fórmula do EVI
        denominator = b08 + C1 * b04 - C2 * b02 + L
        with np.errstate(divide='ignore', invalid='ignore'):
            evi = G * ((b08 - b04) / denominator)
            evi[np.isnan(evi)] = -9999  # valor nodata

        # Atualiza o perfil
        profile = reference_profile.copy()
        profile.update({
            'count': 1,
            'dtype': 'float32',
            'driver': 'GTiff',
            'nodata': -9999
        })

        # Salva ou retorna
        if output_path:
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(evi, 1)

        composite_raster = CompositeRaster(
            composition='evi',
            bands={
                'B02': cropped_bands.get('B02'),
                'B04': cropped_bands.get('B04'),
                'B08': cropped_bands.get('B08')
            },
            filepath=output_path,
            valid=True
        )
        return composite_raster


    def pad_or_crop(self, arr, target_shape):
        arr_rows, arr_cols = arr.shape
        target_rows, target_cols = target_shape

        # Crop se for maior
        cropped = arr[:target_rows, :target_cols]

        # Pad se for menor
        pad_rows = max(0, target_rows - cropped.shape[0])
        pad_cols = max(0, target_cols - cropped.shape[1])

        if pad_rows > 0 or pad_cols > 0:
            cropped = np.pad(
                cropped,
                pad_width=((0, pad_rows), (0, pad_cols)),
                mode='constant',
                constant_values=0
            )
        
        return cropped

    def create_cloud_mask(self, cropped_bands, output_path=None, threshold=0.4, average_over=2, dilation_size=10):
        bands_resolutions = {
            'B01': 60, 'B02': 10, 'B03': 10, 'B04': 10, 'B05': 20, 'B06': 20, 'B07': 20, 
            'B08': 10, 'B8A': 20, 'B09': 60, 'B10': 60, 'B11': 20, 'B12': 20,
        }

        # Use resolução de 20m para melhor performance do s2cloudless
        target_resolution = 10
        
        # Use B05 (20m) como referência em vez de B02 (10m)
        reference_band = cropped_bands.get('B05')
        if reference_band is None:
            reference_band = cropped_bands.get('B02')
            target_resolution = 10
        
        ref_profile = reference_band.profile
        
        # Calcular dimensões corretas baseadas na resolução alvo
        pixel_size_x = abs(ref_profile.get('transform').a)
        pixel_size_y = abs(ref_profile.get('transform').e)
        
        target_height = int(ref_profile.get('height') * (pixel_size_y / target_resolution))
        target_width = int(ref_profile.get('width') * (pixel_size_x / target_resolution))
        
        print(f"Dimensões alvo para {target_resolution}m: {target_height}x{target_width}")
        
        processed_bands = []
        s2cloudless_band_order = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"]

        for band_name in s2cloudless_band_order:
            band_info = cropped_bands.get(band_name)
            
            if band_info is None:
                print(f"Aviso: Banda {band_name} não encontrada, preenchendo com zeros.")
                band_data = np.zeros((target_height, target_width), dtype=np.float32)
            else:
                band_data = band_info.array.astype(np.float32)
                
                # Redimensionar se necessário
                if bands_resolutions[band_name] != target_resolution:
                    print(f"Redimensionando banda {band_name}: {bands_resolutions[band_name]}m -> {target_resolution}m")
                    from skimage.transform import resize
                    band_data = resize(band_data, (target_height, target_width), 
                                    anti_aliasing=True, preserve_range=True)
                
                # Normalização correta para s2cloudless (0-1)
                # Sentinel-2 L2A já vem em reflectância de superfície * 10000
                band_data = np.clip(band_data / 10000.0, 0, 1)
            
            # Garantir dimensões corretas
            band_data = self.pad_or_crop(band_data, (target_height, target_width))
            processed_bands.append(band_data)

        # Criar array no formato esperado pelo s2cloudless: (1, height, width, 13)
        all_bands_stacked = np.stack(processed_bands, axis=-1)
        input_data_for_detector = all_bands_stacked[np.newaxis, ...]
        
        print(f"Shape do input: {input_data_for_detector.shape}")
        print(f"Range dos dados: {input_data_for_detector.min():.3f} - {input_data_for_detector.max():.3f}")
        
        # Configurar detector
        cloud_detector = S2PixelCloudDetector(
            threshold=threshold, 
            average_over=average_over, 
            dilation_size=dilation_size, 
            all_bands=True
        )
        
        # Gerar máscara de nuvens
        cloud_mask = cloud_detector.get_cloud_masks(input_data_for_detector)
        cloud_mask = cloud_mask.squeeze(0)  # Remove batch dimension
        
        print(f"Shape da máscara: {cloud_mask.shape}")
        print(f"Valores únicos na máscara: {np.unique(cloud_mask)}")
        
        # Converter para uint8 (0=sem nuvem, 1=nuvem)
        cloud_mask_binary = cloud_mask.astype(np.uint8)
        
        # Atualizar profile para salvar
        output_profile = reference_band.profile.copy()
        output_profile.update({
            'count': 1,
            'dtype': 'uint8',
            'driver': 'GTiff',
            'height': target_height,
            'width': target_width,
            'compress': 'lzw',
            'tiled': False,
            'nodata': 255,
        })
        
        # Ajustar transform se mudou a resolução
        if target_resolution != pixel_size_x:
            from rasterio.transform import Affine
            old_transform = ref_profile.get('transform')
            new_transform = Affine(
                target_resolution, old_transform.b, old_transform.c,
                old_transform.d, -target_resolution, old_transform.f
            )
            output_profile['transform'] = new_transform

        if output_path:
            with rasterio.open(output_path, 'w', **output_profile) as dst: 
                dst.write(cloud_mask_binary, 1)
        
        return cloud_mask_binary, output_profile

if __name__ == '__main__':
    import rasterio
    b02 = '/home/ppz/Documentos/coding/izisat/auxiliary/Sentinel-2/2025/04/06/T22KGD/L2A/10m/T22KGD_20250406T133211_B02_10m.jp2'
    b03 = '/home/ppz/Documentos/coding/izisat/auxiliary/Sentinel-2/2025/04/06/T22KGD/L2A/10m/T22KGD_20250406T133211_B03_10m.jp2'
    b04 = '/home/ppz/Documentos/coding/izisat/auxiliary/Sentinel-2/2025/04/06/T22KGD/L2A/10m/T22KGD_20250406T133211_B04_10m.jp2'
    b08 = '/home/ppz/Documentos/coding/izisat/auxiliary/Sentinel-2/2025/04/06/T22KGD/L2A/10m/T22KGD_20250406T133211_B08_10m.jp2'
    
    # Lê as bandas como arrays e pega o perfil de uma delas
    with rasterio.open(b02) as b2_src:
        b02 = b2_src.read(1)
        profile = b2_src.profile

    with rasterio.open(b03) as b3_src:
        b03 = b3_src.read(1)

    with rasterio.open(b04) as b4_src:
        b04 = b4_src.read(1)
    
    with rasterio.open(b08) as b8_src:
        b08 = b8_src.read(1)

    # Chama a função
    instance = RasterProcessing()
    rgb_array = instance.create_rgb(b02, b03, b04, reference_profile=profile, output_path='rgb_composite.tif')
    ndvi_array = instance.create_ndvi(b04, b08, profile, output_path='ndvi_composite.tif')
