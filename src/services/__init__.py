
import os

from fastapi import FastAPI, File, UploadFile, Form, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from src.tts import VoiceSynthesizer
from enum import Enum
from typing import Union
from collections import defaultdict


class Server:
    def __init__(self):
        debug = True
        _app = FastAPI(debug=debug)
        
        #
        output_path = os.path.dirname(os.path.abspath(__file__))
        
        static_dir = os.path.join(os.path.dirname(__file__), "static")

        print(f"static_dir: {static_dir}")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            
        
        self._tts = VoiceSynthesizer()
        self.app = _app
        self._reload()
        self._enable_cors

        #
        self.app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

        print("\n🔗 List of API Routes:")
        for route in self.app.router.routes:
            print(f"➡ {route.name}: {route.path}")
        
        

    def _reload(self):
        self.app.router.routes = self.app.router.routes[0:4]  # reset app routes, leave only swaggger rotues, e.g., /docs, /redoc etc.
        self.load_routes()
        self._openapi()

    def _openapi(self):
        if self.app.openapi_schema:
            return self.app.openapi_schema
        
        _openapi_schema = get_openapi(
            title="A Voice Synthesizer Sample Program",
            version="0.0.1",
            description="Application of machine learning in Voice Synthesizer",
            routes=self.app.routes,
        )

        _openapi_schema["components"]["securitySchemes"] = {
            "XCustomAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization"
            }
        }

        _openapi_schema["security"] = [{"XCustomAuth": []}]
            
        self.app.openapi_schema = _openapi_schema
        return


    def _enable_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def load_routes(self):
        app = self.app
        tts = self._tts

        AllModelName = Enum('AllModelName', [(model_name, model_name) for model_name in tts.list_all_models()])
   

        models_by_language = tts.list_models_by_language()
        model_languages = tts.list_models_language()
        language_priority = defaultdict(int)
        model_priority = defaultdict(int)



        for language, models in models_by_language.items():
            for model in models:
                model_priority[model] += len(models_by_language[language])

        model_names = list(sorted(model_priority.keys(), key=lambda model: '%02d%s' % (len(model_priority) + 1 - model_priority[model], model), reverse=False))

        ModelName = Enum('ModelName', [(model_name, model_name) for model_name in model_names])

        for language, models in models_by_language.items():
            for model in models:
                language_priority[language] += len(model_languages[model])

        languages = list(sorted(language_priority.keys(), key=lambda lang: '%02d%s' % (100-language_priority[lang], lang), reverse=False))

        Languages = Enum('Languages', [(lang, lang) for lang in languages])

        @app.get("/languages")
        def list_languages():
            return tts.list_models_by_language()

        # @app.get("/languages/{language}/models")
        # def list_language_models(language: Union[Languages]):
        #     return tts_list_models_by_language()[language.value]

        @app.get("/models")
        def list_models():
            return tts.list_models()

        @app.get("/models/all")
        def list_all_models():
            return tts.list_all_models()

        @app.get("/models/languages")
        def list_model_languages():
            print("list_model_languages")
            return tts.list_models_language()

        @app.get("/models/speakers")
        def list_model_speakers():
            print("list_model_speakers")
            return tts.list_model_speakers()

        @app.get("/models/{model_name}/download")
        def download_model(model_name: AllModelName):
            model_name = model_name.value
            model_name = '/'.join(tts.get_model_components(model_name))
            tts.download_model(model_name, refresh=None)
            return
            # return StreamingResponse(tts.download_model(model_name, refresh=None ), media_type='text/plain')

        @app.get("/models/{model_name}/languages")
        def model_languages(model_name: ModelName):
            print("model_languages")
        #     model_name = model_name.value
        #     return tts_list_model_languages()[model_name]

        @app.get("/models/{model_name}/speakers")
        def model_speakers(model_name: ModelName):
            print("model_speakers")
        #     model_name = model_name.value
        #     speakers = tts_list_model_speakers()
        #     return speakers.get(model_name)
        #     # tts = get_tts(model_name)
        #     # return tts.speakers


        @app.post('/models/{model_name}/generate')
        def model_generate_post(model_name: ModelName,
                                text: str = Form(),
                                language: Union[Languages, None] = Form(None),
                                # language: Union[str, None] = Form(None),
                                speaker: Union[str, None] = Form(None),
                                speaker_wav: UploadFile = File(None),
                                download: bool = Form(False)):


            return tts.generate(model_name, text, language, speaker, speaker_wav, download)


        @app.get('/models/{model_name}/generate')
        def model_generate_get(model_name: ModelName,
                               text: str,
                               language: Union[Languages, None] = None,
                               # language: Union[str, None] = None,
                               speaker: Union[str, None] = None,
                               download: bool = True):
            model_name = model_name.value
            return tts.generate(model_name, text, language, speaker, None, download)


        @app.post('/generate')
        def generate_post(model_name: ModelName = Form(),
                                text: str = Form(),
                                language: Union[Languages, None] = Form(None),
                                # language: Union[str, None] = Form(None),
                                speaker: Union[str, None] = Form(None),
                                speaker_wav: UploadFile = File(None),
                                download: bool = Form(False)):

            return tts.generate(model_name, text, language, speaker, speaker_wav, download)


        @app.get('/generate')
        def generate_get(model_name: ModelName,
                               text: str,
                               language: Union[Languages, None] = None,
                               # language: Union[str, None] = None,
                               speaker: Union[str, None] = None,
                               download: bool = False):

            return tts.generate(model_name, text, language, speaker, None, download)

        

