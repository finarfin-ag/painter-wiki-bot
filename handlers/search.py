from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from services.wikidata import search_painter, get_painter_info
from services.commons import get_paintings
from utils.keyboard import painter_menu, disambiguation_menu
from locales import get, detect_lang


def new_search_button(lang: str) -> InlineKeyboardMarkup:
    label = "🔎 جستجوی نقاش دیگر" if lang == "fa" else "🔎 Search another painter"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(label, callback_data="new_search")
    ]])


async def handle_search(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lang = detect_lang(text)
    context.user_data["lang"] = lang

    msg = await update.message.reply_text(
        get("searching", lang, name=text),
        parse_mode=ParseMode.MARKDOWN,
    )

    candidates = search_painter(text, lang)

    if not candidates and lang == "fa":
        candidates = search_painter(text, "en")

    if not candidates:
        await msg.edit_text(
            get("not_found", lang, name=text),
            reply_markup=new_search_button(lang),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if len(candidates) == 1:
        await msg.delete()
        await show_painter_card(update, context,
                                 candidates[0]["id"], lang)
    else:
        await msg.edit_text(
            get("did_you_mean", lang),
            reply_markup=disambiguation_menu(candidates, lang),
            parse_mode=ParseMode.MARKDOWN,
        )


async def handle_select_callback(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, qid, lang = query.data.split("|", 2)
    context.user_data["lang"] = lang
    await query.message.delete()
    await show_painter_card(update, context, qid, lang,
                             use_callback=True)


async def handle_new_search(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    prompt = (
        "🔎 نام نقاش مورد نظر را بنویسید:"
        if lang == "fa"
        else "🔎 Type a painter's name:"
    )
    await query.message.reply_text(prompt)


async def show_painter_card(update, context, qid: str,
                              lang: str, use_callback: bool = False):
    info = get_painter_info(qid, lang)
    works_data = get_paintings(info["name"])
    count = works_data.get("total", 0)

    caption = get(
        "painter_card", lang,
        name=info["name"],
        born=info["born"],
        died=info["died"],
        age=info["age"],
        nationality=info["nationality"],
        movement=info["movement"],
        bio=info["bio"] or get("unknown", lang),
    )

    keyboard = painter_menu(qid, count, lang) if count > 0 else new_search_button(lang)

    chat_id = (
        update.callback_query.message.chat_id
        if use_callback
        else update.message.chat_id
    )

    if info.get("portrait_url"):
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=info["portrait_url"],
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
            return
        except Exception:
            pass

    await context.bot.send_message(
        chat_id=chat_id,
        text=caption,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def handle_try_again(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    await query.message.delete()
    await query.message.reply_text(
        get("welcome", lang),
        parse_mode=ParseMode.MARKDOWN,
    )
