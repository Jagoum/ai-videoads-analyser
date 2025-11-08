import React, { useState } from 'react';
import { Box, Container, Paper, Typography } from '@mui/material';
import VideoUpload from './components/VideoUpload';
import AnalysisResults from './components/AnalysisResults';
import Header from './components/Header';

function App() {
    const [analysisResults, setAnalysisResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalysisComplete = (results) => {
        setAnalysisResults(results);
        setLoading(false);
        setError(null);
    };

    const handleError = (error) => {
        setError(error.message);
        setLoading(false);
        setAnalysisResults(null);
    };

    const handleStartAnalysis = () => {
        setLoading(true);
        setError(null);
        setAnalysisResults(null);
    };

    return (
        <Box sx={{ flexGrow: 1 }}>
            <Header />
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                <Paper elevation={3} sx={{ p: 3 }}>
                    {error && (
                        <Typography color="error" gutterBottom>
                            {error}
                        </Typography>
                    )}

                    <VideoUpload
                        onAnalysisStart={handleStartAnalysis}
                        onAnalysisComplete={handleAnalysisComplete}
                        onError={handleError}
                        loading={loading}
                    />

                    {analysisResults && (
                        <AnalysisResults results={analysisResults} />
                    )}
                </Paper>
            </Container>
        </Box>
    );
}

export default App;