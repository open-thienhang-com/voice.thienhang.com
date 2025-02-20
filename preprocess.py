import os
import librosa
import numpy as np
import json

# Example of how you might preprocess audio and text
def preprocess_audio(audio_file):
    # Load audio file
    audio, sr = librosa.load(audio_file, sr=22050)
    # Convert audio to mel-spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=80, fmax=8000)
    # Normalize mel-spectrogram
    mel_spectrogram = np.log(mel_spectrogram + 1e-6)
    return mel_spectrogram

def preprocess_text(text):
    # Basic text preprocessing (lowercasing, removing non-alphabet characters)
    return text.lower()

def preprocess_dataset(data_path, output_path):
    dataset = []
    with open(data_path, 'r') as f:
        for line in f.readlines():
            text, audio_file = line.strip().split('|')
            # Preprocess audio and text
            mel_spectrogram = preprocess_audio(audio_file)
            text = preprocess_text(text)
            dataset.append({'text': text, 'mel_spectrogram': mel_spectrogram.tolist()})
    
    # Save processed data to output file
    with open(output_path, 'w') as f:
        json.dump(dataset, f)

# Example usage:
data_path = "dataset.txt"  # Input file with text and audio pairs
output_path = "processed_data.json"  # Output processed data
preprocess_dataset(data_path, output_path)
