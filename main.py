import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from handlers.search import (
    handle_search,
    handle_select_callback,
    handle_try_again,
    handle_new_search,
)
from handlers.paintings import (
    handle_paintings_callback,
    handle_painting_name_input,
)
from locales import get, detect_lang

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context):
    lang = detect_lang(update.message.from_user.language_code or "en")
    context.user_data["lang"] = lang
    await update.message.reply_text(
        get("welcome", lang),
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context):
    lang = context.user_data.get("lang", "en")
    await update.message.reply_text(
        get("help", lang),
        parse_mode="Markdown",
    )


async def cmd_cancel(update: Update, context):
    lang = context.user_data.get("lang", "en")
    context.user_data.pop("search_painting_qid", None)
    await update.message.reply_text(
        get("welcome", lang),
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context):
    if context.user_data.get("search_painting_qid"):
        await handle_painting_name_input(update, context)
    else:
        await handle_search(update, context)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("cancel", cmd_cancel))

    app.add_handler(CallbackQueryHandler(
        handle_select_callback, pattern=r"^select\|"))
    app.add_handler(CallbackQueryHandler(
        handle_try_again, pattern=r"^try_again$"))
    app.add_handler(CallbackQueryHandler(
        handle_new_search, pattern=r"^new_search$"))
    app.add_handler(CallbackQueryHandler(
        handle_paintings_callback,
        pattern=r"^(all|random|search_painting|size|back)\|"))

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message,
    ))

    logger.info("PainterBot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
