#!/usr/bin/env python3
import json
import re
import sys
import subprocess
import os
import signal # Import for signal.SIGTERM
import time # Import for time.sleep

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import date

# Variável global para armazenar os dados do emitente na sessão
# Esta variável será preenchida pelo api_server.py quando usado como API
EMITTER_DATA = {}

# PID file for the server process
PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.pid")

def parse_medication_string(input_string):
    """
    Parses a medication string and returns a list of medication dictionaries.
    Expected format: !MED NOME DOSAGEM [COMENTARIO] POSOLOGIA; NOME DOSAGEM POSOLOGIA
    """
    if not input_string.startswith("!MED "):
        return {"error": "Input must start with '!MED '"}

    medications_raw = input_string[len("!MED "):].strip()
    medication_items = medications_raw.split(';')

    parsed_medications = []
    for item in medication_items:
        item = item.strip()
        if not item:
            continue

        # Regex to capture name, dosage, optional comment, and posology
        # Name: anything until a number (start of dosage)
        # Dosage: number + unit (e.g., 500MG, 0.5ML)
        # Comment: optional, enclosed in []
        # Posology: remaining part of the string
        match = re.match(r"^(.*?)\s+(\d+\.?\d*(?:MG|ML|G|MCG|UI|MG/ML|GOTAS|COMPRIMIDOS|CÁPSULAS|%))\s*(?:\\[(.*?)\\])?\s*(.*)$", item, re.IGNORECASE)

        if match:
            name = match.group(1).strip().upper()
            dosage = match.group(2).strip().upper()
            comment = match.group(3)
            posology = match.group(4).strip().upper()

            if comment:
                comment = comment.strip().upper()

            # Basic validation
            if not name:
                return {"error": f"Medication name cannot be empty in: {item}"}
            if not re.search(r'\d', dosage):
                return {"error": f"Dosage must contain at least one number in: {item}"}
            if not posology:
                return {"error": f"Posology cannot be empty in: {item}"}

            parsed_medications.append({
                "nome": name,
                "dosagem": dosage,
                "comentario": comment,
                "posologia": posology
            })
        else:
            return {"error": f"Could not parse medication item: {item}"}
    
    if not parsed_medications:
        return {"error": "No valid medications found in input."}

    return {"medicacoes": parsed_medications}

def format_medication_text(medication):
    """Formats a single medication dictionary into a human-readable string for PDF."""
    name = medication['nome'].title() # Title case for better readability in PDF
    dosage = medication['dosagem'].upper()
    comment = medication['comentario']
    posology = medication['posologia'].capitalize()

    if comment:
        return f"{name} {dosage} [{comment}] {posology}"
    else:
        return f"{name} {dosage} {posology}"

def get_emitter_data():
    global EMITTER_DATA
    # Quando usado como API, EMITTER_DATA será preenchido externamente.
    # Não solicitamos entrada do usuário aqui.
    return EMITTER_DATA

