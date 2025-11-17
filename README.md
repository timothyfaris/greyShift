# greyShift - Python Version

A Python port of the original Processing sketch for removing color casts from images through tonal analysis and correction.

## Features

- Analyzes images in different tonal ranges (low, mid, high)
- Calculates color offsets to neutralize color casts
- Applies corrections with adjustable intensity (scalar)
- Supports common image formats (JPEG, PNG, TIFF, etc.)
- Command-line interface with flexible options

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python greyshift.py --filepath your_image.jpg
```

### With Custom Scalar (Correction Intensity)
```bash
python greyshift.py --filepath your_image.jpg --scalar 0.8
```

### With Custom Dimensions
```bash
python greyshift.py --filepath your_image.jpg --w 1920 --h 1080 --scalar 0.5
```

## Command Line Arguments

- `--filepath`: **Required** - Path to the input image file
- `--w`, `--width`: Optional - Target width for processing
- `--h`, `--height`: Optional - Target height for processing  
- `--scalar`: Optional - Correction intensity (0.0 to 1.0, default: 1.0)

## How It Works

The application:

1. **Loads** the input image
2. **Analyzes** pixels in different tonal ranges to identify neutral areas
3. **Calculates** color offsets by comparing actual colors to expected neutral values
4. **Applies** corrections to remove color casts
5. **Saves** the corrected image with a descriptive filename

The output filename will be: `original_name_shifted_scalar(value).extension`

## Examples

```bash
# Light correction
python greyshift.py --filepath sunset.jpg --scalar 0.3

# Medium correction
python greyshift.py --filepath portrait.jpg --scalar 0.7

# Full correction
python greyshift.py --filepath landscape.jpg --scalar 1.0

# Resize and correct
python greyshift.py --filepath large_image.jpg --w 1200 --h 800 --scalar 0.6
```

## Technical Notes

- The algorithm analyzes pixels in the mid-tone range (119-139 brightness levels)
- Color offsets are calculated relative to neutral values (64, 129, 193 for low, mid, high tones)
- The scalar parameter controls how much of the calculated correction is applied
- Images are processed in RGB color space

## Differences from Original Processing Version

- Enhanced error handling and validation
- More flexible command-line interface
- Improved performance using NumPy arrays
- Better code organization and documentation
- Support for different image formats and resizing options

## Changelog

### Major Performance Optimization and Feature Enhancements (November 2025)

**Performance Improvements:**
- Implemented vectorized NumPy operations for 10-50x performance improvement
- Core algorithm now processes 10.8M-16.7M pixels/second
- Vectorized `analyze_tonal_ranges()` method using boolean masking
- Eliminated Python loops in favor of NumPy array operations
- Maintained full functionality while achieving massive speed gains

**Feature Enhancements:**
- Added smart thumbnail sizing: 480x720 for portrait, 720x480 for landscape
- Increased upload limit to 64MB for larger image processing
- Preserved original filenames with '_greyshift' suffix and EXIF metadata
- Enhanced UI with dynamic canvas sizing based on image orientation
- Added comprehensive Docker support with multi-stage builds
- Created performance testing suite and optimization documentation
- Improved error handling and user feedback throughout application
- Added proper .gitignore to exclude virtual environments and cache files