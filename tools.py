"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from","with", "in", "is", "it", "of", "on", "or", "that", "the", "to", "was",
}

def _keywords(text: str) -> set[str]:
    """
    Return a set of keywords from a string, lowercased and stripped of stopwords.

    Args:
        text: a string to extract keywords from
    """
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    """
    Return a set of tokens from a size string, lowercased and stripped of stopwords.

    Args:
        size: a size string to extract tokens from
    """
    cleaned = re.sub(r"\([^)]*\)", "", size or "")  # remove parenthetical content
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    """
    Return True if the wanted size matches the listing size, False otherwise.

    Args:
        wanted: the size string to match against
        listing_size: the size string from the listing
    """
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()
    wanted = _keywords(description)

    scored = []
    for item in listings:
        price = item.get("price")
        if max_price is not None and price is not None and price > max_price:
            continue

        item_size = item.get("size", "")
        if size is not None and not _size_matches(size, item_size):
            continue

        text = " ".join([
            item.get("title", ""),
            item.get("description", ""),
            " ".join(item.get("style_tags", [])),
            item.get("category", ""),
        ])
        overlap = wanted & _keywords(text)

        if not overlap:
            continue

        item_copy = dict(item)
        item_copy["_score"] = len(overlap)
        scored.append(item_copy)

    scored.sort(key=lambda item: item["_score"], reverse=True)

    for item in scored:
        item.pop("_score", None)

    return scored[: config.SEARCH_RESULT_LIMIT]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []
    title = new_item.get("title", "this thrifted item")
    description = new_item.get("description", "")
    category = new_item.get("category", "")
    colors = ", ".join(new_item.get("colors") or [])
    size = new_item.get("size", "")
    price = new_item.get("price")
    platform = new_item.get("platform", "")

    if not items:
        prompt = (
            f"You are a stylist. Suggest 1-2 outfit ideas for this thrifted item:\n"
            f"- title: {title}\n"
            f"- category: {category}\n"
            f"- description: {description}\n"
            f"- colors: {colors}\n"
            f"- size: {size}\n"
            f"- price: ${price} on {platform}\n\n"
            "Keep it practical, specific, and stylish. Give general styling advice "
            "without assuming the user owns any wardrobe pieces."
        )
        return generate(prompt, system="You are a helpful fashion stylist.", temperature=0.9)

    wardrobe_lines = []
    for item in items[:10]:
        name = item.get("name", "")
        category_name = item.get("category", "")
        colors_list = ", ".join(item.get("colors") or [])
        palette = item.get("palette", "")
        style = item.get("style", "")
        wardrobe_lines.append(
            f"- {name} ({category_name}; colors: {colors_list}; palette: {palette}; style: {style})"
        )

    prompt = (
        f"You are a stylist. Suggest 1-2 outfits built around this thrifted find:\n"
        f"- title: {title}\n"
        f"- category: {category}\n"
        f"- description: {description}\n"
        f"- colors: {colors}\n"
        f"- size: {size}\n"
        f"- price: ${price} on {platform}\n\n"
        "The user already owns these pieces:\n"
        + "\n".join(wardrobe_lines)
        + "\n\n"
        "Make the outfit suggestions specific and refer to the existing wardrobe pieces by name. "
        "Keep the answer concise but useful."
    )
    return generate(prompt, system="You are a helpful fashion stylist.", temperature=0.9)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        title = new_item.get("title", "this thrifted find")
        price = new_item.get("price")
        platform = new_item.get("platform", "")
        return (
            f"Found {title} for ${price} on {platform}. It has the kind of thrifted "
            "vibe that makes a basic outfit feel a little more intentional."
        )

    title = new_item.get("title", "this thrifted find")
    price = new_item.get("price")
    platform = new_item.get("platform", "")
    prompt = (
        f"Write a real social caption about this thrifted item and outfit.\n"
        f"The person posting BOUGHT this item. They are the buyer, not the seller.\n"
        f"Item: {title}\n"
        f"Price they paid: ${price}\n"
        f"Platform they bought it on: {platform}\n"
        f"Outfit idea: {outfit}\n\n"
        "Requirements:\n"
        "- 2 to 4 sentences total\n"
        "- sound like a real person posting a thrift find they bought\n"
        "- mention the item, price, and platform once each\n"
        "- never say or imply they are selling it, listed it, or have a shop; "
        "no 'grab it', 'link in bio', or 'before I change my mind'\n"
        "- be specific about the vibe and styling\n"
        "- do not sound like an ad or product description\n"
        "- avoid generic filler and keep it natural"
    )
    return generate(prompt, system="You are a social media caption writer.", temperature=0.9)
