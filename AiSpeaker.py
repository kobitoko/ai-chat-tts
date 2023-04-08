from subprocess import *
import time
import sys
import inflect
from TTS.api import TTS
import sounddevice as sd
import emoji

# Seems to works well with py 3.9 (3.10+ not so much due to numpy)
# More see readme of https://github.com/coqui-ai/TTS
# tts --list_models
# TTS.list_models()[0]
# tts_models/en/ljspeech/fast_pitch
# vocoder_models/en/ljspeech/multiband-melgan
# tts --text "Text for TTS" --model_name "<model_type>/<language>/<dataset>/<model_name>" --vocoder_name "<model_type>/<language>/<dataset>/<model_name>" --out_path output/path/speech.wav
# tts --text "Text for TTS" --model_name "tts_models/en/ljspeech/fast_pitch" --vocoder_name "vocoder_models/en/ljspeech/multiband-melgan" --out_path speech.wav
class AiSpeak:
    sampleVoice = "sample.wav"
    inflector = None
    tts = None

    def __init__(self, sample = "sample.wav"):
        self.sampleVoice = sample
        self.inflector = inflect.engine()

        # More see readme of https://github.com/coqui-ai/TTS
        modelName = "tts_models/multilingual/multi-dataset/your_tts"
        
        # gpu true if you have CUDA hardware + installed, also need to reinstall torch with cuda! Needs to be compiled with CUDA to work.
        # `pip3.9 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117`
        self.tts = TTS(modelName, gpu=False)

    def testTts(self):
        initialText = "Hello - 😀 This is a test. -12,345.67. 48!"
        test = initialText
        while(True):
            #name = "out/output_"+ str(time.time()) + ".wav"
            #tts.tts_to_file(text=test, file_path=name, speaker_wav=sampleVoice, language="en")
            numpyWav = self.generateSpeech(line=test)
            sd.play(data=numpyWav, blocking=True)
            print("Type something. To quit, type \"exit\":")
            test = sys.stdin.readline().strip()
            if len(test) <= 1 or test.isspace():
                test = initialText
            elif test == "exit":
                print("Finished.")
                break
            test = self.textConvertNumbers(test)

    def generateSpeech(self, line="Hi!"):
        # replace emojis with a readable description, taken from https://carpedm20.github.io/emoji/docs/#replacing-and-removing-emoji
        editedLine = emoji.replace_emoji(line, replace=lambda chars, data_dict: data_dict['en'])
        # Convert numbers to TTS readable numbers.
        editedLine = self.textConvertNumbers(editedLine)
        return self.tts.tts(text=editedLine, speaker_wav=self.sampleVoice, language="en")

    def textConvertNumbers(self, text=""):
        texts = text.split()
        newTexts = []
        for word in texts:
            if word.isnumeric():
                newTexts.append(self.inflector.number_to_words(word))
                continue
            if len(word) <= 1 and not word.isalnum():
                newTexts.append(word)
                continue
            newWord = word
            prepend = None
            postpend = None
            if newWord[0] == "-":
                prepend = "negative"
                newWord = newWord[1:]
            if not newWord[len(newWord) - 1].isalnum():
                # number is at the end of a sentence of followed by a comma
                postpend = newWord[len(newWord) - 1]
                newWord = newWord[0:-1]
            # Check if its like a decimal separator (US ".") or a digit grouping (US ",") for example 12,345.67
            newWord = newWord.replace(",","")
            # inflector replaces decimal with "point" by default
            isNumber = newWord.replace(".","").isnumeric()

            if prepend != None:
                newTexts.append(prepend)
            if isNumber:
                newTexts.append(self.inflector.number_to_words(newWord))
            else:
                # It is not a number, just add the word
                newTexts.append(word)
                continue
            if postpend != None:
                newTexts.append(postpend)
        return " ".join(newTexts)
