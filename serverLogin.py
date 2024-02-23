# importa o modulo http.server
import os
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import parse_qs, urlparse
import hashlib

class MyHandley(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            # tenta abrir o arquivo
            f = open(os.path.join(path, "index.html"), "r", encoding="utf-8")
            # se existir, envia o conteudo do arquivo
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read().encode("utf-8"))
            f.close()
            return None
        except FileNotFoundError:
            pass
        return super().list_directory(path)

    def do_GET(self):
        # verifica se a rota é enviar
        if self.path == "/login":
            # tenta abrir o arquivo login.html
            try:
                with open(os.path.join(os.getcwd(), "login.html"), "r") as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))  
            except FileNotFoundError:
                self.send_error(404, "File not found")

        elif self.path == "/login_failed":
            # responde ao cliente com a mensagem de login/senha incorreta
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            # le o conteudo da pagina login.html
            with open(os.path.join(os.getcwd(), "login.html"), "r", encoding="utf-8") as login_file:
                 content = login_file.read()
            
            # adiciona mensagem de erro nno conteudo da pagina
            mensagem = "Login ou senha incorreta. Tente novamente!"
            content = content.replace('<!-- Mensagem de erro sera inserida aqui-->', f'<div class="error-message">{mensagem}</div>')

            # envia o conteudo modificado para o cliente
            self.wfile.write(content.encode("utf-8"))

        elif self.path.startswith("/cadastro"):
            # extraindo os parametros da URL
            query_params = parse_qs(urlparse(self.path).query)
            login = query_params.get("email", [""])[0]
            senha = query_params.get("senha", [""])[0]

            # mensagem de boas-vindas
            welcome_message = "Olá, seja bem-vindo"

            # responde ao cliente com a pagina de cadastro
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            # lê o conteudo da pagina cadastro.html
            with open(os.path.join(os.getcwd(), "cadastro.html"), "r", encoding="utf-8") as cadastro_file:
                content = cadastro_file.read()

            # substitui os marcadores de posição pelos valores correspondentes 
            content = content.replace("{login}", login)
            content = content.replace("{senha}", senha)
            content = content.replace("{welcome_message}", welcome_message)

            # envia o conteudo modificado para o cliente
            self.wfile.write(content.encode("utf-8"))
            return
                
        else:
            # se nao for a rota "/login", continiua o comprimento padrao
            super().do_GET()

    def usuario_existente(self, login, senha):
        # verifica se o login ja existe no arquivo
        with open("dados_login.txt", "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    stored_login, stored_senha_hash, stored_nome = line.strip().split(";")
                    if login == stored_login:
                        print ("localizei o login informado")
                        print ("senha:" + senha)
                        print ("senha_armazenada: " + senha)

                        senha_hash = hashlib.sha256(senha.encode("utf-8")).hexdigest()
                        return senha_hash == stored_senha_hash
        return False
    
    # trecho HASH
    def adicionar_usuario(self, login, senha, nome):
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()

        with open("dados_login.txt", "a", encoding="utf-8") as file:
            file.write(f"{login};{senha_hash};{nome}\n")


    def remover_ultima_linha(self, arquivo):
        print("Vou excluir ultima linha")
        with open(arquivo, "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open(arquivo, "r", encoding="utf-8") as file:
            file.readlines(lines[:-1])
    
    def do_POST(self):
        # verifica se a rota é enviar
        if self.path == "/enviar_login":
            # obtem o comprimento do corpo da requisicao
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")

            # parseia os dados ao formulario
            form_data = parse_qs(body, keep_blank_values=True)

            # exibe os dados no terminal
            print("Dados do formulario:")
            print("Email:", form_data.get("email", [""])[0])
            print("Senha:", form_data.get("senha", [""])[0])

            # verifica se o usario ja existe
            login = form_data.get("email",[""])[0]
            senha = form_data.get("senha",[""])[0]

            # dados salvos com sucesso
            if self.usuario_existente(login,senha):
                # abrir pagina resposta
                with open(os.path.join(os.getcwd(), "resposta.html"), "r", encoding="utf-8") as resposta_file:
                    content = resposta_file.read()
                # redireciona o cliente
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode("utf-8")) 
            else:
                # verifica se o login ja existe
                if any(line.startswith(f"{login};") for line in open("dados_login.txt", "r", encoding="utf-8")):
                    self.send_response(302)
                    self.send_header("Location", "/login_failed")
                    self.end_headers()
                    return
                else:
                    # armazena os dados em um arquivo txt
                    self.adicionar_usuario(login, senha, nome='Nome')
                    self.send_response(302)
                    self.send_header("Location", f"/cadastro?login={login}&senha={senha}")
                    self.end_headers()
                    return

        elif self.path.startswith("/confirmar_cadastro"):
            # obtem o comprimento do corpo da requisicao
            content_length = int(self.headers["Content-Length"])
            # le o corpo da requisição
            body = self.rfile.read(content_length).decode("utf-8")
            # parseia os dados ao formulario
            form_data = parse_qs(body, keep_blank_values=True)

            # verifica se o usario ja existe
            login = form_data.get("email",[""])[0]
            senha = form_data.get("senha",[""])[0]
            nome = form_data.get("nome",[""])[0]

            # hash
            senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()

            print("nome:" + nome)

            # verifica se o usuario ja existe
            if self.usuario_existente(login, senha):
                # atualiza o arquivo com o nome, se  asenha estiver correta
                with open ("dados_login.txt","r", encoding="utf") as file:
                    lines = file.readlines()

                with open("dados_login.txt","w",encoding='utf-8') as file:
                    for line in lines:
                        stored_login, stored_senha, stored_nome = line.strip().split(";")
                        if login == stored_login and senha_hash == stored_senha:
                            line = f"{login};{senha_hash};{nome}\n"
                        file.write(line)

                with open(os.path.join(os.getcwd(), "resposta.html"), "r", encoding="utf-8") as resposta_file:
                    content = resposta_file.read()
                
                # redireciona o cliente 
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode("utf-8")) 
            
            else:
                # se o usuario não existe ou a senha esta incorreta, redireciona para outra pagina
                self.remover_ultima_linha("dados_login.txt")
                self.send_response(302)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("A senha nao confere".encode("utf-8"))

        else:
            # se nao for a rota "/submit_login", continua como comportamento
            super(MyHandley, self).do_POST()

# define a porta e o ID a ser utilizado
enderoco_ip = "0.0.0.0"
porta = 8000

# cria um servidor na porta especificada
with socketserver.TCPServer((enderoco_ip, porta), MyHandley) as httpd:  # " "aceita qualquer requisicao de rede
    print(f"Servidor iniciado na porta {porta}")
    # mantem o servidor em execução
    httpd.serve_forever()

