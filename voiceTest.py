import torch
import numpy
import speech_recognition as sr
import whisper

recognizer = None
micDeviceIndex = None
audioModel = None

# Taken from https://github.com/mallorbc/whisper_mic
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
    for id, name in enumerate(sr.Microphone.list_microphone_names()):
        print(str(id) + ": " + name)
    global micDeviceIndex
    micDeviceIndex = 72

def listenToMic(acceptText = "hi computer"):
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
            print(" > you said: " + result["text"])
            if acceptText == "" or result["text"].lower().find(acceptText) > -1:
                keepListening = False
    return result["text"]

initListener()
print("doone: " + listenToMic())