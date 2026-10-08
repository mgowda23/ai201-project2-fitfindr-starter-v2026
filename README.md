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

FitFindr takes a plain-language request like "vintage graphic tee under $30, size M" and searches a set of thrift listings for matches on description, size and price. It picks the best match, suggests one or two outfits using the user's own wardrobe (or general advice if the wardrobe is empty), and writes a short caption they could actually post. If nothing matches, it stops before the outfit step and says what to change: broader words, a different size, or a higher price ceiling.

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

Full output: [results/run_2026-10-07_2144_before.md](results/run_2026-10-07_2144_before.md), from `python run_eval.py --label before` (cache off, temperature 0.9, 9 scenarios × 5 tries, 80 model calls).

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item is the one the next tools receive | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card names price + platform; no reused opening across items | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe still gets styling advice | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**How I scored each try:**
1. PASS if the run wasn't stopped early, the trace shows all five steps, and `fit_card` is non-empty.
2. PASS if the run stopped early, the trace ends at `branch` with no `suggest_outfit` step, and the message names what to change.
3. PASS if the title in `select_item`'s output equals the title `suggest_outfit` received, and `create_fit_card` received the same `lst_` id.
4. Criterion 4 is about five *different* items, so it has five scenarios (items A–E: lst_002, lst_022, lst_011, lst_007, lst_013). Try N in this row is Try 1 of item N. A try PASSES if the card contains the price and the platform, and its first sentence isn't used by any of the other four cards.
5. PASS if `outfit_suggestion` is non-empty with the empty wardrobe and nothing crashed.

**Real output from one try per criterion**

Criterion 1, Try 1: `agent.py::run_agent` → fit card from `tools.py::create_fit_card`:

```
query: vintage graphic tee under $30   (example wardrobe)
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
Fit card:
Still lowkey obsessed I found this Y2K butterfly baby tee for just $18 on Depop. It’s so easy to dress down with baggy dark denim and chunky sneakers, or totally flip the vibe by pairing it with wide-leg trousers and combat boots. Such an effortless little piece to throw on when you don't know what to wear. ✨
```

Criterion 2, Try 1: the branch in `agent.py::run_agent`, message from `agent.py::_nothing_found_message`:

```
- stopped early: yes — Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
- selected_item: (none)
- search_results: 0

[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned [] so stopping early
```

Criterion 3, Try 1: trace from `agent.py::run_agent` (same item at steps 3, 4 and 5):

```
[3] select_item
      in:  6 items: 90s Leather Bomber — Black, 90s Track Jacket — Navy/White Stripe, Leather Belt — Brown, Braided … +3 more
      out: 90s Leather Bomber — Black ($75.0, depop)
[4] suggest_outfit
      in:  90s Leather Bomber — Black ($75.0, depop)
      out: Here are two effortless, grunge-meets-minimalist outfits built around your new 90s leather bomber and items fr…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  item lst_022 + outfit: Here are two effortless, grunge-meets-minimalist outfits built around your new 90s leat…
      out: Scored this vintage 90s leather bomber on Depop for $75 and I am never taking it off. It has that perfect boxy…
```

Criterion 4, Try 1 of each item: `tools.py::create_fit_card`:

```
A lst_002: Scored this vintage butterfly baby tee for just $18 on Depop and I'm obsessed with the early 2000s nostalgic vibe. ... Go grab it on my shop before I change my mind and keep it for myself!🦋✨
B lst_022: Found my ultimate fall jacket—this vintage 90s leather bomber was an absolute steal for $75 on Depop. ...
C lst_011: Scored these khaki low-rise cargos on Poshmark for just $27 and I’m so obsessed with the Y2K utilitarian vibe. ...
D lst_007: Score this light wash cropped denim jacket for just $42 on Poshmark and honestly, I’m obsessed. ...
E lst_013: Found this vintage 90s floral silk slip dress on Depop for just $30 and I'm obsessed with the print. ...
```

Criterion 5, Try 1: `tools.py::suggest_outfit` with an empty wardrobe:

