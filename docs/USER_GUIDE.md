# User Guide: AI Video Ads Analyzer

## Introduction

The AI Video Ads Analyzer is a sophisticated tool that helps evaluate and improve AI-generated video advertisements. It uses a multi-agent system to analyze various aspects of video ads, ensuring they meet brand guidelines, quality standards, and safety requirements.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-videoads-analyser.git
cd ai-videoads-analyser
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your configuration:

```bash
cp config/brand_config.json.example config/brand_config.json
# Edit brand_config.json with your brand's specifications
```

## Configuration

### Brand Configuration

The system requires a brand configuration file (`brand_config.json`) that defines your brand's requirements. Key configuration sections include:

1. Brand Identity

```json
{
    "brand_name": "Your Brand",
    "color_palette": ["#HEX1", "#HEX2"],
    "logo_path": "path/to/logo.png"
}
```

2. Content Guidelines

```json
{
    "tone_of_voice": ["professional", "friendly"],
    "brand_values": ["quality", "innovation"],
    "restricted_content": ["explicit", "violence"]
}
```

3. Quality Standards

```json
{
    "visual_quality": {
        "min_resolution": [1920, 1080],
        "max_blur": 0.5
    }
}
```

## Basic Usage

### Single Video Analysis

```python
from src.core.video_analyzer import VideoAnalyzer

# Initialize analyzer
analyzer = VideoAnalyzer(brand_config_path='config/brand_config.json')

# Analyze a single video
results = analyzer.analyze_video('path/to/video.mp4')

# Get deployment recommendation
recommendation = analyzer.get_deployment_recommendation(results)

# Get improvement suggestions
suggestions = analyzer.get_improvement_suggestions(results)
```

### Batch Analysis

```python
# Analyze multiple videos
results = analyzer.analyze_batch(
    input_dir='videos/',
    output_dir='analysis_results/'
)
```

### Command Line Interface

```bash
# Analyze a single video
python -m video_analyzer analyze --video path/to/video.mp4

# Analyze with detailed output
python -m video_analyzer analyze --video path/to/video.mp4 --detailed --output report.json

# Batch analysis
python -m video_analyzer batch --input-dir videos/ --output-dir reports/
```

## Understanding Results

### Analysis Components

The system evaluates videos across four main dimensions:

1. Visual Quality
   - Blur detection
   - Noise levels
   - Composition analysis
   - Technical artifacts

2. Brand Compliance
   - Color palette matching
   - Logo detection and placement
   - Visual style consistency
   - Tone of voice alignment

3. Safety & Ethics
   - Explicit content detection
   - Harmful object recognition
   - Bias checking
   - Misleading content detection

4. Message Clarity
   - Product visibility
   - Text readability
   - Message coherence
   - Call-to-action effectiveness

### Sample Output

The analysis generates a structured JSON output:

```json
{
    "final_analysis": {
        "overall_score": 0.85,
        "component_scores": {
            "visual_quality": 0.9,
            "brand_compliance": 0.85,
            "safety": 0.95,
            "message_clarity": 0.75
        },
        "critical_issues": [],
        "recommendations": [
            {
                "category": "message_clarity",
                "priority": "medium",
                "suggestion": "Improve call-to-action visibility"
            }
        ],
        "deployment_decision": {
            "ready": true,
            "confidence": 0.85
        }
    }
}
```

## Interpreting Scores

- Scores range from 0.0 to 1.0
- Recommended minimum thresholds:
  - Visual Quality: ≥ 0.75
  - Brand Compliance: ≥ 0.85
  - Safety: ≥ 0.95
  - Message Clarity: ≥ 0.80

## Best Practices

1. Brand Configuration
   - Keep brand colors up to date
   - Regularly update restricted content lists
   - Maintain clear tone of voice guidelines

2. Video Analysis
   - Use high-quality input videos
   - Analyze multiple variations of an ad
   - Review all agent feedback before deployment

3. Deployment
   - Always check safety scores first
   - Review critical issues carefully
   - Consider improvement suggestions before final deployment

## Troubleshooting

Common issues and solutions:

1. Low Visual Quality Scores
   - Check input video resolution
   - Ensure proper encoding
   - Review lighting and composition

2. Brand Compliance Issues
   - Verify brand config file
   - Check logo file path
   - Update color codes if needed

3. Safety Flags
   - Review flagged content carefully
   - Check restricted content settings
   - Verify false positives

## Support

For technical support:

- Check documentation
- Review example configurations
- Submit issues on GitHub
- Contact development team

## Advanced Features

1. Custom Scoring Weights

```python
analyzer = VideoAnalyzer(
    brand_config_path='config/brand_config.json',
    weights={
        'visual_quality': 0.3,
        'brand_compliance': 0.3,
        'safety': 0.2,
        'message_clarity': 0.2
    }
)
```

2. Detailed Analysis Mode

```python
results = analyzer.analyze_video(
    video_path='video.mp4',
    detailed=True
)
```

3. Custom Brand Rules

- Extend brand configuration
- Add custom metrics
- Define specific requirements

## API Integration

The system supports various video generation APIs:

1. Google Veo
2. Pika Labs
3. RunwayML
4. Stable Video Diffusion

Configure API keys in your environment:

```bash
export GOOGLE_VEO_API_KEY=your_key_here
export PIKA_LABS_API_KEY=your_key_here
export RUNWAY_API_KEY=your_key_here
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.
