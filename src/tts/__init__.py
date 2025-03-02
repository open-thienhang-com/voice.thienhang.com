#!/usr/bin/env python3

import os, json
from .wrapper import TTSWrapper , InvalidInputException
from TTS.utils.manage import get_user_data_dir
from TTS.api import TTS

from collections import namedtuple, defaultdict

os.environ.setdefault('TTS_HOME', os.getcwd())
# os.environ.setdefault('XDG_DATA_HOME', os.getcwd())
data_dir = get_user_data_dir('models')

model_speakers = {}


class VoiceSynthesizer:
    def __init__(self, model_name: str ="tts_models", default_model_type: str = "tts_models", data_dir: str = ""):
        self.tts = TTS()
        self.model_name = model_name
        self.model_path = os.path.join(data_dir, model_name)
        self.model_type = default_model_type
        # self.languages = defaultdict(list)
        # self.speakers = model_speakers.get(model_name, {})
        self.models_by_language = defaultdict(list)
        self.model_languages = {}
        self.model_sep = '--'
        self.default_model_type = default_model_type

        # Initialize model components
        # self.model_type, self.lang, self.dataset, self.model = self.get_model_components(model_name)
        self._generate()

    def list_models(self):
        available_models = []
        for model_name in self.list_all_models():
            model_path = self.get_model_path(model_name)
            if not os.path.exists(model_path):
                print(f'model not found: {model_path}')
                continue
            available_models.append(model_name)
        return available_models
    
    def list_all_models(self):
        for model_name in TTS().manager.list_models():
            model_type, lang, dataset, model = model_name.split('/')
            # print(f'model_type: {model_type}, lang: {lang}, dataset: {dataset}, model: {model}')
            if not self.model_type:
                self.model_type = model_type
            elif model_type != self.model_type:
                # print(f'unexpected model type: got {model_type}, expected {self.model_type}')
                continue

        # return [model_sep.join(model_name.split('/')[1:]) for model_name in TTS.list_models()]
        return [self.model_sep.join(model_name.split('/')[1:]) for model_name in TTS().manager.list_models()]
    
    def list_models_language(self):
        if self.model_languages:
            return self.model_languages
        for model_name in self.list_models():
            # Name format: type/language/dataset/model
            # _, lang, _, _ = model_name.split(model_sep)
            _, lang, _, _ = self.get_model_components(model_name)
            # model_type, lang, dataset, model = model_name.split(model_sep)
            # model_full_name = f'{model_type}--{lang}--{dataset}--{model}'
            # model_path = os.path.join(data_dir, model_full_name)
            model_path = self.get_model_path(model_name)
            print(model_path)
            if not os.path.exists(model_path):
                # print(f'model {model_name} NOT present at {model_path}')
                continue

            print(f'model {model_name} downloaded at {model_path}')

            languages = set() if lang == 'multilingual' else set([lang])
            lang_ids_path = os.path.join(model_path, 'language_ids.json')
            if os.path.exists(lang_ids_path):
                with open(lang_ids_path, 'r') as f:
                    data = json.load(f)
                languages |= data.keys()

            # print(f'model {model_name} languages: {", ".join(languages)}')

            self.model_languages[model_name] = list(sorted(languages))

        return self.model_languages


    def list_models_by_language(self):
        if self.models_by_language:
            return self.models_by_language
        model_languages = self.list_models_language()
        for model_name, languages in model_languages.items():
            for language in languages:
                self.models_by_language[language].append(model_name)
        return self.models_by_language

    def list_model_languages():
        return 
   
    def list_model_speakers(self):
        global model_speakers
        if model_speakers:
            return model_speakers
        for model_name in self.list_models():
            model_path = self.get_model_path(model_name)
            speakers = []
            speaker_ids_path = os.path.join(model_path, 'speaker_ids.json')
            if os.path.exists(speaker_ids_path):
                with open(speaker_ids_path, 'r') as f:
                    data = json.load(f)
                speakers = list(data.keys())
            if not speakers:
                speakers_path = os.path.join(model_path, 'speakers.json')
                if os.path.exists(speakers_path):
                    with open(speakers_path, 'r') as f:
                        data = json.load(f)
                    speakers = list(sorted(set(sample.get('name').strip() for fn,sample in data.items())))
            if not speakers:
                speaker_ids_path = os.path.join(model_path, 'speaker_ids.pth')
                if os.path.exists(speaker_ids_path):
                    import zipfile, pickle
                    with zipfile.ZipFile(speaker_ids_path, 'r') as zf:
                        with zf.open('archive/data.pkl') as f:
                            data = pickle.load(f)
                    speakers = list(data.keys())

            # print(f'model {model_name} speakers: {", ".join(speakers)}')

            model_speakers[model_name] = list(speakers)

        return model_speakers

    def get_model_path(self, model_name):
        # Name format: type/language/dataset/model
        # model_type, lang, dataset, model = model_name.split(model_sep)
        model_type, lang, dataset, model = self.get_model_components(model_name)
        model_full_name = f'{model_type}--{lang}--{dataset}--{model}'
        return os.path.join(data_dir, model_full_name)
    
    def get_model_components(self, model_name):
        model_type = self.model_type
        lang, dataset, model = model_name.split(self.model_sep, 2)
        return model_type, lang, dataset, model
    
    def refresh_models(self):
        return 
    
    def download_model(self, model_name, refresh=None):
        import sys, os
        import subprocess
        import asyncio
        print("XXXXXXXXXXXXXXXXXXXXXX {}".format(model_name))
        print(f'Downloading model {model_name}')
        with subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), 'download.py'), '--name', model_name],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONUNBUFFERED='1'), bufsize=0) as proc:
            while proc.poll() == None:
                print(proc.stdout.readlines())
                # yield proc.stdout.read(10)
        print(f'Downloading model {model_name} finished. {os.path.dirname(__file__)}')
        # reset_models()
        # if refresh:
        #     refresh()
        return
    
    def _generate(self):
        try:
            print("ok")
            # model_name = model_name.value
            # if language:
            #     language = language.value

            # tts = self._get_tts(model_name)

            # if speaker_wav:
            #     speaker_wav = speaker_wav.file

            # result = tts(text=text, language=language, speaker=speaker, speaker_wav=speaker_wav)

            # data = [int(0x7fff * sample * 0.4) for sample in result.data]
            # wav_data = raw_audio_data_to_wav(data, result.sample_rate, int)
            # wav_data = raw_audio_data_to_wav(result.data, result.sample_rate)
            # wav_data = tts.get_wav(result)

            # if download:
            #     headers = { 'Content-Disposition': 'attachment; filename=output.wav' }
            # else:
            #     headers = {}

            # return Response(wav_data, media_type='audio/wav', headers=headers)

        except InvalidInputException as e:
            raise e

        except Exception as e:
            raise e
    
    def get_model_path(self, model_name):
        # Name format: type/language/dataset/model
        # model_type, lang, dataset, model = model_name.split(model_sep)
        model_type, lang, dataset, model = self.get_model_components(model_name)
        model_full_name = f'{model_type}--{lang}--{dataset}--{model}'
        return os.path.join(data_dir, model_full_name)
    
    def _get_tts(self, model_name):
        model_type, lang, dataset, self.model = self.get_model_components(model_name)
        return TTSWrapper(
            model_name=model_name,
            model_type=model_type,
            lang=lang,
            dataset=dataset,
            model_sep=self.model_sep,
            default_model_type=self.default_model_type
)
    


