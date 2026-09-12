# 1645 9th St, Berkeley — renovation project

Working files for evaluating and planning a renovation of a 1919 bungalow in Northwest Berkeley.

## Links

- **Subject property (1645 9th St):** https://www.zillow.com/homedetails/1645-9th-St-Berkeley-CA-94710/24838128_zpid/
- **Renovation reference (2435 Valley St):** https://www.zillow.com/homedetails/2435-Valley-St-Berkeley-CA-94702/24835270_zpid/
- **Budget and offer position:** `BUDGET.md` — hard cap $1M all-in; lean scope ~$330–485k; offer $650k (list) as of Sept 10, 2026, which only fits the cap at the low end of lean scope. Summarizes the seller's disclosure package (PDF is in the iCloud folder, not this repo).

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
- 08, 10, 12 kitchen (galley, tile counter, water heater in kitchen)
- 11 rear enclosed porch (unfinished)
- 13, 14 bathroom
- 15, 16, 17 bedroom 1 (front, east side)
- 18, 19, 20 bedroom 2 (rear, sliding door to deck)

## Floor plans

- `floor-plan/existing.png` / `.svg` — the house as listed
- `floor-plan/proposed.png` / `.svg` — current proposal (same rooms as existing; see below)
- `floor-plan/generate.py` — data model (centerline walls with thickness, standard doors with swings, windows, fixtures) that generates both SVGs and prints a room-size table; `floor-plan/export.sh` runs it and re-exports the PNGs
- `index.html` — shareable page with an existing/proposed toggle and both photo galleries, published at https://keithmancuso.github.io/1645-9th-st/

**Draft 4 (Sept 12, 2026) — Keith's sketch, scaled to measurements.** The topology is Keith's Freeform sketch and must not be re-derived from photos (that went badly twice). Coordinates in `generate.py` are feet: x 0 = outside face of the west wall, y 0 = outside face of the rear wall, y grows toward the street. Walls 6″ exterior / 5″ interior. Key lines are named constants at the top of `build()`; [M] in the code = measured.

Measured: bedroom 2's rear wall is 29½″ wall + 5′-5″ slider + 27″ wall = **10′-2″ wide** (the deck is the same width); bedroom 2 is 9′-2″ deep (24″ closet door on its east wall at the rear corner; hall door at the south-east corner); **bedroom 2's closet is 4′-11″ east-west × 3′-5″ north-south**; **bedroom 1 is 8′-2″ × 8′-9″**. The two bedroom widths plus walls make the house **≈19′-9″ wide** (not the 24′-6″ assumed earlier).

Layout: **one straight partition (the fireplace wall) runs the full depth.** West of it, rear to front: bedroom 2 (slider centered-ish on its rear wall, west window), bath with the 3′ hall beside it, living room (fireplace and built-in on the partition, entry door from the porch just south of the fireplace). East of it: the closet strip at the rear, 3′-5″ deep (bedroom 2's closet 4′-11″ wide entered from its east wall; bedroom 1's closet the remaining ≈2′-10″, entered from its north wall), bedroom 1 (window east), kitchen (hall door at the north end of its west wall, side door opposite it, fridge → range → water heater down the partition wall, sink counter east, small 6-lite window into the porch), front porch (projecting). Behind the house: deck (10′-2″, behind bedroom 2) and laundry/shed (behind the east side) side by side at the same depth; the laundry's only door is on its east side. **No hall between the bedrooms.** The hall is only the 3′ strip in front of the bath; the bath door faces the bedroom doors (bedroom 2's on the hall's north end, bedroom 1's on its east side); the kitchen door is on its east side further south and the living room opens off its south end. Floor furnace grate in the hall.

Still guesses: hall width (sets the bath width, drawn 6′-8″); closet depth; bath depth; living room depth; kitchen depth; porch depth and projection; deck/laundry depth; every window.

### Proposed changes (as of Sept 12, 2026)

Keith accepted the existing plan as "close enough" on Sept 12 and reset the proposal. **No rooms move and no walls change; the kitchen stays where it is.** (The earlier kitchen ⇄ bedroom 2 swap and the bath narrowing are dropped.)

1. **Water heater out of the kitchen.** A tankless unit goes on the wall in the laundry / shed (gas, vent, and water lines run from there); the freed corner beside the range becomes counter.
2. **Laundry stays in the shed** (W/D), which keeps its outside-only east door. Nothing else happens to it beyond making it a proper shed.
3. **Floor furnace out** (red-tagged by PG&E, Aug 2026); hall floor patched. Heat by ductless mini-splits with heads in the living room and both bedrooms, outdoor unit on the east side by the shed.
4. **Driveway and Level 2 EV charger** as before: concrete apron, parking pad on the porch side of the front yard, strip down that side to the back-yard gate, charger on the porch wall facing the pad (40–50 A circuit from the new 200 A panel, folded into the rewire). Not drawn on the plan. Which side of the house the driveway is on still needs confirming against photos 02 and 21.
5. Living room, bedrooms, bath, hall, front porch unchanged.

Models: `floor-plan/` (SVG/PNG), `render/scene.py` (Blender/Cycles stills in `render/out/`), `3d/index.html` (self-contained three.js walkthrough; rebuild with `Blender -b render/house.blend -P render/export_gltf.py && python3 3d/build.py`). **`render/` and `3d/` still use the old 26×30 photo-estimated plan and are stale; rebuild them from the current generator geometry (19′-9″ wide, single partition) when needed.**

Open questions: plumbing run for the relocated kitchen; the walkthrough list in the notes on `existing.png` (strip behind the kitchen, hall-side doors, sink wall, rear porch, porch/bedroom-1 wall); which side the driveway is on — photos 02 and 21 show the wide side yard, bins, meter, and rear car gate on the plan-left (west) side, opposite item 4 above; confirm whether the termite report's "rear half bathroom" means there is a second sink/half bath in the rear porch area. The floor furnace is red-tagged by PG&E (Aug 2026) and comes out; heating will be mini-splits (see `BUDGET.md`).

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
- `floor-plan/generate.py` is the source of truth for the plans. After editing, run `floor-plan/export.sh` (regenerates the SVGs and screenshots them with headless Chrome at 2×, sizing the window from the SVG). Change a dimension by editing the model in `build()`; every room label, dimension string, and door cut follows.
- `index.html` galleries are static lists; regenerate if photos are added.
