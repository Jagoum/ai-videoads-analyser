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
async def analyze_video(
    video_file: UploadFile = File(...),
    analyze_full: bool = True
):
    """
    Analyzes a video and returns a comprehensive critique.
    
    Args:
        video_file: The video file to analyze
        analyze_full: If True, analyzes the entire video. If False, only analyzes the first frame.
    """
    if not video_file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a video file."
        )

    try:
        # Create a temporary file to store the video
        temp_file_path = f"/tmp/{video_file.filename}"
        with open(temp_file_path, "wb+") as temp_file:
            contents = await video_file.read()
            temp_file.write(contents)
        
        if analyze_full:
            # Analyze the full video
            scorecard = critique_engine.analyze_video(temp_file_path)
        else:
            # Analyze just the first frame
            cap = cv2.VideoCapture(temp_file_path)
            if not cap.isOpened():
                raise HTTPException(
                    status_code=500, 
                    detail="Could not open video file."
                )
                
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise HTTPException(
                    status_code=500, 
                    detail="Could not read the first frame of the video."
                )
                
            scorecard = critique_engine.analyze_frame(frame)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return {
            "status": "success",
            "analysis": scorecard,
            "metadata": {
                "filename": video_file.filename,
                "content_type": video_file.content_type,
                "analysis_type": "full" if analyze_full else "first_frame"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred during analysis: {str(e)}"
        )

@app.get("/")
def read_root():
    return {"message": "BrandAI Critique Engine is running."}