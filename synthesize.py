from TTS.api import TTS

# Load the trained model
model_path = "path_to_your_trained_model"
config_path = "path_to_your_config_file"
tts = TTS(model_path=model_path, config_path=config_path)

# Generate speech from text
text = "This is a test sentence after training the TTS model."
output_path = "generated_audio.wav"
tts.tts_to_file(text, output_path)

print("Speech synthesis complete. Check 'generated_audio.wav'.")
