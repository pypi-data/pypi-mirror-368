"""
Tests for the emojify module
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from socialmagic.emojify import emojify


def test_emojify_positive():
    """Test emojify with positive sentiment"""
    result = emojify("I love this!")
    assert "I love this!" in result
    assert any(emoji in result for emoji in ['😍', '🚀', '😊'])
    print("✓ Positive sentiment test passed")


def test_emojify_negative():
    """Test emojify with negative sentiment"""
    result = emojify("This is terrible")
    assert "This is terrible" in result
    assert any(emoji in result for emoji in ['😢', '😡', '👎'])
    print("✓ Negative sentiment test passed")


def test_emojify_neutral():
    """Test emojify with neutral sentiment"""
    result = emojify("The book has 200 pages")
    assert "The book has 200 pages" in result
    assert '😐' in result
    print("✓ Neutral sentiment test passed")


def test_emojify_custom_emoji_map():
    """Test emojify with custom emoji mapping"""
    custom_map = {
        'positive': ['🎉'],
        'negative': ['💀'],
        'neutral': ['🤔']
    }
    result = emojify("I love this!", custom_map)
    assert "🎉" in result
    print("✓ Custom emoji map test passed")


def test_emojify_empty_text():
    """Test emojify with empty text"""
    result = emojify("")
    assert len(result) > 0  # Should at least have an emoji
    print("✓ Empty text test passed")


if __name__ == "__main__":
    print("Running emojify tests...")
    print("=" * 30)
    
    try:
        test_emojify_positive()
        test_emojify_negative()
        test_emojify_neutral()
        test_emojify_custom_emoji_map()
        test_emojify_empty_text()
        
        print("=" * 30)
        print("All emojify tests passed! ✅")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Some tests failed! ❌")
