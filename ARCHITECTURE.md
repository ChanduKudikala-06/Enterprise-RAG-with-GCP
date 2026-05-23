# 🏗️ Scalable Enterprise Agentic RAG Architecture
echo "# Enterprise-RAG-with-GCP" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/ChanduKudikala-06/Enterprise-RAG-with-GCP.git
git push -u origin main
This document visualizes the complete cloud-native infrastructure of the system. The architecture is designed for **High Availability**, **Sub-100ms Caching**, and **Automated Event-Driven Ingestion**.

## 🌟 Executive Summary (High-Level View)
This simplified view shows the 6 main pillars of our Enterprise RAG system.

```mermaid
graph TD
    subgraph "1. User Interface"
        A[User Queries] --> B[API Services]
    end

    subgraph "2. Agent Engine"
        B --> C[Multi-Agent Orchestration<br/>LangGraph]
    end

    subgraph "3. Data Ingestion"
        D[Data Sources<br/>GCS] --> E[Auto-Ingestion<br/>Eventarc + Doc AI]
        E --> F[Vector Indexing]
    end

    subgraph "4. Knowledge & LLMs"
        C --> G[Vector DB: Qdrant]
        C --> H[LLMs: Groq & Vertex]
    end

    subgraph "5. State & Cache"
        C --> I[Persistent Memory: SQL]
        C --> J[Semantic Cache: Redis]
    end

    subgraph "6. Monitoring & DevOps"
        K[Logfire & LangSmith]
        L[Terraform & Docker]
    end

    F --> G
```

## 🏗️ Detailed Technical Architecture (Landscape View)

```mermaid
graph LR
    subgraph "User Layer"
        User[("🌐 End User")]
        UI["💻 Streamlit UI<br/>(Cloud Run)"]
    end

    subgraph "API & Orchestration Layer"
        Backend["🧠 Backend API<br/>(FastAPI + LangGraph)"]
        Agent["🤖 Agentic Reasoning<br/>(Planner & Responder)"]
    end

    subgraph "Event-Driven Ingestion Layer"
        GCS_Raw["📥 GCS: Raw Bucket"]
        Eventarc["📡 Eventarc Trigger"]
        Ingestion["⚙️ Ingestion Service<br/>(Cloud Run Webhook)"]
        DocAI["📄 Google Document AI<br/>(OCR & Parsing)"]
    end

    subgraph "State & Storage Layer"
        Postgres[("🐘 Cloud SQL<br/>(Postgres Memory)")]
        Redis[("⚡ Memorystore<br/>(Semantic Cache)")]
        Qdrant[("🔍 Qdrant Cloud<br/>(Vector DB)")]
    end

    subgraph "External Intelligence"
        Groq["🚀 Groq API<br/>(Llama 3.3 70B)"]
        Vertex["✨ Vertex AI<br/>(Embeddings)"]
    end

    subgraph "Observability & Networking"
        Logfire["🔥 Logfire<br/>(Tracing)"]
        LangSmith["🦜 LangSmith<br/>(Agent Eval)"]
        VPC["🔒 Serverless VPC<br/>Connector"]
    end

    %% Flow: User Query
    User --> UI
    UI --> Backend
    Backend --> Agent
    
    %% Flow: Agent Tools
    Agent --> Redis
    Agent --> Qdrant
    Agent --> Groq
    Agent --> Vertex
    
    %% Flow: Persistence
    Agent --> Postgres
    
    %% Flow: Ingestion
    User -- "Upload PDF" --> GCS_Raw
    GCS_Raw -- "Object Finalized" --> Eventarc
    Eventarc -- "HTTPS POST" --> Ingestion
    Ingestion --> DocAI
    Ingestion --> Vertex
    Ingestion --> Qdrant

    %% Networking & Tracing
    Backend -.-> VPC
    Ingestion -.-> VPC
    VPC -.-> Redis
    VPC -.-> Postgres
    
    Backend -.-> Logfire
    Backend -.-> LangSmith
    UI -.-> Logfire
    Ingestion -.-> Logfire
```

## 🛠️ Component Breakdown

### 1. Compute (Cloud Run)
*   **Microservices Architecture**: Split into UI, Backend, and Ingestion to allow independent scaling.
*   **Serverless**: Automatically scales to zero when not in use to save costs.

### 2. Event-Driven Automation
*   **GCS + Eventarc**: Eliminates manual ingestion. Uploading a file to the "Raw" bucket immediately wakes up the Ingestion service.
*   **Document AI**: Uses Google's enterprise-grade OCR for high-fidelity PDF parsing.

### 3. Persistent Memory & Speed
*   **Postgres (Cloud SQL)**: Stores conversation history (Checkpoints) so the Agent remembers past interactions across sessions.
*   **Redis (Memorystore)**: Implements **Semantic Caching** using `redisvl` to return answers in ~50ms if a similar question was asked before.

### 4. Networking & Security
*   **VPC Connector**: Provides a secure "Tunnel" between Cloud Run and the private Database/Cache, ensuring no data travels over the public internet.
*   **IAM Roles**: Follows the Principle of Least Privilege (PoLP) for all Service Accounts.

### 5. Observability
*   **Logfire**: Provides distributed tracing across all three microservices.
*   **LangSmith**: Dedicated evaluation and debugging for the LangGraph agentic flow.
