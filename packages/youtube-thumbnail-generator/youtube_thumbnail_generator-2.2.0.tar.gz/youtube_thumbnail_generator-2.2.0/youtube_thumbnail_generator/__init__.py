"""
YouTube Thumbnail Generator v2.2

A professional YouTube thumbnail generation library with three theme modes, intelligent Chinese/English 
text processing, smart line-breaking algorithms, and full color customization.

Features:
- Three Theme Modes: Dark, Light, Custom with automatic color defaults
- Full Color Customization: title_color, author_color parameters with hex support
- Dynamic Font Scaling: Auto-scaling based on text length (1-17 characters)
- Triangle Control: enable_triangle parameter for overlay management
- Custom Background Support: Use your own 1600x900 templates
- Chinese/English Optimization: 30% larger fonts for Chinese, optimal lengths guidance
- Smart Line-breaking: 9 chars for Chinese titles, intelligent English wrapping
- Professional Templates: All templates included automatically in package

Basic Usage:
    from youtube_thumbnail_generator import FinalThumbnailGenerator
    
    generator = FinalThumbnailGenerator("templates/professional_template.jpg")
    result = generator.generate_final_thumbnail(
        title="Your Amazing Title",
        author="Your Name", 
        theme="dark",  # "dark", "light", or "custom"
        title_color="#FFFFFF",  # Custom colors
        output_path="output.jpg"
    )
"""

__version__ = "2.2.0"
__author__ = "Leo Wang"
__email__ = "leo@example.com"
__license__ = "MIT"

# Import main classes and functions
from .final_thumbnail_generator import FinalThumbnailGenerator
from .text_png_generator import create_text_png
from .function_add_chapter import add_chapter_to_image

# Define what gets imported with "from youtube_thumbnail_generator import *"
__all__ = [
    'FinalThumbnailGenerator',
    'create_text_png', 
    'add_chapter_to_image',
    '__version__'
]