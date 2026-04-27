# All English UI strings — edit text here anytime without touching bot logic

STRINGS = {
    # General
    "welcome": (
        "🎨 *Welcome to PainterBot!*\n\n"
        "I can help you explore painters and their works from Wikimedia.\n\n"
        "Just type any painter's name to begin.\n"
        "_Example: Vincent van Gogh, Frida Kahlo, Rembrandt..._"
    ),
    "help": (
        "🖌 *How to use PainterBot:*\n\n"
        "• Type a painter's name to search\n"
        "• Browse their artworks as thumbnails\n"
        "• Pick any painting to download in your preferred size\n\n"
        "💡 Don't worry about typos — I'll try to find the closest match!"
    ),
    "searching": "🔍 Searching for *{name}*...",
    "not_found": (
        "😕 I couldn't find a painter named *{name}*.\n\n"
        "Try a different spelling or check the name."
    ),
    "did_you_mean": "🤔 Did you mean one of these?",
    "try_again": "🔄 Try another name",
    "error": "⚠️ Something went wrong. Please try again.",

    # Painter card
    "painter_card": (
        "🎨 *{name}*\n\n"
        "🗓 *Born:* {born}\n"
        "✝️ *Died:* {died}\n"
        "🎂 *Age:* {age}\n"
        "🌍 *Nationality:* {nationality}\n"
        "🖌 *Movement:* {movement}\n\n"
        "📖 _{bio}_"
    ),
    "unknown": "Unknown",

    # Artwork menu buttons
    "btn_search_painting": "🔍 Search a specific painting",
    "btn_random": "🎲 5 Random Works",
    "btn_all": "🖼 Show All ({count} works)",
    "btn_back": "⬅️ Back",
    "btn_load_more": "➕ Load More ({remaining} remaining)",

    # Paintings
    "ask_painting_name": (
        "✏️ Type the name of the painting you're looking for:\n"
        "_(or /cancel to go back)_"
    ),
    "painting_not_found": "😕 No painting found with that name. Try another title.",
    "showing_works": "🖼 Showing works by *{name}* ({start}–{end} of {total}):",
    "showing_random": "🎲 Here are 5 random works by *{name}*:",
    "choose_size": (
        "🖼 *{title}*\n\n"
        "Choose your preferred size:"
    ),
    "btn_size_small": "📱 Small (~320px)",
    "btn_size_medium": "🖥 Medium (~800px)",
    "btn_size_large": "🖨 Large (~1920px)",
    "btn_size_original": "📦 Original (full resolution)",
    "sending_file": "⏳ Fetching your image, please wait...",
    "no_works_found": "😕 No artworks found for *{name}* on Wikimedia Commons.",
}
