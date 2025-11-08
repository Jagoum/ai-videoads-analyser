# AI Video Ads Analyzer

An intelligent system for analyzing and critiquing AI-generated video advertisements using a sophisticated multi-agent architecture. The system provides comprehensive analysis across brand compliance, visual quality, content safety, and message clarity dimensions.

## 🌟 Key Features

- **Full Video Analysis**: Process entire videos with frame-by-frame analysis
- **Multi-Agent Architecture**: Specialized agents for different aspects of analysis
- **Real-time Processing**: Stream analysis results as they become available
- **Brand Safety Checks**: Comprehensive content moderation and brand safety analysis
- **Visual Quality Assessment**: Technical and aesthetic quality evaluation
- **Temporal Analysis**: Analyze pacing, transitions, and narrative flow
- **Interactive Frontend**: User-friendly interface with real-time progress tracking
- **Containerized Deployment**: Easy deployment with Docker

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 14+
- Docker & Docker Compose (optional)
- Google Cloud Vision API credentials
- Azure Content Moderator API credentials

1. **Video Input Processing**
   - Supports various video formats
   - Integrates with major AI video generation APIs
   - Frame extraction and analysis capabilities

2. **Brand Analysis Engine**
   - Color palette verification
   - Logo detection and placement analysis
   - Typography and visual style checking

3. **Quality Assessment System**
   - Visual quality metrics
   - Composition analysis
   - Technical artifact detection

4. **Content Safety Analyzer**
   - Harmful content detection
   - Bias and stereotype checking
   - Ethical compliance verification

5. **Message Clarity Evaluator**
   - Product prominence analysis
   - Tagline verification
   - Brand message alignment

## System Architecture

```
Input Video → Multi-Agent Analysis Pipeline → Detailed Scorecard & Recommendations

Agents:
1. Visual Quality Agent
2. Brand Compliance Agent
3. Safety & Ethics Agent
4. Message Clarity Agent
5. Synthesis Agent
```

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-videoads-analyser.git
cd ai-videoads-analyser
```

2. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Build and run with Docker Compose:

```bash
docker-compose up --build
```

The application will be available at:

- Frontend: <http://localhost:80>
- Backend API: <http://localhost:8000>

### Option 2: Local Development

1. Clone and setup Python environment:

```bash
git clone https://github.com/yourusername/ai-videoads-analyser.git
cd ai-videoads-analyser
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Set up frontend:

```bash
cd frontend
npm install
```

3. Configure environment:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Start the services:

Backend:

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend:

```bash
cd frontend
npm start
```

## 📝 Usage Guide

### API Endpoints

#### Analyze Video

```http
POST /analyze_video
Content-Type: multipart/form-data

Parameters:
- video_file: The video file to analyze
- analyze_full: boolean (optional, default: true)
```

Response:

```json
{
  "status": "success",
  "analysis": {
    "overall_score": 0.85,
    "frame_results": {...},
    "temporal_analysis": {...},
    "recommendations": [...]
  },
  "metadata": {
    "filename": "example.mp4",
    "duration": 30.5,
    "frame_count": 915
  }
}
```

### Configuration

Create a brand configuration file (`config/brand_config.json`):

```json
{
  "brand_name": "Example Brand",
  "sampling_rate": 1,
  "max_workers": 4,
  "temporal_window": 5,
  "min_scene_duration": 0.5,
  "brand_agent": {
    "color_palette": ["#FF0000", "#00FF00", "#0000FF"],
    "logo_path": "path/to/logo.png",
    "tone_of_voice": ["professional", "friendly"]
  },
  "safety_agent": {
    "thresholds": {
      "harmful_content": 0.7,
      "bias": 0.6,
      "adult_content": 0.7,
      "violence": 0.6
    }
  }
}
```

### Using the Frontend

1. Upload a video using the drag-and-drop interface
2. Choose between quick analysis (first frame) or full video analysis
3. Monitor progress in real-time
4. Review comprehensive analysis results including:
   - Brand compliance metrics
   - Visual quality assessment
   - Content safety analysis
   - Message clarity evaluation
   - Temporal patterns and transitions
   - Specific recommendations for improvement

## 🔧 Advanced Configuration

### Environment Variables

```bash
# API Keys
GOOGLE_CLOUD_API_KEY=your_google_cloud_key
AZURE_COGNITIVE_KEY=your_azure_key
AZURE_COGNITIVE_ENDPOINT=your_azure_endpoint

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=False

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_UPLOAD_LIMIT=100000000
```

### Analysis Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `sampling_rate` | 1 | Frames per second to analyze |
| `max_workers` | 4 | Maximum parallel processing threads |
| `temporal_window` | 5 | Time window (seconds) for temporal analysis |
| `min_scene_duration` | 0.5 | Minimum scene duration (seconds) |

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html
```

## 🚀 Deployment

### Production Setup

1. Build optimized images:

```bash
docker-compose -f docker-compose.prod.yml build
```

2. Deploy with proper environment:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. Configure Nginx (optional):

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📚 API Documentation

Full API documentation is available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- OpenCV for video processing
- Azure Cognitive Services for content moderation
- Google Cloud Vision AI for image analysis
- FastAPI for the backend framework
- React for the frontend interface
