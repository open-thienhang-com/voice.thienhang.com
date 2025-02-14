import requests
import torchaudio


SAMPLE_MP3_URL = "https://pytorch-tutorial-assets.s3.amazonaws.com/steam-train-whistle-daniel_simon.mp3"

print("Source:", SAMPLE_MP3_URL)
with requests.get(SAMPLE_MP3_URL, stream=True) as response:
  metadata = torchaudio.info(response.raw, format="mp3")

  print(f"Fetched {response.raw.tell()} bytes.")
print(metadata)