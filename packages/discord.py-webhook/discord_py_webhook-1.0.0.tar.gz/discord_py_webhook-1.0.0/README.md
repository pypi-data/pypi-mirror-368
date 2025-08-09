# discord.py-webhook

A powerful and feature-rich Discord webhook library that makes it easy to create, customize, and manage Discord webhooks with extensive configuration options.

## Features

- 🚀 **Simple & Intuitive API** - Easy to use with minimal setup
- 🎨 **Rich Embed Support** - Create beautiful embeds with colors, fields, and media
- 📝 **Multiple Message Types** - Text, embeds, files, and custom content
- ⚡ **Async Support** - Both synchronous and asynchronous operations
- 🔧 **Extensive Customization** - Customize every aspect of your webhooks
- 🛡️ **Error Handling** - Robust error handling and validation
- 📦 **No External Dependencies** - Lightweight with minimal requirements

## Installation

```bash
pip install discord.py-webhook
```

## Quick Start

```python
from discord_webhook import DiscordWebhook, DiscordEmbed

# Create a webhook
webhook = DiscordWebhook(url='YOUR_WEBHOOK_URL')

# Send a simple message
webhook.content = "Hello, Discord!"
webhook.execute()

# Create an embed
embed = DiscordEmbed(title="My Embed", description="This is a test embed", color=242424)
webhook.add_embed(embed)
webhook.execute()
```

## Advanced Usage

### Creating Rich Embeds

```python
from discord_webhook import DiscordWebhook, DiscordEmbed

webhook = DiscordWebhook(url='YOUR_WEBHOOK_URL')

embed = DiscordEmbed(
    title="Server Status",
    description="All systems operational",
    color=0x00ff00,
    url="https://github.com/7vntii"
)

embed.set_author(name="7", url="https://github.com/7vntii", icon_url="https://github.com/7vntii.png")
embed.set_footer(text="Powered by discord.py-webhook")
embed.set_timestamp()

embed.add_embed_field(name="CPU", value="45%", inline=True)
embed.add_embed_field(name="Memory", value="67%", inline=True)
embed.add_embed_field(name="Network", value="Stable", inline=True)

webhook.add_embed(embed)
webhook.execute()
```

### File Uploads

```python
from discord_webhook import DiscordWebhook

webhook = DiscordWebhook(url='YOUR_WEBHOOK_URL')

with open("image.png", "rb") as f:
    webhook.add_file(file=f.read(), filename="image.png")

webhook.content = "Check out this image!"
webhook.execute()
```

### Async Operations

```python
import asyncio
from discord_webhook import AsyncDiscordWebhook

async def send_webhook():
    webhook = AsyncDiscordWebhook(url='YOUR_WEBHOOK_URL')
    webhook.content = "Async webhook message!"
    await webhook.execute()

asyncio.run(send_webhook())
```

### Custom Webhook Configuration

```python
from discord_webhook import DiscordWebhook

webhook = DiscordWebhook(
    url='YOUR_WEBHOOK_URL',
    username="Custom Bot",
    avatar_url="https://example.com/avatar.png"
)

webhook.content = "Message with custom username and avatar!"
webhook.execute()
```

## API Reference

### DiscordWebhook

Main webhook class for sending messages to Discord.

#### Parameters:
- `url` (str): Discord webhook URL
- `username` (str, optional): Override default username
- `avatar_url` (str, optional): Override default avatar
- `content` (str, optional): Message content
- `embeds` (list, optional): List of DiscordEmbed objects

#### Methods:
- `add_embed(embed)`: Add an embed to the webhook
- `add_file(file, filename)`: Add a file to the webhook
- `execute()`: Send the webhook
- `clear_embeds()`: Remove all embeds
- `clear_files()`: Remove all files

### DiscordEmbed

Create rich embeds for your webhook messages.

#### Parameters:
- `title` (str, optional): Embed title
- `description` (str, optional): Embed description
- `color` (int, optional): Embed color (hex)
- `url` (str, optional): Embed URL
- `timestamp` (datetime, optional): Embed timestamp

#### Methods:
- `set_author(name, url, icon_url)`: Set embed author
- `set_footer(text, icon_url)`: Set embed footer
- `set_thumbnail(url)`: Set embed thumbnail
- `set_image(url)`: Set embed image
- `add_embed_field(name, value, inline)`: Add a field to the embed
- `set_timestamp()`: Set current timestamp

## Examples

### Server Status Monitor

```python
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

def send_status_update(status, color):
    webhook = DiscordWebhook(url='YOUR_WEBHOOK_URL')
    
    embed = DiscordEmbed(
        title="Server Status Update",
        description=f"Server is currently {status}",
        color=color
    )
    
    embed.set_footer(text=f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    webhook.add_embed(embed)
    webhook.execute()

# Usage
send_status_update("Online", 0x00ff00)
send_status_update("Offline", 0xff0000)
```

### Notification System

```python
from discord_webhook import DiscordWebhook, DiscordEmbed

def send_notification(title, message, level="info"):
    colors = {
        "info": 0x0099ff,
        "success": 0x00ff00,
        "warning": 0xffff00,
        "error": 0xff0000
    }
    
    webhook = DiscordWebhook(url='YOUR_WEBHOOK_URL')
    embed = DiscordEmbed(title=title, description=message, color=colors.get(level, 0x0099ff))
    webhook.add_embed(embed)
    webhook.execute()

# Usage
send_notification("Task Completed", "Backup finished successfully", "success")
send_notification("Error Detected", "Failed to connect to database", "error")
```

## Error Handling

The library includes comprehensive error handling:

```python
from discord_webhook import DiscordWebhook, DiscordException

try:
    webhook = DiscordWebhook(url='INVALID_URL')
    webhook.execute()
except DiscordException as e:
    print(f"Webhook error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**7** - [GitHub](https://github.com/7vntii) | [YouTube](https://www.youtube.com/@7vntii) | [PyPI](https://pypi.org/user/7vntii)

Email: jj9dptr57@mozmail.com

---

Made with ❤️ by 7
