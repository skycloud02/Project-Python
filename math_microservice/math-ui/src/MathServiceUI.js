import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './MathServiceUI.css';

export default function MathServiceUI() {
  const [operand, setOperand] = useState(0);
  const [operation, setOperation] = useState("fibonacci");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [apiKey, setApiKey] = useState("super-secret-key");
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  const compute = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/compute",
        { operation, operand: parseInt(operand) },
        { headers: { "X-API-Key": apiKey } }
      );
      setResult(response.data);
      fetchHistory();
      fetchLogs();
    } catch (err) {
      alert("Compute Error: " + (err.response?.data?.detail || "Unknown"));
    }
    setLoading(false);
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get("http://localhost:8000/history", {
        headers: { "X-API-Key": apiKey },
      });
      setHistory(res.data);
    } catch (err) {
      console.error("History fetch failed");
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:8000/logs", {
        headers: { "X-API-Key": apiKey },
      });
      setLogs(res.data);
    } catch (err) {
    console.log(err);
      console.error("Log fetch failed");
    }
  };

  useEffect(() => {
    fetchHistory();
    fetchLogs();
  }, []);

  return (
    <div className="container fancy">
      <h2 className="title">🔢 Math Microservice</h2>

      <div className="card">
        <div className="field">
          <label>🔑 API Key:</label>
          <div className="api-input-group">
            <input
              type={apiKeyVisible ? "text" : "password"}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <button className="toggle-btn" onClick={() => setApiKeyVisible(!apiKeyVisible)}>
              {apiKeyVisible ? "🙈 Hide" : "👁 Show"}
            </button>
          </div>
        </div>

        <div className="field">
          <label>🔢 Operand:</label>
          <input
            type="number"
            value={operand}
            onChange={(e) => setOperand(e.target.value)}
          />
        </div>

        <div className="field">
          <label>⚙️ Operation:</label>
          <select
            value={operation}
            onChange={(e) => setOperation(e.target.value)}
          >
            <option value="fibonacci">Fibonacci</option>
            <option value="factorial">Factorial</option>
            <option value="pow">Power (x^2)</option>
          </select>
        </div>

        <button className="compute-btn" onClick={compute} disabled={loading}>
          {loading ? "⏳ Calculating..." : "🧮 Compute"}
        </button>

        {result && (
          <div className="result-box">
            <h4>✅ Result:</h4>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>

      <div className="panel">
        <div className="history-box">
          <h4>📜 Operation History</h4>
          <ul>
            {history.map((item, index) => (
              <li key={index}>
                <strong>{item.operation}({item.operand})</strong> = {item.result}
                <br />
                <small>{new Date(item.timestamp).toLocaleString()}</small>
              </li>
            ))}
          </ul>
        </div>

        <div className="log-box">
          <h4>📘 Event Logs</h4>
          <ul>
            {logs.map((log, index) => (
              <li key={index}>
                <code>{JSON.stringify(log)}</code>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}