# 🏗️ Resume Parser Architecture

## 🧠 Overview
The **AI Resume Parser** is a FastAPI-based intelligent service designed to extract and structure key information from resumes of multiple file formats (`.pdf`, `.docx`, `.txt`, etc.).  
It combines **document parsing** and **AI/LLM-based semantic extraction** to deliver accurate, human-readable structured JSON output.

---

## ⚙️ System Components

### 1. 🧩 FastAPI Backend (`src/main.py`)
- Serves as the **main entry point** for API requests.  
- Exposes endpoints such as:
  - `POST /upload_resume/` → Uploads and parses resume files  
  - `GET /` → Health check endpoint  
- Handles file saving, data flow between parser and LLM, and response formatting.
- Supports asynchronous operations for high performance.

---

### 2. 📄 File Parser (`src/parsers.py`)
- Extracts raw text from different resume formats using libraries such as:
  - `pdfminer.six` for PDF files  
  - `docx2txt` for DOCX files  
  - `textract` or `PyMuPDF` (optional fallback extractors)
- Cleans and normalizes extracted text to make it AI-ready.
- Returns plain text for downstream processing.

---

### 3. 🤖 LLM Client (`src/llm_client.py`)
- Connects to a **Large Language Model API** (e.g., OpenAI, local GPT-based, or Hugging Face).  
- Sends extracted resume text to the LLM for **semantic parsing and structuring**.  
- Returns structured JSON data (name, contact info, experience, skills, education).  
- Supports multiple models configurable via `.env` or environment variables.

---

### 4. 🧱 Models & Schemas (`src/models.py`)
- Defines **Pydantic data models** for:
  - `ParseResultSchema`
  - `PersonalInfo`, `WorkExperience`, `Education`, `Skill`
  - `AIEnhancements` (optional AI scoring and suggestions)
- Ensures data validation and consistent API response format.

---

### 5. 🗄️ Database Layer (`PostgreSQL`)
- Stores:
  - Resume file metadata  
  - Extracted structured data  
  - AI enhancements and insights  
- SQL schema defined in `migrations/001_create_resume_schema.sql`.
- Supports easy integration with ORMs like SQLAlchemy (optional future enhancement).

---

### 6. 🧾 Documentation & Configs
- `docs/architecture.md` → System design and flow explanation.  
- `docs/deployment-guide.md` → Deployment steps for local and cloud environments.  
- `docs/api-specification.yaml` → OpenAPI definition for endpoints.  
- `.env.example` → Example environment file with placeholders for API keys and DB configs.  
- `setup.sh` → Automates project setup and dependency installation.

---

## 🔁 Data Flow Diagram

