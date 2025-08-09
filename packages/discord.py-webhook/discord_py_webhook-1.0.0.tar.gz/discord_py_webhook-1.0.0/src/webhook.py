import json
import requests
import aiohttp
from typing import Optional, List, Dict, Any, Union
from .embed import DiscordEmbed
from .exceptions import DiscordWebhookException, DiscordFileException


class DiscordWebhook:
    def __init__(
        self,
        url: str,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        content: Optional[str] = None,
        embeds: Optional[List[DiscordEmbed]] = None,
    ):
        self.url = url
        self.username = username
        self.avatar_url = avatar_url
        self.content = content
        self.embeds = embeds or []
        self.files = []

    def add_embed(self, embed: DiscordEmbed) -> "DiscordWebhook":
        if len(self.embeds) >= 10:
            raise DiscordWebhookException("Maximum 10 embeds allowed per webhook")
        self.embeds.append(embed)
        return self

    def add_file(self, file: bytes, filename: str) -> "DiscordWebhook":
        if len(self.files) >= 10:
            raise DiscordWebhookException("Maximum 10 files allowed per webhook")
        
        if len(file) > 25 * 1024 * 1024:
            raise DiscordFileException("File size exceeds 25MB limit")
            
        self.files.append({"file": file, "filename": filename})
        return self

    def clear_embeds(self) -> "DiscordWebhook":
        self.embeds.clear()
        return self

    def clear_files(self) -> "DiscordWebhook":
        self.files.clear()
        return self

    def _prepare_payload(self) -> Dict[str, Any]:
        payload = {}
        
        if self.content:
            payload["content"] = self.content
        if self.username:
            payload["username"] = self.username
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url
        if self.embeds:
            payload["embeds"] = [embed.to_dict() for embed in self.embeds]
            
        return payload

    def execute(self) -> requests.Response:
        if not self.content and not self.embeds and not self.files:
            raise DiscordWebhookException("Webhook must have content, embeds, or files")

        payload = self._prepare_payload()
        
        if self.files:
            return self._execute_with_files(payload)
        else:
            return self._execute_json(payload)

    def _execute_json(self, payload: Dict[str, Any]) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, json=payload, headers=headers)
        
        if response.status_code not in [200, 204]:
            raise DiscordWebhookException(f"Webhook failed with status {response.status_code}: {response.text}")
            
        return response

    def _execute_with_files(self, payload: Dict[str, Any]) -> requests.Response:
        data = {"payload_json": json.dumps(payload)}
        files = {}
        
        for i, file_data in enumerate(self.files):
            files[f"file{i}"] = (file_data["filename"], file_data["file"])
            
        response = requests.post(self.url, data=data, files=files)
        
        if response.status_code not in [200, 204]:
            raise DiscordWebhookException(f"Webhook failed with status {response.status_code}: {response.text}")
            
        return response

    def __repr__(self) -> str:
        return f"<DiscordWebhook url='{self.url}' embeds={len(self.embeds)} files={len(self.files)}>"


class AsyncDiscordWebhook:
    def __init__(
        self,
        url: str,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        content: Optional[str] = None,
        embeds: Optional[List[DiscordEmbed]] = None,
    ):
        self.url = url
        self.username = username
        self.avatar_url = avatar_url
        self.content = content
        self.embeds = embeds or []
        self.files = []

    def add_embed(self, embed: DiscordEmbed) -> "AsyncDiscordWebhook":
        if len(self.embeds) >= 10:
            raise DiscordWebhookException("Maximum 10 embeds allowed per webhook")
        self.embeds.append(embed)
        return self

    def add_file(self, file: bytes, filename: str) -> "AsyncDiscordWebhook":
        if len(self.files) >= 10:
            raise DiscordWebhookException("Maximum 10 files allowed per webhook")
        
        if len(file) > 25 * 1024 * 1024:
            raise DiscordFileException("File size exceeds 25MB limit")
            
        self.files.append({"file": file, "filename": filename})
        return self

    def clear_embeds(self) -> "AsyncDiscordWebhook":
        self.embeds.clear()
        return self

    def clear_files(self) -> "AsyncDiscordWebhook":
        self.files.clear()
        return self

    def _prepare_payload(self) -> Dict[str, Any]:
        payload = {}
        
        if self.content:
            payload["content"] = self.content
        if self.username:
            payload["username"] = self.username
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url
        if self.embeds:
            payload["embeds"] = [embed.to_dict() for embed in self.embeds]
            
        return payload

    async def execute(self) -> aiohttp.ClientResponse:
        if not self.content and not self.embeds and not self.files:
            raise DiscordWebhookException("Webhook must have content, embeds, or files")

        payload = self._prepare_payload()
        
        if self.files:
            return await self._execute_with_files(payload)
        else:
            return await self._execute_json(payload)

    async def _execute_json(self, payload: Dict[str, Any]) -> aiohttp.ClientResponse:
        headers = {"Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as response:
                if response.status not in [200, 204]:
                    text = await response.text()
                    raise DiscordWebhookException(f"Webhook failed with status {response.status}: {text}")
                return response

    async def _execute_with_files(self, payload: Dict[str, Any]) -> aiohttp.ClientResponse:
        data = aiohttp.FormData()
        data.add_field("payload_json", json.dumps(payload))
        
        for i, file_data in enumerate(self.files):
            data.add_field(f"file{i}", file_data["file"], filename=file_data["filename"])
            
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=data) as response:
                if response.status not in [200, 204]:
                    text = await response.text()
                    raise DiscordWebhookException(f"Webhook failed with status {response.status}: {text}")
                return response

    def __repr__(self) -> str:
        return f"<AsyncDiscordWebhook url='{self.url}' embeds={len(self.embeds)} files={len(self.files)}>"
