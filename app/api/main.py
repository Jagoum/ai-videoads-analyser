"""
Main FastAPI application for the BrandAI critique engine.
"""
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from app.core.critique_engine import CritiqueEngine
import json

app = FastAPI()

# Load configuration
with open('config/brand_config.json', 'r') as f:
    config = json.load(f)

critique_engine = CritiqueEngine(config)

@app.post("/analyze_video")
async def analyze_video(video_file: UploadFile = File(...)):
    """
    Analyzes the first frame of a video and returns a critique.
    """
    if not video_file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video.")

    try:
        contents = await video_file.read()
        
        # Use OpenCV to read the video from memory
        video_stream = np.frombuffer(contents, np.uint8)
        cap = cv2.VideoCapture(video_stream)
        
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Could not open video file.")
            
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=500, detail="Could not read the first frame of the video.")
            
        # Analyze the frame
        scorecard = critique_engine.analyze_frame(frame)
        
        return scorecard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "BrandAI Critique Engine is running."}