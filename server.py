#!/usr/bin/env python3

debug = True

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='TTS Server', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', '-p', metavar='PORT', type=int, default=8000, help='port')
    parser.add_argument('--host', '-H', metavar='HOST', type=str, default='0.0.0.0', help='listen host, 0.0.0.0 for any (interface), 127.0.0.1 for localhost only')
    parser.add_argument('--reload', '-r', action='store_true', help='auto reload')
    parser.add_argument('--cors', '-c', action='store_true', help='enable CORS')
    parser.add_argument('--debug', '-d', action='store_true', help='debug mode')

    args = parser.parse_args()

    debug = args.debug  # TODO: this does not work for processes forked by uvicorn


from typing import Union
from enum import Enum
from collections import defaultdict
import traceback

from fastapi import FastAPI, File, UploadFile, Form, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

app = FastAPI(debug=debug)

def enable_cors():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# @app.get("/reset")
# def reset():
#     print(app.router.routes)
#     app.router.routes = app.router.routes[0:4]
#     load_routes('y')
#     print(app.router.routes)
#     return ''

# def load_routes(x='x'):
#     from typing import Literal
#     @app.get("/test/{some}")
#     def download_model(some: Literal["a","b", x]):
#         return some

def load_routes(app):

    @app.get("/languages")
    def list_languages():
        return tts_list_models_by_language()

    # @app.get("/languages/{language}/models")
    # def list_language_models(language: Union[Languages]):
    #     return tts_list_models_by_language()[language.value]

    @app.get("/models")
    def list_models():
        return tts_list_models()

    @app.get("/models/all")
    def list_all_models():
        return tts_list_all_models()

    @app.get("/models/languages")
    def list_model_languages():
        return tts_list_model_languages()

    @app.get("/models/speakers")
    def list_model_speakers():
        return tts_list_model_speakers()

    # @app.get("/models/{model_name}/download")
    # def download_model(model_name: AllModelName):
    #     model_name = model_name.value
    #     model_name = '/'.join(tts_model_components(model_name))
    #     return StreamingResponse(tts_download(model_name, reload), media_type='text/plain')
        # return get_tts(model_name).download()

    # This blocks the main thread, use threaded version above
    # @app.get("/models/{model_name}/download-async")
    # async def async_download_model(model_name: AllModelName):
    #     model_name = model_name.value
    #     model_name = '/'.join(tts_model_components(model_name))
    #     return StreamingResponse(tts_async_download(model_name, reload), media_type='text/plain')
    #     # return get_tts(model_name).download()

    # @app.get("/models/{model_name}/languages")
    # def model_languages(model_name: ModelName):
    #     model_name = model_name.value
    #     return tts_list_model_languages()[model_name]

    # @app.get("/models/{model_name}/speakers")
    # def model_speakers(model_name: ModelName):
    #     model_name = model_name.value
    #     speakers = tts_list_model_speakers()
    #     return speakers.get(model_name)
    #     # tts = get_tts(model_name)
    #     # return tts.speakers

    # @app.post('/models/{model_name}/generate')
    # def model_generate_post(model_name: ModelName,
    #                         text: str = Form(),
    #                         language: Union[Languages, None] = Form(None),
    #                         # language: Union[str, None] = Form(None),
    #                         speaker: Union[str, None] = Form(None),
    #                         speaker_wav: UploadFile = File(None),
    #                         download: bool = Form(False)):

    #     return generate(model_name, text, language, speaker, speaker_wav, download)


    # @app.get('/models/{model_name}/generate')
    # def model_generate_get(model_name: ModelName,
    #                        text: str,
    #                        language: Union[Languages, None] = None,
    #                        # language: Union[str, None] = None,
    #                        speaker: Union[str, None] = None,
    #                        download: bool = False):

    #     return generate(model_name, text, language, speaker, None, download)


    # @app.post('/generate')
    # def generate_post(model_name: ModelName = Form(),
    #                         text: str = Form(),
    #                         language: Union[Languages, None] = Form(None),
    #                         # language: Union[str, None] = Form(None),
    #                         speaker: Union[str, None] = Form(None),
    #                         speaker_wav: UploadFile = File(None),
    #                         download: bool = Form(False)):

    #     return generate(model_name, text, language, speaker, speaker_wav, download)


    # @app.get('/generate')
    # def generate_get(model_name: ModelName,
    #                        text: str,
    #                        language: Union[Languages, None] = None,
    #                        # language: Union[str, None] = None,
    #                        speaker: Union[str, None] = None,
    #                        download: bool = False):

    #     return generate(model_name, text, language, speaker, None, download)


    app.mount("/", StaticFiles(directory="examples", html=True), name="static")



def reload():
    # refresh_models()
    app.router.routes = app.router.routes[0:4]  # reset app routes, leave only swaggger rotues, e.g., /docs, /redoc etc.
    load_routes(app)
    app.openapi_schema = create_openapi_schema(app)

load_routes(app)

def create_openapi_schema(app):
    return get_openapi(
        title="TTS Demo",
        version="0.0.1",
        description="Text-To-Speech API",
        routes=app.routes,
    )

def openapi():
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = create_openapi_schema(app)
    return app.openapi_schema

app.openapi = openapi

enable_cors()   # TODO: make use of fork instead of spawn

if __name__ == '__main__':

    import uvicorn

    # TODO: make us of fork instead of spawn
    # if args.cors or True:
    if True:
        enable_cors()

    uvicorn.run("server:app", host=args.host, port=args.port, log_level='info', reload=args.reload)

    # or $ uvicorn server:app --host 0.0.0.0 --port 8000