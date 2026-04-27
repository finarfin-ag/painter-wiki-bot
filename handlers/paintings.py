from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from services.commons import (
    get_paintings, get_random_paintings,
    search_specific_painting, get_image_sizes
)
from services.wikidata import get_painter_info
from utils.keyboard import paintings_navigation, size_menu, painter_menu
from locales import get
import requests

ASK_PAINTING_NAME = 1  # ConversationHandler state


async def handle_paintings_callback(update: Update,
                                     context: ContextTypes.DEFAULT_TYPE):
    """Route all painting-related callback buttons."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split("|")
    action = parts[0]

    if action == "all":
        _, qid, offset, lang = parts
        await show_all_paintings(update, context, qid, int(offset), lang)

    elif action == "random":
        _, qid, lang = parts
        await show_random_paintings(update, context, qid, lang)

    elif action == "search_painting":
        _, qid, lang = parts
        context.user_data["search_painting_qid"] = qid
        context.user_data["lang"] = lang
        await query.message.reply_text(
            get("ask_painting_name", lang),
            parse_mode=ParseMode.MARKDOWN,
        )

    elif action == "size":
        _, size, filename, title, lang = parts[0], parts[1], parts[2], parts[3], parts[4]
        await send_painting_file(update, context, filename, size, title, lang)

    elif action == "back":
        _, qid, lang = parts
        await show_painter_card_from_callback(update, context, qid, lang)


async def show_all_paintings(update, context, qid: str,
                              offset: int, lang: str):
    """Show paginated paintings grid."""
    info = get_painter_info(qid, lang)
    name = info["name"]
    result = get_paintings(name, offset=offset, limit=10)
    works = result["works"]
    total = result["total"]

    if not works:
        await update.callback_query.message.reply_text(
            get("no_works_found", lang, name=name),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    end = offset + len(works)
    caption_header = get("showing_works", lang,
                         name=name, start=offset + 1,
                         end=end, total=total)

    # Send thumbnails as a media group (max 10)
    media = []
    for i, work in enumerate(works):
        cap = f"🖼 {work['title']}" if i == 0 else work["title"]
        media.append(InputMediaPhoto(
            media=work["thumb_url"],
            caption=cap,
        ))

    try:
        await context.bot.send_media_group(
            chat_id=update.callback_query.message.chat_id,
            media=media,
        )
    except Exception:
        # Fallback: send titles as text if media group fails
        titles = "\n".join(f"• {w['title']}" for w in works)
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f"{caption_header}\n\n{titles}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Send navigation buttons separately
    keyboard = paintings_navigation(qid, offset, total, lang)
    await context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=caption_header,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )

    # Store works in context for tap-to-select
    context.user_data["current_works"] = works
    context.user_data["painter_qid"] = qid


async def show_random_paintings(update, context, qid: str, lang: str):
    """Show 5 random paintings."""
    info = get_painter_info(qid, lang)
    name = info["name"]
    works = get_random_paintings(name, count=5)

    if not works:
        await update.callback_query.message.reply_text(
            get("no_works_found", lang, name=name),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    media = []
    for i, work in enumerate(works):
        cap = get("showing_random", lang, name=name) if i == 0 else work["title"]
        media.append(InputMediaPhoto(
            media=work["thumb_url"],
            caption=cap,
        ))

    try:
        await context.bot.send_media_group(
            chat_id=update.callback_query.message.chat_id,
            media=media,
        )
    except Exception:
        pass

    # After random, show size buttons for each work
    for work in works:
        kb = size_menu(work["filename"], work["title"], lang)
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=get("choose_size", lang, title=work["title"]),
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )


async def handle_painting_name_input(update: Update,
                                      context: ContextTypes.DEFAULT_TYPE):
    """Handle user typing a specific painting title."""
    text = update.message.text.strip()
    qid = context.user_data.get("search_painting_qid")
    lang = context.user_data.get("lang", "en")

    if not qid:
        return

    info = get_painter_info(qid, lang)
    works = search_specific_painting(info["name"], text)

    if not works:
        await update.message.reply_text(
            get("painting_not_found", lang),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    for work in works:
        kb = size_menu(work["filename"], work["title"], lang)
        try:
            await update.message.reply_photo(
                photo=work["thumb_url"],
                caption=get("choose_size", lang, title=work["title"]),
                reply_markup=kb,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            await update.message.reply_text(
                get("choose_size", lang, title=work["title"]),
                reply_markup=kb,
                parse_mode=ParseMode.MARKDOWN,
            )


async def send_painting_file(update, context, filename: str,
                              size: str, title: str, lang: str):
    """Download and send the painting at chosen resolution."""
    query = update.callback_query
    await query.message.reply_text(
        get("sending_file", lang),
        parse_mode=ParseMode.MARKDOWN,
    )

    urls = get_image_sizes(filename)
    url = urls.get(size, urls["original"])

    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=url,
            filename=filename,
            caption=f"🖼 {title}",
        )
    except Exception:
        await query.message.reply_text(get("error", lang))


async def show_painter_card_from_callback(update, context, qid: str, lang: str):
    """Re-show painter card when user hits Back."""
    from handlers.search import show_painter_card
    await show_painter_card(update, context, qid, lang, use_callback=True)
