from subprocess import *
import time
import os
import sys
import re
import click
import emoji
from VoiceRecognizer import *
from AiSpeaker import *
import sounddevice as sd

class Talker:
    voiceRecognizer = None
    tts = None
    acceptText = ""
    promptFrame = ""

    def __init__(self, textToSpeechObject, useTextOnly=False, voiceListenerObject=None, promptFrame="<input>"):
        os.environ["PHYTHONUNBUFFERED"] = "1"
        print("running chat")

        self.tts = textToSpeechObject

        # whisper for listening to speech of the user.
        if not useTextOnly:
            self.voiceRecognizer = voiceListenerObject
            self.acceptText = self.voiceRecognizer.getAcceptText()
        self.promptFrame = promptFrame

    def promptifyInput(self, input=""):
        if self.promptFrame.find("<input>") < 0:
            return input
        inputSurround = self.promptFrame.split("<input>")
        modified = inputSurround[0] + input
        if len(inputSurround) > 1:
            modified = modified + inputSurround[1]
        return modified

    def start(self, command = ["chat.exe --interactive-start"], firstPrompt="Hi!", useTextOnly=False):
        try:
            print("Starting up.")
            process = Popen(command, stdout=PIPE, stdin=PIPE)
            running = True
            firstRun = True
            timeTaken = 0.0
            while running:
                if process.stdout.readable():
                    if not firstRun:
                        print("\nReply:")
                    lineByte = process.stdout.readline()
                    textProcessTime = time.time() - timeTaken
                    line = lineByte.decode('utf-8')
                    # clean up the line from the terminal before checking it.
                    line = line.replace(">", "", 1)
                    line = line.strip()
                    # ['\x1b[1m\x1b[32m\x1b[0mMy favorite game is Minecraft.', 'It has a perfect ... use during adventures!', '\x1b[0m']
                    # line still has ansi escape sequences like \x1b[1m\x1b[32m\x1b[0m\x1b[1m\x1b[32m\x1b[0m
                    ansiEscape =re.compile(r'(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]')
                    line = re.sub(ansiEscape,'', line)
                    # Only speak if the line contains anything.
                    if line:
                        if not firstRun:
                            print(" > Processing input time: " + str(textProcessTime) + "s.")
                        print(line)
                        print(" > Generating voice...")
                        numpyWav = self.tts.generateSpeech(line)
                        sd.play(data=numpyWav, blocking=True)
                print("----")
                if firstRun and process.stdin.writable() and firstPrompt != "":
                    # First run recommended because the first processing of both inputs and voice take usually longer than everything after that.
                    input = firstPrompt + "\n"
                    encoded = input.encode('utf-8')
                    process.stdin.write(encoded)
                    process.stdin.flush()
                    timeTaken = time.time()
                elif process.stdin.writable():
                    if not useTextOnly:
                        print("Say something, starting with \"" + self.acceptText + ",\". To quit, say \"exit\"):")
                        input = self.voiceRecognizer.listenToMic().lower().replace(self.acceptText, "", 1).strip()
                        if not (len(input) > 1 and input[0].isalnum()):
                            input = input[1:]
                    else:
                        print("Write something (to quit, type \"exit\"):")
                        input = sys.stdin.readline().strip()
                    inputQuitCheck = input.lower().replace(".", "")
                    if inputQuitCheck == "exit":
                        running = False
                        break
                    elif len(input) <= 1 or input.isspace():
                        input = "Hi!"
                    input = emoji.replace_emoji(input, replace=lambda chars, data_dict: data_dict['en']) + "\n"
                    input = self.promptifyInput(input)
                    print(" > Processed input: " + input)
                    # Newline is important, so the executable knows you've entered something and are done with it.
                    input = input + "\n"
                    encoded = input.encode('utf-8')
                    process.stdin.write(encoded)
                    process.stdin.flush()
                    timeTaken = time.time()
                if firstRun:
                    firstRun = False
                time.sleep(0.01)
        finally:
            process.terminate()
            print("Finished.")

