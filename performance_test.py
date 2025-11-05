#!/usr/bin/env python3
"""
Performance comparison test for greyShift optimizations.
Creates a simple test image and measures processing time.
"""

import time
import numpy as np
from PIL import Image
import tempfile
import os
from greyshift import GreyShift

def create_test_image(width=1000, height=1000):
    """Create a test image with color cast for performance testing."""
    # Create a gradient image with some color cast
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradients with slight color casts
    for y in range(height):
        for x in range(width):
            # Base brightness
            brightness = int(255 * (x + y) / (width + height))
            
            # Add color cast
            img_array[y, x, 0] = min(255, brightness + 30)  # Red cast
            img_array[y, x, 1] = max(0, min(255, brightness - 10))  # Less green
            img_array[y, x, 2] = min(255, brightness + 20)  # Blue cast
    
    return Image.fromarray(img_array)

def benchmark_greyshift(image_path, test_name, width=None, height=None):
    """Benchmark the greyShift processing."""
    print(f"\n{test_name}")
    print("-" * 50)
    
    # Time the processing
    start_time = time.time()
    
    try:
        processor = GreyShift(
            filepath=image_path,
            width=width,
            height=height,
            scalar=0.8
        )
        
        load_time = time.time()
        processor.load_and_resize_image()
        
        analyze_time = time.time()
        processor.analyze_tonal_ranges()
        
        correct_time = time.time()
        processor.apply_correction()
        
        end_time = time.time()
        
        # Calculate times
        total_time = end_time - start_time
        load_duration = analyze_time - load_time
        analyze_duration = correct_time - analyze_time
        correct_duration = end_time - correct_time
        
        print(f"Total processing time: {total_time:.3f} seconds")
        print(f"  - Loading/resizing: {load_duration:.3f} seconds")
        print(f"  - Tonal analysis: {analyze_duration:.3f} seconds")
        print(f"  - Color correction: {correct_duration:.3f} seconds")
        
        return total_time
        
    except Exception as e:
        print(f"Error during processing: {e}")
        return None

def main():
    """Run performance benchmarks."""
    print("greyShift Performance Test")
    print("=" * 50)
    
    # Create test images of different sizes
    test_sizes = [
        (500, 500, "Small Image (500x500)"),
        (1000, 1000, "Medium Image (1000x1000)"),
        (2000, 1000, "Large Image (2000x1000)")
    ]
    
    results = {}
    
    for width, height, name in test_sizes:
        # Create test image
        print(f"\nCreating {name}...")
        test_img = create_test_image(width, height)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            test_img.save(tmp_file.name, 'JPEG', quality=95)
            tmp_path = tmp_file.name
        
        try:
            # Run benchmark
            processing_time = benchmark_greyshift(tmp_path, name)
            if processing_time:
                pixels = width * height
                results[name] = {
                    'time': processing_time,
                    'pixels': pixels,
                    'pixels_per_second': pixels / processing_time
                }
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
    
    # Print summary
    print("\n" + "=" * 50)
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    
    for name, data in results.items():
        print(f"{name}:")
        print(f"  Processing Time: {data['time']:.3f} seconds")
        print(f"  Pixels Processed: {data['pixels']:,}")
        print(f"  Performance: {data['pixels_per_second']:,.0f} pixels/second")
        print()

if __name__ == "__main__":
    main()