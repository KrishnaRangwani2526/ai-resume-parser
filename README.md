# Resume Parser API (Generic)

## Overview
This repository provides a FastAPI-based Resume Parser and Matcher with:
- Upload endpoint
- Parsing (pdf/docx/txt)
- AI/ML integration hooks (OpenAI)
- Resume-job matching with relevancy scoring
- Tests and Dockerfile

## Quickstart (local)
1. Create a virtualenv and install:
2. Create .env file from .env.example and set your OPENAI_API_KEY if you have one.
3. Start:
4. Open docs: http://localhost:8000/docs (OpenAPI spec available automatically)

## Running tests
## Notes
- Place your API keys in environment variables — never check them into source control.
- The LLM client provides graceful fallback if no key is present.
- Improve parsing by adding more domain-specific heuristics or fine-tuning the LLM prompts.

## Production readiness checklist
- Add authentication (e.g., API keys / OAuth)
- Use S3 (or similar) for file storage
- Add rate limiting and quotas
- Add proper monitoring and logging
- Add more robust parsing (OCR for images, better date parsing)
- Harden file upload security (scan for malware, size limits)