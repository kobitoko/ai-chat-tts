from pyllamacpp.model import Model
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

timeTaken = 0.0
voiceSample = ""
keepOutput = False
firstRun = True
input = ""

section = []
spokenSection = ""

def new_text_callback(text: str):
    global section
    global spokenSection
    section.append(text)
    print(text, end="")
    # naively detect a section of a sentence, edgecases like dots in the middle like "etc." sound odd.
    if text == "." or text == "!" or text == "?" or text == ":" or text == ";":
        spokenSection = "".join(section)
        # naive filtering of input so it wont speak what was inputted
        if input.find(spokenSection) > -1:
            section = []
            spokenSection = ""
        else:
            speakSection()
    #prints here one by one each token. note model.generate doesn't return until its done, so execution flow is blocked.

def speakSection():
    global spokenSection
    global section
    spokenSection = "".join(section)
    spokenSection = emoji.replace_emoji(spokenSection, replace=lambda chars, data_dict: data_dict['en'])
    section = []
    if spokenSection == "":
        return
    print(" > Generating voice...")
    name = "out/output_"+ str(time.time()) + ".wav"
    tts.tts_to_file(text=spokenSection, file_path=name, speaker_wav=voiceSample, language="en")
    playsound(name)
    if not keepOutput:
        os.remove(name)

@click.command()
@click.option("--sample", default="sample.wav", help="The voice file to use to inspire the text to speech.", type=str)
@click.option("--first_prompt", default="", help="Whether to start of immediately with a prompt.", type=str)
@click.option("--keep_output", default=False, help="Whether to keep the generated voice file after it is finished with it.", is_flag=True, type=bool)

# Idea is that it speaks parts of the already generated text, so it can respond faster than when it waits on the whole response to complete.
# at the cost of sounding more separated because longer breaks between.
def main(sample, first_prompt, keep_output):
    print("running chat")
    global voiceSample
    global keepOutput
    global timeTaken
    global firstRun
    global input

    voiceSample = sample
    keepOutput = keep_output

    model = Model(ggml_model='./gpt4all-lora-quantized-ggml.bin', n_ctx=512)
    print("Starting up.")
    running = True

    while running:
        if firstRun and first_prompt != "":
            input = first_prompt + "\n"
            timeTaken = time.time()
            model.generate(input, n_predict=55, new_text_callback=new_text_callback, n_threads=8)
            print("Ready!")
        else:
            print("\n----")
            print("Write something (to quit, type quit or exit):")
            input = sys.stdin.readline().lstrip().rstrip()
            if input.lower() == "quit" or input.lower() == "exit":
                running = False
                break
            elif input == "" or input.isspace():
                input = "Hi!"
            # Newline is important, so the executable knows you've entered something and are done with it.
            input = emoji.replace_emoji(input, replace=lambda chars, data_dict: data_dict['en']) + "\n"
            timeTaken = time.time()
            model.generate(input, n_predict=55, new_text_callback=new_text_callback, n_threads=8)
            # speak the last remaining parts.
            speakSection()
        if firstRun:
            firstRun = False
        time.sleep(0.1)

if __name__ == "__main__":
    # run  py -3.9 gpt4all-talker.py

    # More see readme of https://github.com/coqui-ai/TTS
    modelName = "tts_models/multilingual/multi-dataset/your_tts"
    
    # gpu true if you have CUDA hardware + installed, also need to reinstall torch with cuda! Needs to be compiled with CUDA to work.
    # `pip3.9 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117`
    tts = TTS(modelName, gpu=True)
    main()