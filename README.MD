## Ai Chat with TTS

This allows the ability to interact with an ai executable and have it speak out it's response.  
The interaction is with voice input (taken from https://github.com/mallorbc/whisper_mic), but it also supports text input with the `--text-chat` option.  
It uses https://github.com/coqui-ai/TTS for its speech generation.  

This relies on the executable and its model. You can choose which one to use, gpt4all or alpaca.cpp, both work with their respective models. It could work with other executables too, depending how they take their inputs.

### using gpt4all's executable
You can use gpt4all with the binary from https://github.com/nomic-ai/gpt4all/tree/main/chat  
e.g. on windows grab `gpt4all-lora-quantized-win64.exe`.  
The model itself you can get from here: https://github.com/nomic-ai/gpt4all#try-it-yourself  

### using alpaca.cpp's executable
Slightly more complicated: you can grab chat.exe from here: https://github.com/antimatter15/alpaca.cpp/releases/latest  
If you're not on windows, or have it at a different location you can use `py -3.9 chat.py chat --chat-executable "location/here --argument"`.
The model itself I got it from https://github.com/cocktailpeanut/dalai via `npx dalai alpaca install 7B` (btw which it downloads it directly from https://huggingface.co/Pi3141/alpaca-native-7B-ggml/tree/main). Once the npx script finishes the model can be found in `C:\Users\YourUserName\dalai\alpaca\models\7B`. It would need a slight rename though from `ggml-model-q4_0.bin` to `ggml-alpaca-7b-q4.bin`.

### running
For the reason listed in [some issues](https://github.com/kobitoko/ai-chat-tts#some-issues) it runs best with [Python 3.9](https://www.python.org/downloads/release/python-3913/).  
- To run it type `py -3.9 chat.py chat` or `py -3.9 chat.py chat --help` to view more options.  
- You can also run it with different sound input/output, use these options before the command: `py -3.9 chat.py -i -1 -o -1 speaker`.  
  - The index of -1 means it'll use your default device. To get a list of your device indexes: `py -3.9 chat.py devices`  
- There's also a test command to test coqui-ai TTS.  
  - `py -3.9 chat.py speaker`, or `py -3.9 chat.py speaker --help` for more options.  
- There's also a test command to test whisper-mic.  
  - `py -3.9 chat.py listener`, or `py -3.9 chat.py listener --help` for more options.  

### dependencies
To install dependencies:  
You technically don't need nvidia CUDA since it all can run on the cpu:  
`pip3.9 install -r requirements.txt`  
Installing with [CUDA](https://developer.nvidia.com/cuda-downloads): `pip3.9 install -r requirements-gpu.txt`  
Remember then to edit `gpu=True` in the TTS parameter inside `AiSpeaker.py`.  

`sample.wav` is a recording of me saying "The beige hue on the waters of the loch impressed all, including the French queen, before she heard that symphony again, just as young Arthur wanted."  
Which is an english phonetic pangrams which includes some different allophones. Taken from https://clagnut.com/blog/2380/#English_phonetic_pangrams

### some issues
 - If Coqui TTS complains about numpy, you've got a too modern numpy and probably not using python 3.9.  
 - If Coqui TTS complains about [MeCab missing dll](https://stackoverflow.com/a/68751762), put `libmecab.dll` from your site-packages into system32 or whereever MeCab's executable is.  
 