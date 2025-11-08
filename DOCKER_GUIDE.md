# Quick Start Guide

This guide will help you get the AI Video Ads Analyzer up and running using Docker.

## Prerequisites

1. Docker and Docker Compose installed on your system
2. Google Cloud credentials file for the Vision API
3. API keys for video generation services (if using)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-videoads-analyser.git
cd ai-videoads-analyser
```

2. Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

3. Copy and configure brand settings:

```bash
cp config/brand_config.json.example config/brand_config.json
# Edit brand_config.json with your brand guidelines
```

4. Place your Google Cloud credentials file:

```bash
cp path/to/your/credentials.json config/google_credentials.json
```

## Running the Application

1. Build and start the containers:

```bash
docker-compose up --build
```

2. Access the application:

- Frontend: <http://localhost:80>
- Backend API: <http://localhost:8000>
- API Documentation: <http://localhost:8000/docs>

## Usage

1. Open your browser and navigate to <http://localhost>
2. Upload a video file using the drag-and-drop interface
3. Wait for the analysis to complete
4. Review the detailed analysis results

## Stopping the Application

To stop the application:

```bash
docker-compose down
```

## Troubleshooting

1. If the frontend can't connect to the backend:
   - Check that both containers are running: `docker-compose ps`
   - Verify network connectivity: `docker network inspect ai-videoads-analyser_app-network`

2. If video analysis fails:
   - Check Google Cloud credentials
   - Verify API keys in .env file
   - Check container logs: `docker-compose logs backend`

3. For permission issues:
   - Ensure upload directory has correct permissions
   - Check container user permissions

## Additional Configuration

### Customizing Brand Guidelines

Edit `config/brand_config.json` to adjust:

- Color palette
- Logo requirements
- Tone of voice
- Safety thresholds

### Adjusting Resource Limits

Edit `docker-compose.yml` to modify:

- Memory limits
- CPU allocation
- Storage volumes

### Security Considerations

1. API Keys:
   - Store securely in .env file
   - Never commit credentials to version control
   - Rotate keys regularly

2. File Upload Limits:
   - Adjust in nginx.conf
   - Default max: 100MB

3. Access Control:
   - Implement authentication if needed
   - Configure CORS settings

## Maintenance

### Updating the Application

1. Pull latest changes:

```bash
git pull origin main
```

2. Rebuild containers:

```bash
docker-compose up --build
```

### Backup

1. Configuration:
   - Back up .env file
   - Back up brand_config.json
   - Back up Google credentials

2. Analysis Results:
   - Back up uploads directory if needed
   - Export analysis reports regularly

## Support

For issues and support:

1. Check the troubleshooting guide
2. Review container logs
3. Submit GitHub issues
4. Contact development team
