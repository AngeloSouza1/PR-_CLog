import json
import os
import re
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Função para processar JSON e Headers do log
def processar_json(log_text):
    json_match = re.search(r'-- PAYLOAD: ({.*?})\s-- TIMEOUT', log_text, re.DOTALL)
    headers_match = re.search(r'-- HEADERS: ({.*?})\s-- PAYLOAD', log_text, re.DOTALL)

    headers = {}
    if headers_match:
        try:
            headers = json.loads(headers_match.group(1).replace("=>", ":"))  # Substituir => por :
        except json.JSONDecodeError:
            pass

    if json_match:
        json_data = json_match.group(1)
        try:
            return json.loads(json_data), headers
        except json.JSONDecodeError:
            return None, headers
    return None, headers

# Função para gerar comando cURL baseado no JSON processado e nos headers extraídos
def gerar_curl(json_data, headers):
    if not json_data:
        return ""

    # Capturar a URL do log
    url_match = re.search(r'URL:\s*(\S+)', log_text)
    url = url_match.group(1) if url_match else "https://api.monezo.com.br/v1/transactions"

    curl_command = f"curl --location '{url}' \\\n"

    # Adicionando os headers dinâmicos
    for key, value in headers.items():
        curl_command += f"--header '{key}: {value}' \\\n"

    # Adicionando o Content-Type caso não esteja nos headers
    if "Content-Type" not in headers:
        curl_command += "--header 'Content-Type: application/json' \\\n"

    # Adicionando o corpo JSON
    curl_command += f"--data-raw '{json.dumps(json_data, indent=2)}'"

    return curl_command


# Função para copiar texto do campo selecionado, apenas se houver conteúdo
def copiar_texto(campo):
    conteudo = campo.get("1.0", tk.END).strip()
    if conteudo:
        root.clipboard_clear()
        root.clipboard_append(conteudo)
        root.update()
        messagebox.showinfo("Copiado", "📋 Conteúdo copiado para a área de transferência!")
    else:
        messagebox.showwarning("Aviso", "⚠️ Não há conteúdo para copiar!")

# Função para salvar JSON e cURL em arquivos, apenas se houver conteúdo
def salvar_arquivos():
    json_conteudo = json_output.get("1.0", tk.END).strip()
    curl_conteudo = curl_output.get("1.0", tk.END).strip()

    if not json_conteudo and not curl_conteudo:
        messagebox.showwarning("Aviso", "⚠️ Não há conteúdo para salvar!")
        return
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    dir_path = "logs"
    os.makedirs(dir_path, exist_ok=True)

    if json_conteudo:
        file_name_json = f"{dir_path}/CLOG-JSON-{timestamp}.txt"
        with open(file_name_json, "w", encoding="utf-8") as file:
            file.write(json_conteudo)
        messagebox.showinfo("Arquivo Salvo", f"📂 JSON salvo com sucesso!\nLocal: {file_name_json}")

    if curl_conteudo:
        file_name_curl = f"{dir_path}/CLOG-CURL-{timestamp}.txt"
        with open(file_name_curl, "w", encoding="utf-8") as file:
            file.write(curl_conteudo)
        messagebox.showinfo("Arquivo Salvo", f"📂 cURL salvo com sucesso!\nLocal: {file_name_curl}")

# Função principal que processa o log inserido
def processar_log():
    global log_text  # Adicionando como global para capturar na função gerar_curl
    log_text = log_input.get("1.0", tk.END).strip()

    if not log_text:
        messagebox.showwarning("Aviso", "⚠️ Nenhum log inserido!")
        return

    json_data, headers = processar_json(log_text)

    if json_data:
        json_output.config(state=tk.NORMAL)
        curl_output.config(state=tk.NORMAL)

        json_output.delete("1.0", tk.END)
        curl_output.delete("1.0", tk.END)

        json_output.insert(tk.END, json.dumps(json_data, indent=2))
        curl_output.insert(tk.END, gerar_curl(json_data, headers))  # Passa os headers extraídos

        json_output.config(state=tk.DISABLED)
        curl_output.config(state=tk.DISABLED)
    else:
        messagebox.showerror("Erro", "❌ Erro ao processar JSON!")


