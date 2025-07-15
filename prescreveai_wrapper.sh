#!/bin/bash

# Wrapper para o comando prescreveai

# Verifica se o primeiro argumento é 'update'
if [ "$1" == "update" ]; then
    echo "Atualizando PrescreveAI para a versão mais recente..."
    # Executa o script de instalação online, que cuidará da atualização
    curl -fsSL https://andremillet.github.io/prescreveai/install.sh | bash
    exit 0
fi

# Se não for 'update', continua com a execução normal

# O script de instalação define o diretório de instalação correto.
# Este wrapper espera estar no mesmo diretório que o ambiente virtual.
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ativar o ambiente virtual
source "$INSTALL_DIR/.venv/bin/activate"

# Executar o script Python com todos os argumentos passados
exec "$INSTALL_DIR/prescreveai.py" "$@"
