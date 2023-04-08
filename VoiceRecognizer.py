import torch
import numpy
import speech_recognition as sr
import whisper

class RecognizeVoice:
    micDeviceIndex = None
    recognizer = None
    audioModel = None
    acceptText = ""
    def __init__(self, acceptText = "computer", micDeviceIndex=None, model="small.en", energyThreshold=5000, dynamicEnergyThreshold=False, pauseThreshold=800):
        # https://github.com/mallorbc/whisper_mic#available-models-and-languages
        # There are no english models for large
        self.audioModel = whisper.load_model(model)
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energyThreshold
        self.recognizer.dynamic_energy_threshold = dynamicEnergyThreshold
        # default is 0.8, but it has to be int, so in ms and divide by 1000
        self.recognizer.pause_threshold = pauseThreshold / 1000
        self.micDeviceIndex = micDeviceIndex
        self.acceptText = acceptText

    def getAcceptText(self):
        return self.acceptText

    # https://github.com/mallorbc/whisper_mic#available-models-and-languages
    def listenToMic(self):
        result = ""
        keepListening = True
        with sr.Microphone(device_index=self.micDeviceIndex, sample_rate=16000) as mic:
            # https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instanceadjust_for_ambient_noisesource-audiosource-duration-float--1---none
            self.recognizer.adjust_for_ambient_noise(mic, duration=1)
            while(keepListening):
                print(" > Listening...")
                audio = self.recognizer.listen(mic, phrase_time_limit=10)
                audioBuffer = numpy.frombuffer(audio.get_raw_data(), numpy.int16).flatten().astype(numpy.float32)
                torchAudio = torch.from_numpy( audioBuffer / 32768.0)
                result = self.audioModel.transcribe(torchAudio, language='english')
                text = result["text"]
                print(" > you said: " + text)
                if self.acceptText == "" or (text.lower().find(self.acceptText.lower()) > -1) or text.lower().find("exit.") > -1:
                    keepListening = False
        return result["text"]