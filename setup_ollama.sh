#!/bin/bash
echo "Asegurando que Ollama este corriendo y tenga el modelo..."
ollama pull llama3.2
echo "Listo. Ahora puedes correr docker-compose up --build"
