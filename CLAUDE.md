# 1645 9th St, Berkeley — renovation project

Working files for evaluating and planning a renovation of a 1919 bungalow in Northwest Berkeley.

## Links

- **Subject property (1645 9th St):** https://www.zillow.com/homedetails/1645-9th-St-Berkeley-CA-94710/24838128_zpid/
- **Renovation reference (2435 Valley St):** https://www.zillow.com/homedetails/2435-Valley-St-Berkeley-CA-94702/24835270_zpid/
- **Contractor brief:** `contractor-brief.html` — shareable walkthrough brief (disclosure summary, sequenced scope, questions, walkthrough checklist, both plans inlined). Planning estimates are hidden behind a toggle so the page can go to a contractor as-is. Floor plans are pasted in from `floor-plan/*.svg`; re-paste if the plans change.
- **Budget and offer position:** `BUDGET.md` — hard cap $1M all-in; lean scope ~$330–485k; offer ~$575k. Summarizes the seller's disclosure package (PDF is in the iCloud folder, not this repo).

## Subject property — 1645 9th St, Berkeley, CA 94710

| | |
|---|---|
| Price | $649,000 (listed Sept 2026, MLS #41147140) |
| Beds / baths | 2 / 1 |
| Living area | 734 sq ft |
| Lot | 2,613 sq ft |
| Built | 1919 |
| Type | Single-family, single story, no garage, 1 off-street space, rear deck |
| Condition | Listed as a fixer |
| Listing agent | Lela Logene Butler, Better Homes and Gardens / Reliance Partners, (510) 701-4344 |

Listing description: "This is a Fixer with loads of potential located in a nice Northwest Berkeley location. It is close to 4th Street shops, Whole Foods Market, the Berkeley Marina, North Berkeley BART and Highway 80. HES score 8."

Photos: `photos/1645-9th-st/` (21 images, Zillow gallery order, ~1440x960).

Rough photo index:
- 01–03 front exterior, 05 side yard, 21 backyard and deck
- 04, 06, 07, 09 living room (brick fireplace, built-ins, picture rail)
- 08, 10, 12 kitchen (front-right room behind the porch; tile counter, water heater in kitchen)
- 11 rear enclosed porch (shelves, plywood floor, small high window, door from bedroom 1)
- 13, 14 bathroom (14 looks east out the bath door across the hall: furnace grate, kitchen door beyond)
- 15, 16, 17 bedroom 1 (rear-right; door to the rear porch, closet beside it recessed into the back wall)
- 18, 19, 20 bedroom 2 (rear-left, sliding door to deck; the door beside the slider in the rear-east corner is a closet, not a door into bedroom 1; 20 looks toward the hall opening)

## Floor plans

- `floor-plan/existing.png` / `.svg` — the house as listed
- `floor-plan/proposed.png` / `.svg` — current proposal
- `floor-plan/generate.py` — generates both SVGs; edit this, run it, then re-export PNGs with headless Chrome (see below)
- `index.html` — shareable page with an existing/proposed toggle and both photo galleries, published at https://keithmancuso.github.io/1645-9th-st/

The existing plan was reconstructed from the listing photos and Keith's walkthrough notes, not measured. Treat room sizes as ±2 ft.

Layout as drawn (Sept 11 revision, from all 21 photos and Keith's two walkthroughs; the closets were measured on the second, nothing else was):

- **Living room** front-left, ≈15×13. East wall, north to south: shallow brick fireplace (flush on the far side), door to the enclosed front porch. A cased opening at the east end of its north wall is the start of the hall.
- **Hall**: a straight 3 ft corridor from the living room north into the rear-left room, cased at both ends, with the red-tagged floor furnace grate in its floor (photos 09, 12, 14, 20). Bath door on its west side. On its east side it widens into a ≈3×5 bay (the strip Keith first read as part of the kitchen); the kitchen door is on the bay's east wall, opposite the bath, and bedroom 1's door is in the bay's north wall, right beside the rear-left opening, so from the living room you see the two side by side.
- **Bath** ≈10.5×5 on the west of the hall: door at the east end; from it, vanity on the south wall, tub on the north wall with its end at the door, toilet under the west window.
- **Kitchen** front-right, ≈10×14, the room behind the porch, entered by its door off the hall bay. Tile counter and sink under the east window, range and water heater on the porch wall with a small high window into the porch, fridge beside them, side door in the east wall near the kitchen door out to the gravel side yard.
- **Bedroom 2** rear-left, ≈13×12: slider centered on the back wall onto the deck, window on the west wall. A ≈3.5×5 closet (measured 3'5" × 4'11") in its rear-east corner, entered by a door in the east wall beside the slider; the closet itself sits in bedroom 1's rear-west corner. No door between the bedrooms.
- **Bedroom 1** rear-right, ≈12×12: entered from the hall bay by the door beside the rear-left opening; door into the rear porch, east window, and a closet about the same size as bedroom 2's recessed into the porch bay beside the porch door. The partition between the rear rooms lines up with the hall's east wall; the rear-left room is a little wider than the rear-right one.
- **Rear porch** ≈4.5×8, enclosed, on the east end of the back wall, flush with the deck edge (the bump-out is ≈8 wide, but bedroom 1's closet takes its east side, which is why it reads as narrow); shelves, plywood floor, small high window, door to the deck.
- **Deck** ≈18×8 from the west edge of the house to the porch, so it runs past bedroom 2 and along part of bedroom 1's back wall; stairs off its west end drop into the side yard in line with the back wall.

The lot is drawn from photos 01, 03, 05 and 21 and the listed 2,613 sq ft: about 41.5 ft wide (a 12 ft dirt driveway on the west running from the curb to a gate near the house's rear corner, a 3.5 ft gravel side yard on the east with its own gate at the back of the porch) by roughly 70 ft deep (that is more area than the listed 2,613 sq ft, so one of the two is off), with roughly 18 ft of bare backyard behind the deck and 10 ft of gravel front yard to the sidewalk. None of that is measured.

### Proposed changes (as of Sept 9, 2026; door and closet corrections Sept 11)

1. **Kitchen moves to the rear-left room with the slider** so it opens directly onto the deck (eat-in, ≈13×12). Reason: don't want to walk through a bedroom to reach the yard. The new kitchen shares its south wall with the bathroom, so the wet wall is shared. Its corner closet stays as a pantry.
2. **Old kitchen (front-right, ≈10×14) becomes bedroom 1.** Entered through the old kitchen door off the hall bay. No door between the bedrooms. Its plumbing gets abandoned.
3. **Rear-right bedroom stays a bedroom** and becomes bedroom 2 (≈12×12). It keeps its hall door, its door into the rear porch and its closet. Bedroom 1 needs a closet.
4. **Rear porch becomes laundry / mudroom** (≈8×8), reached from bedroom 2 and from the deck; washer, dryer and water heater in it.
5. Living room, bath, hall, front porch unchanged. Floor furnace comes out; mini-splits.

Open questions: measure the rooms on the next visit (only the closets are measured); confirm whether the termite report's "rear half bathroom" means there is a second sink/half bath in the rear porch area, which sits off the rear-right bedroom. The floor furnace is red-tagged by PG&E (Aug 2026) and comes out; heating will be mini-splits (see `BUDGET.md`). 

## Renovation reference — 2435 Valley St, Berkeley, CA 94702

A comparable Berkeley cottage that has already had the kind of renovation we want for 9th St.

| | |
|---|---|
| Price | $995,000 (MLS #41146132) |
| Beds / baths | 2 / 1 |
| Living area | 1,067 sq ft |
| Lot | 3,484 sq ft |
| Built | 1908 |

Features called out in the listing that we like: coved ceilings, wainscoting, refinished oak floors, gas fireplace insert, eat-in kitchen with Fisher & Paykel range, added skylights and raised ceilings, rear expansion.

Photos: `photos/2435-valley-st-reference/` (87 images, Zillow gallery order, 1536x1152).

## Conventions

- Photo filenames are the Zillow gallery position, zero-padded. Do not renumber.
- `floor-plan/generate.py` is the source of truth for the plans. After editing, run:

  ```
  cd floor-plan && python3 generate.py
  for v in existing proposed; do "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size=720,1237 --screenshot="$PWD/$v.png" "file://$PWD/$v.svg"; done
  ```
- On Linux (Claude Code on the web), export PNGs with Playwright's headless shell instead; the `chromium --headless=new` binary there clips the bottom ~90 px of the sheet:

  ```
  for v in existing proposed; do /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size=720,1237 --screenshot="$PWD/$v.png" "file://$PWD/$v.svg"; done
  ```

- `index.html` galleries are static lists; regenerate if photos are added.
- **Pull requests: always auto-merge.** Once a PR is pushed and mergeable, mark it ready and merge it into `main` without asking (Keith, Sept 12, 2026).
