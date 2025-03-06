#!/usr/bin/env python3

import os, json
from .wrapper import TTSWrapper , InvalidInputException
from TTS.utils.manage import get_user_data_dir
from TTS.api import TTS
from collections import namedtuple, defaultdict
import struct

model_speakers = {}


class VoiceSynthesizer:
    def __init__(self, model_name: str ="tts_models", default_model_type: str = "tts_models", data_dir: str = ""):
        os.environ['TTS_HOME'] = os.path.join(os.getcwd(), "models")
        data_dir = get_user_data_dir('tts')

        print("Data Dir", data_dir)
        
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
        # self.generate()
        self.data_dir = data_dir

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
        # if self.model_languages:
        #     return self.model_languages
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
                print(f'model {model_name} NOT present at {model_path}')
                continue

            print(f'model {model_name} downloaded at {model_path}')

            languages = set() if lang == 'multilingual' else set([lang])
            lang_ids_path = os.path.join(model_path, 'language_ids.json')
            if os.path.exists(lang_ids_path):
                with open(lang_ids_path, 'r') as f:
                    data = json.load(f)
                languages |= data.keys()

            print(f'model {model_name} languages: {", ".join(languages)}')

            self.model_languages[model_name] = list(sorted(languages))

        return self.model_languages


    def list_models_by_language(self):

        print("list_models_by_language", self.models_by_language)
        # if self.models_by_language:
        #     return self.models_by_language
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
        print(f'⚓️ Downloading model {model_name}')

        # Path to the download.py script
        script_path = os.path.join(os.path.dirname(__file__), 'download.py')

        # Start subprocess
        with subprocess.Popen([sys.executable, script_path, '--name', model_name],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=dict(os.environ, PYTHONUNBUFFERED='1'), bufsize=1, universal_newlines=True) as proc:
            # Read stdout and stderr line by line
            while True:
                # Read a line of stdout
                stdout_line = proc.stdout.readline()
                if stdout_line:
                    print("🎉 DOWNLOAD : ", stdout_line.strip())  # Print the line from stdout
                else:
                    break  # Exit when there are no more lines

            # Handle stderr (error output)
            stderr_line = proc.stderr.read()
            if stderr_line:
                print(f"Error occurred: {stderr_line.strip()}")

        print(f'Downloading model {model_name} finished. {os.path.dirname(__file__)}')

        # Optionally call refresh() here if needed
        # if refresh:
        #     refresh()

        return
    
    def generate(self, model_name,
                   text: str,
                   language,
                   speaker,
                   speaker_wav,
                   download: bool):
        try:
            print(".....................ok")
            model_name = model_name.value
            if language:
                language = language.value

            tts = self._get_tts(model_name)

            if speaker_wav:
                speaker_wav = speaker_wav.file

            result = tts(text=text, language=language, speaker=speaker, speaker_wav=speaker_wav)

            data = [int(0x7fff * sample * 0.4) for sample in result.data]
            wav_data = raw_audio_data_to_wav(data, result.sample_rate, int)
            wav_data = raw_audio_data_to_wav(result.data, result.sample_rate)
            wav_data = tts.get_wav(result)

            if download:
                headers = { 'Content-Disposition': 'attachment; filename=output.wav' }
            else:
                headers = {}

            print(wav_data, media_type='audio/wav', headers=headers)

        except InvalidInputException as e:
            raise e

        except Exception as e:
            raise e
    
    def get_model_path(self, model_name):
        # Name format: type/language/dataset/model
        # model_type, lang, dataset, model = model_name.split(model_sep)
        model_type, lang, dataset, model = self.get_model_components(model_name)
        model_full_name = f'{model_type}--{lang}--{dataset}--{model}'
        return os.path.join(self.data_dir, model_full_name)
    
    def _get_tts(self, model_name):
        model_type, lang, dataset, self.model = self.get_model_components(model_name)
        print("model_name: ", model_name)
        print("model_type: ", model_type)
        print("lang: ", lang)
        print("dataset: ", dataset)
        
        return TTSWrapper(
            model_name=model_name,
            model_type=model_type,
            lang=lang,
            dataset=dataset,
            model=self.model
        )
    


def raw_audio_data_to_wav(data, sample_rate, sample_type=float):

    if type(data) == bytes and data.startswith("RIFF".encode()):
        return data

    if sample_type is None:
        sample_type = type(data[0])

    if sample_type == float:
        format_tag = 3      # WAVE_FORMAT_IEEE_FLOAT=3, WAVE_FORMAT_PCM=1
        bits_per_sample = 32
    elif sample_type == int:
        format_tag = 1
        bits_per_sample = 16

    bytes_per_sample = bits_per_sample // 8
    ch = 1

    sample_count = len(data)

    chunk1_size = 16
    chunk2_size = sample_count * ch * bytes_per_sample
    chunk_size = 4 + 8 + chunk1_size + 8 + chunk2_size

    header = [
        'RIFF'.encode(),
        struct.pack('i', chunk_size),
        'WAVEfmt '.encode(),
        struct.pack('i', chunk1_size),
        struct.pack('h', format_tag),
        struct.pack('h', ch),
        struct.pack('i', sample_rate),
        struct.pack('i', sample_rate * bytes_per_sample),
        struct.pack('h', bytes_per_sample), # block align
        struct.pack('h', bits_per_sample),
        'data'.encode(),
        struct.pack('i', chunk2_size),
    ]

    if type(data) == bytes:
        data_chunk = data
    elif type(data) == list:
        # https://stackoverflow.com/questions/16368263/python-struct-pack-for-individual-elements-in-a-list
        if sample_type is int:
            data_chunk = struct.pack('h' * sample_count * ch, *data)
        elif sample_type is float:
            data_chunk = struct.pack('f' * sample_count * ch, *data)

    return b''.join(header) + data_chunk