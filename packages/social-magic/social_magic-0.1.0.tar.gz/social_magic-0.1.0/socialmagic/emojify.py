"""
Emojify Module - Text Sentiment to Emoji Converter

This module provides functionality to analyze text sentiment and append
appropriate emojis based on the sentiment score.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random
from typing import Dict, List, Optional


def emojify(text: str, emoji_map: Optional[Dict[str, List[str]]] = None) -> str:
    """
    Analyze text sentiment and append appropriate emoji.
    
    Args:
        text (str): The input text to analyze
        emoji_map (dict, optional): Custom emoji mapping for sentiments
        
    Returns:
        str: Original text with appended emoji based on sentiment
        
    Example:
        >>> emojify("I love this product!")
        "I love this product! 😍"
        >>> emojify("This is terrible")
        "This is terrible 😢"
    """
    # Default emoji mapping
    default_emoji_map = {
        'positive': ['😍', '🚀', '😊'],
        'negative': ['😢', '😡', '👎'],
        'neutral': ['😐']
    }
    
    # Use custom emoji map if provided, otherwise use default
    emoji_mapping = emoji_map if emoji_map else default_emoji_map
    
    # Initialize VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()
    
    # Get sentiment scores
    scores = analyzer.polarity_scores(text)
    compound_score = scores['compound']
    
    # Determine sentiment category
    if compound_score >= 0.05:
        sentiment_category = 'positive'
    elif compound_score <= -0.05:
        sentiment_category = 'negative'
    else:
        sentiment_category = 'neutral'
    
    # Select random emoji from the appropriate category
    emoji_list = emoji_mapping.get(sentiment_category, ['😐'])
    selected_emoji = random.choice(emoji_list)
    
    # Return text with appended emoji
    return f"{text} {selected_emoji}"


if __name__ == "__main__":
    # Example usage
    test_texts = [
        "I absolutely love this!",
        "This is the worst thing ever.",
        "It's okay, nothing special.",
        "Amazing work, fantastic job!",
        "I hate this so much."
    ]
    
    for text in test_texts:
        result = emojify(text)
        print(f"Original: {text}")
        print(f"Emojified: {result}")
        print("-" * 40)
