from TTS.utils.generic_utils import download_model
from TTS.utils.synthesizer import Synthesizer
from TTS.train import train
import yaml

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Start the training process
train(config)