def generate_memed_like_pdf(medications, filename="prescricao_memed.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Margins
    left_margin = inch
    right_margin = width - inch
    top_margin = height - inch
    bottom_margin = inch

    # Fonts
    c.setFont("Helvetica", 10)

    # --- Header Section (SYNAPSI, Doctor Name, CRM) ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, top_margin, "SYNAPSI") # Placeholder for logo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin + 1.5 * inch, top_margin, "Dr. André Batista Millet Neves")
    c.setFont("Helvetica", 10)
    c.drawString(left_margin + 1.5 * inch, top_margin - 15, "Neurologia - CRM 52946788")

    # --- IDENTIFICAÇÃO DO EMITENTE Section ---
    emitter_box_x = left_margin
    emitter_box_y = top_margin - 0.7 * inch - 70 # Adjusted y-position
    emitter_box_width = 3.5 * inch
    emitter_box_height = 1.2 * inch
    c.rect(emitter_box_x, emitter_box_y, emitter_box_width, emitter_box_height)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(emitter_box_x + 5, emitter_box_y + emitter_box_height - 15, "IDENTIFICAÇÃO DO EMITENTE")
    c.line(emitter_box_x, emitter_box_y + emitter_box_height - 20, emitter_box_x + emitter_box_width, emitter_box_y + emitter_box_height - 20)

    emitter = get_emitter_data()
    c.setFont("Helvetica", 8)
    text_y = emitter_box_y + emitter_box_height - 35
    c.drawString(emitter_box_x + 5, text_y, f"Nome: {emitter.get('nome', '')}")
    c.drawString(emitter_box_x + 5, text_y - 10, f"CRM: {emitter.get('crm', '')}")
    c.drawString(emitter_box_x + 5, text_y - 20, f"Endereço: {emitter.get('endereco', '')}")
    c.drawString(emitter_box_x + 5, text_y - 30, f"Telefone: {emitter.get('telefone', '')}")
    c.drawString(emitter_box_x + 5, text_y - 40, f"Cidade e UF: {emitter.get('cidade_uf', '')}")

    # --- RECEITUÁRIO CONTROLE ESPECIAL Section ---
    receituario_box_x = left_margin + emitter_box_width + 0.2 * inch
    receituario_box_y = emitter_box_y
    receituario_box_width = width - right_margin - receituario_box_x
    receituario_box_height = emitter_box_height
    c.rect(receituario_box_x, receituario_box_y, receituario_box_width, receituario_box_height)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(receituario_box_x + 5, receituario_box_y + receituario_box_height - 15, "RECEITUÁRIO CONTROLE ESPECIAL")
    c.line(receituario_box_x, receituario_box_y + receituario_box_height - 20, receituario_box_x + receituario_box_width, receituario_box_y + receituario_box_height - 20)

    c.setFont("Helvetica", 8)
    today = date.today().strftime("%d/%m/%Y")
    c.drawString(receituario_box_x + 5, receituario_box_y + receituario_box_height - 35, f"DATA: {today}")
    c.drawString(receituario_box_x + 5, receituario_box_y + receituario_box_height - 45, "1a. via farmácia")
    c.drawString(receituario_box_x + 5, receituario_box_y + receituario_box_height - 55, "2a. via paciente")

    # --- Patient Information (CLEUZA FERREIRA DE SA) ---
    patient_y = emitter_box_y - 0.2 * inch - 30 # Adjusted y-position
    c.setFont("Helvetica", 9)
    c.drawString(left_margin, patient_y, "CLEUZA FERREIRA DE SA")
    c.drawString(left_margin, patient_y - 10, "CPF: 280.122.406-53")
    c.drawString(left_margin, patient_y - 20, "Endereço: AVENIDA LUCIO COSTA, 17710, RIO DE JANEIRO")
    c.line(left_margin, patient_y - 25, right_margin, patient_y - 25)

    # --- Medications Section ---
    c.setFont("Helvetica", 9)
    current_y = patient_y - 0.5 * inch - 20 # Adjusted start for medications

    for i, med in enumerate(medications):
        med_line = format_medication_text(med)
        c.drawString(left_margin, current_y, med_line)
        current_y -= 15 # Line spacing
        if current_y < bottom_margin + 1.5 * inch: # Check for new page
            c.showPage()
            c.setFont("Helvetica", 9)
            current_y = top_margin - 0.5 * inch # Reset y for new page

    # --- ASSINATURA Section ---
    signature_y = current_y - 0.5 * inch # Position below medications
    c.line(width / 2 - 1 * inch, signature_y, width / 2 + 1 * inch, signature_y)
    c.setFont("Helvetica", 8)
    c.drawString(width / 2 - 0.5 * inch, signature_y - 10, "ASSINATURA")

    # --- IDENTIFICAÇÃO DO COMPRADOR Section ---
    comprador_box_x = left_margin
    comprador_box_y = bottom_margin + 0.5 * inch # Adjusted y-position
    comprador_box_width = 3.5 * inch
    comprador_box_height = 1.2 * inch
    c.rect(comprador_box_x, comprador_box_y, comprador_box_width, comprador_box_height)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(comprador_box_x + 5, comprador_box_y + comprador_box_height - 15, "IDENTIFICAÇÃO DO COMPRADOR")
    c.line(comprador_box_x, comprador_box_y + comprador_box_height - 20, comprador_box_x + comprador_box_width, comprador_box_y + comprador_box_height - 20)

    c.setFont("Helvetica", 8)
    text_y = comprador_box_y + comprador_box_height - 35
    c.drawString(comprador_box_x + 5, text_y, "Nome:")
    c.drawString(comprador_box_x + 5, text_y - 10, "RG:")
    c.drawString(comprador_box_x + 5, text_y - 20, "Endereço:")
    c.drawString(comprador_box_x + 5, text_y - 30, "Telefone:")
    c.drawString(comprador_box_x + 5, text_y - 40, "Cidade e UF:")

    # --- IDENTIFICAÇÃO DO FORNECEDOR Section ---
    fornecedor_box_x = left_margin + comprador_box_width + 0.2 * inch
    fornecedor_box_y = comprador_box_y
    fornecedor_box_width = receituario_box_width
    fornecedor_box_height = comprador_box_height
    c.rect(fornecedor_box_x, fornecedor_box_y, fornecedor_box_width, fornecedor_box_height)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(fornecedor_box_x + 5, fornecedor_box_y + fornecedor_box_height - 15, "IDENTIFICAÇÃO DO FORNECEDOR")
    c.line(fornecedor_box_x, fornecedor_box_y + fornecedor_box_height - 20, fornecedor_box_x + fornecedor_box_width, fornecedor_box_y + fornecedor_box_height - 20)

    c.setFont("Helvetica", 8)
    text_y = fornecedor_box_y + fornecedor_box_height - 35
    c.drawString(fornecedor_box_x + 5, text_y, "DATA")
    c.drawString(fornecedor_box_x + 5, text_y - 10, "ASSINATURA DO FARMACÊUTICO")

    # --- Footer ---
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, bottom_margin - 0.2 * inch, "Av.das Américas - 500. Shopping Downtown.")
    c.drawCentredString(width / 2, bottom_margin - 0.35 * inch, "Bloco 12 sala 207 - Barra da Tijuca")

    c.save()
    print(f"PDF gerado com sucesso: {filename}")

