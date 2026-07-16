# 🚀 DocuMind AI

> **Enterprise RAG Assistant for Intelligent Document Question Answering**

DocuMind AI is an enterprise-style Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents and interact with them using natural language.

Instead of relying solely on a Large Language Model, DocuMind AI retrieves the most relevant document chunks using a hybrid retrieval pipeline before generating accurate, context-aware responses.

---

# Features

* Upload PDF documents
* Intelligent document parsing
* Automatic text chunking
* Semantic Search using Qdrant
* BM25 Keyword Search
* Hybrid Search (Dense + Sparse Retrieval)
* Reciprocal Rank Fusion (RRF)
* Cross-Encoder Re-ranking
* Multi-document support
* Conversation Memory with Redis
* AI Workflow Orchestration using LangGraph
* REST API with FastAPI
* Interactive Streamlit Web Interface

---

# Architecture

```
                    User

                      │

                      ▼

               Streamlit UI

                      │

                      ▼

                FastAPI Backend

                      │

          ┌───────────┴───────────┐

          ▼                       ▼

      LangGraph              Redis Memory

          │

          ▼

    Hybrid Search Pipeline

          │

    ┌─────┴───────────────┐

    ▼                     ▼

Qdrant Vector Search     BM25 Search

    └──────────┬──────────┘

               ▼

     Reciprocal Rank Fusion

               ▼

       CrossEncoder Ranking

               ▼

         LLM Response

               ▼

            User
```

---

# Tech Stack

## Backend

* FastAPI
* Python

## AI Framework

* LangChain
* LangGraph

## Vector Database

* Qdrant Cloud

## Memory

* Redis Cloud

## Embedding Model

* HuggingFace Embeddings

## Re-ranking

* BAAI/bge-reranker-base

## Keyword Search

* BM25

## Frontend

* Streamlit

---

# Project Structure

```
documind-ai/

│

├── app/

│   ├── agents/

│   ├── routers/

│   ├── services/

│   ├── schemas/

│   ├── core/

│   ├── config/

│   └── main.py

│

├── uploads/

├── streamlit_app.py

├── requirements.txt

├── README.md

└── .env
```
# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/documind-ai.git

cd documind-ai
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=

QDRANT_URL=

QDRANT_API_KEY=

REDIS_HOST=

REDIS_PORT=

REDIS_PASSWORD=

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

CHUNK_SIZE=1000

CHUNK_OVERLAP=200
```

---

# Running the Backend

```bash
uvicorn app.main:app --reload
```

FastAPI Documentation:

```
http://localhost:8000/docs
```

---

# Running the Streamlit Frontend

```bash
streamlit run streamlit_app.py
```

---

# API Endpoints

## Upload PDF

```
POST /upload/
```

Uploads a PDF document, extracts its content, generates embeddings, and stores the chunks in Qdrant.

---

## Chat

```
POST /chat/
```

Example Request

```json
{
  "session_id": "123456",
  "source": "document.pdf",
  "question": "What is this document about?"
}
```

Example Response

```json
{
  "answer": "...",
  "session_id": "123456"
}
```

---

# Retrieval Pipeline

The retrieval process consists of multiple stages:

1. User submits a question.
2. LangGraph orchestrates the workflow.
3. Previous conversation is retrieved from Redis.
4. Qdrant performs semantic vector search.
5. BM25 performs keyword search.
6. Reciprocal Rank Fusion (RRF) merges the two result sets.
7. CrossEncoder reranks the retrieved documents.
8. The final context is sent to the LLM.
9. The generated answer is returned to the user.
10. Conversation history is stored in Redis.

---

# Deployment

The project can be deployed using:

* Streamlit Community Cloud (Frontend)
* GitHub Codespaces (Backend)
* Qdrant Cloud (Vector Database)
* Redis Cloud (Conversation Memory)

---

# Future Improvements

* Authentication and user accounts.
* Multiple vector collections.
* Multi-file chat sessions.
* Metadata filtering.
* Citation support.
* OCR support for scanned PDFs.
* Image extraction.
* Role-based access control.
* Docker & Docker Compose deployment.
* Kubernetes support.

---

# Screenshots

## Upload Page

*Add screenshot here.*

---

## Chat Interface

*Add screenshot here.*

---

## System Architecture

*Add architecture diagram here.*

---

# Skills Demonstrated

* Retrieval-Augmented Generation (RAG)
* AI Agents
* LangGraph Workflows
* FastAPI Development
* Streamlit Development
* Vector Databases
* Semantic Search
* Hybrid Retrieval
* CrossEncoder Re-ranking
* Redis Memory
* Prompt Engineering
* REST APIs
* Backend Development
* LLM Applications

---

# Author

**Mohamed Foly**

AI Engineer | Machine Learning Engineer | Backend Developer

GitHub:
https://github.com/YOUR_USERNAME

LinkedIn:
https://www.linkedin.com/in/YOUR_PROFILE

---

# License

This project is released under the MIT License.

```
MIT License

Copyright (c) 2026 Mohamed Foly

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to deal in the Software without restriction...
```
