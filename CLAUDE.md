# 1645 9th St, Berkeley — renovation project

Working files for evaluating and planning a renovation of a 1919 bungalow in Northwest Berkeley.

## Links

- **Subject property (1645 9th St):** https://www.zillow.com/homedetails/1645-9th-St-Berkeley-CA-94710/24838128_zpid/
- **Renovation reference (2435 Valley St):** https://www.zillow.com/homedetails/2435-Valley-St-Berkeley-CA-94702/24835270_zpid/
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
- 11 rear enclosed porch (unfinished)
- 13, 14 bathroom (14 looks east out the bath door: furnace grate in the hall, cased opening into the front-right room beyond)
- 15, 16, 17 bedroom 1 (rear-right, door to the rear porch)
- 18, 19, 20 bedroom 2 (rear, sliding door to deck; door to bedroom 1 in the rear-east corner; the furnace grate in the foreground is in the hall, which is open to this room)

## Floor plans

- `floor-plan/existing.png` / `.svg` — the house as listed
- `floor-plan/proposed.png` / `.svg` — current proposal
- `floor-plan/generate.py` — generates both SVGs; edit this, run it, then re-export PNGs with headless Chrome (see below)
- `index.html` — shareable page with an existing/proposed toggle and both photo galleries, published at https://keithmancuso.github.io/1645-9th-st/

The existing plan was reconstructed from the listing photos only, not measured. Treat room sizes as ±2 ft. Layout as drawn: living room front-left, with the built-in, the brick fireplace (flush on the far side) and the door to the front porch along its east wall; the living room connects to the hall through an inset cased doorway in an alcove at its north-east corner (photos 04, 07); the hall's west end is the bath door with the floor furnace grate right outside it (photo 14), and a cased opening on the hall's east side leads into the front-right room; enclosed front porch front-right; **kitchen behind the porch (front-right, ≈11×12)**, entered from the hall through a cased opening; small central hall open to the rear-left room; narrow bathroom on the left (tub along the long wall, toilet under the west window, door at the east end); **bedroom 1 rear-right (≈13×12) with a door to the rear porch, reached through a door in the rear corner of bedroom 2** (photo 18); bedroom 2 rear-left (≈12×12) with a slider to the deck; unfinished enclosed rear porch off bedroom 1. Bathroom position and door placements are the least certain parts.

Correction, Sept 9: the first draft had the kitchen and bedroom 1 swapped (kitchen rear-right, bedroom 1 front-right). Keith confirmed after the walkthrough that the front-right room is the kitchen today. Room sizes still need checking against a real plan; none was found in the listing or the disclosure package. The first draft also drew a 2 ft double wall between the two rear rooms; there was no evidence for it, so it is now one wall with a single door in the rear corner, where photo 18 shows it. The same photo shows no closet in that corner, so the bedroom 2 closet from the first draft is gone.

### Proposed changes (as of Sept 9, 2026)

1. **Kitchen moves to the rear-left room with the slider** so it opens directly onto the deck (eat-in, ≈12×12). Reason: don't want to walk through a bedroom to reach the yard. The new kitchen shares its south wall with the bathroom, so the wet wall is shared.
2. **Old kitchen (front-right, ≈11×12) becomes bedroom 1.** Its plumbing gets abandoned.
3. **Rear-right bedroom stays a bedroom** and becomes bedroom 2 (≈13×12) with a closet added on the hall wall. It keeps the existing corner door, which now opens from the kitchen; a door from the hall would need the hall's east wall opened. Range goes on the west wall with the sink; the corner door rules out a run on the back wall.
4. **Rear porch becomes laundry / mudroom**, still opening onto the deck; water heater relocates there. Open question: entered from bedroom 2, the deck only, or both.
5. Living room, bath, hall, front porch unchanged in this pass. Bedroom 1 (old kitchen) is entered from the hall through the existing cased opening; hang a door there.

Open questions: verify room sizes and door placements on the next visit (no measured plan exists); confirm whether the termite report's "rear half bathroom" means there is a second sink/half bath in the rear porch area, which now sits off bedroom 1. The floor furnace is red-tagged by PG&E (Aug 2026) and comes out; heating will be mini-splits (see `BUDGET.md`). The proposed sheet omits the furnace for that reason.

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
  for v in existing proposed; do "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size=688,1046 --screenshot="$PWD/$v.png" "file://$PWD/$v.svg"; done
  ```
- On Linux (Claude Code on the web), export PNGs with Playwright's headless shell instead; the `chromium --headless=new` binary there clips the bottom ~90 px of the sheet:

  ```
  for v in existing proposed; do /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size=688,1046 --screenshot="$PWD/$v.png" "file://$PWD/$v.svg"; done
  ```

- `index.html` galleries are static lists; regenerate if photos are added.
