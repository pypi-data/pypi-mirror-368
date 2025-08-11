# simpleslug/simpleslug.py
import re

def slugify(text: str) -> str:
    """
    Convert a string into a URL-friendly slug.
    
    Example:
        slugify("Hello World!") -> "hello-world"
    """
    # Lowercase the text
    text = text.lower()
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text
