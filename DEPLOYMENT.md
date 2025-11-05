# greyShift - Docker Web Deployment

This guide will help you deploy the greyShift application as a web service using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Build and start the application
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d
```

The web application will be available at: **http://localhost:5000**

### 2. Alternative: Docker Build and Run

```bash
# Build the Docker image
docker build -t greyshift-web .

# Run the container
docker run -p 5000:5000 greyshift-web
```

## Usage

1. **Open your browser** and navigate to `http://localhost:5000`
2. **Upload an image** by dragging & dropping or clicking to select
3. **Automatic processing**: The image is automatically processed with optimal settings (70% correction intensity)
4. **Fine-tune if needed**:
   - **Correction Intensity**: Adjust slider from 0.0 (original) to 1.0 (full correction)
   - **Reprocess**: Click "Reprocess with Current Settings" to apply new intensity
5. **Download** the corrected image

## Features

- 📱 **Responsive web interface** - Works on desktop and mobile
- 🖼️ **Drag & drop upload** - Easy file selection
- ⚡ **Automatic processing** - Images are corrected immediately upon upload
- 🔄 **Real-time preview** - Interactive slider to preview different correction intensities
- 📥 **Direct download** - Get your corrected image instantly
- 🔧 **Adjustable intensity** - Fine-tune correction strength from 0% to 100%
- � **Reprocess option** - Apply different settings to the same image

## Supported Formats

- **Input**: JPG, JPEG, PNG, TIFF, BMP, WebP
- **Output**: Same format as input
- **Max file size**: 16MB

## Docker Management

### Stop the Application
```bash
# If running with docker-compose
docker-compose down

# If running with docker run
docker stop <container-id>
```

### View Logs
```bash
# Docker Compose logs (follow live logs)
docker-compose logs -f

# View last 50 log entries
docker-compose logs --tail 50

# Container logs by name
docker logs greyshift_python-greyshift-web-1 -f

# Filter logs by specific events
docker-compose logs | grep "Processing"     # Image processing events
docker-compose logs | grep "ERROR"         # Error events only
docker-compose logs | grep "Page visit"    # User visits
```

#### Log Events Tracked

The application logs the following activities:

- **🚀 Application Startup**: Flask app initialization
- **👤 User Visits**: Page loads with IP address and browser info
- **📁 File Uploads**: Image upload attempts (successful and failed)
- **⚙️ Image Processing**: Processing start, completion time, and image details
- **📊 Image Analysis**: Color cast analysis for live preview
- **📥 Downloads**: When users download processed images
- **🔍 File Access**: Static file serving requests
- **⚠️ Errors**: Failed uploads, processing errors, and system issues
- **🏥 Health Checks**: Docker health monitoring (debug level)

### Rebuild After Changes
```bash
# Rebuild and restart
docker-compose up --build --force-recreate
```

## Configuration

### Environment Variables

You can customize the application by setting environment variables:

```yaml
# In docker-compose.yml
environment:
  - FLASK_ENV=production
  - MAX_CONTENT_LENGTH=33554432  # 32MB in bytes
```

### Persistent Storage

To keep uploaded/processed images between container restarts, uncomment the volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./uploads:/app/uploads
  - ./processed:/app/processed
```

## Health Monitoring

The application includes a health check endpoint:
- **URL**: `http://localhost:5000/health`
- **Response**: `{"status": "healthy"}`

## Production Deployment

For production deployment:

1. **Change the secret key** in `app.py`:
   ```python
   app.config['SECRET_KEY'] = 'your-secure-secret-key-here'
   ```

2. **Use a reverse proxy** (nginx, Apache) for SSL termination

3. **Set up monitoring** and log aggregation

4. **Configure firewall** rules for port 5000

5. **Consider scaling** with multiple containers:
   ```bash
   docker-compose up --scale greyshift-web=3
   ```

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead
```

**Out of memory errors**:
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or reduce max file size in app.py
```

**Permission denied**:
```bash
# On Linux/Mac, ensure Docker has proper permissions
sudo chown -R $USER:$USER ./uploads ./processed
```

### Debug Mode

To run in debug mode for development:

```bash
# Set environment variable
export FLASK_ENV=development

# Or modify docker-compose.yml
environment:
  - FLASK_ENV=development
```

## Security Notes

- The application automatically cleans up old files (1 hour retention)
- File uploads are validated for type and size
- No permanent storage by default
- Consider adding authentication for production use

## Performance Tips

- **Resize large images** using the width/height options to reduce processing time
- **Use appropriate scalar values** - start with 0.5-0.7 for most images
- **Monitor Docker resource usage** in Docker Desktop

## Monitoring & Analytics

### Real-time Monitoring

#### Easy Log Monitoring (Recommended)

Use the included monitoring scripts for user-friendly log viewing:

**Windows PowerShell:**
```powershell
.\monitor_logs.ps1
```

**Linux/macOS:**
```bash
chmod +x monitor_logs.sh
./monitor_logs.sh
```

#### Manual Commands
```bash
# Watch live activity
docker-compose logs -f | grep -E "(Processing|Page visit|Download)"

# Monitor error rates
watch -n 5 'docker-compose logs --since 5m | grep ERROR | wc -l'

# View processing performance
docker-compose logs | grep "Processing completed" | tail -10
```

### Log Analysis Examples

**Find busiest hours:**
```bash
docker-compose logs | grep "Page visit" | awk '{print $1" "$2}' | cut -d: -f1-2 | sort | uniq -c
```

**Most common image types processed:**
```bash
docker-compose logs | grep "Processing started" | grep -o '\.[a-zA-Z]*,' | sort | uniq -c
```

**Average processing times:**
```bash
docker-compose logs | grep "Processing completed" | grep -o 'Time: [0-9.]*s' | awk -F: '{sum+=$2} END {print "Average:", sum/NR "s"}'
```

**Error frequency:**
```bash
docker-compose logs | grep -E "(ERROR|WARNING)" | awk '{print $1}' | sort | uniq -c
```

### Log Retention

By default, logs are kept in memory. For production deployments:

1. **Configure log rotation in docker-compose.yml:**
```yaml
services:
  greyshift-web:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
```

2. **External log aggregation** (recommended for production):
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Grafana Loki
   - Fluentd
   - Docker logging drivers

---

🎉 **Your greyShift web application is now ready for deployment with comprehensive logging!**