if __name__ == "__main__":
    @click.group()
    @click.option("-i", "--input-device", default=-1, help="Choose which input device index to use (-1 for default device).", type=int)
    @click.option("-o", "--output-device", default=-1, help="Choose which output device index to use (-1 for default device).", type=int)
    def cli(input_device, output_device):
        inputIndex = None
        outputIndex = None
        if input_device > -1:
            inputIndex = input_device
        if output_device > -1:
            outputIndex = output_device
        sd.default.samplerate = 16000
        # Index or query string of default input/output device.
        sd.default.device = inputIndex, outputIndex

    @click.command()
    def devices():
        # Taken from https://python-sounddevice.readthedocs.io/en/0.4.6/api/checking-hardware.html#sounddevice.query_devices
        print("The first character of a line is: \n > for the default input device, \n < for the default output device and \n * for the default input/output device.")
        print("After the device ID and the device name, the corresponding host API name is displayed.")
        print("In the end of each line, the maximum number of input and output channels is shown.")
        print(sd.query_devices())

    @click.command()
    @click.option("--first-prompt", default="Hi!", help="Whether to start of immediately with a prompt. Use empty string \"\" to have no first prompt.", type=str)
    @click.option("--prompt-frame", default="Input: <input> \nResponse: ", help="Whether to include a prompt frame that the input gets put into before it is passed to the chat model. \"<input>\" gets replaced by the chat's input.", type=str)
    @click.option("--text-chat", default=False, help="Whether to use text input instead of voice.", is_flag=True, type=bool)
    @click.option("--chat-executable", default="chat.exe --interactive-start", help="Whether to use a specific executable from a certain location, including potential arguments.", type=str)
    @click.option("-a","--accept-text", default="computer", help="The magic word that the listener should use to finish the test with.", type=str)
    @click.option("--whisper-model", default="small.en", help="Which model to use for Whisper, see https://github.com/mallorbc/whisper_mic#available-models-and-languages", type=click.Choice(["tiny","base", "small","medium","tiny.en","base.en", "small.en","medium.en","large"]))
    @click.option("--energy-threshold", default=5000, help="Represents the energy level threshold for sounds. Values below this threshold are considered silence, and values above this threshold are considered speech.", type=int)
    @click.option("--dynamic-energy-threshold", default=False, help="Automatically adjusts Energy Threshold based on the currently ambient noise level while listening.", is_flag=True, type=bool)
    @click.option("--pause-threshold", default=800, help="In milliseconds how long of a pause to recognize a completion of a sentence.", type=int)
    @click.option("-v","--voice-sample", default="sample.wav", help="The voice file to use to inspire the text to speech.", type=str)  
    def chat(first_prompt, text_chat, prompt_frame, chat_executable, accept_text, whisper_model, energy_threshold, dynamic_energy_threshold, pause_threshold, voice_sample):
        tts = AiSpeak(voice_sample)
        listener = RecognizeVoice(acceptText=accept_text, micDeviceIndex=sd.default.device[0], model=whisper_model, energyThreshold=energy_threshold, dynamicEnergyThreshold=dynamic_energy_threshold, pauseThreshold=pause_threshold)
        talker = Talker(textToSpeechObject=tts,  useTextOnly=text_chat, voiceListenerObject=listener, promptFrame=prompt_frame)
        # alpaca.cpp chat.exe build from + the alpaca model at https://github.com/antimatter15/alpaca.cpp
        #chat_executable = ["chat.exe --interactive-start"]
        # gpt4all from https://github.com/nomic-ai/gpt4all/tree/main/chat
        #chat_executable = ["gpt4all-lora-quantized-win64.exe", "--interactive-start"]
        #chat_executable = ["gpt4all-lora-quantized-win64.exe -m gpt4all-lora-unfiltered-quantized.bin"]
        talker.start(chat_executable, first_prompt, text_chat)

    @click.command()
    @click.option("-a","--accept-text", default="computer", help="The magic word that the listener should use to finish the test with.", type=str)
    @click.option("--whisper-model", default="small.en", help="Which model to use for Whisper, see https://github.com/mallorbc/whisper_mic#available-models-and-languages", type=click.Choice(["tiny","base", "small","medium","tiny.en","base.en", "small.en","medium.en","large"]))
    @click.option("--energy-threshold", default=5000, help="Represents the energy level threshold for sounds. Values below this threshold are considered silence, and values above this threshold are considered speech.", type=int)
    @click.option("--dynamic-energy-threshold", default=False, help="Automatically adjusts Energy Threshold based on the currently ambient noise level while listening.", is_flag=True, type=bool)
    @click.option("--pause-threshold", default=800, help="In milliseconds how long of a pause to recognize a completion of a sentence.", type=int)
    def listener(accept_text, whisper_model, energy_threshold, dynamic_energy_threshold, pause_threshold):
        recognizer = RecognizeVoice(acceptText=accept_text, micDeviceIndex=sd.default.device[0], model=whisper_model, energyThreshold=energy_threshold, dynamicEnergyThreshold=dynamic_energy_threshold, pauseThreshold=pause_threshold)
        print("Done listening, result: " + recognizer.listenToMic())

    @click.command()
    @click.option("-v","--voice-sample", default="sample.wav", help="The voice file to use to inspire the text to speech.", type=str)  
    def speaker(voice_sample):
        speaking = AiSpeak(voice_sample)
        speaking.testTts()

    cli.add_command(chat)
    cli.add_command(listener)
    cli.add_command(speaker)
    cli.add_command(devices)
    cli()