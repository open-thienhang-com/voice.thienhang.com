#!/usr/bin/env python3
# utf-8

import re
import argparse
import sys
import os
from TTS.api import TTS



import sys
sys.stdout.reconfigure(encoding='utf-8')

class TTSModelDownloader:
    def __init__(self):
        os.environ['TTS_HOME'] = os.path.join(os.getcwd(), "models")
        self.tts = TTS()

    def list_all_models(self):
        return self.tts.manager.list_models()

    def download_model(self, model_name):
        self.tts.download_model_by_name(model_name)

    def download_selected_models(self, languages=None, datasets=None, models=None, patterns=None, regexps=None, types=None, dryrun=False):
        languages, datasets, models, patterns, regexps, types = languages or [], datasets or [], models or [], patterns or [], regexps or [], types or []
        
        for model_name in self.list_all_models():
            model_type, lang, dataset, model = model_name.split('/')
            
            # print(f"🔖 Selected models: {model_type}, {lang}, {dataset}, {model}")

            # print(f"🔖 Selected conditions: {languages}, {datasets}, {models}, {patterns}, {regexps}, {types}")
            if (languages and lang not in languages) or \
               (datasets and dataset not in datasets) or \
               (models and model not in models) or \
               (types and model_type not in types):
                continue
            
            if patterns and not any(pattern in model_name for pattern in patterns):
                continue
            
            if regexps and not any(re.match(regexp, model_name) for regexp in regexps):
                continue
            
            print(f"✅ Model selected: {model_name}")
            if not dryrun:
                self.download_model(model_name)

    def download_free_vc_wavlm(self, freevc=False, wavlm=False, dryrun=False):
        if freevc:
            model_name = 'voice_conversion_models/multilingual/vctk/freevc24'
            if not dryrun:
                self.download_model(model_name)
            else:
                print(f"Model selected for download: {model_name}")
        
        if wavlm:
            model_name = 'FreeVC WavLM'
            if not dryrun:
                from TTS.vc.modules.freevc.wavlm import get_wavlm
                get_wavlm()
            print(f"Model selected for download: {model_name}")


def main():
    parser = argparse.ArgumentParser(description='TTS Model Downloader', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    group = parser.add_argument_group('Model selection conditions',
                                      description='Conditions of the same type are joined with OR, but different types are joined with AND.')
    group.add_argument('--lang', '-l', action='append', help='Select by language')
    group.add_argument('--dataset', '-d', action='append', help='Select by dataset')
    group.add_argument('--model', '-m', action='append', help='Select by model')
    group.add_argument('--type', '-t', action='append', help='Select by type')
    group.add_argument('--name', '-n', action='append', help='Select by pattern in full name')
    group.add_argument('--re', '-r', action='append', help='Select by matching regex against full name')

    parser.add_argument('--free-vc', '--vc', action='store_true', help='Download FreeVC models including WavLM')
    parser.add_argument('--free-vc-wavlm', '--wavlm', action='store_true', help='Download FreeVC WavLM model')
    parser.add_argument('--all', action='store_true', help='Download all models')
    parser.add_argument('--list-all', action='store_true', help='List all available models')
    parser.add_argument('--dry-run', '--dry', action='store_true', help='List selected models without downloading')

    args = parser.parse_args()

    if not any([args.list_all, args.all, args.lang, args.dataset, args.model, args.name, args.re, args.type, args.free_vc, args.free_vc_wavlm]):
        print('No model selected. Specify selection parameters or use --all to download all models.', file=sys.stderr)
        sys.exit(1)

    downloader = TTSModelDownloader()

    if args.list_all:
        print('🔖 Available models:')
        for model in downloader.list_all_models():
            print(model)
        sys.exit(0)
    
    if args.all:
        args.free_vc = True
        args.free_vc_wavlm = True

    if args.free_vc or args.free_vc_wavlm:
        downloader.download_free_vc_wavlm(args.free_vc, args.free_vc or args.free_vc_wavlm, dryrun=args.dry_run)

    downloader.download_selected_models(args.lang, args.dataset, args.model, args.name, args.re, args.type, dryrun=args.dry_run)

if __name__ == '__main__':
    main()
