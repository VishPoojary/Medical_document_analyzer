from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pymupdf
from io import BytesIO

from services.llm_service import extract_medical_data

app = FastAPI(
    title= "MedDoc",
    description="AI powered medical document extraction ",
    version= "0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials = True,
    allow_methods = ["GET", "POST"],
    allow_headers = "*",
)

class ExtractionRequest(BaseModel):
    text: str = Field(min_length= 1, max_length= 20000)

@app.get("/")
def root():
    return{
        "message": "API is running"
    }

@app.get("/health")
def health():
    return{
        "status": "ok"
    }

@app.post("/api/v1/extract-medical-data")
def extract_document(request: ExtractionRequest):
    try:
        result = extract_medical_data(request.text)
        return result.model_dump()
    except ValueError as exc:
        raise HTTPException(
            status_code= 502,
            detail= "The model returend an invalid and empty response."
        ) from exc
    except Exception as exc:
        print(f"Medical extraction failed: {exc}")
        raise HTTPException(
            status_code= 502,
            detail= "Medical extraction failed. Check the server logs."
        ) from exc

@app.post("/api/v1/extract-medical-file")
async def extract_medical_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="Please upload a .txt file",
        )
    
    content = await file.read()

    if len(content) > 1_00_000:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 1 MB.",
        )

    try:
        text = content.decode("utf-8-sig").strip()
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The file must be encoded as UTF-8 text.",
        )
    
    if not text:
        raise HTTPException(
            status_code=400,
            detail="The file is empty",
        )
    if len(text) > 20_000:
        raise HTTPException(
            status_code=413,
            detail="Extracted text exceeds teh 20,000 character limit.",
        )
    try:
        result = extract_medical_data(text)
        return{
            "filename": file.filename,
            "extracted_data": result.model_dump(),
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="The model returned an invalid and empty response.",
        ) from exc
    except Exception as exc:
        print(f"Medical file extraction faield: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Medical extraction failed. Check server logs.",
        ) from exc
    finally:
        await file.close()


@app.post("/api/v1/extract-medical-pdf")
async def extract_medical_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a .pdf file.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    if len(content) > 5_000_000:
        raise HTTPException(
            status_code=413,
            detail="PDF is too large. Maximum size is 5 MB.",
        )

    try:
        with pymupdf.open(
            stream=content,
            filetype="pdf",
        ) as pdf:
            if pdf.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported.",
                )

            page_count = len(pdf)

            if page_count > 30:
                raise HTTPException(
                    status_code=413,
                    detail="PDF cannot contain more than 30 pages.",
                )

            extracted_text = "\n".join(
                page.get_text() for page in pdf
            ).strip()

    except HTTPException:
        raise
    except Exception as exc:
        print(f"PDF reading error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Check the server terminal.",
        ) from exc
    finally:
        await file.close()

    if not extracted_text:
        raise HTTPException(
            status_code=422,
            detail="No selectable text found. Scanned PDFs require OCR.",
        )

    if len(extracted_text) > 20_000:
        raise HTTPException(
            status_code=413,
            detail="Extracted text exceeds the 20,000 character limit.",
        )

    try:
        result = extract_medical_data(extracted_text)

        return {
            "filename": file.filename,
            "pages": page_count,
            "extracted_data": result.model_dump(),
        }
    except ValueError as exc:
        print(f"PDF extraction validation error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The model returned an invalid or empty response.",
        ) from exc
    except Exception as exc:
        print(f"Medical PDF extraction failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Medical extraction failed. Check the server logs.",
        ) from exc