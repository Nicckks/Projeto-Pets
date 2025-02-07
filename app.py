from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração do MySQL
def get_db_connection():
    try:
        print("Tentando conectar ao banco de dados...")
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        print("Conexão bem sucedida!")
        return connection
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        raise

def enviar_email_recuperacao(email):
    # Configurações do servidor de email
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv('GMAIL_USER')
    sender_password = os.getenv('GMAIL_APP_PASSWORD')

    try:
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Recuperação de Senha - PETs Care"

        body = f"""
        Você solicitou a recuperação de senha.
        
        Para criar uma nova senha, clique no link abaixo:
        http://localhost:8000/reset-password.html?email={email}
        
        Se você não solicitou esta recuperação, ignore este email.
        """
        msg.attach(MIMEText(body, 'plain'))

        # Conectar ao servidor SMTP com mais logs
        print("Conectando ao servidor SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Ativa logs detalhados
        
        print("Iniciando TLS...")
        server.starttls()
        
        print("Tentando login no Gmail...")
        server.login(sender_email, sender_password)
        
        print("Enviando email...")
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        
        print("Fechando conexão...")
        server.quit()
        
        print("Email enviado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro detalhado ao enviar email: {str(e)}")
        return False

@app.route('/recuperar-senha', methods=['POST'])
def recuperar_senha():
    dados = request.get_json()
    email = dados.get('email')

    if not email:
        return jsonify({'erro': 'Email não fornecido'}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Adicionar logs para debug
        print(f"\n=== TENTATIVA DE RECUPERAÇÃO DE SENHA ===")
        print(f"Email recebido: '{email}'")
        
        # Primeiro vamos ver todos os emails no banco
        cursor.execute('SELECT email FROM usuario')
        todos_emails = cursor.fetchall()
        print("\nEmails cadastrados no banco:")
        for user in todos_emails:
            print(f"Email: '{user['email']}'")
        
        # Agora verificamos o email específico
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"\nUsuário encontrado:")
            print(f"ID: {usuario['ID']}")
            print(f"Nome: {usuario['nome']}")
            print(f"Email: {usuario['email']}")
            
            if enviar_email_recuperacao(email):
                return jsonify({'mensagem': 'Email de recuperação enviado com sucesso'}), 200
            else:
                return jsonify({'erro': 'Erro ao enviar email de recuperação'}), 500
        else:
            print(f"\nEmail não encontrado no banco")
            return jsonify({'erro': 'Email não encontrado'}), 404

    except mysql.connector.Error as err:
        print(f"\nErro MySQL: {err}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    except Exception as e:
        print(f"\nErro não esperado: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def verificar_senha(senha_fornecida, senha_hash_banco):
    try:
        print(f"\nVerificando senha:")
        print(f"Senha fornecida: {senha_fornecida}")
        print(f"Hash do banco: {senha_hash_banco}")
        
        # Verifica se a senha corresponde ao hash usando o método do Werkzeug
        return check_password_hash(senha_hash_banco, senha_fornecida)
        
    except Exception as e:
        print(f"Erro ao verificar senha: {e}")
        return False

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    nome_usuario = dados.get('nome_usuario')
    senha = dados.get('senha')
    
    print("\n=== TENTATIVA DE LOGIN ===")
    print(f"Nome de usuário recebido: '{nome_usuario}'")
    print(f"Senha recebida: '{senha}'")
    
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar usuário pelo nome de usuário
        query = 'SELECT * FROM usuario WHERE nome_usuario = %s'
        cursor.execute(query, (nome_usuario,))
        usuario_encontrado = cursor.fetchone()
        
        if usuario_encontrado:
            print("\nUsuário encontrado no banco:")
            print(f"Nome de usuário: {usuario_encontrado['nome_usuario']}")
            
            # Verificar a senha
            senha_banco = usuario_encontrado['senha']
            
            if verificar_senha(senha, senha_banco):
                print("\nLogin bem sucedido!")
                usuario_dict = {
                    'id': usuario_encontrado['ID'],
                    'nome': usuario_encontrado['nome'],
                    'nome_usuario': usuario_encontrado['nome_usuario'],
                    'cpf': usuario_encontrado['cpf'],
                    'email': usuario_encontrado['email']
                }
                return jsonify({'usuario': usuario_dict}), 200
            else:
                print("\nSenha incorreta")
                return jsonify({'erro': 'Usuário ou senha inválidos'}), 401
        else:
            print("\nUsuário não encontrado")
            return jsonify({'erro': 'Usuário ou senha inválidos'}), 401

    except mysql.connector.Error as err:
        print(f"\nErro MySQL: {err}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    except Exception as e:
        print(f"\nErro não esperado: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/atualizar-senha', methods=['POST'])
def atualizar_senha():
    dados = request.get_json()
    email = dados.get('email')
    nova_senha = dados.get('nova_senha')

    if not email or not nova_senha:
        return jsonify({'erro': 'Email e nova senha são obrigatórios'}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o email existe
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({'erro': 'Email não encontrado'}), 404

        # Gerar hash da nova senha
        senha_hash = generate_password_hash(nova_senha, method='scrypt')
        
        # Atualizar a senha com o hash
        cursor.execute('UPDATE usuario SET senha = %s WHERE email = %s', 
                      (senha_hash, email))
        conn.commit()
        
        return jsonify({'mensagem': 'Senha atualizada com sucesso'}), 200

    except mysql.connector.Error as err:
        print(f"Erro MySQL: {err}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    except Exception as e:
        print(f"Erro não esperado: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/registrar', methods=['POST'])
def registrar():
    dados = request.get_json()
    nome_usuario = dados.get('nome_usuario')
    nome = dados.get('nome')
    cpf = dados.get('cpf')
    email = dados.get('email')
    senha = dados.get('senha')

    if not all([nome_usuario, nome, cpf, email, senha]):
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o nome de usuário já existe
        cursor.execute('SELECT * FROM usuario WHERE nome_usuario = %s', (nome_usuario,))
        if cursor.fetchone():
            return jsonify({'erro': 'Nome de usuário já existe'}), 400
        
        # Verificar se o email já existe
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        if cursor.fetchone():
            return jsonify({'erro': 'Email já cadastrado'}), 400
        
        # Verificar se o CPF já existe
        cursor.execute('SELECT * FROM usuario WHERE cpf = %s', (cpf,))
        if cursor.fetchone():
            return jsonify({'erro': 'CPF já cadastrado'}), 400

        # Gerar hash da senha antes de salvar
        senha_hash = generate_password_hash(senha, method='scrypt')

        # Inserir novo usuário com a senha hash
        cursor.execute('''
            INSERT INTO usuario (nome_usuario, nome, cpf, email, senha)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nome_usuario, nome, cpf, email, senha_hash))
        
        conn.commit()
        
        return jsonify({'mensagem': 'Usuário registrado com sucesso'}), 201

    except mysql.connector.Error as err:
        print(f"Erro MySQL: {err}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    except Exception as e:
        print(f"Erro não esperado: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
