"""
Integration tests for the FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app
import cv2
import numpy as np
import os

client = TestClient(app)

@pytest.fixture
def sample_video(tmp_path):
    """Creates a sample video file for testing."""
    video_path = str(tmp_path / "test_video.mp4")
    
    # Create a simple video
    frames = []
    for i in range(10):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.putText(frame, str(i), (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        frames.append(frame)
    
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (100, 100))
    for frame in frames:
        out.write(frame)
    out.release()
    
    return video_path

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_analyze_video_endpoint_success(sample_video):
    with open(sample_video, "rb") as f:
        response = client.post(
            "/analyze_video",
            files={"video_file": ("test_video.mp4", f, "video/mp4")},
            params={"analyze_full": "true"}
        )
    
    assert response.status_code == 200
    result = response.json()
    
    assert "status" in result
    assert result["status"] == "success"
    assert "analysis" in result
    assert "metadata" in result

def test_analyze_video_endpoint_invalid_file():
    response = client.post(
        "/analyze_video",
        files={"video_file": ("test.txt", b"not a video", "text/plain")},
    )
    
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_analyze_video_endpoint_first_frame_only(sample_video):
    with open(sample_video, "rb") as f:
        response = client.post(
            "/analyze_video",
            files={"video_file": ("test_video.mp4", f, "video/mp4")},
            params={"analyze_full": "false"}
        )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["metadata"]["analysis_type"] == "first_frame"

def test_analyze_video_endpoint_missing_file():
    response = client.post("/analyze_video")
    assert response.status_code == 422  # FastAPI validation error

def test_analyze_video_endpoint_empty_file():
    response = client.post(
        "/analyze_video",
        files={"video_file": ("empty.mp4", b"", "video/mp4")},
    )
    
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_analyze_video_endpoint_concurrent_requests(sample_video):
    """Test handling multiple concurrent video analysis requests."""
    import asyncio
    import httpx
    
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as ac:
        # Create multiple concurrent requests
        tasks = []
        for _ in range(3):
            with open(sample_video, "rb") as f:
                files = {"video_file": ("test_video.mp4", f.read(), "video/mp4")}
                task = ac.post("/analyze_video", files=files)
                tasks.append(task)
        
        # Execute requests concurrently
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests were successful
        for response in responses:
            assert response.status_code == 200
            assert "analysis" in response.json()

def test_analyze_video_endpoint_large_file(tmp_path):
    """Test handling of a large video file."""
    # Create a large video file
    video_path = str(tmp_path / "large_video.mp4")
    
    # Create a video with many frames
    frames = []
    for i in range(100):  # 100 frames
        frame = np.zeros((1920, 1080, 3), dtype=np.uint8)  # Full HD frame
        cv2.putText(frame, str(i), (800, 500), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255))
        frames.append(frame)
    
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920, 1080))
    for frame in frames:
        out.write(frame)
    out.release()
    
    with open(video_path, "rb") as f:
        response = client.post(
            "/analyze_video",
            files={"video_file": ("large_video.mp4", f, "video/mp4")},
            params={"analyze_full": "true"}
        )
    
    assert response.status_code == 200
    assert "analysis" in response.json()

def test_analyze_video_endpoint_corrupted_file(tmp_path):
    """Test handling of a corrupted video file."""
    corrupted_video = str(tmp_path / "corrupted.mp4")
    with open(corrupted_video, "wb") as f:
        f.write(b"corrupted video content")
    
    with open(corrupted_video, "rb") as f:
        response = client.post(
            "/analyze_video",
            files={"video_file": ("corrupted.mp4", f, "video/mp4")},
        )
    
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()