# PrescreveAI

![PrescreveAI Logo (Placeholder)](https://via.placeholder.com/150x50?text=PrescreveAI)

## Propósito

O **PrescreveAI** é uma ferramenta de linha de comando (CLI) e um servidor de API projetado para auxiliar na geração e gerenciamento de prescrições médicas. Ele permite que usuários e outros programas:

*   **Parseiem** strings de medicação complexas em um formato estruturado.
*   **Gerem** prescrições em formato PDF, com opções de layout (incluindo um layout similar a modelos de receituários controlados).
*   **Exponham** essa funcionalidade via uma API HTTP para integração com sistemas externos.

Nosso objetivo é simplificar o processo de criação de prescrições, tornando-o mais eficiente e menos propenso a erros.

## Status do Projeto: Em Desenvolvimento

Este projeto está atualmente em fase de desenvolvimento ativo. Novas funcionalidades estão sendo adicionadas e melhorias estão sendo implementadas continuamente. Embora as funcionalidades básicas estejam operacionais, ele **não está pronto para uso em ambientes de produção** e pode conter bugs ou ter funcionalidades incompletas.

Sua contribuição e feedback são muito bem-vindos!

## Como Instalar

Para instalar o PrescreveAI em seu sistema e tê-lo disponível globalmente, abra seu terminal e execute o seguinte comando:

```bash
curl -fsSL https://andremillet.github.io/prescreveai/install.sh | bash
```

Este comando irá:

1.  Clonar o repositório do PrescreveAI para `/opt/prescreveai`.
2.  Configurar um ambiente virtual Python (`.venv`).
3.  Instalar todas as dependências necessárias.
4.  Criar um link simbólico para o comando `prescreveai` em `/usr/local/bin`, tornando-o acessível de qualquer lugar no seu terminal.

## Como Usar

Após a instalação, você pode interagir com o PrescreveAI de duas maneiras principais:

### 1. Interface de Linha de Comando (CLI) Interativa

Para iniciar a CLI interativa, basta digitar:

```bash
prescreveai
```

Dentro da CLI, você pode:

*   **Inserir medicações:** Digite a string de medicação no formato `!MED NOME DOSAGEM [COMENTARIO] POSOLOGIA; ...`.
    Exemplo:
    ```
    !MED Paracetamol 500mg [comprimido] 1 comprimido a cada 6 horas; Ibuprofeno 400mg [capsula] 1 capsula a cada 8 horas;
    ```
*   **Gerar PDFs:** Após inserir uma medicação, você pode gerar um PDF digitando `imprimir` ou `imprimir [template]`.
    *   `imprimir` (ou `imprimir memed`): Gera um PDF com um layout similar a um receituário controlado (`prescricao_memed.pdf`).
    *   `imprimir simple`: Gera um PDF com um layout mais simples (`prescricao_simple.pdf`).
    *   Ao gerar o PDF, o programa solicitará os dados do emitente (médico) interativamente.
*   **Sair:** Digite `exit` ou `quit`.

### 2. Servidor de API HTTP

Para iniciar o servidor de API, que permite a integração programática com outros sistemas, use:

```bash
prescreveai serve
```

O servidor será iniciado em segundo plano na porta `8000` (por padrão). Você pode acessar a documentação interativa da API (Swagger UI) em `http://localhost:8000/docs`.

#### Comandos de Gerenciamento do Servidor:

*   **Verificar Status:**
    ```bash
prescreveai status
    ```
*   **Parar Servidor:**
    ```bash
prescreveai stop
    ```

### 3. Atualização do Programa

Para atualizar o PrescreveAI para a versão mais recente, execute:

```bash
prescreveai update
```

Este comando fará um `git pull` no diretório de instalação e reinstalará as dependências.

## Contribuição

Sinta-se à vontade para abrir issues, enviar pull requests ou entrar em contato para discutir melhorias e novas funcionalidades.

## Licença

[Ainda a ser definida]
