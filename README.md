# Smart Agent V2 - Native Android WhatsApp AI Agent

Production-ready, multi-tenant AI Agent backend running natively on Android via Termux. Integrated with FastAPI, SQLite, and Meta WhatsApp Cloud API.

## 🚀 Features

- **Native Termux Deployment**: Runs entirely on Android using pre-compiled binary wheels (no Rust compiler issues).
- **Multi-Tenant Session Persistence**: Phone-number isolated conversation context powered by SQLite (`tenant_sessions`).
- **Asynchronous Processing**: Fast Webhook responses (<100ms) using FastAPI `BackgroundTasks` to satisfy Meta's strict 3-second timeout limit.
- **Tools & RAG Router**: Automated query classification (RAG vector knowledge vs. Order database lookup).
- **Daemon Process Management**: Background execution script (`service.sh`) with status monitoring and log rotation.
- **Production Healthcheck**: Integrated `/health` endpoint for monitoring system stability.

## 🛠 Architecture


