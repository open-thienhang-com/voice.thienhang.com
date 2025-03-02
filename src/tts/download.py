#!/usr/bin/env python3

import re

from TTS.api import TTS

tts = None

def list_all_models():
    global tts
    if not tts:
        tts = TTS()
    return tts.manager.list_models()

def download_model(model_name):
    print("ppppppppppppppppppppppppppppppppppppppp1111111111111")
    global tts
    if not tts:
        tts = TTS()
    tts.download_model_by_name(model_name)

    print("ppppppppppppppppppppppppppppppppppppppp")

def download_selected_models(languages=[], datasets=[], models=[], patterns=[], regexps=[], types=[], dryrun=False):
    print("======================== bbbbbbbbbb", models )
    for model_name in list_all_models():
        model_type, lang, dataset, model = model_name.split('/')
        # print(" >>> {} {} {} {}".format(model_type, lang, dataset, model))
        if languages and lang not in languages:
            continue
        if datasets and dataset not in datasets:
            continue
        if models and model not in models:
            continue
        if types and model_type not in types:
            continue
        if patterns:
            for pattern in patterns:
                if pattern in model_name:
                    break
            else:
                continue
        if regexps:
            for regexp in regexps:
                if re.match(regexp, model_name):
                    break
            else:
                continue
        print("========================" )
        if not dryrun:
            print(f'downloading model {model_name}')
            download_model(model_name)
        else:
            print(f'model selected for download: {model_name}')

def download_free_vc_wavlm(freevc=False, wavlm=False, dryrun=False):
    # download FreeVC WavLM model
    if freevc:
        model_name = 'voice_conversion_models/multilingual/vctk/freevc24'
        if not dryrun:
            print(f'downloading model {model_name}')
            download_model(model_name)
        else:
            print(f'model selected for download: {model_name}')
    if wavlm:
        model_name = 'FreeVC WavLM'
        if not dryrun:
            print(f'downloading model {model_name}')
            from TTS.vc.modules.freevc.wavlm import get_wavlm
            get_wavlm()
        else:
            print(f'model selected for download: {model_name}')


if __name__ == '__main__':
    import argparse, sys, os


    parser = argparse.ArgumentParser(description='TTS Model Downloader', formatter_class=argparse.ArgumentDefaultsHelpFormatter, epilog='')

    group = parser.add_argument_group('Model selection conditions',
                                      description='Conditions of the same type are joined with OR operator, however, '
                                      + 'conditions with different types are joined with AND operator.')

    group.add_argument('--lang', '-l', metavar='LANG', action='append', type=str, help='select by language')
    group.add_argument('--dataset', '-d', metavar='DATASET', action='append', type=str, help='select by dataset')
    group.add_argument('--model', '-m', metavar='MODEL', action='append', type=str, help='select by model')
    group.add_argument('--type', '-t', metavar='TYPE', action='append', type=str, help='select by type')
    group.add_argument('--name', '-n', metavar='PATTERN', action='append', type=str,
                       help='select by pattern in full name, i.e., type/lang/dataset/model')
    group.add_argument('--re', '-r', metavar='REGEX', action='append', type=str,
                       help='select by matching regex against full name, i.e., type/lang/dataset/model')

    parser.add_argument('--free-vc', '--vc', action='store_true', help='download FreeVC models including WavLM model')
    parser.add_argument('--free-vc-wavlm', '--wavlm', action='store_true', help='download FreeVC WavLM model')
    parser.add_argument('--all', action='store_true', help='download all models')
    parser.add_argument('--list-all', action='store_true', help='list all downloadable models')
    parser.add_argument('--dry-run', '--dry', action='store_true', help='do not download, list selected models only')

    args = parser.parse_args()

    if not args.list_all and not args.all and not args.lang and not args.dataset and not args.model and not args.name and not args.re and not args.type \
        and not args.free_vc and not args.free_vc_wavlm:
        print('No model selected, either specify model selection parameters or --all to download all available models', file=sys.stderr)
        sys.exit(1)

    # from TTS.utils.manage import set_data_path

    custom_path = os.path.join(os.getcwd(), "tts/models") 
    os.environ.setdefault('TTS_HOME',custom_path)
    # set_data_path(custom_path)  
    data_dir = custom_path  

    # Kiểm tra lại đường dẫn mới
    print("Model will be saved in:", data_dir)

    if args.list_all:
        print('TYPE/LANG/DATASET/MODEL')
        for model_name in list_all_models():
            print(model_name)
        print("Exxit {}".format(model_name))
        sys.exit(0)
   
    if args.all:
        args.free_vc = True
        args.free_vc_wavlm = True

    if args.free_vc or args.free_vc_wavlm:
        download_free_vc_wavlm(args.free_vc, args.free_vc or args.free_vc_wavlm, dryrun=args.dry_run)
    
    print(args)
    download_selected_models(args.lang, args.dataset, args.model, args.name, args.re, args.type, dryrun=args.dry_run)