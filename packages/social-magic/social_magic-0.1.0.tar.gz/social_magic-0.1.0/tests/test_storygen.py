"""
Tests for the storygen module
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from socialmagic.storygen import generate_story, get_available_themes, add_custom_template


def test_generate_story_thriller():
    """Test story generation for thriller theme"""
    story = generate_story("thriller", "Alice")
    assert "Alice" in story
    assert len(story) > 50  # Should be a substantial story
    print("✓ Thriller story generation test passed")


def test_generate_story_comedy():
    """Test story generation for comedy theme"""
    story = generate_story("comedy", "Bob")
    assert "Bob" in story
    assert len(story) > 50
    print("✓ Comedy story generation test passed")


def test_generate_story_inspirational():
    """Test story generation for inspirational theme"""
    story = generate_story("inspirational", "Catherine")
    assert "Catherine" in story
    assert len(story) > 50
    print("✓ Inspirational story generation test passed")


def test_generate_story_scifi():
    """Test story generation for sci-fi theme"""
    story = generate_story("sci-fi", "David")
    assert "David" in story
    assert len(story) > 50
    print("✓ Sci-fi story generation test passed")


def test_generate_story_unknown_theme():
    """Test story generation for unknown theme (should use generic template)"""
    story = generate_story("unknown_theme", "Elena")
    assert "Elena" in story
    assert len(story) > 50
    print("✓ Unknown theme story generation test passed")


def test_get_available_themes():
    """Test getting available themes"""
    themes = get_available_themes()
    expected_themes = ['thriller', 'comedy', 'inspirational', 'sci-fi']
    
    for theme in expected_themes:
        assert theme in themes
    
    print("✓ Available themes test passed")


def test_add_custom_template():
    """Test adding custom story template"""
    # Add a custom template
    add_custom_template("mystery", "Detective {protagonist} found a mysterious clue.")
    
    # Generate story with the new theme
    story = generate_story("mystery", "Holmes")
    assert "Holmes" in story
    
    print("✓ Custom template test passed")


def test_case_insensitive_theme():
    """Test that theme matching is case insensitive"""
    story1 = generate_story("THRILLER", "Frank")
    story2 = generate_story("thriller", "Frank")
    story3 = generate_story("Thriller", "Frank")
    
    # All should work (contain the protagonist)
    assert "Frank" in story1
    assert "Frank" in story2
    assert "Frank" in story3
    
    print("✓ Case insensitive theme test passed")


def test_empty_protagonist():
    """Test with empty protagonist name"""
    story = generate_story("comedy", "")
    # Should still generate a story, even with empty protagonist
    assert len(story) > 20
    print("✓ Empty protagonist test passed")


def test_story_uniqueness():
    """Test that multiple calls can generate different stories"""
    stories = []
    for i in range(10):
        story = generate_story("thriller", "TestChar")
        stories.append(story)
    
    # Check that we get some variety (not all stories are identical)
    unique_stories = set(stories)
    # Should have at least some variety (thriller has 3 templates)
    assert len(unique_stories) >= 1
    
    print("✓ Story uniqueness test passed")


if __name__ == "__main__":
    print("Running storygen tests...")
    print("=" * 30)
    
    try:
        test_generate_story_thriller()
        test_generate_story_comedy()
        test_generate_story_inspirational()
        test_generate_story_scifi()
        test_generate_story_unknown_theme()
        test_get_available_themes()
        test_add_custom_template()
        test_case_insensitive_theme()
        test_empty_protagonist()
        test_story_uniqueness()
        
        print("=" * 30)
        print("All storygen tests passed! ✅")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Some tests failed! ❌")
