
from types import SimpleNamespace

import pymupdf
import pytest
from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)


def fake_extraction(text):
    return SimpleNamespace(
        model_dump=lambda: {
            "patient_name": "John Doe",
            "diagnosis": ["Type 2 Diabetes Mellitus"],
            "medications": [
                {
                    "name": "Metformin",
                    "dose": "500 mg",
                    "frequency": "twice daily",
                }
            ],
            "lab_results": [
                {
                    "name": "HbA1c",
                    "value": "7.2",
                    "unit": "%",
                    "reference_range": None,
                }
            ],
            "important_findings": [],
        }
    )


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "API is running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_text_extraction(monkeypatch):
    monkeypatch.setattr(main, "extract_medical_data", fake_extraction)

    response = client.post(
        "/api/v1/extract-medical-data",
        json={"text": "Synthetic medical report"},
    )

    assert response.status_code == 200
    assert response.json()["patient_name"] == "John Doe"
    assert response.json()["diagnosis"] == [
        "Type 2 Diabetes Mellitus"
    ]


def test_txt_file_upload(monkeypatch):
    monkeypatch.setattr(main, "extract_medical_data", fake_extraction)

    response = client.post(
        "/api/v1/extract-medical-file",
        files={
            "file": (
                "sample.txt",
                b"Synthetic medical report",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "sample.txt"
    assert response.json()["extracted_data"]["patient_name"] == "John Doe"


def test_txt_endpoint_rejects_pdf():
    response = client.post(
        "/api/v1/extract-medical-file",
        files={
            "file": (
                "sample.pdf",
                b"not a real PDF",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400


def test_pdf_file_upload(monkeypatch):
    monkeypatch.setattr(main, "extract_medical_data", fake_extraction)

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Patient Name: John Doe. Synthetic medical report."
    )
    pdf_bytes = document.tobytes()
    document.close()

    response = client.post(
        "/api/v1/extract-medical-pdf",
        files={
            "file": (
                "sample.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "sample.pdf"
    assert response.json()["pages"] == 1
    assert response.json()["extracted_data"]["patient_name"] == "John Doe"


def test_pdf_endpoint_rejects_invalid_pdf():
    response = client.post(
        "/api/v1/extract-medical-pdf",
        files={
            "file": (
                "broken.pdf",
                b"this is not a valid PDF",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400