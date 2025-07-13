#!/bin/bash

# Caminho absoluto para o diretório do projeto
PROJECT_DIR="/home/woulschneider/petri-dish/prescreveai"

# Ativar o ambiente virtual
source "$PROJECT_DIR/.venv/bin/activate"

# Executar o script Python com todos os argumentos passados
exec "$PROJECT_DIR/prescreveai.py" "$@"
