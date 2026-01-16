# AI Sales Buddy
## Technology Stack

**Prepared for:** Hyundai Motor India  
**Prepared by:** Maigic.AI  
**Version:** 1.0 | December 2025

---

<br/>

## Architecture Overview

<br/>

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                                   USER                                                  │
│                            (Sales Consultant)                                           │
│                                    │                                                    │
│                         Text / Voice / Avatar                                           │
│                                    ▼                                                    │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │                            FRONTEND                                             │  │
│   │                                                                                 │  │
│   │                  React  •  WebSocket  •  Voice SDK                              │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                                    │
│                                    ▼                                                    │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │                            BACKEND                                              │  │
│   │                                                                                 │  │
│   │                  Python (FastAPI)  •  REST + WebSocket                          │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                                    │
│               ┌────────────────────┼────────────────────┐                              │
│               │                    │                    │                              │
│               ▼                    ▼                    ▼                              │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                       │
│   │                 │  │                 │  │                 │                       │
│   │   AI ENGINE     │  │   DATABASES     │  │   EXTERNAL      │                       │
│   │                 │  │                 │  │                 │                       │
│   │   Gemini Pro    │  │   MongoDB       │  │   Hyundai LMS   │                       │
│   │   (LLM)         │  │   (Profiles)    │  │   (Data)        │                       │
│   │                 │  │                 │  │                 │                       │
│   │   Vector DB     │  │   Redis         │  │   Web Search    │                       │
│   │   (RAG)         │  │   (Cache)       │  │   (Competitor)  │                       │
│   │                 │  │                 │  │                 │                       │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘                       │
│                                                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                                 │  │
│   │                          CLOUD (GCP / AWS)                                      │  │
│   │                                                                                 │  │
│   │                    Docker  •  Auto-scaling  •  Mumbai Region                    │  │
│   │                                                                                 │  │
│   └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

<br/>

---

<br/>

## Core Technologies

<br/>

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React | Chat widget UI |
| **Backend** | Python + FastAPI | API server |
| **LLM** | Gemini Pro | Response generation |
| **Vector DB** | Pinecone / Vertex AI | Document search (RAG) |
| **Database** | MongoDB | User profiles & history |
| **Cache** | Redis | Fast data access |
| **Voice** | Azure Speech | Speech-to-Text, Text-to-Speech |
| **Cloud** | GCP / AWS | Hosting (India region) |

<br/>

---

<br/>

## External Integrations

<br/>

| Integration | Method | Purpose |
|-------------|--------|---------|
| **Hyundai LMS** | REST API | Product data, training |
| **Hyundai SSO** | OAuth 2.0 | User authentication |
| **Web Search** | Search API | Competitor information |
| **Avatar** | D-ID | Animated responses |

<br/>

---

<br/>

**Prepared by:** Maigic.AI

*Confidential - For Hyundai Motor India Only*
