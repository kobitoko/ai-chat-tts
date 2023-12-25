## Ai Chat with TTS

This allows the ability to interact with a large language model and have it speak out its response.  
The interaction is with voice input (taken from https://github.com/mallorbc/whisper_mic), but it also supports text input with the `--text-chat` option.  
It uses https://github.com/coqui-ai/TTS for its speech generation.  

It relies on https://github.com/jmorganca/ollama for the LLM, which you can get from https://ollama.ai/ and [the models that are available on there](https://ollama.ai/library).  
You can choose which model to use, and [change other parameters by editing Modelfile](https://github.com/jmorganca/ollama/blob/main/docs/modelfile.md).  
You can find Modelfiles made by others for Ollama at https://ollamahub.com/.


### Ollama setup with Docker
You can easily run it through the docker image https://hub.docker.com/r/ollama/ollama  
This option works well for windows.  
```
docker pull ollama/ollama
```
and run the ollama docker with
```
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```
The python script basically just expects ollama to be available at `http://localhost:11434`  

### Install dependencies
To install dependencies:  
You technically don't need nvidia CUDA since it all can run on the cpu:  
`pip3.9 install -r requirements.txt`  
Installing with [CUDA](https://developer.nvidia.com/cuda-downloads): `pip3.9 install -r requirements-gpu.txt`  
Remember then [to edit](https://github.com/kobitoko/ai-chat-tts/blob/main/AiSpeaker.py#L31C5-L31C5) `gpu=True` in the TTS parameter inside `AiSpeaker.py`.  

`sample.wav` is a recording of me saying "The beige hue on the waters of the loch impressed all, including the French queen, before she heard that symphony again, just as young Arthur wanted."  
Which is an english phonetic pangrams which includes some different allophones. Taken from https://clagnut.com/blog/2380/#English_phonetic_pangrams

### Running
For the reason listed in [some issues](https://github.com/kobitoko/ai-chat-tts#some-issues) it runs best with [Python 3.9](https://www.python.org/downloads/release/python-3913/).  

#### With docker
Assuming you have docker installed and runnning, as well as python 3.9 and this project's dependencies installed:  
You can run this script to get/start the docker and run the python script.
```
./runchat.sh
```
#### Just the python script
Running the python script manually, assuming ollama is available at `http://localhost:11434`:  
- To run it type `py -3.9 chat.py chat` or `py -3.9 chat.py chat --help` to view more options.  
- You can also run it with different sound input/output, use these options before the command: `py -3.9 chat.py -i -1 -o -1 speaker`.  
  - The index of -1 means it'll use your default device. To get a list of your device indexes: `py -3.9 chat.py devices`  
- There's also a test command to test coqui-ai TTS.  
  - `py -3.9 chat.py speaker`, or `py -3.9 chat.py speaker --help` for more options.  
- There's also a test command to test whisper-mic.  
  - `py -3.9 chat.py listener`, or `py -3.9 chat.py listener --help` for more options.  

### Some issues
 - If Coqui TTS complains about numpy, you've got a too modern numpy and probably not using python 3.9.  
 - If Coqui TTS complains about [MeCab missing dll](https://stackoverflow.com/a/68751762), put `libmecab.dll` from your site-packages into system32 or whereever MeCab's executable is.  
 