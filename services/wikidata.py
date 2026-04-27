import requests
from difflib import get_close_matches

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIPEDIA_API_EN = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_API_FA = "https://fa.wikipedia.org/w/api.php"

# Artist type Wikidata IDs — add more here later to expand beyond painters
ENTITY_TYPES = {
    "painter": "Q1028181",
    # "sculptor": "Q1281618",
    # "illustrator": "Q644687",
    # "architect": "Q42973",
}

HEADERS = {"User-Agent": "PainterBot/1.0 (Telegram Bot; educational project)"}


def search_painter(name: str, lang: str = "en") -> list[dict]:
    """
    Search Wikidata for painters matching the given name.
    Returns a list of candidates: [{id, label, description}]
    """
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": lang,
        "fallbacklanguage": "en",
        "type": "item",
        "limit": 10,
        "format": "json",
    }
    try:
        r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        results = r.json().get("search", [])

        # Filter to only keep painters
        painters = []
        for item in results:
            qid = item.get("id")
            if qid and _is_painter(qid):
                painters.append({
                    "id": qid,
                    "label": item.get("label", name),
                    "description": item.get("description", ""),
                })
        return painters
    except Exception:
        return []


def _is_painter(qid: str) -> bool:
    """Check if a Wikidata entity is a painter (or future artist type)."""
    params = {
        "action": "wbgetclaims",
        "entity": qid,
        "property": "P106",  # P106 = occupation
        "format": "json",
    }
    try:
        r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
        claims = r.json().get("claims", {}).get("P106", [])
        painter_ids = set(ENTITY_TYPES.values())
        for claim in claims:
            val = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(val, dict) and val.get("id") in painter_ids:
                return True
        return False
    except Exception:
        return False


def get_painter_info(qid: str, lang: str = "en") -> dict:
    """
    Fetch full painter info from Wikidata + Wikipedia.
    Returns a dict with name, born, died, age, nationality, movement, bio, portrait_url
    """
    data = _get_wikidata_claims(qid, lang)
    bio = _get_wikipedia_extract(qid, lang)
    return {**data, "bio": bio}


def _get_wikidata_claims(qid: str, lang: str) -> dict:
    """Extract structured fields from Wikidata claims."""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "languages": f"{lang}|en",
        "props": "labels|claims",
        "format": "json",
    }
    try:
        r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
        entity = r.json().get("entities", {}).get(qid, {})
        claims = entity.get("claims", {})
        labels = entity.get("labels", {})

        name = (
            labels.get(lang, {}).get("value")
            or labels.get("en", {}).get("value")
            or qid
        )

        born = _extract_date(claims, "P569")
        died = _extract_date(claims, "P570")
        age = _calc_age(born, died)
        nationality = _extract_label(claims, "P27", lang)
        movement = _extract_label(claims, "P135", lang)
        portrait_url = _extract_portrait(claims)

        return {
            "qid": qid,
            "name": name,
            "born": born or "?",
            "died": died or "?",
            "age": age or "?",
            "nationality": nationality or "?",
            "movement": movement or "?",
            "portrait_url": portrait_url,
        }
    except Exception:
        return {
            "qid": qid, "name": qid, "born": "?", "died": "?",
            "age": "?", "nationality": "?", "movement": "?", "portrait_url": None,
        }


def _extract_date(claims: dict, prop: str) -> str | None:
    try:
        val = claims[prop][0]["mainsnak"]["datavalue"]["value"]["time"]
        # Format: +1853-03-30T00:00:00Z
        parts = val.lstrip("+").split("T")[0].split("-")
        year, month, day = parts[0], parts[1], parts[2]
        from datetime import date
        months = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]
        m = months[int(month) - 1] if month != "00" else ""
        d = str(int(day)) if day != "00" else ""
        return " ".join(filter(None, [d, m, year]))
    except Exception:
        return None


def _calc_age(born: str | None, died: str | None) -> str | None:
    try:
        by = int(born.split()[-1])
        dy = int(died.split()[-1]) if died and died != "?" else None
        if dy:
            return str(dy - by)
        from datetime import date
        return str(date.today().year - by)
    except Exception:
        return None


def _extract_label(claims: dict, prop: str, lang: str) -> str | None:
    """Resolve a claim's value QID to a human-readable label."""
    try:
        qid = claims[prop][0]["mainsnak"]["datavalue"]["value"]["id"]
        params = {
            "action": "wbgetentities",
            "ids": qid,
            "languages": f"{lang}|en",
            "props": "labels",
            "format": "json",
        }
        r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
        labels = r.json()["entities"][qid]["labels"]
        return (
            labels.get(lang, {}).get("value")
            or labels.get("en", {}).get("value")
        )
    except Exception:
        return None


def _extract_portrait(claims: dict) -> str | None:
    """Get the Wikimedia Commons portrait image URL."""
    try:
        filename = claims["P18"][0]["mainsnak"]["datavalue"]["value"]
        filename = filename.replace(" ", "_")
        # Build Commons thumbnail URL (800px)
        import hashlib
        md5 = hashlib.md5(filename.encode()).hexdigest()
        return (
            f"https://upload.wikimedia.org/wikipedia/commons/thumb/"
            f"{md5[0]}/{md5[0:2]}/{filename}/800px-{filename}"
        )
    except Exception:
        return None


def _get_wikipedia_extract(qid: str, lang: str) -> str:
    """Get a one-paragraph bio from Wikipedia in the correct language."""
    api = WIKIPEDIA_API_FA if lang == "fa" else WIKIPEDIA_API_EN
    # First get the Wikipedia page title from Wikidata sitelinks
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "sitelinks",
        "sitefilter": f"{lang}wiki",
        "format": "json",
    }
    try:
        r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
        sitelinks = r.json()["entities"][qid].get("sitelinks", {})
        title = sitelinks.get(f"{lang}wiki", {}).get("title")
        if not title:
            # Fallback to English
            r2 = requests.get(WIKIDATA_API, params={
                **params, "sitefilter": "enwiki"
            }, headers=HEADERS, timeout=10)
            sitelinks2 = r2.json()["entities"][qid].get("sitelinks", {})
            title = sitelinks2.get("enwiki", {}).get("title")
            api = WIKIPEDIA_API_EN
        if not title:
            return ""
        # Now get the extract
        r3 = requests.get(api, params={
            "action": "query",
            "titles": title,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "exsentences": 3,
            "format": "json",
        }, headers=HEADERS, timeout=10)
        pages = r3.json()["query"]["pages"]
        page = next(iter(pages.values()))
        extract = page.get("extract", "")
        # Return first 300 chars cleanly
        return extract[:300].strip() + ("..." if len(extract) > 300 else "")
    except Exception:
        return ""


def fuzzy_suggest(name: str, candidates: list[str]) -> list[str]:
    """Return close string matches for typo correction."""
    return get_close_matches(name, candidates, n=3, cutoff=0.5)
