import { useState } from "react";
import "./App.css";
import "./components/result.css"

export default function App() {
  const [result, setResult] = useState();
  const [question, setQuestion] = useState<string | undefined>("");
  const [file, setFile] = useState();
  const [timestamp, setTimestamp] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleQuestionChange = (event: any) => {
    console.log("Question changed:", event.target.value);
    setQuestion(event.target.value);
  };

  const handleFileChange = (event: any) => {
    console.log("File selected:", event.target.files[0].name);
    setFile(event.target.files[0]);
    const newTimestamp = new Date().toISOString();
    setTimestamp(newTimestamp);
  };

  const handleSubmit = (event: any) => {
    event.preventDefault();
    console.log("Form submitted with question:", question);
    setIsLoading(true);
    console.log("Loading state set to true");

    const formData = new FormData();
    if (file) {
      console.log("Appending file to formData");
      formData.append("file", file);
    }
    if (question) {
      console.log("Appending question to formData");
      formData.append("question", question);
    }
    formData.append("timestamp", timestamp);

    console.log("Sending fetch request to backend");
    fetch(`${process.env.REACT_APP_BACKEND_URL}/predict`, {
           method: "POST",
           body: formData,
    })
      .then((response) => {
        console.log("Received response from backend");
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
        <label className="questionLabel" htmlFor="question">
          Question:
        </label>
        <input
          className="questionInput"
          id="question"
          type="text"
          value={question}
          onChange={handleQuestionChange}
          placeholder="Ask your question here"
        />
        <br />
        <label className="fileLabel" htmlFor="file">
          Upload file:
        </label>
        <input
          type="file"
          id="file"
          name="file"
          accept=".csv, .pdf, .docx, .txt"
          onChange={handleFileChange}
          className="fileInput"
        />
        <br />
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
