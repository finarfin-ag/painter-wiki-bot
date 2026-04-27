import requests
import random
import hashlib

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "PainterBot/1.0 (Telegram Bot; educational project)"}


def _get_painter_category(painter_name: str) -> str | None:
    candidates = [
        f"Paintings by {painter_name}",
        f"Works by {painter_name}",
        f"Art by {painter_name}",
    ]
    for cat in candidates:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{cat}",
            "cmnamespace": 6,
            "cmlimit": 1,
            "format": "json",
        }
        try:
            r = requests.get(COMMONS_API, params=params,
                             headers=HEADERS, timeout=10)
            members = r.json()["query"]["categorymembers"]
            if members:
                return cat
        except Exception:
            continue
    return None


def _search_commons_files(painter_name: str, offset: int = 0,
                           limit: int = 10) -> dict:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"file:{painter_name} painting",
        "srnamespace": 6,
        "srlimit": limit,
        "sroffset": offset,
        "format": "json",
    }
    try:
        r = requests.get(COMMONS_API, params=params,
                         headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        total = data["query"]["searchinfo"]["totalhits"]
        results = data["query"]["search"]
        works = _parse_results(results)
        return {"total": total, "offset": offset, "works": works}
    except Exception:
        return {"total": 0, "offset": 0, "works": []}


def _get_category_files(category: str, offset: int = 0,
                         limit: int = 10) -> dict:
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmnamespace": 6,
        "cmlimit": limit,
        "format": "json",
    }
    if offset:
        params["cmoffset"] = str(offset)
    try:
        r = requests.get(COMMONS_API, params=params,
                         headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        members = data["query"]["categorymembers"]
        params2 = {**params, "cmlimit": 500}
        params2.pop("cmoffset", None)
        r2 = requests.get(COMMONS_API, params=params2,
                           headers=HEADERS, timeout=10)
        total = len(r2.json()["query"]["categorymembers"])
        works = _parse_results(members)
        return {"total": total, "offset": offset, "works": works}
    except Exception:
        return {"total": 0, "offset": 0, "works": []}


def _parse_results(results: list) -> list[dict]:
    works = []
    for item in results:
        title = item.get("title", "")
        filename = title.replace("File:", "").replace(" ", "_")
        if not filename:
            continue
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in ("jpg", "jpeg", "png", "gif", "tif", "tiff", "webp"):
            continue
        thumb = _build_thumb_url(filename, 320)
        clean_title = title.replace("File:", "").rsplit(".", 1)[0]
        works.append({
            "title": clean_title,
            "filename": filename,
            "thumb_url": thumb,
        })
    return works


def get_paintings(painter_name: str, offset: int = 0,
                   limit: int = 10) -> dict:
    cat = _get_painter_category(painter_name)
    if cat:
        return _get_category_files(cat, offset, limit)
    return _search_commons_files(painter_name, offset, limit)


def get_random_paintings(painter_name: str, count: int = 5) -> list[dict]:
    result = get_paintings(painter_name, offset=0, limit=50)
    works = result.get("works", [])
    if len(works) <= count:
        return works
    return random.sample(works, count)


def search_specific_painting(painter_name: str,
                               painting_title: str) -> list[dict]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f'"{painting_title}" "{painter_name}"',
        "srnamespace": 6,
        "srlimit": 5,
        "format": "json",
    }
    try:
        r = requests.get(COMMONS_API, params=params,
                         headers=HEADERS, timeout=10)
        r.raise_for_status()
        results = r.json()["query"]["search"]
        return _parse_results(results)
    except Exception:
        return []


def get_image_sizes(filename: str) -> dict:
    return {
        "small": _build_thumb_url(filename, 320),
        "medium": _build_thumb_url(filename, 800),
        "large": _build_thumb_url(filename, 1920),
        "original": _build_original_url(filename),
    }


def _build_thumb_url(filename: str, width: int) -> str:
    filename = filename.replace(" ", "_")
    md5 = hashlib.md5(filename.encode()).hexdigest()
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext in ("pdf", "djvu", "ogg", "ogv", "webm"):
        return _build_original_url(filename)
    return (
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/"
        f"{md5[0]}/{md5[0:2]}/{filename}/{width}px-{filename}"
    )


def _build_original_url(filename: str) -> str:
    filename = filename.replace(" ", "_")
    md5 = hashlib.md5(filename.encode()).hexdigest()
    return (
        f"https://upload.wikimedia.org/wikipedia/commons/"
        f"{md5[0]}/{md5[0:2]}/{filename}"
    )
