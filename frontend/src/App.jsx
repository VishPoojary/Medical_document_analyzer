
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(event) {
    event.preventDefault();

    if (!file) {
      setError("Please select a TXT or PDF file.");
      return;
    }

    const isTxt = file.name.toLowerCase().endsWith(".txt");
    const isPdf = file.name.toLowerCase().endsWith(".pdf");

    if (!isTxt && !isPdf) {
      setError("Only TXT and PDF files are supported.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const endpoint = isPdf
        ? "/api/v1/extract-medical-pdf"
        : "/api/v1/extract-medical-file";

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Document extraction failed.");
      }

      setResult(data.extracted_data);
    } catch (err) {
      setError(
        err.message || "Could not connect to the MedLens API."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="header">
        <div className="logo">VCare</div>
        <span className="header-label">AI Medical Document Analyzer</span>
      </header>

      <section className="hero">
        <p className="eyebrow">DOCUMENT INTELLIGENCE</p>
        <h1>Understand medical reports faster.</h1>
        <p className="subtitle">
          Upload a TXT or PDF report to extract diagnoses,
          medications, laboratory results, and important findings.
        </p>
      </section>

      <section className="panel">
        <h2>Upload a medical report</h2>
        <p className="muted">
          Supported formats: .txt and text-based .pdf. Maximum size: 5 MB.
        </p>

        <form onSubmit={handleUpload}>
          <label className="dropzone">
            <span className="upload-icon">↑</span>
            <strong>
              {file ? file.name : "Choose a report"}
            </strong>
            <span className="muted">
              Select a TXT or PDF file from your computer
            </span>
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={(event) => {
                setFile(event.target.files?.[0] || null);
                setResult(null);
                setError("");
              }}
            />
          </label>

          <button type="submit" disabled={loading || !file}>
            {loading ? "Analyzing report..." : "Analyze report"}
          </button>
        </form>

        {loading && (
          <p className="status" role="status">
            Extracting information. This may take a little time.
          </p>
        )}

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
      </section>

      {result && (
        <section className="results">
          <h2>Extracted information</h2>
          <p className="muted">
            AI-extracted information may be incomplete or inaccurate.
            Verify every result against the original report.
          </p>

          <ResultCard
            title="Patient name"
            items={
              result.patient_name ? [result.patient_name] : []
            }
          />

          <ResultCard title="Diagnoses" items={result.diagnosis} />

          <ResultCard
            title="Medications"
            items={result.medications.map((medication) =>
              [
                medication.name,
                medication.dose,
                medication.frequency,
              ]
                .filter(Boolean)
                .join(" — ")
            )}
          />

          <ResultCard
            title="Laboratory results"
            items={result.lab_results.map((lab) =>
              [
                lab.name,
                lab.value,
                lab.unit,
                lab.reference_range
                  ? `(Reference: ${lab.reference_range})`
                  : "",
              ]
                .filter(Boolean)
                .join(" ")
            )}
          />

          <ResultCard
            title="Important findings"
            items={result.important_findings}
          />
        </section>
      )}

      <footer>
        MedLens is an educational prototype, not a diagnostic tool.
      </footer>
    </main>
  );
}

function ResultCard({ title, items = [] }) {
  return (
    <article className="result-card">
      <h3>{title}</h3>
      {items.length > 0 ? (
        <ul>
          {items.map((item, index) => (
            <li key={`${title}-${index}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No information extracted.</p>
      )}
    </article>
  );
}

export default App;