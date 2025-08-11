"""
BubbleTea component classes for building rich chatbot responses
"""

from typing import List, Literal, Optional, Union
from pydantic import BaseModel


class Text(BaseModel):
    """A text component for displaying plain text messages"""
    type: Literal["text"] = "text"
    content: str

    def __init__(self, content: str):
        super().__init__(content=content)


class Image(BaseModel):
    """An image component for displaying images"""
    type: Literal["image"] = "image"
    url: str
    alt: Optional[str] = None
    content: Optional[str] = None

    def __init__(self, url: str, alt: Optional[str] = None, content: Optional[str] = None):
        super().__init__(url=url, alt=alt, content=content)


class Markdown(BaseModel):
    """A markdown component for rich text formatting"""
    type: Literal["markdown"] = "markdown"
    content: str

    def __init__(self, content: str):
        super().__init__(content=content)


class Card(BaseModel):
    """A single card component for displaying an image"""
    type: Literal["card"] = "card"
    image: Image
    text: Optional[str] = None
    markdown: Optional[Markdown] = None
    card_value: Optional[str] = None

    def __init__(self, image: Image, text: Optional[str] = None, markdown: Optional[Markdown] = None, card_value: Optional[str] = None):
        super().__init__(image=image, text=text, markdown=markdown, card_value=card_value)


class Cards(BaseModel):
    """A cards component for displaying multiple cards in a layout"""
    type: Literal["cards"] = "cards"
    orient: Literal["wide", "tall"] = "wide"
    cards: List[Card]

    def __init__(self, cards: List[Card], orient: Literal["wide", "tall"] = "wide"):
        super().__init__(cards=cards, orient=orient)


class Done(BaseModel):
    """A done component to signal end of streaming"""
    type: Literal["done"] = "done"


class Pill(BaseModel):
    """A single pill component for displaying text"""
    type: Literal["pill"] = "pill"
    text: str
    pill_value: Optional[str] = None

    def __init__(self, text: str, pill_value: Optional[str] = None):
        super().__init__(text=text, pill_value=pill_value)


class Pills(BaseModel):
    """A pills component for displaying multiple pill items in a layout"""
    type: Literal["pills"] = "pills"
    pills: List[Pill]

    def __init__(self, pills: List[Pill]):
        super().__init__(pills=pills)


class Video(BaseModel):
    """A video component for displaying video content"""
    type: Literal["video"] = "video"
    url: str

    def __init__(self, url: str):
        super().__init__(url=url)


class Block(BaseModel):
    """A block component to indicate long-running operations"""
    type: Literal["block"] = "block"
    timeout: int = 60  # seconds, default 60

    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)


class Error(BaseModel):
    """An error component for displaying error messages"""
    type: Literal["error"] = "error"
    title: str
    description: Optional[str] = None
    code: Optional[str] = None

    def __init__(self, title: str, description: Optional[str] = None, code: Optional[str] = None):
        super().__init__(title=title, description=description, code=code)


# Type alias for all components
Component = Union[Text, Image, Markdown, Card, Cards, Done, Pill, Pills, Video, Block, Error]


class BaseComponent(BaseModel):
    """A unified wrapper for any component, with metadata like thread_id"""
    thread_id: Optional[str] = None
    payload: List[Component]
    
    def __init__(self, payload: Component, thread_id: Optional[str] = None):
        super().__init__(payload=payload, thread_id=thread_id)
