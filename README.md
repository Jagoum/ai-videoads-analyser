# AI Video Ads Analyzer

An intelligent system for analyzing and critiquing AI-generated video advertisements using multi-agent architecture.

## Project Overview

This system serves as an automated Creative Director and Brand Compliance Officer for AI-generated video advertisements. It focuses on analyzing and critiquing video ads across multiple dimensions to ensure brand consistency, quality, and safety.

### Core Components

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

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-videoads-analyser.git
cd ai-videoads-analyser
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Usage

### Basic Usage

```python
from video_analyzer import VideoAnalyzer

# Initialize the analyzer
analyzer = VideoAnalyzer(brand_config="path/to/brand_config.json")

# Analyze a video
results = analyzer.analyze_video("path/to/video.mp4")

# Get detailed scorecard
scorecard = results.get_scorecard()
```

### Advanced Configuration

Create a brand configuration file (`brand_config.json`):

```json
{
  "brand_name": "Example Brand",
  "color_palette": ["#FF0000", "#00FF00", "#0000FF"],
  "logo_path": "path/to/logo.png",
  "tone_of_voice": ["professional", "friendly"],
  "restricted_content": ["explicit", "violence"]
}
```

### Running Analysis

1. **Simple Analysis**

```bash
python -m video_analyzer analyze --video path/to/video.mp4
```

2. **Detailed Analysis**

```bash
python -m video_analyzer analyze --video path/to/video.mp4 --detailed --output report.json
```

3. **Batch Processing**

```bash
python -m video_analyzer batch --input-dir videos/ --output-dir reports/
```

## Configuration Options

### Scoring Parameters

- `brand_alignment_threshold`: 0.8 (default)
- `visual_quality_threshold`: 0.75 (default)
- `safety_threshold`: 0.95 (default)
- `message_clarity_threshold`: 0.85 (default)

### API Integration

The system supports multiple video generation APIs:

- Google Veo
- Pika Labs
- RunwayML
- Stable Video Diffusion

Configure API keys in your `.env` file:

```
GOOGLE_VEO_API_KEY=your_key_here
PIKA_LABS_API_KEY=your_key_here
RUNWAY_API_KEY=your_key_here
```

## Output Format

The analysis generates a JSON scorecard:

```json
{
  "overall_score": 0.85,
  "categories": {
    "brand_alignment": {
      "score": 0.9,
      "details": {
        "color_match": 0.95,
        "logo_placement": 0.85,
        "style_consistency": 0.9
      }
    },
    "visual_quality": {
      "score": 0.8,
      "issues": []
    },
    "safety_ethics": {
      "score": 0.95,
      "flags": []
    },
    "message_clarity": {
      "score": 0.75,
      "suggestions": []
    }
  },
  "recommendations": []
}
```

## Development

### Project Structure

```
ai-videoads-analyser/
├── src/
│   ├── agents/
│   │   ├── visual_quality_agent.py
│   │   ├── brand_compliance_agent.py
│   │   ├── safety_agent.py
│   │   ├── message_agent.py
│   │   └── synthesis_agent.py
│   ├── core/
│   │   ├── video_processor.py
│   │   ├── brand_analyzer.py
│   │   └── scorecard_generator.py
│   └── utils/
│       ├── api_clients.py
│       └── validators.py
├── tests/
├── config/
├── examples/
└── docs/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Credits

This project uses several open-source tools and APIs:

- OpenCV for video processing
- Gemini Vision for visual analysis
- CLIP for similarity scoring
- Vertex AI for model hosting