```
query: denim jacket under $50   (empty wardrobe)
Outfit suggestion:
Here are two stylish, versatile ways to style this cropped light-wash denim jacket, playing up its structured shoulders and vintage feel:

### Look 1: The Modern Prep & Play
*A fresh, textural mix that balances the ruggedness of denim with refined, polished pieces.*

*   **Top:** A crisp white poplin button-down shirt, worn untucked so the longer hem peaks out beneath the cropped jacket for a cool, layered proportion play.
*   **Bottoms:** Pleated, wide-leg trousers in a rich camel or chocolate brown to anchor the light blue wash.
...
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
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five tries reached `create_fit_card` and returned a non-empty fit card; every trace has 5 steps. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET (5/5) | All five traces end at `[3] branch` with no `suggest_outfit` step, and the message names the description, the size and the price to change. |
| 3 | Selected item is the one the next tools receive | 5 of 5 | MET (5/5) | In all five traces, `select_item` output, `suggest_outfit` input and `create_fit_card` input are the same item (90s Leather Bomber, `lst_022`). |
| 4 | Fit card names price + platform; no reused opening across items | 4 of 5 | MET (5/5) | All five item cards (Try 1 of A–E) contain the price and the platform, and no two share a first sentence. |
| 4 (revised) | Fit card names price + platform and presents the user as the buyer, all 5 items | 5 of 5 | **MISSED (4/5)** | Scored over all 25 item cards (5 items × 5 tries). Try 1 failed: item A's card ends "Go grab it on my shop before I change my mind". Tries 2–5 had no seller wording on any item. |
| 5 | Empty wardrobe still gets styling advice | 5 of 5 | MET (5/5) | `outfit_suggestion` was non-empty in all five tries (1,731–2,312 characters of general advice), with no crash. |

**Diagnoses**

**Every original criterion was met, and I think some targets were too low.** Criterion 1 at 4 of 5 could never realistically miss: `search_listings` is a deterministic keyword match over a fixed file, and the parser is regex, so the same query finds the same item every time. The only real risk in that path is the model being unreachable, which is a separate failure mode. If I rewrote it, it would be 5 of 5. Criterion 4 was the weakest: it passed while the run showed a real problem, so I revised it in `criteria.md` (original left in place).

**Criterion 4 (revised): MISSED, 4/5. Place: the model's output, from `tools.py::create_fit_card`. The prompt allows it.**
The search, the branch and the session all worked. Every seller-worded card received the right item and the right outfit (criterion 3 shows the item reaching `create_fit_card` intact). The problem is the prompt. It tells the model to "sound like a real person posting a thrift find" and to "mention the item, price, and platform once each", but it never says *who* the person is relative to the item. Depop and Poshmark are both resale marketplaces, so "item + price + platform" is also exactly what a sales listing contains, and at temperature 0.9 the model sometimes writes one: "Finally found the ultimate Y2K butterfly baby tee and listed it on Depop for just $18!" (matching-query Try 4) and "Go grab it on my shop before I change my mind" (item A Try 1).

The pattern: both misses in the eval are the same listing, `lst_002` on Depop. The two seller captions I saw in earlier manual runs ("debating if I should keep them or list them on my Depop shop" for `lst_001`, and "over on my Depop shop" for `lst_002` again, with the empty wardrobe) were also Depop items. That's 4 seller captions in total, all Depop and none Poshmark, though 25 of the 40 eval cards were Depop and 15 Poshmark, so the Poshmark sample is smaller. It's one problem, not four: the prompt leaves the poster's role open, and the platform name pulls toward listing language.

**Not a criterion miss, but found while testing:** the captions are heavily templated. 35 of 40 contain "for just $", 27 of 40 say "obsessed", and 23 of 40 start with "Found" or "Still". None of my criteria measure this, and I'm not counting it as a miss. It's noted in What's Still Broken.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path** (5 steps; `search_listings` runs through MCP)

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      in:  10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are two effortless ways to style your new Y2K butterfly baby tee using pieces from your wardrobe:  **Outf…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  item lst_002 + outfit: Here are two effortless ways to style your new Y2K butterfly baby tee using pieces from…
      out: Found this adorable butterfly baby tee for just $18 on Depop and I'm obsessed with the print. I've been living…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
  ...
  Fit card: Found this adorable butterfly baby tee for just $18 on Depop and I'm obsessed with the print. I've been living for the Y2K streetwear vibe lately, so styling it with baggy dark wash jeans and an off-the-shoulder vintage jacket is my new go-to. It also looks super cool dressed down with wide-leg trousers and combat boots for that effortless model-off-duty look!
```

