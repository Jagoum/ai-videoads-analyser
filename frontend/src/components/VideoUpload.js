import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
    Box,
    Button,
    CircularProgress,
    Typography,
    FormControlLabel,
    Switch,
    LinearProgress
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

function VideoUpload({ onAnalysisStart, onAnalysisComplete, onError, loading }) {
    const [analyzeFull, setAnalyzeFull] = useState(true);
    const [progress, setProgress] = useState(0);

    const onDrop = async (acceptedFiles) => {
        const file = acceptedFiles[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('video_file', file);

        try {
            onAnalysisStart();
            setProgress(0);

            const response = await axios.post(
                '/analyze_video',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                    params: {
                        analyze_full: analyzeFull
                    },
                    onUploadProgress: (progressEvent) => {
                        const percentCompleted = Math.round(
                            (progressEvent.loaded * 100) / progressEvent.total
                        );
                        setProgress(percentCompleted);
                    }
                }
            );

            onAnalysisComplete(response.data);
        } catch (error) {
            onError(error.response?.data?.detail || 'Failed to analyze video');
        } finally {
            setProgress(0);
        }
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'video/mp4': ['.mp4'],
            'video/avi': ['.avi'],
            'video/quicktime': ['.mov'],
        },
        multiple: false,
        disabled: loading,
    });

    return (
        <Box sx={{ textAlign: 'center', my: 4 }}>
            <FormControlLabel
                control={
                    <Switch
                        checked={analyzeFull}
                        onChange={(e) => setAnalyzeFull(e.target.checked)}
                        disabled={loading}
                    />
                }
                label="Full Video Analysis"
                sx={{ mb: 2 }}
            />

            <Box
                {...getRootProps()}
                sx={{
                    border: '2px dashed #ccc',
                    borderRadius: 2,
                    p: 4,
                    mb: 2,
                    cursor: loading ? 'not-allowed' : 'pointer',
                    backgroundColor: isDragActive ? '#f0f0f0' : 'transparent',
                    opacity: loading ? 0.7 : 1,
                }}
            >
                <input {...getInputProps()} />
                <CloudUploadIcon sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                    {isDragActive
                        ? 'Drop the video here'
                        : 'Drag and drop a video file here, or click to select'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    Supported formats: MP4, AVI, MOV
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    {analyzeFull
                        ? 'Full video analysis may take several minutes'
                        : 'Quick analysis of the first frame only'}
                </Typography>
            </Box>

            {loading && (
                <Box sx={{ width: '100%', mt: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <CircularProgress size={24} sx={{ mr: 2 }} />
                        <Typography variant="body1">
                            {progress ? `Uploading: ${progress}%` : 'Analyzing video...'}
                        </Typography>
                    </Box>
                    {progress > 0 && (
                        <LinearProgress
                            variant="determinate"
                            value={progress}
                            sx={{ height: 8, borderRadius: 2 }}
                        />
                    )}
                </Box>
            )}
        </Box>
    );
}

export default VideoUpload;