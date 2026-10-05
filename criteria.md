# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

The search should be good enough to find at least one real listing most of the time, but not perfect. The listing data is limited and some user phrasing will miss the exact wording in the dataset, so a 4 of 5 target is realistic while still meaning the agent is doing the main flow correctly.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling `suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

This path is much easier to control than the matching-query path because the search has no valid result to work with. The branch should always terminate cleanly and explain whether the user should change the description, size, or price limit, so a 5 of 5 target is appropriate here.

---

## 3. The selected item is the same one that reaches the next tool

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

Given a query that matches at least one listing, the item stored in `session["selected_item"]` is the same listing passed into `suggest_outfit`, and the ID matches in at least 5 of 5 tries.

**Why this target:**

The item moves through a plain dict, with no model call between the search and the next tool, and the query is parsed with regex, so the same query always selects the same item. Nothing random happens on this path, which means a single mismatch would be a bug in the loop rather than noise. That's why the target is 5 of 5 and not 4 of 5.

---

## 4. The fit card mentions the item details and varies by item

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

Given five different matching listings, the fit card mentions the item price and platform in at least 4 of 5 tries, and the fit cards do not reuse the same opening sentence in at least 4 of 5 tries.

**Why this target:**

A fit card is not just a model response — it has to read like a real caption. If it omits the price or platform, it reads like a generic description. If the first sentence is identical across different items, it is acting like a template instead of a real post.

---

## 5. An empty wardrobe still produces styling advice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

Given a user with an empty wardrobe, `suggest_outfit` still returns a non-empty styling suggestion in 5 of 5 tries.

**Why this target:**

The empty-wardrobe path is a real user behavior in this project, and the starter explicitly says to handle it instead of crashing or returning an empty string. This is a simple and reliable check that the tool still works when the wardrobe has no saved items.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
