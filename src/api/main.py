"""
FastAPI backend for the Video Analyzer system.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import os
import uvicorn
from ..core.video_analyzer import VideoAnalyzer

app = FastAPI(title="AI Video Ads Analyzer API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize video analyzer
analyzer = VideoAnalyzer(brand_config_path='config/brand_config.json')

# Upload directory
UPLOAD_DIR = os.getenv('UPLOAD_FOLDER', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnalysisResponse(BaseModel):
    overall_score: float
    component_scores: Dict[str, float]
    critical_issues: List[str]
    recommendations: List[Dict[str, Any]]
    deployment_decision: Dict[str, Any]

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze an uploaded video file.
    """
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    try:
        # Analyze video
        results = analyzer.analyze_video(file_path)
        
        # Extract relevant information
        final_analysis = results['final_analysis']
        
        return AnalysisResponse(
            overall_score=final_analysis['overall_score'],
            component_scores=final_analysis['component_scores'],
            critical_issues=final_analysis['critical_issues'],
            recommendations=final_analysis['recommendations'],
            deployment_decision=final_analysis['deployment_decision']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)