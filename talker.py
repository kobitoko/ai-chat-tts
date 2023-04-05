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

@click.command()
@click.option("--sample", default="sample.wav", help="The voice file to use to inspire the text to speech.", type=str)
@click.option("--first_prompt", default="Hi!", help="Whether to start of immediately with a prompt.", type=str)
@click.option("--keep_output", default=False, help="Whether to keep the generated voice file after it is finished with it.", is_flag=True, type=bool)

def main(sample, first_prompt, keep_output):
    os.environ["PHYTHONUNBUFFERED"] = "1"
    # alpaca.cpp chat.exe build from + the alpaca model at https://github.com/antimatter15/alpaca.cpp
    #command = ["chat.exe", "--interactive-start"]
    # gpt4all from https://github.com/nomic-ai/gpt4all/tree/main/chat
    command = ["gpt4all-lora-quantized-win64.exe", "--interactive-start"]

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

        process = Popen(command, stdout=PIPE, stdin=PIPE)
        print("Starting up.")
        running = True
        firstRun = True
        timeTaken = 0.0
        while running:
            if  process.stdout.readable():
                print("\nReply:")
                lineByte = process.stdout.readline()
                textProcessTime = time.time() - timeTaken
                # clean up the line from the terminal
                line = lineByte.decode('utf-8')
                line = line.replace(">", "", 1)
                line = line.lstrip().rstrip()
                # ['\x1b[1m\x1b[32m\x1b[0mMy favorite game is Minecraft.', 'It has a perfect balance between creativity, exploration, problem solving and collaboration with other players in the world.', 'I love building structures from blocks or crafting items to use during adventures!', '\x1b[0m']
                # line still has ansi escape sequences like \x1b[1m\x1b[32m\x1b[0m\x1b[1m\x1b[32m\x1b[0m
                ansiEscape =re.compile(r'(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]')
                line = re.sub(ansiEscape,'', line)
                # replace emojis with a readable description, taken from https://carpedm20.github.io/emoji/docs/#replacing-and-removing-emoji
                line = emoji.replace_emoji(line, replace=lambda chars, data_dict: data_dict['en'])
                if line:
                    print(line)
                    if not firstRun:
                        print(" > Processing input time: " + str(textProcessTime) + "s.")
                    print(" > Generating voice...")
                    #tts = gTTS(line, lang="en")
                    #tts.save("file.mp3")
                    #tts.tts_to_file(text=line, file_path="output.wav")
                    name = "out/output_"+ str(time.time()) + ".wav"
                    tts.tts_to_file(text=line, file_path=name, speaker_wav=sample, language="en")
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
                print("Write something (to quit, type quit or exit):")
                input = sys.stdin.readline().lstrip().rstrip()
                if input.lower() == "quit" or input.lower() == "exit":
                    running = False
                    break
                elif input == "" or input.isspace():
                    input = "Hi!"
                # Newline is important, so the executable knows you've entered something and are done with it.
                input = emoji.replace_emoji(input, replace=lambda chars, data_dict: data_dict['en']) + "\n"
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

if __name__ == "__main__":
    main()