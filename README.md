# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listing data for matches to a description, with optional size and price filters
- **Inputs:** 'description' (str), 'size' (str or None), 'max_price' (float or None)
- **Returns:** A list of listing dicts, each with id, title, description, category, style_tags, size, condition, price, colors, brand, platform. Best keyword match first, at most SEARCH_RESULT_LIMIT. Size matches whole size tokens ("M" matches "S/M", "S" does not match "US 9"); "One Size" always matches.
- **When it has nothing:** Returns an empty list []

### `suggest_outfit`

- **What it does:** Suggests outfit combinations for a chosen item using the user’s wardrobe when available.
- **Inputs:** `new_item` (dict, one listing from search_listings), `wardrobe` (dict with an "items" list, which may be empty)
- **Returns:** A non-empty string with outfit suggestions.
- **When it has nothing:** Returns general styling advice when the wardrobe is empty.

### `create_fit_card`

- **What it does:** Writes a 2–4 sentence social-media caption for the item and outfit, mentioning the item, its price and its platform once each.
- **Inputs:** 'outfit' (str), 'new_item' (dict)
- **Returns:** A string caption with the item and outfit details of 2-4 sentences.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a fallback caption built from the title, price and platform, without calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings returns an empty list, put a message in session["error"] naming what the user could change (description, size, or price) and stop without calling suggest_outfit. Otherwise take the first result, put it in session["selected_item"], and go to suggest_outfit.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`. "$30", "under $30" or "below $25" becomes `max_price`. "size M", "size US 9", "size W30", or a trailing ", M" becomes `size`. Whatever is left becomes `description`. Size has to come after "size" or a trailing comma, so "medium wash jeans" doesn't get parsed as size M. I chose regex because it's free and gives the same answer every time. The trade-off: "under thirty dollars" isn't recognized, so no price ceiling is set and those words stay in the description.

**What moves through the session:** `query` → `parsed` (description, size, max_price) → `search_results` → `selected_item` (the first result) → `outfit_suggestion` → `fit_card`. If the search comes back empty, `error` gets set and `selected_item`, `outfit_suggestion` and `fit_card` all stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two effortless ways to style your new Y2K butterfly baby tee using pieces from your wardrobe:

**Outfit 1: High-Contrast Y2K Streetwear**
*   **Top:** Y2K Baby Tee — Butterfly Print
*   **Bottoms:** Baggy straight-leg jeans, dark wash
*   **Outerwear:** Vintage black denim jacket (worn off the shoulders for that true 2000s vibe)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* The fitted, cropped silhouette of the baby tee balances out the voluminous dark wash jeans, while the black denim jacket and white sneakers tie the whole cool, casual look together.

**Outfit 2: Elevated Model-Off-Duty**
*   **Top:** Y2K Baby Tee — Butterfly Print
*   **Bottoms:** Wide-leg khaki trousers
*   **Accessories:** Brown leather belt + Black crossbody bag
*   **Shoes:** Black combat boots
*   *Why it works:* Pairing the ultra-feminine, pink-and-purple butterfly tee with structured khaki trousers creates a great high-low mix. Cinch the trousers with your brown leather belt and anchor the outfit with the black combat boots for a slightly edgy finish.

  Fit card: Found this adorable butterfly baby tee for just $18 on Depop and I'm obsessed with the print. I've been living for the Y2K streetwear vibe lately, so styling it with baggy dark wash jeans and an off-the-shoulder vintage jacket is my new go-to. It also looks super cool dressed down with wide-leg trousers and combat boots for that effortless model-off-duty look!

0 model calls this session, 2 served from cache
```

**The empty path** (stops before `suggest_outfit`; `fit_card` stays `None`):

```
$ python agent.py
...
=== A query it can't ===
  stopped: Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
  fit_card is None — it should still be None here
```

**The three tools, tested one at a time**

