import numpy as np
import rasterio
import matplotlib.pyplot as plt
from s2cloudless import S2PixelCloudDetector

# Caminho base para suas bandas Sentinel-2
base_path = "/home/ppz/Documentos/coding/izisat/auxiliary/Sentinel-2/2025/04/11/T22KGE/L2A/"

# Mapeamento de bandas para seus caminhos e resoluções
# A ordem das bandas é importante para o s2cloudless (B01, B02, ..., B12)
band_info = {
    "B01": {"path": base_path + "60m/T22KGE_20250411T133149_B01_60m.jp2", "resolution": 60},
    "B02": {"path": base_path + "10m/T22KGE_20250411T133149_B02_10m.jp2", "resolution": 10},
    "B03": {"path": base_path + "10m/T22KGE_20250411T133149_B03_10m.jp2", "resolution": 10},
    "B04": {"path": base_path + "10m/T22KGE_20250411T133149_B04_10m.jp2", "resolution": 10},
    "B05": {"path": base_path + "20m/T22KGE_20250411T133149_B05_20m.jp2", "resolution": 20},
    "B06": {"path": base_path + "20m/T22KGE_20250411T133149_B06_20m.jp2", "resolution": 20},
    "B07": {"path": base_path + "20m/T22KGE_20250411T133149_B07_20m.jp2", "resolution": 20},
    "B08": {"path": base_path + "10m/T22KGE_20250411T133149_B08_10m.jp2", "resolution": 10},
    "B8A": {"path": base_path + "20m/T22KGE_20250411T133149_B8A_20m.jp2", "resolution": 20},
    "B09": {"path": base_path + "60m/T22KGE_20250411T133149_B09_60m.jp2", "resolution": 60},
    "B10": {"path": "N/A", "resolution": 60}, # Band B10 is not strictly required by s2cloudless and often not provided for L2A
    "B11": {"path": base_path + "20m/T22KGE_20250411T133149_B11_20m.jp2", "resolution": 20},
    "B12": {"path": base_path + "20m/T22KGE_20250411T133149_B12_20m.jp2", "resolution": 20},
}

# Define a resolução alvo para todas as bandas (ex: 20m)
target_resolution = 20

# Carregar uma banda de 10m ou 20m para obter as dimensões de referência
# Usaremos B02 (10m) para obter as dimensões e depois redimensionar para 20m
with rasterio.open(band_info["B02"]["path"]) as src:
    # Calcular as novas dimensões para a resolução alvo
    target_height = int(src.height * (src.res[0] / target_resolution))
    target_width = int(src.width * (src.res[1] / target_resolution))
    print(f"Dimensões alvo: {target_height}x{target_width}")
    output_profile = src.profile

# Lista para armazenar as bandas redimensionadas e normalizadas
processed_bands = []

# Ordem das bandas esperada pelo s2cloudless (todas as 13)
# B01, B02, B03, B04, B05, B06, B07, B08, B8A, B09, B10, B11, B12
s2cloudless_band_order = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"]

for band_name in s2cloudless_band_order:
    info = band_info[band_name]
    band_path = info["path"]

    if band_path == "N/A":
        # Se B10 não estiver disponível, preencha com zeros ou com a média das outras bandas (não ideal)
        # s2cloudless pode ainda funcionar sem ela, mas é bom ter uma placeholder
        print(f"Aviso: Banda {band_name} não encontrada, preenchendo com zeros.")
        # Cria uma banda de zeros com as dimensões alvo
        band_data = np.zeros((target_height, target_width), dtype=np.float32)
    else:
        with rasterio.open(band_path) as src:
            # Ler a banda
            band_data = src.read(1).astype(np.float32)

            # Redimensionar se a resolução for diferente da alvo
            if info["resolution"] != target_resolution:
                from skimage.transform import resize
                band_data = resize(band_data, (target_height, target_width), anti_aliasing=True)

            # Normalizar os valores de refletância (L2A é geralmente de 0 a 10000, normalizamos para 0 a 1)
            # Os valores máximos para as bandas Sentinel-2 L2A podem ser um pouco maiores que 10000
            # Alguns softwares os colocam na escala de 0 a 10000 para refletância.
            # Aqui, dividimos por 10000 para normalizar.
            band_data = band_data / 10000.0

    processed_bands.append(band_data)

# Empilhar todas as bandas para criar o array de entrada (altura, largura, bandas)
# Em seguida, adicionamos uma dimensão extra para o "batch" (1, altura, largura, bandas)
# que é o formato esperado pelo s2cloudless
all_bands_stacked = np.stack(processed_bands, axis=-1)
print(f"Shape das bandas empilhadas: {all_bands_stacked.shape}")

# Adicionar a dimensão do batch
input_data_for_detector = all_bands_stacked[np.newaxis, ...]
print(f"Shape da entrada para o detector: {input_data_for_detector.shape}")

# Inicializar o detector de nuvens
# all_bands=True porque estamos fornecendo 13 bandas
cloud_detector = S2PixelCloudDetector(threshold=0.1, average_over=2, dilation_size=7, all_bands=True)

print("Calculando probabilidade de nuvens...")
cloud_prob = cloud_detector.get_cloud_probability_maps(input_data_for_detector)
print(f"Shape da probabilidade de nuvens: {cloud_prob.shape}")

