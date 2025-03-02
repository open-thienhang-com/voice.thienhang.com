#!/usr/bin/env python3
import os
import io
import json
import struct
import torch
import asyncio
import subprocess
from collections import namedtuple, defaultdict
from TTS.api import TTS
from TTS.utils.manage import get_user_data_dir

data_dir = get_user_data_dir('tts')

default_model_type = None
model_languages = {}
model_speakers = {}
models_by_language = defaultdict(list)
model_sep = '--'

def reset_models():
    global model_languages, model_speakers, models_by_language, default_model_type
    model_languages.clear()
    model_speakers.clear()
    models_by_language.clear()
    default_model_type = None

def tts_model_components(model_name):
    model_type = default_model_type
    lang, dataset, model = model_name.split(model_sep, 2)
    return model_type, lang, dataset, model

def tts_list_all_models():
    global default_model_type
    all_models = TTS().manager.list_models()
    model_names = []
    
    for model_name in all_models:
        model_type, lang, dataset, model = model_name.split('/')
        if not default_model_type:
            default_model_type = model_type
        elif model_type != default_model_type:
            print(f'Unexpected model type: got {model_type}, expected {default_model_type}')
            continue
        model_names.append(model_sep.join(model_name.split('/')[1:]))
    
    return model_names

def tts_list_models():
    return [model for model in tts_list_all_models() if os.path.exists(tts_model_path(model))]

def tts_model_path(model_name):
    model_type, lang, dataset, model = tts_model_components(model_name)
    return os.path.join(data_dir, f'{model_type}--{lang}--{dataset}--{model}')

def tts_list_model_languages():
    global model_languages
    if model_languages:
        return model_languages
    
    for model_name in tts_list_models():
        _, lang, _, _ = tts_model_components(model_name)
        model_path = tts_model_path(model_name)
        languages = set() if lang == 'multilingual' else {lang}
        
        lang_ids_path = os.path.join(model_path, 'language_ids.json')
        if os.path.exists(lang_ids_path):
            with open(lang_ids_path, 'r') as f:
                languages |= json.load(f).keys()
        
        model_languages[model_name] = sorted(languages)
    
    return model_languages

def tts_list_model_speakers():
    global model_speakers
    if model_speakers:
        return model_speakers
    
    for model_name in tts_list_models():
        model_path = tts_model_path(model_name)
        speakers = []
        
        for speaker_file in ['speaker_ids.json', 'speakers.json']:
            file_path = os.path.join(model_path, speaker_file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    speakers = list(json.load(f).keys())
                    break
        
        model_speakers[model_name] = speakers
    
    return model_speakers

def tts_list_models_by_language():
    if models_by_language:
        return models_by_language
    
    for model_name, languages in tts_list_model_languages().items():
        for language in languages:
            models_by_language[language].append(model_name)
    
    return models_by_language

def raw_audio_data_to_wav(data, sample_rate, sample_type=float):
    if isinstance(data, bytes) and data.startswith(b'RIFF'):
        return data
    
    format_tag = 3 if sample_type == float else 1
    bits_per_sample = 32 if sample_type == float else 16
    bytes_per_sample = bits_per_sample // 8
    chunk1_size, ch = 16, 1
    chunk2_size = len(data) * ch * bytes_per_sample
    chunk_size = 4 + 8 + chunk1_size + 8 + chunk2_size
    
    header = b''.join([
        b'RIFF', struct.pack('i', chunk_size), b'WAVEfmt ',
        struct.pack('i', chunk1_size), struct.pack('h', format_tag),
        struct.pack('h', ch), struct.pack('i', sample_rate),
        struct.pack('i', sample_rate * bytes_per_sample),
        struct.pack('h', bytes_per_sample), struct.pack('h', bits_per_sample),
        b'data', struct.pack('i', chunk2_size)
    ])
    
    return header + struct.pack(('f' if sample_type == float else 'h') * len(data), *data)

TTSResult = namedtuple('TTSResult', 'data, sample_rate, text, language, speaker')

class TTSWrapper:
    def __init__(self, model_name):
        self.model_type, self.lang, self.dataset, self.model = tts_model_components(model_name)
        self.model_name = f'{self.model_type}/{self.lang}/{self.dataset}/{self.model}'
        self.tts = TTS(self.model_name)

    @property
    def speakers(self):
        return [x.strip() for x in self.tts.speakers or []]

    @property
    def languages(self):
        return list(set(self.tts.languages or []) | {self.lang})

    def __call__(self, text, language=None, speaker=None):
        if not text:
            raise ValueError('Input text not specified')
        return TTSResult(self.tts.tts(text=text, language=language, speaker=speaker),
                         self.tts.synthesizer.tts_config.audio.sample_rate, text, language or self.lang, speaker)

async def tts_async_download(model_name, refresh=None):
    proc = await asyncio.create_subprocess_exec(sys.executable, 'tts_download_models.py', '--name', model_name,
                                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ)
    while proc.returncode is None:
        yield await proc.stdout.read(10)
    reset_models()
    if refresh:
        refresh()

if __name__ == '__main__':
    print(tts_list_model_speakers())
