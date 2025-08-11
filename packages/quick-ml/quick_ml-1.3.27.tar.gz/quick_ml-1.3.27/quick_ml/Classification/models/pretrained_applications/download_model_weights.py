import os
import requests
from tqdm import tqdm

# CONFIG
PROJECT_ID = '20562478'
VERSION = '1.3.23'

MODELS = {
    'alexnet' : {
    True : "alexnet.keras", 
    False : "alexnet_notop.keras"
    }
}

base_url = f'https://gitlab.com/api/v4/projects/{PROJECT_ID}/packages/generic/quick_ml/{VERSION}/'

CACHE_DIR = os.path.expanduser("~/.quick_ml")

def download_model_weights(model, include_top = True):

    if model not in MODELS:
        raise ValueError(f"Model '{model}' not found. Available: {list(MODELS.keys())}")



    url = base_url + model + "/" + MODELS[model][include_top]
    filename = url.split('/')[-1]
    modelname = filename.split('.')[0]
    r = requests.get(url , stream = True)

    cache_path = os.path.join(CACHE_DIR, filename)

    # Make sure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(cache_path):
        print(f"✅ Found cached model weights at {cache_path}")
        return cache_path

    else:
        print(f"⬇ Downloading {filename}...")


        factor = 1024  * 1 ## 4 MB Chunks

        total_size = int(r.headers.get('content-length'), 0)


        block_size = 1024 * factor


        print(f"Downloading weights for {modelname[0].upper() + modelname[1:]} model.")
        with tqdm(total = total_size, unit = 'B', unit_scale = True) as progress_bar:
            #with open(filename, 'wb') as file:
            with open(cache_path, 'wb') as file:
                for data in r.iter_content(block_size):
                    file.write(data)
                    progress_bar.update(len(data))

        print(f"✅ Downloaded and saved to cache: {cache_path}")
        return cache_path


download_model_weights('alexnet', True)