print("Calculando máscara de nuvens...")
cloud_mask = cloud_detector.get_cloud_masks(input_data_for_detector)
print(f"Shape da máscara de nuvens: {cloud_mask.shape}")
with rasterio.open('cloud_mask.tif', 'w', **output_profile) as dst: 
    dst.write(cloud_mask.astype(rasterio.uint8))
# Remover a dimensão extra do batch para visualização
cloud_prob_display = cloud_prob[0]
cloud_mask_display = cloud_mask[0]

# --- Visualização dos resultados ---
plt.figure(figsize=(20, 10))

# Visualizar a imagem RGB original (B04, B03, B02) - Opcional, se você quiser ver a cena
# Se você redimensionou para 20m, a visualização será em 20m
try:
    # Encontrar os índices das bandas B04, B03, B02 na sua lista 's2cloudless_band_order'
    idx_b04 = s2cloudless_band_order.index("B04")
    idx_b03 = s2cloudless_band_order.index("B03")
    idx_b02 = s2cloudless_band_order.index("B02")

    rgb_image = all_bands_stacked[:, :, [idx_b04, idx_b03, idx_b02]]

    # Como normalizamos para 0-1, podemos multiplicar por 3 para uma melhor visualização em RGB
    # ou ajustar o contraste com vmin/vmax no imshow
    rgb_image_display = np.clip(rgb_image * 2.5, 0, 1) # Ajuste o fator para melhor visualização

    plt.subplot(1, 3, 1)
    plt.imshow(rgb_image_display)
    plt.title("Imagem RGB (B04, B03, B02)")
    plt.axis("off")
except Exception as e:
    print(f"Não foi possível exibir a imagem RGB. Erro: {e}")
    # Se não puder exibir RGB, ajuste os subplots para apenas 2

plt.subplot(1, 3, 2 if 'rgb_image' in locals() else 1)
plt.imshow(cloud_prob_display, cmap="viridis", vmin=0, vmax=1)
plt.title("Probabilidade de Nuvem")
plt.colorbar(label="Probabilidade")
plt.axis("off")

plt.subplot(1, 3, 3 if 'rgb_image' in locals() else 2)
plt.imshow(cloud_mask_display, cmap=plt.cm.gray)
plt.title("Máscara de Nuvem")
plt.axis("off")

plt.tight_layout()
plt.show()





    def create_cloud_mask(self, cropped_bands, output_path=None):
        bands_resolutions = {
            'B01': 60,
            'B02': 10,
            'B03': 10,
            'B04': 10,
            'B05': 20,
            'B06': 20,
            'B07': 20,
            'B08': 10,
            'B8A': 20,
            'B09': 60,
            'B10': 60,
            'B11': 20,
            'B12': 20,
        }

        target_resolution = 20

        # Carregar uma banda de 10m ou 20m para obter as dimensões de referência
        # Usaremos B02 (10m) para obter as dimensões e depois redimensionar para 20m
        
        with rasterio.open(cropped_bands.get('B02').filepath) as src:
            # Calcular as novas dimensões para a resolução alvo
            target_height = int(src.height * (src.res[0] / target_resolution))
            target_width = int(src.width * (src.res[1] / target_resolution))
            print(f"Dimensões alvo: {target_height}x{target_width}")
            output_profile = src.profile

        processed_bands = []
        s2cloudless_band_order = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"]

        for band_name in s2cloudless_band_order:
            info = cropped_bands.get(band_name, 'N/A')
            
            if info == "N/A":
                print(f"Aviso: Banda {band_name} não encontrada, preenchendo com zeros.")
                band_data = np.zeros((target_height, target_width), dtype=np.float32)
            else:
                band_path = info.filepath
                with rasterio.open(band_path) as src:
                    # Ler a banda
                    band_data = src.read(1).astype(np.float32)

                    # Redimensionar se a resolução for diferente da alvo
                    if bands_resolutions[band_name] != target_resolution:
                        from skimage.transform import resize
                        band_data = resize(band_data, (target_height, target_width), anti_aliasing=True)

                    # Normalizar os valores de refletância (L2A é geralmente de 0 a 10000, normalizamos para 0 a 1)
                    # Os valores máximos para as bandas Sentinel-2 L2A podem ser um pouco maiores que 10000
                    # Alguns softwares os colocam na escala de 0 a 10000 para refletância.
                    # Aqui, dividimos por 10000 para normalizar.
                    band_data = band_data / 10000.0

            processed_bands.append(band_data)

        # Empilhar todas as bandas para criar o array de entrada (altura, largura, bandas)
        # Em seguida, adicionamos uma dimensão extra para o "batch" (1, altura, largura, bandas)
        # que é o formato esperado pelo s2cloudless
        all_bands_stacked = np.stack(processed_bands, axis=-1)
        input_data_for_detector = all_bands_stacked[np.newaxis, ...]
        cloud_detector = S2PixelCloudDetector(threshold=0.1, average_over=2, dilation_size=7, all_bands=True)
        cloud_prob = cloud_detector.get_cloud_probability_maps(input_data_for_detector)
        cloud_mask = cloud_detector.get_cloud_masks(input_data_for_detector)
        with rasterio.open('cloud_mask.tif', 'w', **output_profile) as dst: 
            dst.write(cloud_mask.astype(rasterio.uint8))