def generate_simple_pdf(medications, filename="prescricao_simple.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, height - inch, "Prescrição Médica Simples")

    emitter = get_emitter_data()
    c.setFont("Helvetica", 12)
    y_pos = height - inch - 0.5 * inch
    c.drawString(inch, y_pos, f"Dr(a). {emitter.get('nome', '')}")
    c.drawString(inch, y_pos - 20, f"CRM: {emitter.get('crm', '')}")
    c.drawString(inch, y_pos - 40, f"Data: {date.today().strftime('%d/%m/%Y')}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y_pos - 80, "Medicações:")
    c.setFont("Helvetica", 12)
    current_y = y_pos - 100

    for i, med in enumerate(medications):
        med_line = format_medication_text(med)
        c.drawString(inch, current_y, f"{i+1}. {med_line}")
        current_y -= 20
        if current_y < inch: # New page if content goes too low
            c.showPage()
            c.setFont("Helvetica", 12)
            current_y = height - inch

    c.save()
    print(f"PDF gerado com sucesso: {filename}")

# --- Server Management Functions ---
def start_server():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, ".venv", "bin", "python3")
    api_server_path = os.path.join(script_dir, "api_server.py")

    if not os.path.exists(api_server_path):
        print(f"Erro: api_server.py não encontrado em {api_server_path}")
        sys.exit(1)

    command = [venv_python, "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000"]

    env = os.environ.copy()
    env['PYTHONPATH'] = script_dir + os.pathsep + env.get('PYTHONPATH', '')

    print(f"Iniciando servidor FastAPI com: {' '.join(command)}")
    try:
        process = subprocess.Popen(command, env=env, preexec_fn=os.setsid) # Use setsid to create a new process group
        
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))
        print(f"Servidor FastAPI iniciado em segundo plano (PID: {process.pid}). Acesse http://localhost:8000/docs")
    except FileNotFoundError:
        print(f"Erro: interpretador Python ou uvicorn não encontrado em {venv_python}. Certifique-se de que o ambiente virtual está ativado e uvicorn está instalado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao iniciar o servidor FastAPI: {e}")
        sys.exit(1)

def stop_server():
    if not os.path.exists(PID_FILE):
        print("Servidor não está rodando (arquivo PID não encontrado).")
        return

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    try:
        # Send SIGTERM to the process group to ensure all child processes are killed
        os.killpg(pid, signal.SIGTERM)
        print(f"Servidor FastAPI (PID: {pid}) interrompido.")
    except ProcessLookupError:
        print(f"Servidor FastAPI (PID: {pid}) não encontrado ou já encerrado.")
    except Exception as e:
        print(f"Erro ao tentar parar o servidor: {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def server_status():
    if not os.path.exists(PID_FILE):
        print("Servidor não está rodando (arquivo PID não encontrado).")
        return

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    try:
        # Sending signal 0 checks if the process exists without killing it
        os.kill(pid, 0)
        print(f"Servidor FastAPI está rodando com PID: {pid}.")
    except ProcessLookupError:
        print(f"Servidor FastAPI (PID: {pid}) não está rodando (processo não encontrado).")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE) # Clean up stale PID file
    except Exception as e:
        print(f"Erro ao verificar status do servidor: {e}")

