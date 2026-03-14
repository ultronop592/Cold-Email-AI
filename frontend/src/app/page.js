"use client";

import { useState } from "react";
import styles from "./page.module.css";

export default function Home() {
  const [jobUrl, setJobUrl] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!jobUrl.trim() || !resumeFile) {
      setError("Provide a job URL and upload a resume file first.");
      return;
    }

    const formData = new FormData();
    formData.append("job_url", jobUrl.trim());
    formData.append("resume", resumeFile);

    try {
      setLoading(true);
      const response = await fetch("/api/generate-email", {
        method: "POST",
        body: formData,
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload?.error || "Request failed.");
      }

      setResult(payload);
    } catch (submitError) {
      setError(submitError.message || "Unable to process the request.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <main className={styles.shell}>
        <section className={styles.hero}>
          <p className={styles.badge}>Cold Email AI</p>
          <h1>Frontend Test Console</h1>
          <p>
            Use this panel to send a job post URL and resume directly to your
            FastAPI backend and inspect generated output.
          </p>
        </section>

        <form className={styles.formCard} onSubmit={handleSubmit}>
          <label className={styles.field}>
            <span>Job Post URL</span>
            <input
              type="url"
              placeholder="https://example.com/job-post"
              value={jobUrl}
              onChange={(event) => setJobUrl(event.target.value)}
              required
            />
          </label>

          <label className={styles.field}>
            <span>Resume File (PDF)</span>
            <input
              type="file"
              accept=".pdf"
              onChange={(event) => setResumeFile(event.target.files?.[0] || null)}
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Generating..." : "Test API"}
          </button>
        </form>

        {error ? <p className={styles.error}>{error}</p> : null}

        <section className={styles.resultsGrid}>
          <article className={styles.resultCard}>
            <h2>Email Draft</h2>
            <pre>{result?.email || "No response yet."}</pre>
          </article>

          <article className={styles.resultCard}>
            <h2>Suggestions</h2>
            <pre>{result?.suggestions || "No response yet."}</pre>
          </article>

          <article className={styles.resultCard}>
            <h2>Job Analysis</h2>
            <pre>{result?.job_analysis || "No response yet."}</pre>
          </article>

          <article className={styles.resultCard}>
            <h2>Resume Analysis</h2>
            <pre>{result?.resume_analysis || "No response yet."}</pre>
          </article>
        </section>
      </main>
    </div>
  );
}
