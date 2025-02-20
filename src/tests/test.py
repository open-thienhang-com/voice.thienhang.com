from gtts import gTTS
tts = gTTS('Xin chào!', lang='vi')
tts.save('hello.mp3')