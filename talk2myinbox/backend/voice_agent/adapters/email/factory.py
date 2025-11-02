"""
Email Adapter Factory
Creates the appropriate email adapter based on configuration
"""

from .base import BaseEmailAdapter
from .gmail_adapter import GmailAdapter
from typing import Literal


class EmailAdapterFactory:
    """
    Factory for creating email adapters based on provider type.

    Supports:
    - gmail_api: Gmail via Google API
    - imap_smtp: Generic IMAP/SMTP (coming soon)
    - outlook_graph: Microsoft Outlook via Graph API (coming soon)
    """

    @staticmethod
    def create(
        provider: Literal["gmail_api", "imap_smtp", "outlook_graph"] = "gmail_api",
        **kwargs
    ) -> BaseEmailAdapter:
        """
        Create an email adapter for the specified provider.

        Args:
            provider: Email provider type
            **kwargs: Provider-specific configuration

        Returns:
            BaseEmailAdapter instance

        Raises:
            ValueError: If provider is not supported
        """

        if provider == "gmail_api":
            return GmailAdapter(
                credentials_path=kwargs.get("credentials_path"),
                token_path=kwargs.get("token_path"),
                use_mock=kwargs.get("use_mock", False)
            )

        elif provider == "imap_smtp":
            # TODO: Implement IMAP/SMTP adapter
            raise NotImplementedError(
                "IMAP/SMTP adapter is not yet implemented. "
                "Use 'gmail_api' for now."
            )

        elif provider == "outlook_graph":
            # TODO: Implement Outlook Graph adapter
            raise NotImplementedError(
                "Outlook Graph adapter is not yet implemented. "
                "Use 'gmail_api' for now."
            )

        else:
            raise ValueError(
                f"Unknown email provider: {provider}. "
                f"Supported providers: gmail_api, imap_smtp, outlook_graph"
            )

    @staticmethod
    def get_supported_providers() -> list[str]:
        """Get list of supported email providers"""
        return ["gmail_api", "imap_smtp", "outlook_graph"]

    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of currently available (implemented) providers"""
        return ["gmail_api"]  # Only Gmail is fully implemented