**Empty search** (3 steps; stops at the branch, so `suggest_outfit` and `create_fit_card` never run)

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned [] so stopping early

  Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.

0 model calls this session
```

**On the MCP move:** I registered `search_listings` in `mcp_server.py` with `@mcp.tool()`, keeping the same inputs as my Tool Inventory (`description` str, `size` str or None, `max_price` float or None); `python mcp_client.py` lists it with those three inputs. In `agent.py::run_agent` I replaced the direct `search_listings(...)` call with `call_tool("search_listings", {...})`. Nothing behaved differently afterwards: for `'graphic tee'` under $30, the MCP call returned the same 6 listing dicts as the direct call (compared with `==`, result `True`), and the impossible query still returns `[]` through MCP, so the branch didn't need to change.

### Failure modes, triggered on purpose

**1. Empty search.** Handled from the start by the branch in `agent.py::run_agent` (see the empty-search trace above). It stops before `suggest_outfit` and names the three things to change.

**2. Empty wardrobe.** Handled from the start by `tools.py::suggest_outfit`, which switches to a general-advice prompt when `wardrobe["items"]` is empty. No crash, and no empty string:

```
$ python app.py ask 'vintage graphic tee under $30' --empty-wardrobe
(running with an empty wardrobe)
...
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are two stylish, trend-forward ways to style this Y2K butterfly baby tee:  ### Look 1: The Off-Duty Model…
      →    0 wardrobe item(s)
...
  Outfit:   Here are two stylish, trend-forward ways to style this Y2K butterfly baby tee:

