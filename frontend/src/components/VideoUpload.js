import React from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

function VideoUpload({ onAnalysisStart, onAnalysisComplete, onError, loading }) {
    const onDrop = async (acceptedFiles) => {
        const file = acceptedFiles[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            onAnalysisStart();

            const response = await axios.post('/api/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            onAnalysisComplete(response.data);
        } catch (error) {
            onError(error.response?.data || { message: 'Failed to analyze video' });
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
            <Box
                {...getRootProps()}
                sx={{
                    border: '2px dashed #ccc',
                    borderRadius: 2,
                    p: 4,
                    mb: 2,
                    cursor: 'pointer',
                    backgroundColor: isDragActive ? '#f0f0f0' : 'transparent',
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
            </Box>

            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <CircularProgress />
                    <Typography variant="body1" sx={{ ml: 2 }}>
                        Analyzing video...
                    </Typography>
                </Box>
            )}
        </Box>
    );
}

export default VideoUpload;