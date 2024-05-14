import { useState } from "react";
import "./App.css";
import "./components/result.css"

export default function App() {
  const [result, setResult] = useState<string | undefined>();
  const [question, setQuestion] = useState<string | undefined>("");
  const [file, setFile] = useState<File | null>(null);
  const [timestamp, setTimestamp] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleQuestionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("Question changed:", event.target.value);
    setQuestion(event.target.value);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("Manual selected:", event.target.files?.[0].name);
    setFile(event.target.files?.[0] || null);
    const newTimestamp = new Date().toISOString();
    setTimestamp(newTimestamp);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log("Form submitted with question:", question);
    setIsLoading(true);

    const formData = new FormData();
    if (file) {
      formData.append("file", file);
    }
    if (question) {
      formData.append("question", question);
    }
    formData.append("timestamp", timestamp);

    fetch(`${process.env.REACT_APP_BACKEND_URL}/predict`, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Successfully fetched data:", data);
        setIsLoading(false);
        setResult(data.result);
        setQuestion("");
      })
      .catch((error) => {
        console.error("Fetch error:", error);
        setIsLoading(false);
        setResult(undefined);
      });
  };

  return (
    <div className="appBlock">
      <form onSubmit={handleSubmit} className="form">
        <span className="fileLabel">Upload Your User Manual (PDF only):</span>
        <input
          type="file"
          id="file"
          name="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="fileInput"
        />
        <label className="questionLabel" htmlFor="question">
          Ask your question:
        </label>
        <input
          className="questionInput"
          id="question"
          type="text"
          value={question}
          onChange={handleQuestionChange}
          placeholder="Enter your question here"
        />
        <button
          className="submitBtn"
          type="submit"
          disabled={!file || !question}
        >
          Submit
        </button>
      </form>
      <div className="resultOutput">
        {isLoading ? (
          <p className="inProgress">...in progress...</p>
        ) : (
          result && <p style={{ whiteSpace: 'pre-wrap' }}>Result: {result}</p>
        )}
      </div>
    </div>
  );
}
