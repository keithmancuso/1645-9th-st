#!/usr/bin/env python3
"""Generate floor-plan SVGs for 1645 9th St. Run: python3 generate.py
Produces existing.svg and proposed.svg. Units are feet; y grows toward the street (south on the drawing)."""
S = 14                 # px per foot
OX, OY = 165, 540      # origin: house NW corner. Lot spans x -8..29.5, y -26..44

def build(variant):
    out = []
    W, H = 688, int(OY + 49.8*S)
    def P(x, y): return (OX + x*S, OY + y*S)
    def rect(x1,y1,x2,y2,fill="#fff",stroke="#222",sw=3):
        a=P(x1,y1); b=P(x2,y2)
        out.append(f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]}" height="{b[1]-a[1]}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def line(x1,y1,x2,y2,stroke="#222",sw=3,dash=None):
        a=P(x1,y1); b=P(x2,y2); d=f' stroke-dasharray="{dash}"' if dash else ''
        out.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="square"{d}/>')
    def label(x,y,t,size=13,bold=True,fill="#222"):
        p=P(x,y)
        out.append(f'<text x="{p[0]}" y="{p[1]}" font-size="{size}" text-anchor="middle" fill="{fill}" font-weight="{"bold" if bold else "normal"}">{t}</text>')
    def window(x1,y1,x2,y2):
        line(x1,y1,x2,y2,stroke="#fbfaf7",sw=5); line(x1,y1,x2,y2,stroke="#3a7bd5",sw=2.5)
    def door(x,y,w,dir):
        if dir in 'ns':
            line(x,y,x+w,y,stroke="#fbfaf7",sw=6); s=-1 if dir=='n' else 1
            a=P(x,y); b=P(x+w,y); c=P(x,y+s*w)
            out.append(f'<path d="M{a[0]},{a[1]} L{c[0]},{c[1]} A{w*S},{w*S} 0 0 {1 if s<0 else 0} {b[0]},{b[1]}" fill="none" stroke="#666" stroke-width="1.5"/>')
        else:
            line(x,y,x,y+w,stroke="#fbfaf7",sw=6); s=1 if dir=='e' else -1
            a=P(x,y); b=P(x,y+w); c=P(x+s*w,y)
            out.append(f'<path d="M{a[0]},{a[1]} L{c[0]},{c[1]} A{w*S},{w*S} 0 0 {1 if s>0 else 0} {b[0]},{b[1]}" fill="none" stroke="#666" stroke-width="1.5"/>')
    def opening(x1,y1,x2,y2):
        line(x1,y1,x2,y2,stroke="#fbfaf7",sw=6)
    def circle(x,y,r,fill="#ddd"):
        c=P(x,y); out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r*S}" fill="{fill}" stroke="#222" stroke-width="1"/>')

    proposed = variant == "proposed"
    title = "Proposed Layout" if proposed else "Existing Layout (as listed)"
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
    out.append(f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>')
    out.append(f'<text x="40" y="44" font-size="22" font-weight="bold" fill="#222">1645 9th St, Berkeley — {title}</text>')
    out.append(f'<text x="40" y="68" font-size="13" fill="#555">2 bed · 1 bath · 734 sq ft · built 1919 · 2,613 sq ft lot · single-story bungalow</text>')
    if proposed:
        out.append(f'<text x="40" y="86" font-size="12" fill="#555">Change: kitchen moves from the front-right room to the rear-left room with the slider, opening onto the deck.</text>')
        out.append(f'<text x="40" y="102" font-size="12" fill="#555">Old kitchen → bedroom 1, entered through its strip beside the hall. Rear porch → mudroom. Furnace out.</text>')
    else:
        out.append(f'<text x="40" y="86" font-size="12" fill="#a33">From the listing photos; room positions corrected after the walkthrough. Sizes are estimates (±2 ft), not measured.</text>')

    # lot: 2,613 sq ft per listing. Width and depths are read from photos 01, 05, 21, not measured:
    # ≈8 ft driveway on the west, ≈3.5 ft gravel side yard on the east (photo 03), ≈18 ft backyard to the rear fence, ≈10 ft front yard to the sidewalk
    rect(-8,-26,29.5,44,fill="#f1eee6",stroke="#8a6a3a",sw=2)
    for x1,y1,x2,y2 in [(-8,-26,29.5,-26),(-8,-26,-8,44),(29.5,-26,29.5,44)]: line(x1,y1,x2,y2,stroke="#8a6a3a",sw=3)
    line(-8,44,29.5,44,stroke="#999",sw=1.5)   # front lot line / sidewalk
    rect(26.2,-26,29.5,44,fill="#e9e4d8",stroke="none",sw=0)   # east side yard, gravel
    line(26,26,27.1,26,stroke="#8a6a3a",sw=3); line(28.4,26,29.5,26,stroke="#8a6a3a",sw=3); label(27.8,25,"gate",7,False,"#555")
    p=P(28.1,34); out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(-90)" font-size="7" text-anchor="middle" fill="#555">gravel side yard ≈ 3.5 ft</text>')
    line(-8,6,-3.2,6,stroke="#8a6a3a",sw=3); line(-0.2,6,0,6,stroke="#8a6a3a",sw=3); label(-4,4.8,"gate",7,False,"#555")   # side-yard gate (photos 01, 21)
    label(10,-18.5,"BACKYARD",12); label(10,-16.9,"≈ 37' × 18' to the rear fence · bare dirt",9,False,"#555")
    # driveway (photos 01, 02): dirt, from the curb along the west side of the house to the gate; the one off-street space
    rect(-8,6.2,-0.3,44,fill="#e4dfd3",stroke="#b8ad98",sw=1)
    p=P(-4.1,27); out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(-90)" font-size="10" font-weight="bold" text-anchor="middle" fill="#222">DRIVEWAY</text>')
    p=P(-2.9,27); out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(-90)" font-size="8" text-anchor="middle" fill="#555">dirt · ≈ 8 × 40 ft · off-street space · curb cut</text>')
    label(9,39.6,"FRONT YARD",10); label(9,41,"gravel beds · ≈ 10' to sidewalk",9,False,"#555")
    rect(19,36.6,22,44,fill="#ddd",stroke="#999",sw=1)   # front walk
    label(10,45.6,"sidewalk · 9th Street",9,False,"#555")
    # deck (Keith): wider than the rear-left room, overlaps part of the rear-right room's back wall; stairs off its west end in line with the back wall
    rect(0,-8,18,0,fill="#e8dcc8",stroke="#8a6a3a",sw=2)
    for i in range(1,18): line(i,-8,i,0,stroke="#c9b48f",sw=1)
    label(9,-4.6,"DECK",12); label(9,-3,"≈ 18' × 8'",11,False,"#555")
    rect(-4,-3.5,0,0,fill="#e8dcc8",stroke="#8a6a3a",sw=2)
    for i in range(1,4): line(-i,-3.5,-i,0,stroke="#8a6a3a",sw=1)
    label(-2,-4.3,"stairs down",7,False,"#555")
    # rear porch bump-out (Keith: narrow; photo 11: shelves, plywood floor, small high window), flush with the deck edge
    rect(18,-8,26,0,fill="#f3efe6",stroke="#222",sw=3)
    if proposed:
        label(22,-5.2,"LAUNDRY /",9); label(22,-4.1,"MUDROOM",9); label(22,-2.9,"≈ 8' × 8'",8,False,"#555")
    else:
        label(22,-5,"REAR PORCH",9); label(22,-3.8,"enclosed · ≈ 8' × 8'",8,False,"#555"); label(22,-2.7,"shelves",7,False,"#555")
    window(20,-8,24,-8); window(26,-6,26,-3)
    door(18,-7,2.5,'w')                                     # porch -> deck
    door(20,0,2.5,'n')                                      # bedroom 1 -> porch (photo 16)
    # main house
    rect(0,0,26,30,fill="#fff",stroke="#222",sw=4)
    rect(16,26,26,34,fill="#f3efe6",stroke="#222",sw=3)
    label(21,29.3,"FRONT PORCH",11); label(21,30.7,"enclosed entry · ≈ 10' × 8'",10,False,"#555")
    door(19,34,3,'n'); window(16,30.5,16,33.5); window(23,34,25.5,34)
    label(21,35.4,"concrete steps",9,False,"#555")
    # interior walls
    line(13.5,0,13.5,12); line(13.5,12,26,12)   # partition between the rear rooms, in line with the hall's east wall; rear-left a little wider than rear-right (Keith)
    line(0,12,10.5,12); line(10.5,12,10.5,17)   # bath: 0-10.5 × 12-17
    line(13.5,12,13.5,17)                        # hall's east wall = kitchen's west wall
    line(0,17,10.5,17); line(13.5,17,15,17)      # living room north wall, with the hall opening between
    opening(10.5,17,13.5,17); opening(10.5,12,13.5,12)   # hall: straight, cased both ends, living room -> rear-left room (photo 09)
    line(15,12,15,26)                            # front-right room's west wall: passage side (with the door) and the fireplace wall
    door(13.5,0.4,2.2,'e')                                # rear-left room -> rear-right room, in the rear corner: the rear-right room's only entrance (Keith)
    # fireplace / built-in on the living room's east wall (photo 07): built-in, fireplace, porch door
    rect(13.8,20,15,23.2,fill="#c0553f",stroke="#222",sw=1.5); label(14.4,21.8,"FP",8,True,"#fff")
    # bath (photos 13, 14): from the east-end door, vanity left (south wall), tub right (north wall, end at the door), toilet under the west window
    rect(5.5,12,10.5,14.5,fill="#eee",stroke="#222",sw=1); label(8,13.5,"tub",9,False)
    rect(4.5,15.5,10.5,17,fill="#eee",stroke="#222",sw=1); label(7.5,16.5,"vanity",8,False)
    e=P(1.4,14.6); out.append(f'<ellipse cx="{e[0]}" cy="{e[1]}" rx="{1*S}" ry="{0.7*S}" fill="#fff" stroke="#222" stroke-width="1"/>')
    label(6.5,15.2,"BATH",11)
    door(10.5,14.5,2.5,'w')                                # bath door, off the hall
    if not proposed:
        rect(11.2,12.8,12.8,14.2,fill="#888",stroke="#222",sw=1); label(12,15.2,"furnace",6,False,"#555")   # floor furnace grate in the hall (photos 09, 12, 14, 20)
        label(12,16.3,"HALL",7)
        opening(13.5,12.6,13.5,16.4); door(15,13.5,2.5,'e')  # hall -> short passage -> kitchen door (photos 12, 14)
        door(26,12.8,2.7,'e')                                # kitchen side door out to the east side yard (Keith)
        # existing: bedroom 2 rear-left, bedroom 1 rear-right, kitchen front-right (L-shaped: the strip beside the hall plus the room behind the porch)
        line(4.5,0,9,0,stroke="#fbfaf7",sw=6); line(4.5,0,9,0,stroke="#3a7bd5",sw=5); label(6.75,-0.6,"sliding glass door, centered",8,False,"#3a7bd5")
        label(6.75,5.5,"BEDROOM 2",14); label(6.75,7,"≈ 13' × 12'",11,False,"#555")
        label(19.75,5.5,"BEDROOM 1",14); label(19.75,7,"≈ 12' × 12'",11,False,"#555"); label(19.75,8.3,"entered from bedroom 2 · door to porch",8,False,"#555")
        # kitchen (photos 08, 10, 12): tile counter and sink under the east window, range + WH + small window on the porch wall, fridge beside, pantry shelves at the north end
        rect(24,15,26,24,fill="#eee",stroke="#222",sw=1); label(25,22.2,"tile",8,False); label(25,23.1,"counter",8,False)
        rect(24,17.5,26,20.5,fill="#ddd",stroke="#222",sw=1); label(25,19.2,"sink",8,False)
        rect(15.5,23.6,18,25.8,fill="#ddd",stroke="#222",sw=1); label(16.75,24.9,"range",8,False)
        circle(19.2,24.9,0.8); label(19.2,25.2,"WH",7,False)
        rect(20.3,23.3,22.8,25.8,fill="#ddd",stroke="#222",sw=1); label(21.55,24.7,"fridge",8,False)
        line(21.5,26,23.5,26,stroke="#fbfaf7",sw=6); line(21.5,26,23.5,26,stroke="#3a7bd5",sw=2.5); label(22.5,26.9,"small window to porch",7,False,"#3a7bd5")
        label(20.5,18.5,"KITCHEN",14); label(20.5,20,"≈ 11' × 14' · galley",10,False,"#555")
    else:
        label(12,15.6,"HALL",7)
        # the old kitchen's strip beside the hall is bedroom 1's entry; the old kitchen door is the opening
        opening(13.5,12.6,13.5,16.4); door(15,13.5,2.5,'e')
        door(26,12.8,2.7,'e')                                # existing side door to the east side yard
        # kitchen rear-left (eat-in, opens to the deck); its old corner door into the closet gets closed
        line(4.5,0,9,0,stroke="#fbfaf7",sw=6); line(4.5,0,9,0,stroke="#3a7bd5",sw=5); label(6.75,-0.6,"sliding / French door to deck",8,False,"#3a7bd5")
        rect(0.2,1.5,2,11.8,fill="#eee",stroke="#222",sw=1); label(1.1,3.4,"counter",7,False)
        rect(0.2,4.5,2,7,fill="#ddd",stroke="#222",sw=1); label(1.1,5.9,"sink",7,False)
        rect(0.2,8,2.2,10.5,fill="#ddd",stroke="#222",sw=1); label(1.2,9.4,"range",7,False)
        rect(3,9.5,5.5,11.8,fill="#ddd",stroke="#222",sw=1); label(4.25,10.8,"fridge",8,False)
        rect(5,2.5,10,5.5,fill="#f4e9d0",stroke="#8a6a3a",sw=1); label(7.5,4.3,"table / island",8,False,"#555")
        label(7.5,7.6,"KITCHEN (eat-in)",14); label(7.5,9,"≈ 13' × 12' · opens to deck",10,False,"#555")
        label(19.75,6,"BEDROOM 2",13); label(19.75,7.4,"≈ 12' × 12' · door to mudroom · no closet",9,False,"#555")
        label(20.5,18.5,"BEDROOM 1",14); label(20.5,20,"≈ 11' × 14' · former kitchen · no closet",10,False,"#555")
    # shared: doors, windows, labels
    door(15,26.5,2.5,'e')
    window(0,3,0,7); window(0,13,0,15.5); window(0,19,0,22); window(0,25,0,28); window(3,30,9,30); window(26,17,26,21); window(26,6,26,9)
    label(7.5,23,"LIVING ROOM",15); label(7.5,24.6,"≈ 15' × 13' · brick fireplace",10,False,"#555")
    # dims / north / street / legend
    line(-9.3,0,-9.3,30,stroke="#777",sw=1); p=P(-10.1,15)
    out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(-90)" font-size="10" text-anchor="middle" fill="#555">house ≈ 30 ft</text>')
    line(31.5,-26,31.5,44,stroke="#777",sw=1); p=P(32.4,9)
    out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(90)" font-size="10" text-anchor="middle" fill="#555">lot ≈ 70 ft (2,613 sq ft ÷ 37.5 ft, assumed)</text>')
    line(-8,-28.5,29.5,-28.5,stroke="#777",sw=1); label(10.75,-29.2,"lot ≈ 37.5 ft",10,False,"#555")
    p=P(35,-21); out.append(f'<g transform="translate({p[0]},{p[1]})"><polygon points="0,-18 6,4 0,0 -6,4" fill="#222"/><text x="0" y="18" font-size="11" text-anchor="middle" font-weight="bold">N</text></g>')
    label(10,47.2,'"N" is drawn as away from the street, not true north · lot edges are estimates from photos',8,False,"#555")
    ly=OY+48.6*S
    out.append(f'<line x1="40" y1="{ly}" x2="70" y2="{ly}" stroke="#3a7bd5" stroke-width="2.5"/><text x="78" y="{ly+4}" font-size="11" fill="#555">window / glass</text>')
    out.append(f'<text x="190" y="{ly+4}" font-size="11" fill="#555">gap in wall = open doorway · arc = door swing · FP = brick fireplace · WH = water heater</text>')
    out.append('</svg>')
    return '\n'.join(out), W, H

import os
here = os.path.dirname(os.path.abspath(__file__))
for v in ("existing", "proposed"):
    svg, W, H = build(v)
    open(os.path.join(here, f"{v}.svg"), "w").write(svg)
    print(v, W, H)