`search_listings`, a query that matches (6 results; the first two shown in full, the other four trimmed to id / title / size / price):

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, ...]
  ... lst_017 Mesh Long-Sleeve Top — Black (S/M, $15.0)
  ... lst_033 Vintage Band Tee — Faded Grey (L, $19.0)
  ... lst_011 Low-Rise Cargo Pants — Khaki (W29, $27.0)
  ... lst_015 Vintage Graphic Hoodie — Faded Black (L, $26.0)
```

`search_listings`, the empty case (returns an empty list, not None):

```
$ python -c "from tools import search_listings; print(search_listings('ballgown', size='XXS', max_price=5))"
[]
```

`suggest_outfit`, with the example wardrobe:

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two effortless, everyday outfits built around your new vintage Levi’s 501s and pieces you already own:

**1. The Off-Duty Cool Look**
*   **Top:** White ribbed tank top
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag, Brown leather belt
*   **Why it works:** Tuck the white ribbed tank into the 501s, cinch it with the brown leather belt, and layer the vintage black denim jacket on top. Finish with chunky white sneakers and the black crossbody bag for an effortless, high-contrast 90s-inspired street style.

**2. The Cozy & Edgy Look**
*   **Top:** Oversized grey crewneck sweatshirt (or layer the Black cropped zip hoodie over the White ribbed tank top)
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt, Black crossbody bag
*   **Why it works:** Pair the medium wash 501s with the oversized grey crewneck for a relaxed silhouette. Cinch the waist with the brown leather belt to add shape, and ground the look with black combat boots and the black crossbody bag for a cool, grungy edge.
```

`suggest_outfit`, the empty-wardrobe case (general advice instead of a crash; trimmed):

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
Vintage Levi’s 501s in a medium wash are the ultimate wardrobe holy grail—they are timeless, incredibly versatile, and the light knee-fading gives them that effortless, "broken-in" feel right out of the box.

Here are two distinct, practical ways to style these jeans:

### Outfit 1: The Parisian-Chic Casual (Effortless & Elevated)
* **Top:** A fitted, long-sleeve black-and-white striped Breton tee, slightly tucked in to highlight the waist of the 501s.
* **Footwear:** Pointed-toe black leather ankle boots (which peek out neatly from the hem) or classic black leather ballet flats.
...
```

`create_fit_card`:

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Still not over finding these vintage Levi's 501 jeans for just $38 on depop. Threw them on with my beat-up white sneakers and a simple tee for the ultimate effortless 90s coffee run fit. Nothing beats breaking in a real pair of vintage denim.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked an AI assistant to explain the code in `agent.py` so I could understand what `run_agent` needed to do before writing it myself.
- *What came back:* It didn't just explain. It went ahead and rewrote `agent.py`, adding `parse_query`, the branch, and `_nothing_found_message`. It also added code from the next unit: a `_search()` function that called `search_listings` over MCP and silently fell back to the local function, a `try/except ModelUnavailable` block, and trace labels saying "search_listings (via MCP)". My `mcp_server.py` doesn't register any tool yet, so every run quietly fell back, and the trace said MCP was being used when it wasn't. Its docstrings even said "In unit 3 this function does not exist."
- *What I changed:* I deleted `_search()` and made `run_agent` call `search_listings(parsed["description"], parsed["size"], parsed["max_price"])` directly. I also removed the MCP trace labels and the Unit 4 `try/except`. Then I read through `parse_query` and `run_agent` line by line and reran both paths to check that the branch and the session still worked.

**Moment 2**

- *What I asked for:* I asked Claude to review my uncommitted work and help me split it into one commit per milestone.
- *What came back:* It found that my Tool Inventory said `create_fit_card` mentions "brand, size, and price", but my code asks the model for the price and the platform. Brand is `None` for most listings, so the spec promised something the data often can't give. It also pointed out that my criterion 3 (state) targeted 4 of 5 without saying why it wasn't stricter.
- *What I changed:* I rewrote the `create_fit_card` spec to say the caption mentions the item, its price and its platform once each, and I added the listing fields to the `search_listings` return line. I also changed criterion 3 to 5 of 5, because the item passes through a dict with no model call in between, so any mismatch would be a bug rather than noise.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
