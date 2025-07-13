#!/bin/bash

# Nome do repositório e do diretório
REPO_NAME="prescreveai"

# URL do repositório Git
REPO_URL="https://github.com/andremillet/prescreveai.git"

# Diretório de instalação (pode ser ajustado)
INSTALL_DIR="/opt/$REPO_NAME"

# Cores para mensagens
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Iniciando a instalação do PrescreveAI...${NC}"

# 1. Clonar o repositório
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${RED}Diretório de instalação $INSTALL_DIR já existe. Removendo...${NC}"
    sudo rm -rf "$INSTALL_DIR"
fi

echo -e "${GREEN}Clonando o repositório do GitHub...${NC}"
sudo git clone "$REPO_URL" "$INSTALL_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao clonar o repositório. Verifique a URL e sua conexão.${NC}"
    exit 1
fi

cd "$INSTALL_DIR"

# 2. Criar e ativar o ambiente virtual
echo -e "${GREEN}Configurando o ambiente virtual...${NC}"
python3 -m venv .venv

if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao criar o ambiente virtual. Certifique-se de que python3-venv está instalado.${NC}"
    exit 1
fi

source .venv/bin/activate

# 3. Instalar dependências
echo -e "${GREEN}Instalando dependências Python...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar dependências. Verifique o requirements.txt.${NC}"
    exit 1
fi

# 4. Tornar o wrapper executável
echo -e "${GREEN}Configurando permissões do wrapper...${NC}"
chmod +x prescreveai_wrapper.sh

# 5. Criar link simbólico em /usr/local/bin
echo -e "${GREEN}Criando link simbólico para o comando 'prescreveai'...${NC}"
sudo ln -sf "$INSTALL_DIR/prescreveai_wrapper.sh" /usr/local/bin/prescreveai

if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao criar o link simbólico. Permissão negada?${NC}"
    exit 1
fi

echo -e "\n${GREEN}Instalação do PrescreveAI concluída com sucesso!${NC}"
echo "Você pode agora usar o comando 'prescreveai'."
echo "Experimente:"
echo "  prescreveai"
echo "  prescreveai serve"