# --- CLI Logic ---
def run_cli():
    import io # Import here to avoid circular dependency with sys.stdin/stdout

    print("Bem-vindo ao PrescreveAI CLI!")
    print("Digite a linha de medicação (ex: !MED AMITRIPTILINA 25MG NOITE; ALPRAZOLAM 2MG NOITE;)")
    print("Digite 'imprimir [template]' para gerar um PDF da última prescrição. Templates: memed (padrão), simple.")
    print("Digite 'exit' ou 'quit' para sair.")

    last_parsed_medications = [] # Armazena a última lista de medicações processadas

    while True:
        try:
            # Use sys.stdin para entrada interativa
            sys.stdout.write("> ")
            sys.stdout.flush()
            user_input = sys.stdin.readline().strip()
        except EOFError: # Handle Ctrl+D
            print("\nSaindo...")
            break

        if user_input.lower() in ["exit", "quit"]:
            print("Saindo...")
            break
        elif user_input.lower().startswith("imprimir"):
            parts = user_input.lower().split()
            template_name = "memed" # Default template
            if len(parts) > 1:
                template_name = parts[1]

            if last_parsed_medications:
                # Temporarily set EMITTER_DATA for CLI interactive use
                # This will be overwritten by API calls
                global EMITTER_DATA
                EMITTER_DATA = {}
                # get_emitter_data() will now prompt the user

                if template_name == "memed":
                    generate_memed_like_pdf(last_parsed_medications)
                elif template_name == "simple":
                    generate_simple_pdf(last_parsed_medications)
                else:
                    print(f"Template desconhecido: {template_name}. Usando o template padrão (memed).")
                    generate_memed_like_pdf(last_parsed_medications)
            else:
                print("Nenhuma medicação processada para imprimir. Por favor, insira uma prescrição primeiro.")
            continue
        elif not user_input:
            continue

        result = parse_medication_string(user_input)

        if "error" in result:
            print(f"Erro: {result['error']}")
        else:
            last_parsed_medications = result['medicacoes'] # Armazena para uso futuro

            print("\n--- Saída Formatada ---")
            for i, med in enumerate(last_parsed_medications):
                print(f"{i+1}. {format_medication_text(med)}")
                print("-" * 20) # Separator for multiple medications

            print("\n--- Saída JSON ---")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("--------------------\n")

# --- Install Instructions ---
def show_install_instructions():
    print("\nBem-vindo ao PrescreveAI!")
    print("Para instalar o PrescreveAI e tê-lo disponível globalmente, execute o seguinte comando:")
    print("\ncurl -fsSL https://andremillet.github.io/prescreveai/install.sh | bash\n")
    print("Após a instalação, você poderá usar os comandos 'prescreveai' e 'prescreveai serve'.")

# --- Update Function ---
def update_program():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    install_dir = os.path.abspath(os.path.join(script_dir, "..")) # Assuming installed in /opt/prescreveai

    print("\nIniciando atualização do PrescreveAI...")

    # 1. Navegar para o diretório de instalação
    if not os.path.exists(install_dir) or not os.path.isdir(install_dir):
        print(f"Erro: Diretório de instalação não encontrado em {install_dir}. Certifique-se de que o PrescreveAI foi instalado corretamente.")
        sys.exit(1)
    
    os.chdir(install_dir)

    # 2. Fazer git pull
    print("Puxando as últimas alterações do repositório...")
    try:
        subprocess.run(["git", "pull"], check=True, capture_output=True, text=True)
        print("Alterações puxadas com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao puxar alterações do Git: {e.stderr}")
        sys.exit(1)

    # 3. Ativar o ambiente virtual e instalar dependências
    print("Atualizando dependências do ambiente virtual...")
    venv_activate_script = os.path.join(install_dir, ".venv", "bin", "activate")
    requirements_file = os.path.join(install_dir, "requirements.txt")

    if not os.path.exists(venv_activate_script):
        print(f"Erro: Ambiente virtual não encontrado em {venv_activate_script}. Recrie o ambiente virtual ou reinstale o PrescreveAI.")
        sys.exit(1)
    
    if not os.path.exists(requirements_file):
        print(f"Erro: requirements.txt não encontrado em {requirements_file}. Não foi possível atualizar as dependências.")
        sys.exit(1)

    # Execute pip install dentro do ambiente virtual
    try:
        # Use o interpretador python do venv diretamente
        venv_python = os.path.join(install_dir, ".venv", "bin", "python3")
        subprocess.run([venv_python, "-m", "pip", "install", "-r", requirements_file], check=True, capture_output=True, text=True)
        print("Dependências atualizadas com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao atualizar dependências: {e.stderr}")
        sys.exit(1)

    print("\nPrescreveAI atualizado com sucesso para a versão mais recente!")

# --- Main entry point for the script --- 
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "serve":
            start_server()
        elif command == "stop":
            stop_server()
        elif command == "status":
            server_status()
        elif command == "install":
            show_install_instructions()
        elif command == "update":
            update_program()
        else:
            # Run the interactive CLI for other commands or no command
            run_cli()
    else:
        # Run the interactive CLI if no command is provided
        run_cli()