import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files);
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError("Please select a video file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append('video_file', selectedFile);

        setIsLoading(true);
        setError(null);
        setAnalysisResult(null);

        try {
            const response = await axios.post('/analyze_video', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setAnalysisResult(response.data);
        } catch (err) {
            setError(err.response ? err.response.data.detail : "An unknown error occurred.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>BrandAI: AI Ad Critique Engine</h1>
                <div className="upload-section">
                    <input type="file" accept="video/*" onChange={handleFileChange} />
                    <button onClick={handleUpload} disabled={isLoading}>
                        {isLoading ? 'Analyzing...' : 'Analyze Video'}
                    </button>
                </div>
                {error && <p className="error-message">{error}</p>}
            </header>
            {analysisResult && (
                <div className="results-section">
                    <h2>Analysis Results</h2>
                    <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

export default App;