# Third-party imports
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

# Standard library imports
import logging

logger = logging.getLogger(__name__)


class TelegramPlugin:
    """
    A Telegram bot plugin that handles user interactions and forwards messages to an AI agent.

    This class sets up and manages a Telegram bot using the Python Telegram API (`python-telegram-bot`).
    It includes handlers for commands (e.g., `/start`) and message processing. User messages are
    forwarded to the AI agent, and responses are sent back via Telegram.

    Features:
        - Handles incoming text messages and forwards them to the AI agent.
        - Supports command handlers (e.g., `/start`).
        - Implements error handling to prevent bot crashes.
        - Splits long responses exceeding Telegram's 4096-character limit.

    Attributes:
        bot_token (str): The Telegram bot token for authentication.
        agent (Agent): The AI agent instance responsible for processing user messages.
        application (Application): The Telegram bot application instance.
    """

    def __init__(self, bot_token: str, agent):
        """
        Initializes the Telegram bot plugin and sets up message handlers.

        Args:
            bot_token (str): The Telegram bot token used for authentication.
            agent (Agent): The AI agent that processes user messages and generates responses.
        """
        logger.info("Initializing TelegramPlugin")
        self.agent = agent
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()

        # Set up command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        logger.info("TelegramPlugin initialization complete")

    async def start(self, update: Update, context: CallbackContext) -> None:
        """
        Handles the `/start` command and sends a welcome message to the user.

        This method is triggered when a user sends the `/start` command in the Telegram chat.
        It provides an introduction message to guide the user on how to interact with the bot.

        Args:
            update (Update): The incoming update from Telegram, containing user details.
            context (CallbackContext): The callback context for handling additional metadata.
        """
        try:
            await update.message.reply_text(
                "Hello! I am your Crypto.com AI Agent. Send me a message to interact!"
            )
        except Exception as e:
            logger.error(f"[TelegramPlugin/start] - Error in /start command: {e}")
            await update.message.reply_text("An error occurred. Please try again.")

    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        """
        Processes user messages and forwards them to the AI agent.

        This method retrieves the user's input message, sends it to the AI agent for processing,
        and returns the AI-generated response back to the user.

        It also ensures that responses exceeding Telegram's character limit (4096 characters)
        are split into multiple messages.

        Args:
            update (Update): The incoming update containing the user's message.
            context (CallbackContext): The callback context containing bot metadata.
        """
        try:
            user_message = update.message.text
            chat_id = update.message.chat_id
            response = self.agent.interact(user_message, thread_id=chat_id)

            # Handle long messages (4096-char Telegram limit)
            MAX_MESSAGE_LENGTH = 4096
            if len(response) > MAX_MESSAGE_LENGTH:
                for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                    await update.message.reply_text(
                        response[i : i + MAX_MESSAGE_LENGTH]
                    )
            else:
                await update.message.reply_text(response)

        except Exception as e:
            logger.error(
                f"[TelegramPlugin/handle_message] - Error in handle_message: {e}"
            )
            await update.message.reply_text(
                "An error occurred while processing your request."
            )

    def run(self):
        """
        Starts the Telegram bot with error handling.
        """
        logger.info("Starting Telegram bot polling...")
        try:
            self.application.run_polling()
        except KeyboardInterrupt:
            logger.info("Telegram bot stopped by user")
        except Exception as e:
            logger.error(f"Error running Telegram bot: {e}")
        finally:
            logger.info("Telegram bot shutdown complete")
