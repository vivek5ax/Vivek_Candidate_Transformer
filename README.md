# 🚀 Candidate Transformer

Candidate Transformer is an AI-powered resume intelligence platform. It seamlessly extracts, normalizes, and enriches candidate data from raw resumes (and optionally recruiter CSVs) into a beautifully structured, projected profile.

![Candidate Transformer](https://img.shields.io/badge/Status-Active-success.svg)
![React](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-teal)

## ✨ Key Features

* **Hybrid Extraction Engine**: Combines deterministic logic (RegEx, Layout Parsing) with advanced NLP (spaCy) and font-size heuristics for highly accurate extraction without relying on external APIs.
* **Dual Extraction Modes**: 
  * **Resume Only**: Upload a standard PDF/Word document for instant AI extraction.
  * **Resume + CSV**: Upload a resume alongside recruiter CSV data for cross-referencing and enriched projections.
* **Interactive Profile Builder**: A dynamic UI allowing you to manually toggle and customize exactly which fields (Contact Info, Experience, Education, etc.) appear in the final profile.
* **Data Provenance & Confidence**: Hover over any extracted data point to instantly see exactly *where* it was found (Source File), *how* it was found (Method), and its *Confidence Score*.
* **Beautiful Dark-Mode UI**: Built from scratch using modern glassmorphism, floating UI elements, and sleek CSS transitions.

## 🛠️ Technology Stack

**Frontend**
* React 18
* Vite
* TypeScript
* Vanilla CSS (Custom Glassmorphism Design System)

**Backend**
* Python 3.10+
* FastAPI (RESTful API architecture)
* `pdfplumber` / `PyMuPDF` (Document Parsing)
* SpaCy (Named Entity Recognition)
* Pydantic (Data Validation & Modeling)

---

## 🚀 Getting Started

Follow these instructions to get the project running locally on your machine.


### 1. Backend Setup
Navigate into the backend directory, set up your virtual environment, and install dependencies.
```bash
cd backend
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```


**Run the Backend Server**
```bash
python -m app.main
```
The FastAPI backend will start running on `http://localhost:8000`.

### 2. Frontend Setup
Open a new terminal window, navigate into the frontend directory, and install dependencies.
```bash
cd frontend
npm install

# Start the development server
npm run dev
```
The React frontend will start running on `http://localhost:5173`.

## 🧠 How It Works / What We Built

We engineered a full-stack, AI-driven pipeline that transforms messy, unstructured resume data into a clean, canonical JSON schema, and dynamically projects it into a beautiful React frontend.

### 1. Hybrid Extraction Pipeline (`backend/app/extractors/`)
Instead of relying on a single point of failure, our backend routes the uploaded document through multiple specialized engines:
* **Layout Parsers (`pdfplumber`)**: Used for structured sections like contact info and tabular experience data.
* **NLP & Regex (`spaCy`)**: Used for named entity recognition (NER), dates, emails, and URLs.
* **Heuristics & Taxonomy Engine**: Used for complex tasks, such as utilizing font-size analysis to pinpoint the candidate's name and mapping unstructured skills into primary/secondary buckets based on a robust taxonomy mapping.

### 2. Multi-Source Merging & Provenance (`backend/app/pipeline/`)
When extracting from multiple sources (e.g., a Resume + a Recruiter CSV), the system uses a **Merge Policy Engine**. If data conflicts, the engine determines the source of truth based on predefined weights. 
* *Data Provenance*: Every single extracted field retains metadata about *where* it came from (the source file), *how* it was extracted (the method), and a *Confidence Score*.

### 3. Dynamic Projection Engine (`backend/app/projection/`)
The raw, canonical candidate model contains massive amounts of data. The Projection Engine listens to the frontend configuration and intelligently filters, shapes, and projects only the requested fields (with their provenance metadata) back to the client.

### 4. Interactive Profile Builder (`frontend/src/pages/Builder.tsx`)
The React frontend receives the projected data and renders it in a highly modular, draggable, and interactive Configuration Panel.
* **Dynamic Tooltips**: Hovering over any data point displays a translucent tooltip populated entirely dynamically by the backend's Provenance tracking (showing Source, Method, and Confidence), allowing users to trust the AI's output.

---

## 📝 License
This project is open-source and available under the MIT License.