import os
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import parse_qs

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/atividades":
            try:
                with open(os.path.join(os.getcwd(), "CadastroDeAtividades.html"), "r", encoding="utf-8") as login_file:
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

    def do_POST(self):
            # Verificar se a rota é "/cad_atividade"
        if self.path == "/cad_atividade":
            # Obter o comprimento do corpo da requisição
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")

            # Parsear os dados do formulário
            form_data = parse_qs(body, keep_blank_values=True)

            # Exibir os dados no terminal
            print("Dados do formulário:")
            print("Código:", form_data.get("codigo", [""])[0])
            print("Descrição:", form_data.get("descricao", [""])[0])

            # Verificar se o usuário já existe
            codigo = form_data.get("codigo", [""])[0]
            descricao = form_data.get("descricao", [""])[0]

            with open("dados_atividade.txt", "a", encoding="utf-8") as file:
                line = f"{codigo};{descricao}\n"
                file.write(line)

                with open(os.path.join(os.getcwd(), "resposta.html"), "r", encoding="utf-8") as resposta_file:
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
