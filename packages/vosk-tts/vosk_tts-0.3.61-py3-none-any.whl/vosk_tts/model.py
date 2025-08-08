import os
import sys
import datetime
import json
import onnxruntime
import requests
import logging
import re

from urllib.request import urlretrieve
from zipfile import ZipFile
from pathlib import Path
from tqdm import tqdm
from tokenizers.implementations import BertWordPieceTokenizer

# Remote location of the models and local folders
MODEL_PRE_URL = "https://alphacephei.com/vosk/models/"
MODEL_LIST_URL = MODEL_PRE_URL + "model-list.json"
MODEL_DIRS = [os.getenv("VOSK_MODEL_PATH"), Path("/usr/share/vosk"),
        Path.home() / "AppData/Local/vosk", Path.home() / ".cache/vosk"]

def list_models():
    response = requests.get(MODEL_LIST_URL, timeout=10)
    for model in response.json():
        print(model["name"])

def list_languages():
    response = requests.get(MODEL_LIST_URL, timeout=10)
    languages = {m["lang"] for m in response.json()}
    for lang in languages:
        print (lang)

class Model:
    def __init__(self, model_path=None, model_name=None, lang=None):
        if model_path is None:
            model_path = self.get_model_path(model_name, lang)
        else:
            model_path = Path(model_path)

        onnx_providers = onnxruntime.get_available_providers()
        providers = [p for p in onnx_providers if p in ["CUDAExecutionProvider", "CPUExecutionProvider"]]

        sess_options = onnxruntime.SessionOptions()
#        sess_options.log_severity_level = 0
        logging.info(f"Loading model from {model_path}")
        self.onnx = onnxruntime.InferenceSession(str(model_path / "model.onnx"), sess_options=sess_options, providers=providers)

        self.dic = {}
        probs = {}
        for line in open(model_path / "dictionary", encoding='utf-8'):
           items = line.split(maxsplit=2)
           prob = float(items[1])
           if probs.get(items[0], 0) < prob:
               self.dic[items[0]] = items[2]
               probs[items[0]] = prob

        self.config = json.load(open(model_path / "config.json"))

        if os.path.exists(model_path / "bert/vocab.txt"):
            self.tokenizer = BertWordPieceTokenizer(vocab=str(model_path / "bert/vocab.txt"), unk_token="[UNK]", lowercase=False)
            self.bert_onnx = onnxruntime.InferenceSession(str(model_path / "bert/model.onnx"), sess_options=sess_options, providers=providers)
        else:
            self.tokenizer = None

    def get_model_path(self, model_name, lang):
        if model_name is None:
            model_path = self.get_model_by_lang(lang)
        else:
            model_path = self.get_model_by_name(model_name)
        return model_path

    def get_model_by_name(self, model_name):
        for directory in MODEL_DIRS:
            if directory is None or not Path(directory).exists():
                continue
            model_file_list = os.listdir(directory)
            model_file = [model for model in model_file_list if model == model_name]
            if model_file != []:
                return Path(directory, model_file[0])
        response = requests.get(MODEL_LIST_URL, timeout=10)
        result_model = [model["name"] for model in response.json() if model["name"] == model_name]
        if result_model == []:
            print("model name %s does not exist" % (model_name))
            sys.exit(1)
        else:
            self.download_model(Path(directory, result_model[0]))
            return Path(directory, result_model[0])

    def get_model_by_lang(self, lang):
        for directory in MODEL_DIRS:
            if directory is None or not Path(directory).exists():
                continue
            model_file_list = os.listdir(directory)
            model_file = [model for model in model_file_list if
                    re.match(r"vosk-model(-small)?-{}".format(lang), model)]
            if model_file != []:
                return Path(directory, model_file[0])
        response = requests.get(MODEL_LIST_URL, timeout=10)
        result_model = [model["name"] for model in response.json() if
                model["lang"] == lang and model["type"] == "small" and model["obsolete"] == "false"]
        if result_model == []:
            print("lang %s does not exist" % (lang))
            sys.exit(1)
        else:
            self.download_model(Path(directory, result_model[0]))
            return Path(directory, result_model[0])

    def download_model(self, model_name):
        if not (model_name.parent).exists():
            (model_name.parent).mkdir(parents=True)
        with tqdm(unit="B", unit_scale=True, unit_divisor=1024, miniters=1,
                desc=(MODEL_PRE_URL + str(model_name.name) + ".zip").rsplit("/",
                    maxsplit=1)[-1]) as t:
            reporthook = self.download_progress_hook(t)
            urlretrieve(MODEL_PRE_URL + str(model_name.name) + ".zip",
                    str(model_name) + ".zip", reporthook=reporthook, data=None)
            t.total = t.n
            with ZipFile(str(model_name) + ".zip", "r") as model_ref:
                model_ref.extractall(model_name.parent)
            Path(str(model_name) + ".zip").unlink()

    def download_progress_hook(self, t):
        last_b = [0]
        def update_to(b=1, bsize=1, tsize=None):
            if tsize not in (None, -1):
                t.total = tsize
            displayed = t.update((b - last_b[0]) * bsize)
            last_b[0] = b
            return displayed
        return update_to

