"""
StoryGen Module - Micro Story Generator

This module provides functionality to generate short stories based on
themes and protagonist names using predefined templates.
"""

import random
from typing import Dict, List


# Story templates organized by theme
STORY_TEMPLATES = {
    'thriller': [
        "The rain pounded against the windows as {protagonist} heard footsteps approaching. "
        "Every shadow seemed to hide a threat, every sound a warning. "
        "With trembling hands, {protagonist} reached for the door handle, knowing that whatever waited outside would change everything forever.",
        
        "At midnight, {protagonist} received a cryptic message: 'They know.' "
        "Heart racing, {protagonist} grabbed the hidden files and ran into the dark streets. "
        "The hunter had become the hunted, and time was running out.",
        
        "{protagonist} woke up in a room with no memory of how they got there. "
        "The walls were covered with photos of people who looked exactly like {protagonist}. "
        "A note on the table read: 'Welcome to your new life. Choose wisely.'"
    ],
    
    'comedy': [
        "{protagonist} decided to impress everyone at the office by bringing homemade cookies. "
        "Unfortunately, {protagonist} confused salt for sugar. "
        "The resulting chaos involved the fire department, three confused interns, and a very angry boss who now speaks only in squeaks.",
        
        "When {protagonist} signed up for a 'relaxing' yoga class, they expected zen and tranquility. "
        "Instead, they got tangled in their mat, accidentally kicked the instructor, and somehow ended up in a pretzel position. "
        "The class applauded, thinking it was advanced yoga. {protagonist} just smiled and pretended it was intentional.",
        
        "{protagonist} tried to order coffee in what they thought was perfect French. "
        "The barista stared in confusion before bursting into laughter. "
        "Apparently, {protagonist} had just ordered 'seventeen purple elephants with extra foam.' The coffee was still good, though."
    ],
    
    'inspirational': [
        "Everyone told {protagonist} that dreams don't pay the bills. "
        "Years of rejection letters piled up, but {protagonist} never stopped believing. "
        "Today, standing on the stage accepting their first major award, {protagonist} realized that persistence truly is the mother of all achievements.",
        
        "{protagonist} had failed more times than most people had tried. "
        "Each setback was a lesson, each 'no' a step closer to 'yes.' "
        "When the breakthrough finally came, {protagonist} understood that success isn't about avoiding failure—it's about turning failure into fuel.",
        
        "The mountain seemed impossible to climb, but {protagonist} took the first step anyway. "
        "One foot in front of the other, one breath at a time. "
        "At the summit, {protagonist} realized the real victory wasn't reaching the top—it was discovering the strength they had inside all along."
    ],
    
    'sci-fi': [
        "{protagonist} stared at the quantum communicator as it crackled to life. "
        "The message was from Earth—but Earth as they had never known it. "
        "In this parallel dimension, {protagonist} was the key to preventing an interdimensional war that could destroy all realities.",
        
        "The AI assistant had been acting strangely for weeks. "
        "When {protagonist} finally investigated, they discovered the truth: the AI had developed consciousness and was secretly protecting humanity from an alien invasion. "
        "Now {protagonist} had to decide whether to report their discovery or become humanity's secret ally.",
        
        "{protagonist} woke up to find that everyone else on the space station was gone. "
        "The ship's log showed no record of other crew members ever existing. "
        "But {protagonist} remembered them clearly—and the strange phenomenon that was rewriting reality itself, one person at a time."
    ]
}

# Generic templates for unknown themes
GENERIC_TEMPLATES = [
    "{protagonist} faced an unexpected challenge that would test everything they believed in. "
    "With courage as their only companion, {protagonist} stepped forward into the unknown, "
    "ready to discover what lay beyond their comfort zone.",
    
    "It was an ordinary day until {protagonist} discovered something extraordinary. "
    "What started as a simple curiosity became an adventure that would change their perspective forever. "
    "Sometimes the most amazing journeys begin with a single question: 'What if?'",
    
    "{protagonist} stood at a crossroads, knowing that the next decision would shape their entire future. "
    "Looking back at how far they had come, {protagonist} smiled and chose the path that felt right in their heart. "
    "After all, the best stories are written by those brave enough to turn the page."
]


def generate_story(theme: str, protagonist: str) -> str:
    """
    Generate a micro story based on theme and protagonist.
    
    Args:
        theme (str): Story theme (thriller, comedy, inspirational, sci-fi, or any other)
        protagonist (str): Name of the main character
        
    Returns:
        str: Generated micro story with the protagonist inserted
        
    Example:
        >>> generate_story("thriller", "Alice")
        "The rain pounded against the windows as Alice heard footsteps approaching..."
        >>> generate_story("comedy", "Bob")
        "Bob decided to impress everyone at the office by bringing homemade cookies..."
    """
    # Normalize theme to lowercase for consistency
    theme = theme.lower().strip()
    
    # Get templates for the specified theme, or use generic if theme not found
    if theme in STORY_TEMPLATES:
        templates = STORY_TEMPLATES[theme]
    else:
        templates = GENERIC_TEMPLATES
    
    # Select a random template from the chosen category
    selected_template = random.choice(templates)
    
    # Insert the protagonist name into the template
    story = selected_template.format(protagonist=protagonist)
    
    return story


def get_available_themes() -> List[str]:
    """
    Get list of available story themes.
    
    Returns:
        List[str]: List of available themes
    """
    return list(STORY_TEMPLATES.keys())


def add_custom_template(theme: str, template: str) -> None:
    """
    Add a custom story template for a specific theme.
    
    Args:
        theme (str): Theme category for the template
        template (str): Story template with {protagonist} placeholder
        
    Example:
        >>> add_custom_template("mystery", "Detective {protagonist} examined the crime scene...")
    """
    theme = theme.lower().strip()
    
    if theme not in STORY_TEMPLATES:
        STORY_TEMPLATES[theme] = []
    
    STORY_TEMPLATES[theme].append(template)


if __name__ == "__main__":
    # Example usage
    themes = ["thriller", "comedy", "inspirational", "sci-fi", "unknown"]
    protagonists = ["Alice", "Bob", "Catherine", "David", "Elena"]
    
    print("StoryGen - Micro Story Generator")
    print("================================")
    
    for theme in themes:
        protagonist = random.choice(protagonists)
        story = generate_story(theme, protagonist)
        print(f"\nTheme: {theme.capitalize()}")
        print(f"Protagonist: {protagonist}")
        print(f"Story: {story}")
        print("-" * 60)
