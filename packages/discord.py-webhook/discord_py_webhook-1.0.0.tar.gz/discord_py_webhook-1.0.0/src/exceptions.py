class DiscordException(Exception):
    """Base exception for discord.py-webhook library."""
    pass


class DiscordWebhookException(DiscordException):
    """Exception raised when webhook operations fail."""
    pass


class DiscordEmbedException(DiscordException):
    """Exception raised when embed operations fail."""
    pass


class DiscordFileException(DiscordException):
    """Exception raised when file operations fail."""
    pass
