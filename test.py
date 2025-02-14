import torch
import torchaudio
import torchaudio.transforms as T
from dp.preprocessing.text import LanguageTokenizer

# Ensure compatibility with torch.load() changes in PyTorch 2.6+
torch.serialization.add_safe_globals([LanguageTokenizer])
torch.serialization.weights_only = False  # Explicitly allow loading full model state

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Ensure proper audio backend for MP3
torchaudio.set_audio_backend("sox_io")

def load_audio(filepath):
    """Load an audio file and return the waveform and sample rate."""
    waveform, sample_rate = torchaudio.load(filepath)
    print(f"Waveform shape: {waveform.shape}")  # Shape: (Channels, Samples)
    print(f"Sample rate: {sample_rate}")
    return waveform, sample_rate

def setup_tts_pipeline(device):
    """Initialize the Tacotron2 text-to-speech pipeline."""
    bundle = torchaudio.pipelines.TACOTRON2_WAVERNN_PHONE_LJSPEECH
    
    # Override torch.load behavior to fully load the checkpoint
    processor = bundle.get_text_processor() 

    tacotron2 = bundle.get_tacotron2()
    
    # Explicitly reload without weights_only=True
    checkpoint_path = "path/to/checkpoint"
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    
    return processor, tacotron2

def text_to_speech(text, processor, tacotron2, device):
    """Convert text to speech using Tacotron2."""
    with torch.inference_mode():
        processed, lengths = processor(text)
        print("Processed tokens:", [processor.tokens[i] for i in processed[0, : lengths[0]]])

        # Move tensors to device
        processed = processed.to(device)
        lengths = lengths.to(device)

        # Generate spectrogram
        spec, _, _ = tacotron2.infer(processed, lengths)
        return spec

def main():
    """Main function to execute the text-to-speech pipeline."""
    # Load audio
    waveform, sample_rate = load_audio("hello.mp3")

    # Setup TTS pipeline
    processor, tacotron2 = setup_tts_pipeline(device)

    # Input text
    text = "Hello world! Text to speech!"

    # Run inference
    spectrogram = text_to_speech(text, processor, tacotron2, device)

    # Placeholder functions (define them in your actual implementation)
    print_stats(waveform, sample_rate=sample_rate)
    plot_waveform(waveform, sample_rate)
    plot_specgram(waveform, sample_rate)
    play_audio(waveform, sample_rate)

if __name__ == "__main__":
    main()
