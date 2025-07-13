# Como Utilizar o `prescreveai` como Subprocesso (CLI-based API)

Este documento descreve como interagir programaticamente com o script `prescreveai` a partir de outros programas ou scripts, tratando-o como uma "API" baseada em linha de comando.

## O que é uma "CLI-based API"?

Uma API (Application Programming Interface) é um conjunto de definições e protocolos que permite que diferentes softwares se comuniquem. Tradicionalmente, APIs são frequentemente baseadas em HTTP (como APIs RESTful), onde a comunicação ocorre através de requisições de rede.

No entanto, o `prescreveai` foi projetado como uma ferramenta de linha de comando (CLI). Ao utilizá-lo como um subprocesso, você está essencialmente usando sua interface de linha de comando como uma API. Isso significa que você envia dados para o `prescreveai` através de sua entrada padrão (`stdin`) e ele retorna resultados através de sua saída padrão (`stdout`) e saída de erro padrão (`stderr`).

## Por que usar como subprocesso?

*   **Reusabilidade:** Permite que a lógica de parsing e geração de PDF do `prescreveai` seja utilizada por outros programas sem a necessidade de reescrever o código.
*   **Integração:** Facilita a integração do `prescreveai` em sistemas maiores, scripts de automação ou programas escritos em diferentes linguagens de programação.
*   **Flexibilidade:** Você pode controlar o `prescreveai` e obter seus resultados de forma programática.

## Como Utilizar (Exemplo em Python)

A maneira mais comum de interagir com programas de linha de comando em Python é através do módulo `subprocess`.

```python
import subprocess
import json
import os # Para construir o caminho do interpretador do ambiente virtual

def generate_prescription(medication_string, emitter_data=None, template="memed"):
    """
    Gera uma prescrição usando o script prescreveai.

    Args:
        medication_string (str): A string de medicação no formato "!MED ...".
        emitter_data (dict, optional): Um dicionário com os dados do emitente.
                                       Ex: {'nome': 'Dr. Ficticio', 'crm': '123456 RJ', ...}
                                       Se None, o script prescreveai solicitará interativamente (não recomendado para uso programático).
        template (str): O template do PDF a ser usado ('memed' ou 'simple').

    Returns:
        dict: Um dicionário contendo a saída JSON do prescreveai, ou um erro.
              Também gera um arquivo PDF no diretório de execução.
    """
    # Caminho para o interpretador Python dentro do ambiente virtual
    # Certifique-se de que este caminho esteja correto para o seu ambiente
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'bin', 'python3')
    prescreveai_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prescreveai.py')

    command_input = f"{medication_string}\n"

    # Adiciona o comando imprimir com o template
    command_input += f"imprimir {template}\n"

    # Se os dados do emitente forem fornecidos, adicione-os à entrada
    # É crucial que todos os campos esperados pelo script sejam fornecidos
    if emitter_data:
        command_input += f"{emitter_data.get('nome', '')}\n"
        command_input += f"{emitter_data.get('crm', '')}\n"
        command_input += f"{emitter_data.get('endereco', '')}\n"
        command_input += f"{emitter_data.get('telefone', '')}\n"
        command_input += f"{emitter_data.get('cidade_uf', '')}\n"
    else:
        # Se emitter_data não for fornecido, o script prescreveai esperará por ele interativamente.
        # Para uso programático, é altamente recomendado fornecer emitter_data.
        print("Aviso: emitter_data não fornecido. O script prescreveai pode aguardar entrada interativa.")
    
    command_input += "exit\n" # Comando para sair do prescreveai

    try:
        # Executa o prescreveai como um subprocesso
        process = subprocess.run(
            [venv_python, prescreveai_script],
            input=command_input,
            capture_output=True,
            text=True, # Decodifica stdout/stderr como texto
            check=True # Levanta uma exceção se o comando retornar um código de erro
        )

        # A saída JSON é a última parte da saída padrão
        # Precisamos extrair apenas a parte JSON
        output_lines = process.stdout.splitlines()
        json_output_start = -1
        for i, line in enumerate(output_lines):
            if line.strip() == "--- Saída JSON ---":
                json_output_start = i + 1
                break
        
        if json_output_start != -1:
            json_block = []
            for i in range(json_output_start, len(output_lines)):
                line = output_lines[i].strip()
                if line == "--------------------":
                    break
                json_block.append(line)
            
            try:
                return json.loads("".join(json_block))
            except json.JSONDecodeError:
                return {"error": "Failed to decode JSON output", "raw_output": process.stdout}
        else:
            return {"error": "JSON output not found in prescreveai output", "raw_output": process.stdout}

    except subprocess.CalledProcessError as e:
        return {"error": f"prescreveai command failed: {e}", "stdout": e.stdout, "stderr": e.stderr}
    except FileNotFoundError:
        return {"error": f"Python interpreter or prescreveai script not found. Check paths: {venv_python}, {prescreveai_script}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    # Exemplo de uso:
    med_str = "!MED Dipirona 500mg [comprimido] 1 comprimido a cada 6 horas; Amoxicilina 250mg [capsula] 1 capsula a cada 8 horas;"
    
    emitter_info = {
        'nome': 'Dr. Exemplo',
        'crm': 'CRM 123456 SP',
        'endereco': 'Rua da Amostra, 456',
        'telefone': '(11) 1234-5678',
        'cidade_uf': 'São Paulo - SP'
    }

    print("--- Gerando prescrição com template memed ---")
    result_memed = generate_prescription(med_str, emitter_info, template="memed")
    print(json.dumps(result_memed, indent=2, ensure_ascii=False))

    print("\n--- Gerando prescrição com template simple ---")
    result_simple = generate_prescription(med_str, emitter_info, template="simple")
    print(json.dumps(result_simple, indent=2, ensure_ascii=False))

    # Para verificar os PDFs gerados, procure por 'prescricao_memed.pdf' e 'prescricao_simple.pdf'
    # no diretório onde você executou este script.
```

## Considerações Importantes:

*   **Caminho do Interpretador Python:** É crucial que o caminho para o interpretador Python dentro do seu ambiente virtual (`./.venv/bin/python3`) e o caminho para o script `prescreveai.py` estejam corretos. O exemplo acima usa `os.path.abspath(__file__)` para tentar construir caminhos relativos ao script que está chamando.
*   **Entrada Completa:** A string de entrada (`command_input`) deve conter todas as linhas que o `prescreveai` espera, incluindo a string de medicação, o comando `imprimir` (com o template desejado), **todos os dados do emitente (se `emitter_data` for fornecido)** e, finalmente, o comando `exit` para encerrar o `prescreveai` de forma limpa.
*   **Quebras de Linha:** Use `\n` para simular a tecla Enter entre as linhas de entrada.
*   **Parsing da Saída:** O `prescreveai` imprime tanto a saída formatada quanto a JSON. O script de exemplo inclui lógica para extrair especificamente o bloco JSON.
*   **Localização do PDF:** Os arquivos PDF (`prescricao_memed.pdf`, `prescricao_simple.pdf`) serão gerados no diretório de trabalho atual do script que está chamando o `prescreveai`.
*   **Tratamento de Erros:** O uso de `try...except` com `subprocess.CalledProcessError` é fundamental para capturar erros que ocorram durante a execução do `prescreveai`.

Ao seguir estas instruções, você pode integrar o `prescreveai` em seus próprios programas e automatizar a geração de prescrições.
