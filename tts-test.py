from subprocess import *
import time
import sys
import os
from TTS.api import TTS
from playsound import playsound
#from pydub import AudioSegment

# Seems to works well with py 3.9 (3.10+ not so much due to numpy)
# More see readme of https://github.com/coqui-ai/TTS
# tts --list_models
# TTS.list_models()[0]
# tts_models/en/ljspeech/fast_pitch
# vocoder_models/en/ljspeech/multiband-melgan
# tts --text "Text for TTS" --model_name "<model_type>/<language>/<dataset>/<model_name>" --vocoder_name "<model_type>/<language>/<dataset>/<model_name>" --out_path output/path/speech.wav
# tts --text "Text for TTS" --model_name "tts_models/en/ljspeech/fast_pitch" --vocoder_name "vocoder_models/en/ljspeech/multiband-melgan" --out_path speech.wav

# run  py -3.9 talker.py
print("running voice previewer")
useWavTTS = True
# modelName = "tts_models/en/ljspeech/fast_pitch"
# modelName = "tts_models/en/ljspeech/tacotron2-DDC"
# modelName = "tts_models/en/ljspeech/tacotron2-DDC"
modelName = "tts_models/multilingual/multi-dataset/your_tts" if useWavTTS else "tts_models/en/ljspeech/fast_pitch"

# TODO: Perhaps use number_to_words pip install inflect to replace numbers to tts readable words in the input.
def textConvertNumbers(text):
    return text

#vocoder = "vocoder_models/en/ljspeech/multiband-melgan"
#vocoder = "vocoder_models/en/ljspeech/hifigan_v2"
#tts = TTS(modelName, gpu=False, vocoder_path=vocoder)
tts = TTS(modelName, gpu=True)
a = "Hello everyone! Welcome, this is a test voice."
while(True):
    name = "out/output_"+ str(time.time()) + ".wav"
    tts.tts_to_file(text=a, file_path=name, speaker_wav="sample.wav", language="en") if useWavTTS else tts.tts_to_file(text=a, file_path=name)
    time.sleep(0.1)
    playsound(name)
    print("Input:")
    a = sys.stdin.readline().strip()
    if a == "" or a.isspace():
        a = "Hi!"
    a = textConvertNumbers(a)
    os.remove(name)
