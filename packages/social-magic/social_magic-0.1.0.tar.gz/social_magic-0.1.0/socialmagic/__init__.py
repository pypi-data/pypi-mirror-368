"""
SocialMagic - A Python library for social media content enhancement

Features:
- Text sentiment to emoji conversion
- Fake/manipulated image detection
- Micro story generation
"""

from .emojify import emojify
from .fakebuster import is_similar
from .storygen import generate_story

__version__ = "0.1.0"
__author__ = "SocialMagic Team"

__all__ = ["emojify", "is_similar", "generate_story"]