### Look 1: The Off-Duty Model (Casual & Edgy)
*Balance the sweet, feminine energy of the butterfly print with relaxed, utilitarian bottoms.*
* **Bottoms:** Low-rise, wide-leg cargo pants in a neutral shade like khaki, olive green, or grey.
...
```

**3. Model unavailable.** This one was **not** handled. With one character removed from the key in `.env`, `run_agent` had no `try/except`, so the exception escaped the loop. `app.py`'s catch-all printed it as one line, and the search results (6 listings) were lost:

```
$ AI201_CACHE=0 python app.py ask 'black leather jacket size M'
...
[3] selected_item
      out: {'id': 'lst_022', 'title': '90s Leather Bomber — Black', ...

ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```

Run directly as `python agent.py`, it would have been a full traceback, because nothing in the agent caught it. I wrapped the `suggest_outfit` and `create_fit_card` calls in `agent.py::run_agent` in `try / except ModelUnavailable`. The handler sets `session["error"]`, keeps the search results, and leaves `fit_card` as `None`. Same command, after:

```
$ AI201_CACHE=0 python app.py ask 'black leather jacket size M' --trace
...
[3] select_item
      out: 90s Leather Bomber — Black ($75.0, depop)
[4] model unavailable
      →    stopping; search results kept in the session

  The model couldn't be reached, so the outfit and caption steps didn't run.
The search still worked: 6 listing(s) found, best match 90s Leather Bomber — Black ($75.0 on depop).
What to try: check GEMINI_API_KEY in your .env (run `python test.py` to confirm it works), then run the same query again.
What the service said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** One prompt, in `tools.py::create_fit_card`. Nothing else changed: the scenarios, search, loop and temperature (0.9) were all the same. The prompt now says outright that the poster is the buyer. I relabelled the inputs from "Price" / "Platform" to "Price they paid" / "Platform they bought it on", and added one requirement:

```diff
  f"Write a real social caption about this thrifted item and outfit.\n"
+ f"The person posting BOUGHT this item. They are the buyer, not the seller.\n"
  f"Item: {title}\n"
- f"Price: ${price}\n"
- f"Platform: {platform}\n"
+ f"Price they paid: ${price}\n"
+ f"Platform they bought it on: {platform}\n"
  ...
- "- sound like a real person posting a thrift find\n"
+ "- sound like a real person posting a thrift find they bought\n"
  "- mention the item, price, and platform once each\n"
+ "- never say or imply they are selling it, listed it, or have a shop; "
+ "no 'grab it', 'link in bio', or 'before I change my mind'\n"
```

**Which failure it was meant to fix:** Criterion 4 (revised), which MISSED at 4/5. The diagnosis put the problem in the model's output: the prompt never said who the poster was relative to the item, so "item + price + platform" on a resale site sometimes came out as a sales listing ("listed it on Depop for just $18", "Go grab it on my shop before I change my mind").

### Run Log — After

Full output: [results/run_2026-10-08_1602_after.md](results/run_2026-10-08_1602_after.md), from `python run_eval.py --label after` (cache off, temperature 0.9, 9 scenarios × 5 tries). Scored exactly the same way as the before run.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item is the one the next tools receive | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card names price + platform; no reused opening across items | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4 (revised). Price + platform, user presented as the buyer, all 5 items | 5 of 5 | PASS | PASS | PASS | PASS | PASS | **MET (5/5)**, was MISSED (4/5) |
| 5. Empty wardrobe still gets styling advice | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Real output, criterion 4 (revised), item A (`lst_002`, the item that failed before), Try 1, from `tools.py::create_fit_card`:

```
Before: Scored this vintage butterfly baby tee for just $18 on Depop and I'm obsessed with the early 2000s nostalgic vibe. ... Go grab it on my shop before I change my mind and keep it for myself!🦋✨
After:  Scored this vintage butterfly baby tee on Depop for just $18, and I’m so obsessed. I already planned two ways to style it, ranging from baggy dark-wash denim for classic Y2K street style to sharp khak…
```

**Did it help, and how do I know:**

It fixed the problem it targeted, but it made the captions more repetitive, and I can't fully prove the fix from one run.

- **Seller wording went from 2 of 40 cards to 0 of 40.** Revised criterion 4 went from MISSED (4/5) to MET (5/5), and every card still names the price and the platform (40/40, same as before). Item A, the one that failed before, came back as a buyer's post in all 5 tries.
- **The evidence is real but thin.** Seller wording only happened in 2 of 40 cards before (5%), so a clean run of 40 is what I'd hope to see if the fix worked, but it isn't proof. If the true rate had stayed at 5%, a run of 40 with zero seller cards would still happen about 13% of the time. Several more runs would be needed to be sure.
- **Side effect: the captions got more templated.** Before, openings were spread out ("Found" 14, "Still" 9, "Scored" 7, "Score" 6, other 4). After, **36 of 40 cards open with "Scored"**. Telling the model "they bought it" seems to have pulled every caption toward the same buyer verb. "obsessed" went from 27 to 30 of 40, and "for just $" from 35 to 29. The original criterion 4 still passes, because the first sentences differ by item name, which is exactly why I said in Milestone 4 that it measures the wrong thing. Two cards for the same item (`lst_002`) now share an identical first sentence, e.g. "Scored this Y2K butterfly baby tee on Depop for just $18 and I am officially obsessed."
- **Everything else held.** Criteria 1, 2, 3 and 5 are MET (5/5) in both runs. The prompt change didn't touch the search, the branch or the session.

**About the two runs marked OUTAGE:** my first two attempts at this run happened while Gemini was returning `503 UNAVAILABLE: This model is currently experiencing high demand`. Only 12 and 14 of 40 model tries got through. I kept the first as [results/run_2026-10-08_1358_after_OUTAGE.md](results/run_2026-10-08_1358_after_OUTAGE.md) and deleted the second, which showed the same thing. I didn't score either, because they measure the outage, not the prompt. They were a real-world test of the Milestone 2 handler, though: in the kept file, all 28 failed tries end with "The model couldn't be reached… The search still worked…" and none crashed. I reran once the model answered 6 test calls in a row.



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [x] criteria.md has five numbered criteria, each with a target
       [x] Each criterion has a reason underneath it
       [x] All five unit 3 sections above have real content
       [x] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [x] Planning Loop names the branch rule and agent.py::run_agent
       [x] Sample Run: one full query plus the three per-tool tests, as text
       [x] At least four new commits
       [x] Repository URL submitted — WRITE IT DOWN, you submit the same one
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
