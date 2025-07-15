#!/bin/bash

# --- Configurações ---
# Diretório de instalação dentro da home do usuário, sem necessidade de sudo.
INSTALL_BASE_DIR="$HOME/.local/share"
INSTALL_DIR="$INSTALL_BASE_DIR/prescreveai"
# Diretório para binários do usuário, geralmente já está no PATH.
BIN_DIR="$HOME/.local/bin"

# Cores para mensagens
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Iniciando a instalação do PrescreveAI...${NC}"

# --- Pré-instalação ---
# Garante que os diretórios de destino existam.
mkdir -p "$INSTALL_BASE_DIR"
mkdir -p "$BIN_DIR"

# Verifica se o diretório de instalação já existe e o remove para uma instalação limpa.
if [ -d "$INSTALL_DIR" ]; then
    echo "Diretório de instalação existente encontrado. Removendo para uma instalação limpa..."
    rm -rf "$INSTALL_DIR"
fi

# --- Instalação ---
# Copia os arquivos da aplicação para o diretório de instalação.
# O script espera ser executado de dentro do diretório do projeto descompactado.
echo "Copiando arquivos da aplicação..."
# Cria o diretório de destino e copia o conteúdo do diretório atual para ele.
mkdir -p "$INSTALL_DIR"
cp -r ./* "$INSTALL_DIR/"


# Entra no diretório de instalação para continuar o processo.
cd "$INSTALL_DIR"

# --- Ambiente Virtual ---
echo -e "${GREEN}Configurando o ambiente virtual Python...${NC}"
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao criar o ambiente virtual. Verifique se 'python3' e 'python3-venv' estão instalados.${NC}"
    exit 1
fi

# Ativa o ambiente virtual para os próximos comandos.
source .venv/bin/activate

# --- Dependências ---
echo -e "${GREEN}Instalando dependências a partir da pasta 'packages'...${NC}"
# Instala os pacotes da pasta 'packages' sem precisar de conexão com a internet.
pip install --no-index --find-links=packages -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar as dependências. Verifique a pasta 'packages' e o 'requirements.txt'.${NC}"
    exit 1
fi

# --- Wrapper e Link Simbólico ---
echo -e "${GREEN}Configurando o comando 'prescreveai'...${NC}"
# Torna o script wrapper executável.
chmod +x prescreveai_wrapper.sh

# Cria um link simbólico no diretório de binários do usuário.
ln -sf "$INSTALL_DIR/prescreveai_wrapper.sh" "$BIN_DIR/prescreveai"
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao criar o link simbólico em $BIN_DIR.${NC}"
    exit 1
fi

# --- Pós-instalação ---
# Verifica se o diretório de binários do usuário está no PATH.
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "\n${RED}AVISO:${NC} O diretório $BIN_DIR não parece estar no seu PATH."
    echo "Para usar o comando 'prescreveai' de qualquer lugar, adicione a seguinte linha ao seu"
    echo "arquivo de configuração de shell (como ~/.bashrc, ~/.zshrc, ou ~/.profile):"
    echo -e "\n  export PATH=\"$BIN_DIR:\$PATH\"\n"
    echo "Depois, reinicie seu terminal ou execute 'source ~/.bashrc' (ou o arquivo equivalente)."
fi

echo -e "\n${GREEN}Instalação do PrescreveAI concluída com sucesso!${NC}"
echo "Você pode agora usar o comando 'prescreveai'."
echo "Experimente:"
echo "  prescreveai"
echo "  prescreveai serve"
