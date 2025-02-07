# PETs Care

Sistema web para gerenciamento de clínica veterinária com funcionalidades de autenticação e recuperação de senha.

## 🚀 Funcionalidades

- Sistema de Login/Logout
- Registro de novos usuários
- Recuperação de senha via email
- Menu lateral responsivo
- Interface adaptativa para diferentes dispositivos
- Validação de senhas na recuperação
- Criptografia de senhas usando Werkzeug
- Verificação de duplicidade de usuários/emails/CPF

## 📋 Pré-requisitos

### Frontend
- Servidor HTTP local (pode usar Python ou qualquer outro)
- Navegador web moderno
- Node.js (opcional, para usar npm como servidor alternativo)

### Backend
- Python 3.x
- MySQL Server
- MySQL Workbench (recomendado para gerenciamento do banco)

### Bibliotecas Python
Instale as dependências usando pip:
```bash
pip install flask
pip install flask-cors
pip install mysql-connector-python
pip install werkzeug
pip install email-validator
pip install python-dotenv
```

### Configuração do MySQL
1. Instale o MySQL Server:
   - Windows: Baixe o instalador do [site oficial MySQL](https://dev.mysql.com/downloads/installer/)
   - Linux: `sudo apt install mysql-server`
   - macOS: `brew install mysql`

2. Configure o MySQL:
   - Usuário padrão: root
   - Senha: defina durante a instalação
   - Porta padrão: 3306

3. Crie o banco de dados:
```sql
CREATE DATABASE pets;
USE pets;

CREATE TABLE usuario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    nome TEXT,
    nome_usuario TEXT,
    senha VARCHAR(255),
    cpf TEXT,
    email TEXT
);

CREATE TABLE mensagem (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    remetente_id INT,
    destinatario_id INT,
    conteudo TEXT,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (remetente_id) REFERENCES usuario(ID),
    FOREIGN KEY (destinatario_id) REFERENCES usuario(ID)
);

CREATE TABLE caes (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    nome TEXT,
    idade TEXT,
    raca TEXT,
    genero TEXT,
    status TEXT,
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(ID)
);

CREATE TABLE fotos (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    cao_id INT,
    url_foto TEXT,
    FOREIGN KEY (cao_id) REFERENCES caes(ID)
);

CREATE TABLE documentos (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    cao_id INT,
    pedigree TEXT,
    registro_saude_vacina TEXT,
    identificacao_micro TEXT,
    mapeamento_genetico TEXT,
    ancestralidade TEXT,
    FOREIGN KEY (cao_id) REFERENCES caes(ID)
);
```

### Configuração do Gmail
Para a funcionalidade de recuperação de senha:
1. Conta Gmail
2. Verificação em duas etapas ativada
3. Senha de app configurada

## 🔧 Configuração do Ambiente

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd [nome-do-repositorio]
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/macOS:
```bash
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente (crie um arquivo .env):
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=pets
GMAIL_USER=seu.email@gmail.com
GMAIL_APP_PASSWORD=sua_senha_de_app
```

## 🚀 Executando o Projeto

1. Inicie o servidor backend:
```bash
python app.py
```

2. Inicie o servidor frontend:
```bash
python -m http.server 8000
```

3. Acesse no navegador:
```
http://localhost:8000
```

[resto do README continua igual...]
