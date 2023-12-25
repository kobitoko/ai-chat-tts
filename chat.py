from subprocess import *
import time
import sys
import click
import emoji
from VoiceRecognizer import *
from AiSpeaker import *
import sounddevice as sd
import json
import requests

class Talker:
    voiceRecognizer = None
    tts = None
    acceptText = ""
    # a nanoseconds is 10^-9 of a second.
    SecondInNanoseconds = 1000000000
    modelName = "chat-model"
    chatContext = []

    def __init__(self, textToSpeechObject, useTextOnly=False, voiceListenerObject=None):
        print("running chat")

        self.tts = textToSpeechObject

        # whisper for listening to speech of the user.
        if not useTextOnly:
            self.voiceRecognizer = voiceListenerObject
            self.acceptText = self.voiceRecognizer.getAcceptText()

    def start(self, firstPrompt="Hi!", useTextOnly=False):
        modelFile = open("Modelfile", "r")
        modelFileContent = modelFile.read()
        print("Model File Content:" + modelFileContent)
        modelFile.close()
        print("Creating model based on Modelfile, might take a while if this is the first time running: it'll download the model.")
        # Ask to create a model based on the modelFile, if it already exists its okay. 
        # https://github.com/jmorganca/ollama/blob/main/docs/api.md#create-a-model
        request = requests.post(
            "http://localhost:11434/api/create",
            json = {
                "name": self.modelName,
                "modelfile": modelFileContent,
                "stream": True
                }
        )
        try:
            request.raise_for_status()
            for line in request.iter_lines():
                body = json.loads(line)
                # print stream status result immediately
                print("Model creation status:" + body.get("status"), end="\n", flush=True)
                if body.get("status") == "success":
                    request.close()
                    self.runPromptLoop(firstPrompt, useTextOnly)
        finally:
            request.close()
    
    def runPromptLoop(self, firstPrompt="Hi!", useTextOnly=False):
        try:
            running = True
            firstRun = True
            while running:
                print("----------------")
                if firstRun:
                    input = firstPrompt
                else:
                    # not first run, we check for user input, to use as prompts.
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
                if len(input) <= 1 or input.isspace():
                    # no valid input exists, use a default one.
                    input = "Hi!"
                input = emoji.replace_emoji(input, replace=lambda chars, data_dict: data_dict['en']) + "\n"
                print(" > Processed input: " + input)
                # send prompt request to ollama server.
                # https://github.com/jmorganca/ollama/blob/main/docs/api.md#request-no-streaming
                request = requests.post(
                    "http://localhost:11434/api/generate",
                    json = {"model": self.modelName, "prompt": input, "stream": False, "context": self.chatContext}
                )
                request.raise_for_status()
                for line in request.iter_lines():
                    body = json.loads(line)
                    response = body.get("response")
                    if len(self.chatContext) == 0:
                        self.chatContext = body.get("context")
                    print("Model response:" + response)
                    s = int(body.get("total_duration")) / self.SecondInNanoseconds
                    print ("Model generation duration in sec:" + str(s))
                    if body.get("done") is not True:
                        raise Exception("Reponse model isn't done. Streaming should be disabled if it isn't.")
                    print(" > Generating voice...")
                    numpyWav = self.tts.generateSpeech(response)
                    sd.play(data=numpyWav, blocking=True)
                request.close()
                if firstRun:
                    firstRun = False
                time.sleep(0.01)
        finally:
            request.close()
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
    @click.option("--text-chat", default=False, help="Whether to use text input instead of voice.", is_flag=True, type=bool)
    @click.option("-a","--accept-text", default="computer", help="The magic word that the listener should use to finish the test with.", type=str)
    @click.option("--whisper-model", default="small.en", help="Which model to use for Whisper, see https://github.com/mallorbc/whisper_mic#available-models-and-languages", type=click.Choice(["tiny","base", "small","medium","tiny.en","base.en", "small.en","medium.en","large"]))
    @click.option("--energy-threshold", default=5000, help="Represents the energy level threshold for sounds. Values below this threshold are considered silence, and values above this threshold are considered speech.", type=int)
    @click.option("--dynamic-energy-threshold", default=False, help="Automatically adjusts Energy Threshold based on the currently ambient noise level while listening.", is_flag=True, type=bool)
    @click.option("--pause-threshold", default=800, help="In milliseconds how long of a pause to recognize a completion of a sentence.", type=int)
    @click.option("-v","--voice-sample", default="sample.wav", help="The voice file to use to inspire the text to speech.", type=str)  
    def chat(first_prompt, text_chat, accept_text, whisper_model, energy_threshold, dynamic_energy_threshold, pause_threshold, voice_sample):
        tts = AiSpeak(voice_sample)
        listener = RecognizeVoice(acceptText=accept_text, micDeviceIndex=sd.default.device[0], model=whisper_model, energyThreshold=energy_threshold, dynamicEnergyThreshold=dynamic_energy_threshold, pauseThreshold=pause_threshold)
        talker = Talker(textToSpeechObject=tts,  useTextOnly=text_chat, voiceListenerObject=listener)
        talker.start(first_prompt, text_chat)

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