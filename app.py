#!/usr/bin/env python3
"""
Flask web application for greyShift image processing.
"""

import os
import uuid
import logging
import datetime
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import tempfile
import shutil
from pathlib import Path
from greyshift import GreyShift

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64MB max file size

# Configure logging for Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - greyShift - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("greyShift Flask application starting up")
logger.info(f"Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")

# Middleware to log all requests
@app.before_request
def log_request_info():
    """Log information about each incoming request."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.info(f"Request: {request.method} {request.path} - IP: {client_ip}")

# Create directories for uploads and processed images
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
DISPLAY_FOLDER = 'display'  # For UI display thumbnails
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(DISPLAY_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_display_thumbnail(image_path, output_path):
    """Create a display thumbnail: 480x720 for portrait, 720x480 for landscape."""
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Determine orientation and set appropriate limits
        if height > width:  # Portrait
            max_width, max_height = 480, 720
        else:  # Landscape or square
            max_width, max_height = 720, 480
        
        # Check if resizing is needed
        if width > max_width or height > max_height:
            # Calculate scaling factor to fit within max dimensions
            width_ratio = max_width / width
            height_ratio = max_height / height
            scale_ratio = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = int(width * scale_ratio)
            new_height = int(height * scale_ratio)
            
            # Resize the image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img_resized.save(output_path, quality=90, optimize=True)
            return True
        else:
            # Image is already within limits, just copy
            img.save(output_path, quality=90, optimize=True)
            return False
    except Exception as e:
        logger.error(f"Error creating display thumbnail: {e}")
        # If thumbnail creation fails, copy original
        shutil.copy2(image_path, output_path)
        return False


def cleanup_old_files():
    """Clean up old uploaded and processed files."""
    import time
    current_time = time.time()
    
    for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, DISPLAY_FOLDER]:
        for file_path in Path(folder).glob('*'):
            if current_time - file_path.stat().st_mtime > 3600:  # 1 hour old
                try:
                    os.remove(file_path)
                except OSError:
                    pass

@app.route('/')
def index():
    """Main page with upload form."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    logger.info(f"Page visit - IP: {client_ip}, User-Agent: {user_agent}")
    
    cleanup_old_files()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.warning(f"Upload attempt without file - IP: {client_ip}")
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning(f"Upload attempt with empty filename - IP: {client_ip}")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type upload: {file.filename} - IP: {client_ip}")
            return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400
        
        # Get parameters
        scalar = float(request.form.get('scalar', 1.0))
        
        # Validate scalar
        if scalar <= 0 or scalar > 1:
            return jsonify({'error': 'Scalar must be between 0 and 1'}), 400
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer after reading size
        
        logger.info(f"Processing started - File: {filename}, Size: {file_size/1024:.1f}KB, Scalar: {scalar}, IP: {client_ip}")
        
        # Save uploaded file
        upload_filename = f"{unique_id}_original.{file_ext}"
        upload_path = os.path.join(UPLOAD_FOLDER, upload_filename)
        file.save(upload_path)
        
        # Create display thumbnail for UI (480x720 portrait, 720x480 landscape)
        display_filename = f"{unique_id}_display.{file_ext}"
        display_path = os.path.join(DISPLAY_FOLDER, display_filename)
        was_resized = create_display_thumbnail(upload_path, display_path)
        
        logger.info(f"Created display thumbnail: {display_path}, exists: {os.path.exists(display_path)}")
        
        # Process the image
        logger.info(f"Starting image processing with GreyShift...")
        start_time = datetime.datetime.now()
        
        try:
            processor = GreyShift(
                filepath=upload_path,
                scalar=scalar
            )
            
            logger.info(f"GreyShift processor initialized, calling process_with_memory_optimization()...")
            # Process with memory optimization (resize for analysis, apply to original)
            output_path = processor.process_with_memory_optimization(max_dimension=3280)
            processing_time = (datetime.datetime.now() - start_time).total_seconds()
            
            logger.info(f"Processing completed in {processing_time:.2f}s, output: {output_path}")
            
        except Exception as proc_error:
            logger.error(f"Processing failed during GreyShift.process_with_memory_optimization(): {str(proc_error)}")
            raise
        
        # Move processed file to processed folder
        processed_filename = f"{unique_id}_processed.{file_ext}"
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        shutil.move(output_path, processed_path)
        
        logger.info(f"Processed file moved to: {processed_path}, exists: {os.path.exists(processed_path)}")
        
        # Get image info
        original_img = Image.open(upload_path)
        processed_img = Image.open(processed_path)
        
        logger.info(f"Processing completed - File: {filename}, Time: {processing_time:.2f}s, Original: {original_img.size}, IP: {client_ip}")
        
        # Create display thumbnail for processed image too
        processed_display_filename = f"{unique_id}_processed_display.{file_ext}"
        processed_display_path = os.path.join(DISPLAY_FOLDER, processed_display_filename)
        create_display_thumbnail(processed_path, processed_display_path)
        
        logger.info(f"Created processed display thumbnail: {processed_display_path}, exists: {os.path.exists(processed_display_path)}")
        
        # Generate absolute URLs for better compatibility
        original_url = url_for('serve_file', folder='display', filename=display_filename, _external=False)
        processed_url = url_for('serve_file', folder='display', filename=processed_display_filename, _external=False)
        download_url = url_for('download_file_with_original_name',
                              processed_filename=processed_filename,
                              original_filename=filename,
                              scalar=scalar,
                              _external=False)
        
        logger.info(f"Generated URLs - Original: {original_url}, Processed: {processed_url}, Download: {download_url}")
        
        result = {
            'success': True,
            'original_url': original_url,
            'processed_url': processed_url,
            'original_size': f"{original_img.size[0]}×{original_img.size[1]}",
            'processed_size': f"{processed_img.size[0]}×{processed_img.size[1]}",
            'scalar': scalar,
            'download_url': download_url
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Processing failed - File: {file.filename if 'file' in locals() else 'Unknown'}, Error: {str(e)}, IP: {client_ip}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/files/<folder>/<filename>')
def serve_file(folder, filename):
    """Serve uploaded or processed files."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    if folder not in ['uploads', 'processed', 'display']:
        logger.warning(f"Invalid folder access attempt: {folder} - IP: {client_ip}")
        return "Invalid folder", 404
    
    file_path = os.path.join(folder, filename)
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {folder}/{filename} - IP: {client_ip}")
        return "File not found", 404
    
    logger.info(f"File served: {folder}/{filename} - IP: {client_ip}")
    return send_file(file_path)

@app.route('/download/<processed_filename>/<original_filename>')
def download_file_with_original_name(processed_filename, original_filename):
    """Download processed file with original filename + _greyshift_scalar()."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    file_path = os.path.join(PROCESSED_FOLDER, processed_filename)
    if not os.path.exists(file_path):
        logger.warning(f"Download attempt for missing file: {processed_filename} - IP: {client_ip}")
        return "File not found", 404
    
    # Get scalar value from query parameters
    scalar = request.args.get('scalar', '1.0')
    
    # Create the new filename: original name + _greyshift_scalar(value) + extension
    name_parts = original_filename.rsplit('.', 1)
    if len(name_parts) == 2:
        new_filename = f"{name_parts[0]}_greyshift_scalar({scalar}).{name_parts[1]}"
    else:
        new_filename = f"{original_filename}_greyshift_scalar({scalar})"
    
    logger.info(f"File downloaded: {processed_filename} as {new_filename} - IP: {client_ip}")
    return send_file(file_path, as_attachment=True, download_name=new_filename)


@app.route('/download/<filename>')
def download_file(filename):
    """Legacy download route - for backward compatibility."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(file_path):
        logger.warning(f"Download attempt for missing file: {filename} - IP: {client_ip}")
        return "File not found", 404
    
    logger.info(f"File downloaded: {filename} - IP: {client_ip}")
    return send_file(file_path, as_attachment=True, 
                     download_name=f"greyshift_{filename}")

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Analyze image and return correction offsets for accurate preview."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.warning(f"Analysis attempt without file - IP: {client_ip}")
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning(f"Analysis attempt with empty filename - IP: {client_ip}")
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type for analysis: {file.filename} - IP: {client_ip}")
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        logger.info(f"Image analysis started - File: {file.filename} - IP: {client_ip}")
        
        # Save temporary file
        temp_filename = f"temp_analyze_{uuid.uuid4()}.jpg"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_path)
        
        try:
            # Analyze the image to get correction offsets (resize if needed for memory)
            processor = GreyShift(filepath=temp_path, scalar=1.0)
            
            # Load and check size
            original_img = Image.open(temp_path)
            if original_img.mode != 'RGB':
                original_img = original_img.convert('RGB')
            
            original_width, original_height = original_img.size
            max_dimension = max(original_width, original_height)
            
            if max_dimension > 3280:
                # Resize for analysis
                scale_factor = 3280 / max_dimension
                analysis_width = int(original_width * scale_factor)
                analysis_height = int(original_height * scale_factor)
                processor.img = original_img.resize((analysis_width, analysis_height), Image.Resampling.LANCZOS)
            else:
                processor.img = original_img
            
            processor.analyze_tonal_ranges()
            
            logger.info(f"Image analysis completed - File: {file.filename}, Offsets: R:{processor.red_avg_offset:.2f}, G:{processor.green_avg_offset:.2f}, B:{processor.blue_avg_offset:.2f} - IP: {client_ip}")
            
            # Return the calculated offsets (convert numpy types to Python floats for JSON)
            result = {
                'red_avg_offset': float(processor.red_avg_offset),
                'green_avg_offset': float(processor.green_avg_offset),
                'blue_avg_offset': float(processor.blue_avg_offset),
                'success': True
            }
            
            return jsonify(result), 200
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
                
    except Exception as e:
        logger.error(f"Analysis failed - File: {file.filename if 'file' in locals() else 'Unknown'}, Error: {str(e)} - IP: {client_ip}")
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint for Docker."""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.debug(f"Health check - IP: {client_ip}")
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    logger.info("Starting greyShift Flask application in standalone mode")
    app.run(debug=False, host='0.0.0.0', port=5000)