# Função para limpar os campos
def limpar_campos():
    log_input.delete("1.0", tk.END)
    json_output.config(state=tk.NORMAL)
    curl_output.config(state=tk.NORMAL)

    json_output.delete("1.0", tk.END)
    curl_output.delete("1.0", tk.END)

    json_output.config(state=tk.DISABLED)
    curl_output.config(state=tk.DISABLED)

# Criando a janela principal
root = tk.Tk()
root.title("C-LOG --- Conversor de Logs")
root.geometry("1920x980")
root.minsize(1000, 900)
root.configure(bg="#2C3E50")

# Layout principal
root.grid_rowconfigure(1, weight=1)  # Log
root.grid_rowconfigure(2, weight=3)  # JSON e cURL
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Criando um frame para os botões no topo (sem borda e fundo transparente)
menu_frame = tk.Frame(root, bg="#2C3E50", padx=10, pady=5)
menu_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

def criar_botao(parent, text, command):
    btn = tk.Button(
        parent, text=text, command=command,
        borderwidth=0, bg="#2C3E50", fg="white",
        font=("Arial", 12), activebackground="#3A506B",
        highlightthickness=0
    )
    btn.bind("<Enter>", lambda e: btn.config(bg="#3A506B"))
    btn.bind("<Leave>", lambda e: btn.config(bg="#2C3E50"))
    return btn

btn_processar = criar_botao(menu_frame, "✅ Processar", processar_log)
btn_processar.pack(side=tk.LEFT, padx=10, pady=8)

btn_salvar = criar_botao(menu_frame, "💾 Salvar", salvar_arquivos)
btn_salvar.pack(side=tk.LEFT, padx=10)

btn_limpar = criar_botao(menu_frame, "🗑️ Limpar", limpar_campos)
btn_limpar.pack(side=tk.LEFT, padx=10)

btn_sair = criar_botao(menu_frame, "❌ Sair", root.quit)
btn_sair.pack(side=tk.RIGHT, padx=10)

# Criando a área de entrada do log
log_frame = tk.Frame(root, bg="#2C3E50")
log_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=3)

tk.Label(log_frame, text="📥 Insira o Log:", fg="white", bg="#2C3E50", font=("Arial", 12, "bold")).pack(anchor="w")

log_input = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Courier", 10), height=5)
log_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

# Criando um frame para exibir JSON e cURL lado a lado
output_frame = tk.Frame(root, bg="#2C3E50")
output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=3)

# JSON à esquerda
json_frame = tk.Frame(output_frame, bg="#2C3E50")
json_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=3)

json_label_frame = tk.Frame(json_frame, bg="#2C3E50")
json_label_frame.pack(fill=tk.X)

tk.Label(json_label_frame, text="📄 JSON Gerado:", font=("Arial", 12, "bold"), bg="#2C3E50", fg="white").pack(side=tk.LEFT)

btn_copiar_json = tk.Button(
    json_label_frame, text="📋", command=lambda: copiar_texto(json_output),
    borderwidth=0, bg="#2C3E50", fg="white", font=("Arial", 12), highlightthickness=0
)
btn_copiar_json.pack(side=tk.RIGHT, padx=5)

json_output = scrolledtext.ScrolledText(json_frame, wrap=tk.WORD, font=("Courier", 10))
json_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
json_output.config(state=tk.DISABLED)

# cURL à direita
curl_frame = tk.Frame(output_frame, bg="#2C3E50")
curl_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=3)

curl_label_frame = tk.Frame(curl_frame, bg="#2C3E50")
curl_label_frame.pack(fill=tk.X)

tk.Label(curl_label_frame, text="🌍 cURL Gerado:", font=("Arial", 12, "bold"), bg="#2C3E50", fg="white").pack(side=tk.LEFT)

btn_copiar_curl = tk.Button(
    curl_label_frame, text="📋", command=lambda: copiar_texto(curl_output),
    borderwidth=0, bg="#2C3E50", fg="white", font=("Arial", 12), highlightthickness=0
)
btn_copiar_curl.pack(side=tk.RIGHT, padx=5)

curl_output = scrolledtext.ScrolledText(curl_frame, wrap=tk.WORD, font=("Courier", 10))
curl_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
curl_output.config(state=tk.DISABLED)

# Rodando a aplicação
root.mainloop()
