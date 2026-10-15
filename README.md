# AI Medical Document Analyzer

This is an educational full-stack application that uses an LLM to extract structured information from medical documents.

## Features

* Upload TXT and text-based PDF files.
* Extract medical information using Google Gemini.
* Return structured JSON using Pydantic models.
* Display diagnoses, medications, laboratory results, and important findings in a React interface.
* Validate requests and handle common file-processing errors.
* Automated backend API tests using pytest.

## Tech Stack

* **Frontend:** React, Vite
* **Backend:** Python, FastAPI
* **AI:** Google Gemini API
* **PDF Processing:** PyMuPDF
* **Validation:** Pydantic
* **Testing:** pytest, FastAPI TestClient

## Local Setup

### Backend

1. Navigate to `backend/`.
2. Create and activate a Python virtual environment.
3. Install dependencies using `python -m pip install -r requirements.txt`.
4. Create a `.env` file based on `.env.example` and add your Gemini API key.
5. Start the server using `fastapi dev app/main.py`.

### Frontend

1. Navigate to `frontend/`.
2. Run `npm install`.
3. Run `npm run dev`.

## Testing

From the backend directory, run:

`python -m pytest app/test_main.py -v`

## Limitations

* Scanned PDFs requiring OCR are not currently supported.
* AI-extracted information can be incomplete or inaccurate.
* This project is an educational prototype, not a diagnostic or treatment tool.
* API availability and usage limits depend on the AI provider.
