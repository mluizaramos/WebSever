import os
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import parse_qs

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/atividadesDaTurma":
            try:
                with open(os.path.join(os.getcwd(), "TurmaAtividade.html"), "r", encoding="utf-8") as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))  
            except FileNotFoundError:
                self.send_error(404, "File not found")
        else:
        # Se não for a rota "/turmas", continuar com o comportamento padrão
            super().do_GET()
    
    def dados_existente(self, login, turma):
        # Verifica se a login existe no arquivo de turmas
        with open("dados_login.txt", "r", encoding="utf-8") as login_file:
            for line in login_file:
                stored_login = line.strip().split(';')[0]  
                if login == stored_login:
                    break
            else:
                return False
        
        # Verifica se a turma existe no arquivo de turmas
        with open("dados_turma.txt", "r", encoding="utf-8") as turma_file:
            for line in turma_file:
                stored_turma = line.strip().split(';')[0]
                if turma == stored_turma:
                    return True
        return False
        

    def do_POST(self):
        # Verificar se a rota é "/confrimarAtividade"
        if self.path == "/confirmarAtividade":
            # Obter o comprimento do corpo da requisição
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")

            # Parsear os dados do formulário
            form_data = parse_qs(body, keep_blank_values=True)

            # Exibir os dados no terminal
            print("Dados do formulário:")
            print("Nome:", form_data.get("nome", [""])[0])
            print("Turma:", form_data.get("turma", [""])[0])

            # Verificar se o usuário já existe
            login = form_data.get("nome", [""])[0]
            turma = form_data.get("turma", [""])[0]

            # chamar a função 'usuario_existente' existem e se sim
            if self.dados_existente(login,turma):
                with open ("dados_login_turma.txt","a", encoding="utf-8") as file:
                    line = f"{login};{turma}\n"
                    file.write(line)
                    # abrir pagina resposta
                    with open(os.path.join(os.getcwd(), "resposta.html"), "r", encoding="utf-8") as resposta_file:
                        content = resposta_file.read()
                    # redireciona o cliente
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode("utf-8")) 
            else:
                # abrir pagina resposta
                    with open(os.path.join(os.getcwd(), "resposta-negativa.html"), "r", encoding="utf-8") as resposta_file:
                        content = resposta_file.read()
                    # redireciona o cliente
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode("utf-8")) 
            
        else:
            # Se não for a rota "/cad_turma", continuar com o comportamento padrão
            super().do_POST()


# Define o endereço IP e a porta a serem utilizados
endereco_ip = "0.0.0.0"
porta = 8000

# Cria um servidor na porta especificada
with socketserver.TCPServer((endereco_ip, porta), MyHandler) as httpd:
    print(f"Servidor iniciado na porta {porta}")
    # Mantém o servidor em execução
    httpd.serve_forever()
