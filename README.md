# Acessment AI

Acessment AI é uma API para automação da correção de provas no sistema americano, utilizando inteligência artificial e OCR para extrair e corrigir respostas de estudantes a partir de imagens e PDFs. O projeto foi desenvolvido com Django, Celery, Redis, Cloudinary e integra modelos generativos para extração de dados.

---

## ✨ Funcionalidades

- **Registro e autenticação de usuários** (JWT)
- **Upload de provas e gabaritos** (PDF ou imagem)
- **Extração automática de respostas** via IA (Google Gemini)
- **Correção automática** baseada em chave de respostas
- **Classificação automática** (Aprovado/Reprovado)
- **Dashboard de estatísticas** (total de alunos, aprovados, reprovados)
- **API RESTful documentada** (OpenAPI/Swagger)
- **Processamento assíncrono** com Celery + Redis

---

## 🚀 Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/acessment-ai.git
cd acessment-ai
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (já existe um exemplo no repositório):

```
CLOUD_NAME=...
CLOUD_API_KEY=...
CLOUD_API_SECRET=...
GOOGLE_API_KEY=...
DJANGO_SECRET_KEY=...
DB_ENGINE=django.db.backends.postgresql
DB_HOST=...
DB_PORT=...
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
```

### 5. Realize as migrações do banco de dados

```bash
python manage.py migrate
```

### 6. Inicie o servidor Django

```bash
python manage.py runserver
```

### 7. Inicie o Redis (necessário para o Celery)

Certifique-se de que o Redis está rodando em `localhost:6379`.

### 8. Inicie o worker do Celery

```bash
celery -A acessmentAi worker --loglevel=info
```

---

## 📚 Documentação da API

A documentação OpenAPI está disponível no arquivo [`docs.yaml`](docs.yaml).

Principais endpoints:

- `POST /api/register` — Registro de usuário
- `POST /api/login` — Login e obtenção de tokens JWT
- `GET /api/get-me` — Dados do usuário autenticado
- `POST /api/extract-pdf-text/` — Extrai respostas de um PDF de prova
- `POST /api/upload-test` — Upload de imagens de respostas dos alunos
- `PUT /api/update-student/<student_id>` — Atualiza dados do aluno
- `GET /api/get-students` — Lista todos os alunos
- `GET /api/get-total-students` — Total de alunos
- `GET /api/get-total-aprovados` — Total de aprovados
- `GET /api/get-total-reprovados` — Total de reprovados

---

## 🛠️ Tecnologias Utilizadas

- **Django** & **Django REST Framework**
- **Celery** + **Redis** (processamento assíncrono)
- **Cloudinary** (armazenamento de imagens)
- **Google Gemini** (IA generativa para extração de dados)
- **PyPDF2** (leitura de PDFs)
- **PostgreSQL** (banco de dados)
- **Swagger/OpenAPI** (documentação)

---

## 📂 Estrutura do Projeto

```
acessment-ai/
│
├── api/
│   ├── models/
│   ├── views/
│   ├── serializers.py
│   ├── tasks.py
│   ├── features.py
│   └── ...
├── templates/
│   └── teste.html
├── acessmentAi/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── requirements.txt
├── docs.yaml
└── README.md
```
---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 💡 Observações

- O projeto está em desenvolvimento e pode sofrer alterações.
- Para dúvidas, sugestões ou contribuições, abra uma issue ou envie um pull
