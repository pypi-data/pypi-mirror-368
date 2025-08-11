"""
FakeBuster Module - Fake/Manipulated Image Detection

This module provides functionality to detect similarity between images
using perceptual hashing to identify potential fake or manipulated images.
"""

import imagehash
from PIL import Image
from typing import Union
import os


def is_similar(img_path1: str, img_path2: str, threshold: int = 90) -> bool:
    """
    Compare two images for similarity using perceptual hashing.
    
    Args:
        img_path1 (str): Path to the first image
        img_path2 (str): Path to the second image
        threshold (int): Similarity threshold percentage (0-100)
        
    Returns:
        bool: True if images are similar (>= threshold), False otherwise
        
    Raises:
        FileNotFoundError: If either image file doesn't exist
        Exception: If images cannot be processed
        
    Example:
        >>> is_similar("image1.jpg", "image2.jpg", 85)
        True
        >>> is_similar("different1.jpg", "different2.jpg", 90)
        False
    """
    # Check if both image files exist
    if not os.path.exists(img_path1):
        raise FileNotFoundError(f"Image file not found: {img_path1}")
    if not os.path.exists(img_path2):
        raise FileNotFoundError(f"Image file not found: {img_path2}")
    
    try:
        # Open and compute perceptual hashes for both images
        with Image.open(img_path1) as img1:
            hash1 = imagehash.phash(img1)
        
        with Image.open(img_path2) as img2:
            hash2 = imagehash.phash(img2)
        
        # Calculate hash difference (lower = more similar)
        hash_diff = hash1 - hash2
        
        # Convert to similarity percentage
        # Maximum possible hash difference for phash is 64 (8x8 hash)
        max_diff = 64
        similarity_percentage = ((max_diff - hash_diff) / max_diff) * 100
        
        # Return True if similarity meets or exceeds threshold
        return similarity_percentage >= threshold
        
    except Exception as e:
        raise Exception(f"Error processing images: {str(e)}")


def get_similarity_percentage(img_path1: str, img_path2: str) -> float:
    """
    Get the exact similarity percentage between two images.
    
    Args:
        img_path1 (str): Path to the first image
        img_path2 (str): Path to the second image
        
    Returns:
        float: Similarity percentage (0.0 to 100.0)
        
    Example:
        >>> get_similarity_percentage("image1.jpg", "image2.jpg")
        87.5
    """
    # Check if both image files exist
    if not os.path.exists(img_path1):
        raise FileNotFoundError(f"Image file not found: {img_path1}")
    if not os.path.exists(img_path2):
        raise FileNotFoundError(f"Image file not found: {img_path2}")
    
    try:
        # Open and compute perceptual hashes for both images
        with Image.open(img_path1) as img1:
            hash1 = imagehash.phash(img1)
        
        with Image.open(img_path2) as img2:
            hash2 = imagehash.phash(img2)
        
        # Calculate hash difference
        hash_diff = hash1 - hash2
        
        # Convert to similarity percentage
        max_diff = 64
        similarity_percentage = ((max_diff - hash_diff) / max_diff) * 100
        
        return round(similarity_percentage, 2)
        
    except Exception as e:
        raise Exception(f"Error processing images: {str(e)}")


if __name__ == "__main__":
    # Example usage (requires actual image files)
    print("FakeBuster Image Similarity Detection")
    print("====================================")
    print("This module compares images using perceptual hashing.")
    print("Use is_similar(img1, img2, threshold) to detect similar images.")
    print("Use get_similarity_percentage(img1, img2) for exact similarity score.")
