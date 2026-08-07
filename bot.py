import logging
import re
from os import environ
from password_strength import PasswordStats
from telegram import Update, Message
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes


# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logging.getLogger('httpx').setLevel(logging.WARNING)


def strengthCheck(text: str, username: str) -> str:
    # Check the "passwords" level and return a message with the rating
    text = text.strip()
    strength = PasswordStats(text).strength()
    uppers = len(re.findall(r'[A-Z]', text))
    lowers = len(re.findall(r'[a-z]', text))
    numbers = len(re.findall(r'[0-9]', text))
    specials = len(text) - uppers - lowers - numbers
    logging.log(logging.DEBUG, f"Checking password strength for '{text}' by {username}: {int(strength * 100)}%")
    if strength < .25:
        out = f"Sorry {username}, but your password is weak. You really need to work on that!"
    elif strength < 0.50:
        out = f"Not too bad, but still a bit weak, {username}!"
    elif strength < 0.90:
        out = f"Quite good but still not perfect. Do better next time, {username}!"
    else:
        out = f"Wow! That is a really strong password. I am proud of you, {username}!"
    out = out + (f"\nLength: {len(text)}, Uppercase: {uppers}, Lowercase: {lowers}, Numbers: {numbers}, "
                 f"Special: {specials}, Score: {int(strength * 100)}%")
    return out


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="You're a cutie!")


async def helptext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Reply to the password you want to check."
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        if update.message.reply_to_message is not None:
            if update.message.reply_to_message.text is None:
                # Reply was not to text, so a sticker or similar
                await helptext(update, context)
                return
            # The bot was ordered to check a password from another message by replying to it
            if update.message.reply_to_message.from_user:
                if update.message.reply_to_message.from_user.username is None:
                    username = update.message.reply_to_message.from_user.first_name
                else:
                    username = "@" + update.message.reply_to_message.from_user.username
                if update.message.quote is not None:
                    # The bot was ordered to check a quoted password
                    text = update.message.quote.text
                else:
                    text = update.message.reply_to_message.text
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=strengthCheck(text, username))
        else:
            # The bot was directly spoken to
            text = update.message.text
            if text is not None:
                if text.startswith("/"):
                    # remove the command from the input
                    parts = text.split(" ", 1)
                    if len(parts) == 1:
                        await helptext(update, context)
                        return
                    text = parts[1]
                if update.message.from_user.username is None:
                    username = update.message.from_user.first_name
                else:
                    username = "@" + update.message.from_user.username
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=strengthCheck(text, username))
            else:
                # Text is None
                await helptext(update, context)


async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="This bot does not store any data whatsoever.\n"
                                        "Any input and connected data is immediately "
                                        "discarded after answering your query.")


class BotMentionFilter(filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        bot_username = message.get_bot().username
        return message.text is not None and f"@{bot_username}" in message.text


if __name__ == '__main__':
    # check if the env variable for the api-token is set
    if environ["API_TOKEN"] is None:
        raise ValueError("API_TOKEN environment variable not set")

    # create the bot application and configure it
    application = ApplicationBuilder().token(environ["API_TOKEN"]).build()

    start_handler = CommandHandler('start', start)
    check_handler = CommandHandler('check', check)
    help_handler = CommandHandler('help', helptext)
    privacy_handler = CommandHandler('privacy', privacy)
    reply_mention_handler = MessageHandler(filters.REPLY & BotMentionFilter(), check)
    mention_handler = MessageHandler(BotMentionFilter(), helptext)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, check)

    application.add_handler(start_handler)
    application.add_handler(check_handler)
    application.add_handler(help_handler)
    application.add_handler(privacy_handler)
    application.add_handler(echo_handler)
    application.add_handler(reply_mention_handler)
    application.add_handler(mention_handler)

    # let's fly...
    application.run_polling()
