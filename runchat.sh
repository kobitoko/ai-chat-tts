#!/bin/bash

echo "Checking if ollama docker container exists"
if docker container inspect ollama
then
	echo "starting ollama docker on localhost:11434"
	docker start ollama
else
	echo "Pulling ollama docker image"
	docker pull ollama/ollama
	echo "running ollama docker on localhost:11434"
    docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
fi
echo "Starting the chat script"
py -3.9 chat.py chat
