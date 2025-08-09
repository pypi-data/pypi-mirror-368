import pytest
from unittest.mock import Mock, patch
from discord_webhook import DiscordWebhook, DiscordEmbed, DiscordException

class TestDiscordWebhook:
    def test_webhook_creation(self):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        assert webhook.url == "https://discord.com/api/webhooks/test"
        assert webhook.content is None
        assert len(webhook.embeds) == 0
        assert len(webhook.files) == 0

    def test_webhook_with_content(self):
        webhook = DiscordWebhook(
            url="https://discord.com/api/webhooks/test",
            content="Test message"
        )
        assert webhook.content == "Test message"

    def test_add_embed(self):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        embed = DiscordEmbed(title="Test", description="Test description")
        webhook.add_embed(embed)
        assert len(webhook.embeds) == 1
        assert webhook.embeds[0] == embed

    def test_add_file(self):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        test_file = b"test file content"
        webhook.add_file(test_file, "test.txt")
        assert len(webhook.files) == 1
        assert webhook.files[0]["file"] == test_file
        assert webhook.files[0]["filename"] == "test.txt"

    def test_clear_embeds(self):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        embed = DiscordEmbed(title="Test")
        webhook.add_embed(embed)
        assert len(webhook.embeds) == 1
        webhook.clear_embeds()
        assert len(webhook.embeds) == 0

    def test_clear_files(self):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        webhook.add_file(b"test", "test.txt")
        assert len(webhook.files) == 1
        webhook.clear_files()
        assert len(webhook.files) == 0

    @patch('requests.post')
    def test_execute_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        webhook.content = "Test message"
        response = webhook.execute()

        assert response.status_code == 200
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_execute_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        webhook.content = "Test message"

        with pytest.raises(DiscordException):
            webhook.execute()

    def test_execute_no_content(self):
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/test")
        with pytest.raises(DiscordException):
            webhook.execute()

class TestDiscordEmbed:
    def test_embed_creation(self):
        embed = DiscordEmbed(title="Test", description="Test description")
        assert embed.title == "Test"
        assert embed.description == "Test description"

    def test_set_author(self):
        embed = DiscordEmbed()
        embed.set_author("Test Author", "https://example.com", "https://example.com/icon.png")
        assert embed.author["name"] == "Test Author"
        assert embed.author["url"] == "https://example.com"
        assert embed.author["icon_url"] == "https://example.com/icon.png"

    def test_set_footer(self):
        embed = DiscordEmbed()
        embed.set_footer("Test Footer", "https://example.com/icon.png")
        assert embed.footer["text"] == "Test Footer"
        assert embed.footer["icon_url"] == "https://example.com/icon.png"

    def test_add_field(self):
        embed = DiscordEmbed()
        embed.add_embed_field("Field 1", "Value 1", True)
        assert len(embed.fields) == 1
        assert embed.fields[0]["name"] == "Field 1"
        assert embed.fields[0]["value"] == "Value 1"
        assert embed.fields[0]["inline"] is True

    def test_to_dict(self):
        embed = DiscordEmbed(title="Test", description="Test description", color=0x00ff00)
        embed_dict = embed.to_dict()
        assert embed_dict["title"] == "Test"
        assert embed_dict["description"] == "Test description"
        assert embed_dict["color"] == 0x00ff00
