import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from .exceptions import DiscordEmbedException


class DiscordEmbed:
    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[int] = None,
        url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.title = title
        self.description = description
        self.color = color
        self.url = url
        self.timestamp = timestamp
        self.author = {}
        self.footer = {}
        self.thumbnail = {}
        self.image = {}
        self.fields = []

    def set_author(
        self, name: str, url: Optional[str] = None, icon_url: Optional[str] = None
    ) -> "DiscordEmbed":
        self.author = {"name": name}
        if url:
            self.author["url"] = url
        if icon_url:
            self.author["icon_url"] = icon_url
        return self

    def set_footer(
        self, text: str, icon_url: Optional[str] = None
    ) -> "DiscordEmbed":
        self.footer = {"text": text}
        if icon_url:
            self.footer["icon_url"] = icon_url
        return self

    def set_thumbnail(self, url: str) -> "DiscordEmbed":
        self.thumbnail = {"url": url}
        return self

    def set_image(self, url: str) -> "DiscordEmbed":
        self.image = {"url": url}
        return self

    def add_embed_field(
        self, name: str, value: str, inline: bool = False
    ) -> "DiscordEmbed":
        if len(self.fields) >= 25:
            raise DiscordEmbedException("Maximum 25 fields allowed per embed")
        
        self.fields.append({
            "name": name,
            "value": value,
            "inline": inline
        })
        return self

    def set_timestamp(self, timestamp: Optional[datetime] = None) -> "DiscordEmbed":
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp.isoformat()
        return self

    def to_dict(self) -> Dict[str, Any]:
        embed_dict = {}
        
        if self.title:
            embed_dict["title"] = self.title
        if self.description:
            embed_dict["description"] = self.description
        if self.color:
            embed_dict["color"] = self.color
        if self.url:
            embed_dict["url"] = self.url
        if self.timestamp:
            embed_dict["timestamp"] = self.timestamp
        if self.author:
            embed_dict["author"] = self.author
        if self.footer:
            embed_dict["footer"] = self.footer
        if self.thumbnail:
            embed_dict["thumbnail"] = self.thumbnail
        if self.image:
            embed_dict["image"] = self.image
        if self.fields:
            embed_dict["fields"] = self.fields
            
        return embed_dict

    def __repr__(self) -> str:
        return f"<DiscordEmbed title='{self.title}' description='{self.description}'>"
