"""
Agent Module.

This module defines the `Agent` class, which serves as the primary interface
for interacting with the LangGraph-based workflow. The Agent encapsulates
the workflow graph and provides high-level methods for initialization and
user interaction.
"""

# Standard library imports
from typing import Optional, Self

# Internal application imports
from crypto_com_agent_client.config.logging_config import configure_logging
from crypto_com_agent_client.core.handlers.interaction_handler import InteractionHandler
from crypto_com_agent_client.lib.initializer import Initializer
from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
from crypto_com_agent_client.lib.types.llm_config import LLMConfig
from crypto_com_agent_client.lib.types.plugins_config import PluginsConfig
from crypto_com_agent_client.lib.utils.storage import Storage
from crypto_com_agent_client.plugins.social.discord_plugin import DiscordPlugin
from crypto_com_agent_client.plugins.social.telegram_plugin import TelegramPlugin
from crypto_com_agent_client.plugins.storage.sqllite_plugin import SQLitePlugin


class Agent:
    """
    The `Agent` class encapsulates the LangGraph workflow and provides a
    high-level interface for managing interactions. It supports initialization
    with LLM, blockchain, and optional LangFuse configurations.

    Attributes:
        handler (InteractionHandler): The interaction handler that manages user input and workflow state.

    Example:
        >>> from lib.client import Agent
        >>> agent = Agent.init(
        ...     llm_config={
        ...         "provider": "OpenAI",
        ...         "model": "gpt-4",
        ...         "provider-api-key": "your-api-key",
        ...     },
        ...     blockchain_config={
        ...         "api-key": "developer-sdk-api-key",
        ...     },
        ...     plugins={
        ...         "personality": {
        ...             "tone": "friendly",
        ...             "language": "English",
        ...             "verbosity": "high",
        ...         },
        ...         "instructions": "You are a humorous assistant.",
        ...         "storage": custom_storage,
        ...     },
        ... )
        >>> response = agent.interact("Hello! What can you do?")
        >>> print(response)
    """

    def __init__(
        self: Self,
        handler: InteractionHandler,
        telegram_plugin: Optional[TelegramPlugin] = None,
        discord_plugin: Optional[DiscordPlugin] = None,
    ) -> None:
        """
        Initializes the Agent instance.

        Args:
            handler (InteractionHandler): The interaction handler that processes user input
                and manages workflow state.

        Example:
            >>> from core.handlers.interaction_handler import InteractionHandler
            >>> handler = InteractionHandler(app=compiled_workflow, storage=custom_storage)
            >>> agent = Agent(handler=handler)
        """
        self.handler: InteractionHandler = handler
        self.telegram_plugin = telegram_plugin
        self.discord_plugin = discord_plugin

    @staticmethod
    def init(
        llm_config: LLMConfig = None,
        blockchain_config: BlockchainConfig = None,
        plugins: PluginsConfig = None,
    ) -> "Agent":
        """
        Initializes the Agent with LLM, blockchain, and plugin configurations.

        Args:
            llm_config (LLMConfig): Configuration for the LLM provider.
                Example:
                    {
                        "provider": "OpenAI",
                        "model": "gpt-4",
                        "provider-api-key": "your-api-key"
                    }
            blockchain_config (BlockchainConfig): Configuration for the blockchain client.
                Example:
                    {
                        "api-key": "developer-sdk-api-key"
                    }
            plugins (PluginsConfig): Additional configurations and integrations.
                Example:
                    {
                        "personality": {
                            "tone": "friendly",
                            "language": "English",
                            "verbosity": "high",
                        },
                        "instructions": "You are a humorous assistant.",
                        "storage": custom_storage,
                    }

        Returns:
            Agent: An initialized `Agent` instance with the workflow configured.

        Raises:
            ValueError: If any required configurations are missing or invalid.

        Example:
            >>> agent = Agent.init(
            ...     llm_config={
            ...         "provider": "OpenAI",
            ...         "model": "gpt-4",
            ...         "provider-api-key": "your-api-key",
            ...         "temperature": 0,
            ...     },
            ...     blockchain_config={
            ...         "api-key": "developer-sdk--api-key",
            ...     },
            ...     plugins={
            ...         "personality": {
            ...             "tone": "friendly",
            ...             "language": "English",
            ...             "verbosity": "high",
            ...         },
            ...         "instructions": "You are a humorous assistant.",
            ...         "storage": custom_storage,
            ...     },
            ... )
        """
        # Convert to types
        llm_config = LLMConfig(**(llm_config))
        blockchain_config = BlockchainConfig(**(blockchain_config))
        plugins = PluginsConfig(**(plugins or {}))

        # Configure logging
        configure_logging(llm_config)

        # Use Initializer to set up the workflow
        initializer = Initializer(
            llm_config=llm_config,
            blockchain_config=blockchain_config,
            plugins=plugins,
        )

        # Initialize storage
        storage: SQLitePlugin | Storage = plugins.storage

        # Create InteractionHandler
        handler = InteractionHandler(
            app=initializer.workflow,
            storage=storage,
            blockchain_config=blockchain_config,
            debug_logging=llm_config.debug_logging,
        )

        telegram_plugin = None
        if plugins.telegram and isinstance(plugins.telegram, dict):
            bot_token = plugins.telegram.get("bot_token")
            if bot_token:
                telegram_plugin = TelegramPlugin(bot_token=bot_token, agent=handler)

        discord_plugin = None
        if plugins.discord and isinstance(plugins.discord, dict):
            bot_token = plugins.discord.get("bot_token")
            if bot_token:
                discord_plugin = DiscordPlugin(bot_token=bot_token, agent=handler)

        return Agent(
            handler=handler,
            telegram_plugin=telegram_plugin,
            discord_plugin=discord_plugin,
        )

    def interact(self: Self, input: str, thread_id: Optional[int] = None) -> str:
        """
        Processes user input through the workflow and returns the generated response.

        Args:
            input (str): The user's input message.
            thread_id (int, optional): A thread ID for contextual execution.

        Returns:
            str: The response generated by the workflow.

        Example:
            >>> response = agent.interact("Hello, what can you do?")
            >>> print(response)
        """
        return self.handler.interact(user_input=input, thread_id=thread_id)

    def start_telegram(self):
        """
        Starts the Telegram bot if it has been configured.
        """
        if self.telegram_plugin:
            print("Starting Telegram bot...")
            self.telegram_plugin.run()
        else:
            raise ValueError(
                "Telegram bot is not configured. Provide 'bot_token' in the plugin config."
            )

    def start_discord(self):
        """
        Starts the Discord bot if it has been configured.
        """
        if self.discord_plugin:
            print("Starting Discord bot...")
            self.discord_plugin.run()
        else:
            raise ValueError(
                "Discord bot is not configured. Provide 'bot_token' in the plugin config."
            )
