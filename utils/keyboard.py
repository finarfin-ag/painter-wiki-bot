from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from locales import get


def painter_menu(qid: str, count: int, lang: str) -> InlineKeyboardMarkup:
    """Main menu shown after painter card."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            get("btn_search_painting", lang),
            callback_data=f"search_painting|{qid}|{lang}"
        )],
        [InlineKeyboardButton(
            get("btn_random", lang),
            callback_data=f"random|{qid}|{lang}"
        )],
        [InlineKeyboardButton(
            get("btn_all", lang, count=count),
            callback_data=f"all|{qid}|0|{lang}"
        )],
    ])


def paintings_navigation(qid: str, offset: int, total: int,
                          lang: str) -> InlineKeyboardMarkup:
    """Pagination buttons for artwork grid."""
    rows = []
    remaining = total - offset - 10
    if remaining > 0:
        rows.append([InlineKeyboardButton(
            get("btn_load_more", lang, remaining=remaining),
            callback_data=f"all|{qid}|{offset + 10}|{lang}"
        )])
    rows.append([InlineKeyboardButton(
        get("btn_back", lang),
        callback_data=f"back|{qid}|{lang}"
    )])
    return InlineKeyboardMarkup(rows)


def size_menu(filename: str, title: str, lang: str) -> InlineKeyboardMarkup:
    """Size selection buttons for a single painting."""
    safe_title = title[:40].replace("|", "-")
    safe_filename = filename.replace("|", "-")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            get("btn_size_small", lang),
            callback_data=f"size|small|{safe_filename}|{safe_title}|{lang}"
        )],
        [InlineKeyboardButton(
            get("btn_size_medium", lang),
            callback_data=f"size|medium|{safe_filename}|{safe_title}|{lang}"
        )],
        [InlineKeyboardButton(
            get("btn_size_large", lang),
            callback_data=f"size|large|{safe_filename}|{safe_title}|{lang}"
        )],
        [InlineKeyboardButton(
            get("btn_size_original", lang),
            callback_data=f"size|original|{safe_filename}|{safe_title}|{lang}"
        )],
    ])


def disambiguation_menu(candidates: list[dict], lang: str) -> InlineKeyboardMarkup:
    """Show painter candidates when search is ambiguous."""
    rows = []
    for c in candidates[:5]:
        label = c["label"]
        desc = c.get("description", "")
        btn_text = f"{label} — {desc[:30]}" if desc else label
        rows.append([InlineKeyboardButton(
            btn_text,
            callback_data=f"select|{c['id']}|{lang}"
        )])
    rows.append([InlineKeyboardButton(
        get("try_again", lang),
        callback_data="try_again"
    )])
    return InlineKeyboardMarkup(rows)
