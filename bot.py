import logging
import re
from os import environ
from password_strength import PasswordStats
from telegram import Update
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
    logging.log(logging.INFO, f"Checking password strength for '{text}' by {username}: {int(strength * 100)}%")
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


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message is not None:
        # The bot was ordered to check a password from another message by replying to it
        if update.message.reply_to_message.from_user.username is None:
            username = update.message.reply_to_message.from_user.first_name
        else:
            username = "@" + update.message.reply_to_message.from_user.username
        if update.message.quote is not None:
            # The bot was ordered to check a quoted password
            text = update.message.quote['text']
        else:
            text = update.message.reply_to_message.text
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=strengthCheck(text, username))
    else:
        # The bot was directly spoken to
        text = update.message.text
        if text.startswith("/"):
            # remove the command from the input
            parts = text.split(" ", 1)
            if len(parts) == 1:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="You need to reply to the password you want to check.\n"
                         "You can also quote it or enter it with the command."
                )
                return
            text = parts[1]
        if update.message.from_user.username is None:
            username = update.message.from_user.first_name
        else:
            username = "@" + update.message.from_user.username
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=strengthCheck(text, username))


if __name__ == '__main__':
    # check if the env variable for the api-token is set
    if environ["API_TOKEN"] is None:
        raise ValueError("API_TOKEN environment variable not set")

    # create the bot application and configure it
    application = ApplicationBuilder().token(environ["API_TOKEN"]).build()

    start_handler = CommandHandler('start', start)
    check_handler = CommandHandler('check', check)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, check)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(check_handler)

    # let's fly...
    application.run_polling()
