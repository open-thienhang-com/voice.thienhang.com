import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Device: {device}")

# List available 🐸TTS models
print(TTS().list_models())

tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)

# Input text for synthesis
text = "Hello! This is a machine learning-powered voice synthesizer."

# Generate speech and save to a file
tts.tts_to_file(text=text, file_path="examples/output2.wav")

print("Speech synthesis complete! Check 'output.wav'.")

tts.tts_with_vc_to_file(
    "Wie sage ich auf Italienisch, dass ich dich liebe?",
    speaker_wav="target/speaker.wav",
    file_path="output.wav"
)
