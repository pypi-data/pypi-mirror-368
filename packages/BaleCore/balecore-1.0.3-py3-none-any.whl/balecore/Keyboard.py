from typing import Optional, Any

class Keyboard:
    """
    A class representing a keyboard entity with text, URL, and query capabilities.
    
    Attributes:
        text (str): The display text for the keyboard item.
        url (str, optional): A URL associated with the keyboard item. Defaults to None.
        query (str, optional): A search query associated with the keyboard item. Defaults to None.
        copy_text (str, optional): A text to be copied when the button is clicked. Defaults to None.
    """
    
    def __init__(
        self,
        text: str,
        url: Optional[str] = None,
        query: Optional[str] = None,
        copy_text: Optional[str] = None,
    ) -> None:
        """
        Initialize the Keyboard instance.
        
        Args:
            text (str): The display text for the keyboard item.
            url (str, optional): A URL associated with the keyboard item. Defaults to None.
            query (str, optional): A search query associated with the keyboard item. Defaults to None.
            copy_text (str, optional): A text to be copied when the button is clicked. Defaults to None.
            
        Raises:
            ValueError: If text is empty or not a string.
        """
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        if not text.strip():
            raise ValueError("Text cannot be empty")
            
        self.text = text.strip()
        self.url = url
        self.query = query
        self.copy_text = copy_text

    def __repr__(self) -> str:
        """Return a string representation of the Keyboard instance."""
        return f"Keyboard(text='{self.text}', url={self.url}, query={self.query}, copy_text={self.copy_text})"

    def __eq__(self, other: Any) -> bool:
        """Compare two Keyboard instances for equality."""
        if not isinstance(other, Keyboard):
            return False
        return (
            self.text == other.text
            and self.url == other.url
            and self.query == other.query
            and self.copy_text == other.copy_text
        )