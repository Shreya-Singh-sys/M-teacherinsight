# M-TeacherInsight – AI Teaching Assistant (Microsoft Azure Aligned)

M-TeacherInsight is an AI-powered teaching insight platform designed to help educators
analyze classroom delivery, engagement, clarity, and interaction using speech, video,
and AI-driven feedback.

This repository is migrated from our earlier prototype and aligned with Microsoft Azure
services for scalable, secure, and production-ready deployment.

---

## Architecture Overview

Frontend (Web App)
↓
Azure App Service (Backend API – FastAPI)
↓
Azure Speech Services (Speech → Text)
↓
OpenAI GPT-4o-mini (LLM Reasoning Engine – External)
↓
Azure Speech Services (Text → Speech)
↓
User

---

## Microsoft Azure Services Used

- Azure App Service – Frontend & Backend Hosting
- Azure Speech Services – Speech-to-Text & Text-to-Speech
- Azure Entra ID – Authentication & User Identity
- Azure Blob Storage – Audio, Video & Session Storage
- Azure Monitor – Application Monitoring & Logs

> Note: External OpenAI GPT-4o-mini is currently used for rapid prototyping.
> The architecture is provider-agnostic and can be migrated to Azure OpenAI seamlessly.

---

## Key Features

- AI-powered teaching feedback
- Speech clarity, pace, and vocal analysis
- Classroom engagement and interaction insights
- Session history and progress tracking
- Secure authentication and scalable backend

---

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI (Python)
- AI: Azure Speech Services, OpenAI GPT-4o-mini
- Storage: Azure Blob Storage (planned)
- Monitoring: Azure Monitor

---

## Project Status

Core AI pipelines and backend logic are implemented.
Current work focuses on Microsoft Azure service alignment and deployment.
