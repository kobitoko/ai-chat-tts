## Ai Chat with TTS

Rough idea was to interact with the ai and have it speak out it's response.  
The interaction would be with voice input (like https://github.com/mallorbc/whisper_mic) but that's a TODO.  
It uses https://github.com/coqui-ai/TTS for its speech generation.

This relies on the executable and its model. You can choose which one to use, gpt4all or alpaca.cpp, both work with their respective models.

### gpt4all
You can use gpt4all with the binary from https://github.com/nomic-ai/gpt4all/tree/main/chat  
e.g. on windows grab `gpt4all-lora-quantized-win64.exe`.  
The model itself you can get from here: https://github.com/nomic-ai/gpt4all#try-it-yourself  

### alpaca.cpp
Slightly more complicated: you can grab chat.exe from here: https://github.com/antimatter15/alpaca.cpp/releases/latest  
If you're not on windows, probably need to change the command used in Popen in `talker.py`.
The model itself I got it from https://github.com/cocktailpeanut/dalai via `npx dalai alpaca install 7B` (btw which it downloads it directly from https://huggingface.co/Pi3141/alpaca-native-7B-ggml/tree/main). Once the npx script finishes the model can be found in `C:\Users\YourUserName\dalai\alpaca\models\7B`. It would need a slight rename though from `ggml-model-q4_0.bin` to `ggml-alpaca-7b-q4.bin`.


If Coqui TTS complains about [MeCab missing dll](https://stackoverflow.com/a/68751762), put `libmecab.dll` from your site-packages into system32 or whereever MeCab's executable is.  
If you're like me and installed python via microsoft store (yes idk why I did that) the dll could be found in `C:\Users\username\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\lib\site-packages\MeCab`.  
If Coqui TTS complains about numpy, you've got a too modern numpy and probably not using python 3.9.

For the reason above it runs best with [Python 3.9](https://www.python.org/downloads/release/python-3913/), to run it type `py -3.9 talker.py` or `py -3.9 talker.py --help` to view its parameters.  
There's also a test app to test coqui-ai TTS. `py -3.9 tts-test.py`.  

To install dependencies:  
You technically don't need [CUDA](https://developer.nvidia.com/cuda-downloads) since it all can run on the cpu too.  
So you could just install `requirements.txt`'s `torch`, `torchaudio`, and `torchvision` without the `+cu118` part and remove the `--extra-index-url` line from the file. Just remember to put `gpu=False` in the TTS parameter `talker.py` and `tts-test`.  
`pip3.9 install -r requirements.txt`  

`sample.wav` is just a recording of https://www.youtube.com/watch?v=fkoy1_R5N8M  
