from app.services.story_generator import StoryGenerator
from app.services.image_generator import ImageGenerator

# Create singleton instances
story_generator = StoryGenerator()
image_generator = ImageGenerator()

# Re-export services
__all__ = ["story_generator", "image_generator"] 