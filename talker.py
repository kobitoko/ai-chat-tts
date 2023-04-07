from subprocess import *
import time
import os
import sys
import re
import click
import emoji
from TTS.api import TTS
#from gtts import gTTS
#from io import BytesIO
#from pydub import AudioSegment
from playsound import playsound
import torch
import numpy
import speech_recognition as sr
import whisper
import inflect

recognizer = None
micDeviceIndex = None
audioModel = None
inflector = None

@click.command()
@click.option("--sample", default="sample.wav", help="The voice file to use to inspire the text to speech.", type=str)
@click.option("--first_prompt", default="Hi!", help="Whether to start of immediately with a prompt.", type=str)
@click.option("--keep_output", default=False, help="Whether to keep the generated voice file after it is finished with it.", is_flag=True, type=bool)
@click.option("--use_voice", default=False, help="Whether to use voice input instead of text", is_flag=True, type=bool)

def main(sample, first_prompt, keep_output, use_voice):
    os.environ["PHYTHONUNBUFFERED"] = "1"
    # alpaca.cpp chat.exe build from + the alpaca model at https://github.com/antimatter15/alpaca.cpp
    command = ["chat.exe", "--interactive-start"]
    # gpt4all from https://github.com/nomic-ai/gpt4all/tree/main/chat
    #command = ["gpt4all-lora-quantized-win64.exe", "--interactive-start"]

    # run  py -3.9 talker.py
    print("running chat")
    try:

        # More see readme of https://github.com/coqui-ai/TTS
        modelName = "tts_models/multilingual/multi-dataset/your_tts"
        
        # gpu true if you have CUDA hardware + installed, also need to reinstall torch with cuda! Needs to be compiled with CUDA to work.
        # `pip3.9 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117`
        tts = TTS(modelName, gpu=True)
        #tts.tts_to_file(text="Hello! Testing here. Is this ok?", file_path="output.wav")
        #tts = gTTS("Hello!", lang="en")
        #tts.save("file.mp3")
        #mp3Fp = BytesIO()
        #tts.write_to_fp(mp3Fp)
        #AudioSegment.from_mp3("file.mp3")
        #playsound("file.mp3")
        
        #py3.9 if installed via microsoft store (idk why i did that):
        # if it complains about MeCab missing dll, put `libmecab.dll` from here below into system32 from https://stackoverflow.com/a/68751762
        #C:\Users\username\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\lib\site-packages\MeCab

        initListener()

        global inflector
        inflector = inflect.engine()

        process = Popen(command, stdout=PIPE, stdin=PIPE)
        print("Starting up.")
        running = True
        firstRun = True
        timeTaken = 0.0
        while running:
            if process.stdout.readable():
                print("\nReply:")
                lineByte = process.stdout.readline()
                textProcessTime = time.time() - timeTaken
                line = lineByte.decode('utf-8')
                # clean up the line from the terminal before checking it.
                line = line.replace(">", "", 1)
                line = line.strip()
                # ['\x1b[1m\x1b[32m\x1b[0mMy favorite game is Minecraft.', 'It has a perfect balance between creativity, exploration, problem solving and collaboration with other players in the world.', 'I love building structures from blocks or crafting items to use during adventures!', '\x1b[0m']
                # line still has ansi escape sequences like \x1b[1m\x1b[32m\x1b[0m\x1b[1m\x1b[32m\x1b[0m
                ansiEscape =re.compile(r'(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]')
                line = re.sub(ansiEscape,'', line)
                # Only speak if the line contains anything.
                if line:
                    # replace emojis with a readable description, taken from https://carpedm20.github.io/emoji/docs/#replacing-and-removing-emoji
                    line = emoji.replace_emoji(line, replace=lambda chars, data_dict: data_dict['en'])

                    print(line)
                    # Convert numbers to TTS readable numbers.
                    line = textConvertNumbers(line)

                    if not firstRun:
                        print(" > Processing input time: " + str(textProcessTime) + "s.")
                    print(" > Generating voice...")
                    #tts = gTTS(line, lang="en")
                    #tts.save("file.mp3")
                    #tts.tts_to_file(text=line, file_path="output.wav")
                    name = "out/output_"+ str(time.time()) + ".wav"
                    # emotions are ["Neutral", "Happy", "Sad", "Angry", "Dull"]
                    tts.tts_to_file(text=line, file_path=name, speaker_wav=sample, language="en", emotion="Happy", speed=1)
                    time.sleep(0.1)
                    playsound(name)
                    if not keep_output:
                        os.remove(name)
            print("----")
            if firstRun and process.stdin.writable() and first_prompt != "":
                # First run recommended because the first processing of both inputs and voice take usually longer than everything after that.
                input = first_prompt + "\n"
                encoded = input.encode('utf-8')
                process.stdin.write(encoded)
                process.stdin.flush()
                timeTaken = time.time()
                print("Ready!")
            elif process.stdin.writable():
                if use_voice:
                    print("Say something, starting with \"Computer,\". To quit, say \"exit\"):")
                    input = listenToMic().replace("Computer,", "", 1).strip()
                else:
                    print("Write something (to quit, type \"exit\"):")
                    input = sys.stdin.readline().strip()
                inputQuitCheck = input.lower().replace(".", "")
                if inputQuitCheck == "exit":
                    running = False
                    break
                elif input == "" or input.isspace():
                    input = "Hi!"
                input = emoji.replace_emoji(input, replace=lambda chars, data_dict: data_dict['en']) + "\n"
                # Newline is important, so the executable knows you've entered something and are done with it.
                input = input + "\n"
                encoded = input.encode('utf-8')
                process.stdin.write(encoded)
                process.stdin.flush()
                timeTaken = time.time()
            if firstRun:
                firstRun = False
            time.sleep(0.1)
    finally:
        print("Finished.")
        process.terminate()

def initListener():
    global recognizer
    global audioModel
    # https://github.com/mallorbc/whisper_mic#available-models-and-languages
    # There are no english models for large 
    model = "small.en"
    audioModel = whisper.load_model(model)
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 5000
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 0.8

# https://github.com/mallorbc/whisper_mic#available-models-and-languages
def listenToMic(acceptText = "Computer"):
    result = ""
    keepListening = True
    with sr.Microphone(device_index=micDeviceIndex, sample_rate=16000) as mic:
        # https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instanceadjust_for_ambient_noisesource-audiosource-duration-float--1---none
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        while(keepListening):
            print(" > Listening...")
            audio = recognizer.listen(mic, phrase_time_limit=10)
            audioBuffer = numpy.frombuffer(audio.get_raw_data(), numpy.int16).flatten().astype(numpy.float32)
            torchAudio = torch.from_numpy( audioBuffer / 32768.0)
            result = audioModel.transcribe(torchAudio, language='english')
            text = result["text"]
            print(" > you said: " + text)
            if acceptText == "" or (text.lower().find(acceptText.lower()) > -1) or text.lower().find("exit.") > -1:
                keepListening = False
    return result["text"]

def textConvertNumbers(text=""):
    texts = text.split()
    newTexts = []
    for word in texts:
        if word.isnumeric():
            newTexts.append(inflector.number_to_words(word))
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
            newTexts.append(inflector.number_to_words(newWord))
        else:
            # It is not a number, just add the word
            newTexts.append(word)
            continue
        if postpend != None:
            newTexts.append(postpend)
    return " ".join(newTexts)

if __name__ == "__main__":
    main()