import os, json
import io
from collections import namedtuple, defaultdict
from TTS.api import TTS

class InvalidInputException(Exception):
    pass

TTSResult = namedtuple('TTSResult', 'data, sample_rate, text, language, speaker')

class TTSWrapper:

    def __init__(self, model_name: str = "", model_type: str = "", lang: str='en', dataset: str='ljspeech', model_sep: str='--', default_model_type: str='tts_models'):
        self.model_type = model_type
        self.lang = lang 
        self.dataset = dataset 
        self.model_name = '/'.join([self.model_type, self.lang, self.dataset, self.model])
        self.freevc = self.model != 'your_tts'
        self.tts = TTS(self.model_name)

    @property
    def speakers(self):
        return [x.strip() for x in self.tts.speakers or []]

    @property
    def languages(self):
        return list(set(self.tts.languages or []) | set([lang]))

    def download(self):
        self.tts.download_model_by_name(self.model_name)

    def get_wav(self, data):
        if type(data) is TTSResult:
            data = data.data
        output = io.BytesIO()
        self.tts.synthesizer.save_wav(data, output)
        return output.getvalue()

    def __call__(self, text, language=None, speaker=None, speaker_wav=None):
        if not text:
            raise InvalidInputException('input text not specified')
        if not self.tts.is_multi_speaker:
            speaker = None
            # speaker_wav = None
        elif not speaker_wav and not speaker:
            speaker = self.tts.speakers[0]
        if not self.tts.is_multi_lingual:
            language = None
        elif not language:
            raise InvalidInputException('language not specified for multi-lingual model')
        if self.freevc and speaker_wav:
            import librosa
            speaker_wav, _ = librosa.load(speaker_wav, sr=16000)#, sr=self.config.audio.input_sample_rate)
            return TTSResult(self.tts.tts_with_vc(text=text, language=language, speaker_wav=speaker_wav),
                             self.tts.synthesizer.tts_config.audio.sample_rate, text, language or self.lang, speaker)
        return TTSResult(self.tts.tts(text=text, language=language, speaker=speaker, speaker_wav=speaker_wav),
                         self.tts.synthesizer.tts_config.audio.sample_rate, text, language or self.lang, speaker)
    

