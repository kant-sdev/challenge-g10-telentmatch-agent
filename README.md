# TalentMatch AI Agent

O **TalentMatch AI Agent** é o motor de inteligência artificial da plataforma **TalentMatch**, desenvolvido em **Python** utilizando **FastAPI**, **Google Gemini API**, **SentenceTransformers** e **ChromaDB**.

O agente é responsável pelo processamento de currículos em formato PDF, extração estruturada de perfis profissionais, geração de embeddings vetoriais e execução de buscas semânticas utilizando arquitetura **RAG (Retrieval-Augmented Generation)** para recomendação de candidatos.

---

## 🏗️ Arquitetura

```text
       Frontend / Backend (Spring Boot)
                       │
                       ▼
               FastAPI AI Agent
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
   Google Gemini    Embeddings    ChromaDB
    (RAG Engine)   (MiniLM-L6)  (Vector Store)
```

### Tecnologias Utilizadas

- **Core Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
- **Motor de IA & LLM**: [Google GenAI SDK](https://ai.google.dev/) (`gemini-3.5-flash-lite`)
- **Embeddings Vetoriais**: `SentenceTransformers` (`all-MiniLM-L6-v2`)
- **Banco Vetorial**: [ChromaDB](https://www.trychroma.com/) (Persistência local / Volume Docker)
- **Processamento de PDF**: `PyPDF2`
- **Containerização**: Docker & Docker Compose

---

## 📋 Requisitos Prévia

- Python 3.11+ (para execução local direta)
- Docker & Docker Compose (para execução containerizada)
- Chave de API da **Google Gemini API** (`GEMINI_API_KEY`)

---

## 🚀 Configuração Local com Docker

### 1. Clonar o repositório e acessar a pasta

```bash
cd telematch-agent
```

### 2. Configurar variáveis de ambiente

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e insira sua chave da API do Gemini:

```env
GEMINI_API_KEY=sua_chave_gemini_aqui
ALLOWED_ORIGINS=http://localhost:5173,https://talentmatch.replit.app,*
```

### 3. Iniciar a aplicação via Docker Compose

```bash
docker compose up --build
```

A API estará disponível em: `http://localhost:8000`

---

## 🐍 Executando sem Docker (Ambiente Virtual)

### 1. Criar e ativar o ambiente virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Iniciar o servidor de desenvolvimento

```bash
uvicorn app.main:app --reload
```

---

## 📡 Endpoints da API

### 1. Upload e Processamento de Currículo

- **Rota**: `POST /upload/cv`
- **Content-Type**: `multipart/form-data`
- **Parâmetros**:
  - `file` (obrigatório): Arquivo PDF do currículo.
  - `group_id` (opcional): ID do grupo no sistema ou `"global"` (padrão: `"global"`).
  - `user_id` (opcional): ID único do usuário (gerado automaticamente se omitido).

**Exemplo de Resposta**:
```json
{
  "message": "Currículo processado com sucesso.",
  "filename": "CV_JoaoSilva.pdf",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "group_id": "global",
  "candidate": {
    "name": "JOÃO SILVA",
    "email": "joao@exemplo.com",
    "phone": "(11) 99999-9999",
    "linkedin_url": "https://linkedin.com/in/joao-silva",
    "github_url": "https://github.com/joao-silva",
    "summary": "Desenvolvedor Backend especialista em Java e Spring Boot.",
    "skills": ["Java", "Spring Boot", "Docker", "PostgreSQL"],
    "experience_level": "Pleno",
    "years_experience": 4,
    "education": ["Engenharia de Software"],
    "certifications": ["AWS Cloud Practitioner"],
    "languages": ["Português", "Inglês"]
  },
  "chunks": 3,
  "embeddings": 3
}
```

---

### 2. Busca Semântica e Recomendação RAG

- **Rota**: `POST /search/`
- **Content-Type**: `application/json`
- **Payload Exemplo**:
```json
{
  "query": "Pode me recomendar alguém com experiência em Java e Spring Boot?",
  "group_id": "global",
  "limit": 5
}
```

**Exemplo de Resposta**:
```json
{
  "recommendation": "Recomendamos o candidato João Silva devido à sua sólida experiência em Java e ecossistema Spring.",
  "matches": [
    {
      "name": "JOÃO SILVA",
      "linkedin_url": "https://linkedin.com/in/joao-silva",
      "github_url": "https://github.com/joao-silva",
      "relevance": "Possui 4 anos de experiência com Java, Spring Boot, PostgreSQL e Docker."
    }
  ]
}
```

---

### 3. Health Check (Verificação de Saúde)

- **Rota**: `GET /health`
- **Resposta**:
```json
{
  "status": "healthy"
}
```

---

## 📄 Swagger / OpenAPI Documentation

A documentação interativa das rotas pode ser acessada em:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 💾 Persistência de Dados no Docker

Os embeddings gerados e indexados no **ChromaDB** são persistidos na pasta `./data/chroma`. No Docker Compose, esse diretório é montado através do volume nomeado `chroma_data`, garantindo que os dados armazenados não sejam perdidos ao reiniciar os containers.
