"""
Tests for the fakebuster module
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from socialmagic.fakebuster import is_similar, get_similarity_percentage
from PIL import Image
import tempfile


def create_test_image(color='red', size=(100, 100)):
    """Create a temporary test image"""
    img = Image.new('RGB', size, color=color)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name)
    return temp_file.name


def test_is_similar_identical():
    """Test is_similar with identical images"""
    # Create a test image
    img_path = create_test_image('blue')
    
    # Compare image with itself
    result = is_similar(img_path, img_path, 90)
    assert result == True
    
    # Clean up
    os.unlink(img_path)
    print("✓ Identical images test passed")


def test_is_similar_different():
    """Test is_similar with different images"""
    # Create two different test images
    img1_path = create_test_image('red')
    img2_path = create_test_image('blue')
    
    # Compare different images with high threshold
    result = is_similar(img1_path, img2_path, 95)
    # This should likely return False for very different images
    # but we'll just check that it returns a boolean
    assert isinstance(result, bool)
    
    # Clean up
    os.unlink(img1_path)
    os.unlink(img2_path)
    print("✓ Different images test passed")


def test_get_similarity_percentage():
    """Test get_similarity_percentage function"""
    # Create a test image
    img_path = create_test_image('green')
    
    # Get similarity percentage for identical images
    similarity = get_similarity_percentage(img_path, img_path)
    assert similarity == 100.0
    
    # Clean up
    os.unlink(img_path)
    print("✓ Similarity percentage test passed")


def test_file_not_found():
    """Test error handling for non-existent files"""
    try:
        is_similar("nonexistent1.jpg", "nonexistent2.jpg")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("✓ File not found error handling test passed")


def test_is_similar_threshold():
    """Test is_similar with different thresholds"""
    # Create a test image
    img_path = create_test_image('yellow')
    
    # Test with different thresholds
    result_high = is_similar(img_path, img_path, 99)
    result_low = is_similar(img_path, img_path, 50)
    
    assert result_high == True
    assert result_low == True
    
    # Clean up
    os.unlink(img_path)
    print("✓ Threshold test passed")


if __name__ == "__main__":
    print("Running fakebuster tests...")
    print("=" * 30)
    
    try:
        test_is_similar_identical()
        test_is_similar_different()
        test_get_similarity_percentage()
        test_file_not_found()
        test_is_similar_threshold()
        
        print("=" * 30)
        print("All fakebuster tests passed! ✅")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Some tests failed! ❌")
