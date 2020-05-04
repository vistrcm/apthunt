import shutil
from pathlib import Path

import requests
from fastai2.learner import load_learner


def maybe_download_model(url):
    f_name = url.split('/')[-1]
    local_path = Path("/tmp/model_{}".format(f_name))
    print(f"f_name: {f_name}")
    print(f"local_path: {local_path}")

    if local_path.exists():  # exit if file exists
        print("file {} exists".format(local_path))
        return local_path

    r = requests.get(url, stream=True)
    with open(local_path, 'wb') as model_file:
        shutil.copyfileobj(r.raw, model_file)

    return local_path


def get_learner(model_url="https://storage.googleapis.com/sv-fastai/models/apthunt/20200503_cltab.pkl"):
    print(f"downloading model from {model_url}")
    path = maybe_download_model(model_url)
    learn = load_learner(path)
    return learn
