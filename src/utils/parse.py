import argparse

parser = argparse.ArgumentParser(description='TTS Server', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--port', '-p', metavar='PORT', type=int, default=8000, help='port')
parser.add_argument('--host', '-H', metavar='HOST', type=str, default='0.0.0.0', help='listen host, 0.0.0.0 for any (interface), 127.0.0.1 for localhost only')
parser.add_argument('--reload', '-r', action='store_true', help='auto reload')
parser.add_argument('--cors', '-c', action='store_true', help='enable CORS')
parser.add_argument('--debug', '-d', action='store_true', help='debug mode')
