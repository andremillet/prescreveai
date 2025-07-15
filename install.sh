#!/bin/bash

# Script para baixar e instalar o pacote PrescreveAI

set -e # Encerra o script se qualquer comando falhar

# --- Configurações ---
# URL do pacote .tar.gz hospedado no GitHub Releases
PACKAGE_URL="https://github.com/user-attachments/files/21224012/prescreveai.tar.gz"

# Nome do arquivo do pacote
PACKAGE_FILE="prescreveai.tar.gz"

# Diretório temporário para o download
TMP_DIR=$(mktemp -d -t prescreveai-install-XXXXXX)

# Cores para mensagens
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para limpar o diretório temporário na saída
cleanup() {
    echo "Limpando arquivos temporários..."
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# --- Início da Execução ---
echo -e "${GREEN}Baixando o pacote de instalação do PrescreveAI...${NC}"

# Navega para o diretório temporário
cd "$TMP_DIR"

# Baixa o pacote (-L para seguir redirecionamentos)
curl -fsSL -o "$PACKAGE_FILE" "$PACKAGE_URL"
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao baixar o pacote de: $PACKAGE_URL${NC}"
    exit 1
fi

echo -e "${GREEN}Pacote baixado. Extraindo...${NC}"

# Extrai o pacote
tar -xzf "$PACKAGE_FILE"
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao extrair o pacote.${NC}"
    exit 1
fi

# Executa o script de instalação local
echo -e "${GREEN}Iniciando o script de instalação local...${NC}"

if [ -f "./install.sh" ]; then
    chmod +x ./install.sh
    ./install.sh
else
    echo -e "${RED}Script de instalação 'install.sh' não encontrado no pacote.${NC}"
    exit 1
fi

echo -e "${GREEN}Processo de instalação concluído.${NC}"

