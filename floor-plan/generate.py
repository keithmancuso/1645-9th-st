#!/usr/bin/env python3
"""Generate floor-plan SVGs for 1645 9th St. Run: python3 generate.py
Produces existing.svg and proposed.svg. Units are feet; y grows toward the street (south on the drawing)."""
S = 14                 # px per foot
OX, OY = 165, 540      # origin: house NW corner. Lot spans x -8..28, y -27..46

def build(variant):
    out = []
    W, H = 688, int(OY + 51.6*S)
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
        line(x1,y1,x2,y2,stroke="#fbfaf7",sw=6); line(x1,y1,x2,y2,stroke="#999",sw=1,dash="4,4")
    def circle(x,y,r,fill="#ddd"):
        c=P(x,y); out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r*S}" fill="{fill}" stroke="#222" stroke-width="1"/>')

    proposed = variant == "proposed"
    title = "Proposed Layout" if proposed else "Existing Layout (as listed)"
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
    out.append(f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>')
    out.append(f'<text x="40" y="44" font-size="22" font-weight="bold" fill="#222">1645 9th St, Berkeley — {title}</text>')
    out.append(f'<text x="40" y="68" font-size="13" fill="#555">2 bed · 1 bath · 734 sq ft · built 1919 · 2,613 sq ft lot · single-story bungalow</text>')
    if proposed:
        out.append(f'<text x="40" y="86" font-size="12" fill="#1a7a3c">Change: kitchen moves from the front-right room to the rear-left room with the slider, opening onto the deck.</text>')
        out.append(f'<text x="40" y="102" font-size="12" fill="#1a7a3c">Old kitchen → bedroom 1. Rear-right stays a bedroom (2), closet added. Furnace out, mini-splits in.</text>')
    else:
        out.append(f'<text x="40" y="86" font-size="12" fill="#a33">From the listing photos; room positions corrected after the walkthrough. Sizes are estimates (±2 ft), not measured.</text>')

    # lot: 2,613 sq ft per listing. Width and depths are read from photos 01, 05, 21, not measured:
    # ≈8 ft side yard / parking on the west, ≈2 ft on the east, ≈19 ft backyard to the rear fence, ≈12 ft front yard to the sidewalk
    rect(-8,-27,28,46,fill="#f1eee6",stroke="#8a6a3a",sw=2)
    for x1,y1,x2,y2 in [(-8,-27,28,-27),(-8,-27,-8,46),(28,-27,28,46)]: line(x1,y1,x2,y2,stroke="#8a6a3a",sw=3)
    line(-8,46,28,46,stroke="#999",sw=1.5)   # front lot line / sidewalk
    line(-8,6,-3.2,6,stroke="#8a6a3a",sw=3); line(-0.2,6,0,6,stroke="#8a6a3a",sw=3); label(-4,4.8,"gate",7,False,"#555")   # side-yard gate (photos 01, 21)
    label(10,-19,"BACKYARD",12); label(10,-17.4,"≈ 36' × 19' to the rear fence · bare dirt",9,False,"#555")
    label(-4,20,"side yard /",8,False,"#555"); label(-4,21.2,"parking",8,False,"#555"); label(-4,22.4,"≈ 8' wide",8,False,"#555")
    label(8,41,"FRONT YARD",10); label(8,42.4,"gravel · ≈ 12' to sidewalk",9,False,"#555")
    rect(19,36.6,22,46,fill="#ddd",stroke="#999",sw=1)   # front walk
    label(10,47.6,"sidewalk · 9th Street",9,False,"#555")
    # deck (photo 21): between the rear porch and the slider; stairs off its west end step down westward toward the side gate
    rect(6,-8,17,0,fill="#e8dcc8",stroke="#8a6a3a",sw=2)
    for i in range(1,11): line(6+i,-8,6+i,0,stroke="#c9b48f",sw=1)
    label(11.5,-4.2,"DECK",12); label(11.5,-2.6,"≈ 11' × 8'",11,False,"#555")
    rect(2,-8,6,-4.5,fill="#e8dcc8",stroke="#8a6a3a",sw=2)
    for i in range(1,4): line(2+i,-8,2+i,-4.5,stroke="#8a6a3a",sw=1)
    label(4,-3.4,"stairs down",7,False,"#555"); label(4,-2.4,"to side gate",7,False,"#555")
    # rear porch bump-out
    rect(17,-8,26,0,fill="#f3efe6",stroke="#222",sw=3)   # same depth as the deck
    if proposed:
        label(21.5,-4.6,"LAUNDRY / MUDROOM",10); label(21.5,-3.2,"existing rear porch · ≈ 9' × 8'",9,False,"#555")
    else:
        label(21.5,-4.6,"REAR PORCH",11); label(21.5,-3.2,"enclosed · ≈ 9' × 8'",10,False,"#555")
    window(19,-8,24,-8); door(17,-5.5,2.5,'e'); window(26,-5.5,26,-2.5)
    # main house
    rect(0,0,26,30,fill="#fff",stroke="#222",sw=4)
    rect(16,26,26,34,fill="#f3efe6",stroke="#222",sw=3)
    label(21,29.3,"FRONT PORCH",11); label(21,30.7,"enclosed entry · ≈ 10' × 8'",10,False,"#555")
    door(19,34,3,'n'); window(16,30.5,16,33.5); window(23,34,25.5,34)
    label(21,35.4,"concrete steps",9,False,"#555")
    # shared interior walls
    line(12.5,0,12.5,12); line(12.5,12,26,12)   # one wall between the rear rooms, in line with the alcove return at the living-room doorway
    line(0,12,9,12); line(0,17,12.5,17); line(9,12,9,17)
    line(12.5,15.5,12.5,17); opening(12.5,15.5,15,15.5)   # inset doorway: living room -> hall, in an alcove at the NE corner (photos 04, 07)
    line(15,12,15,26)                                     # hall / kitchen wall continues as the fireplace wall
    opening(15,12.8,15,15.2)                              # hall -> front-right room, cased opening (photo 14)
    line(21,12,21,14.5); line(21,14.5,26,14.5)
    # fireplace / built-in
    rect(12.8,21,15,24.4,fill="#c0553f",stroke="#222",sw=1.5); label(13.9,22.9,"FP",9,True,"#fff")   # brick fireplace sits in the living room; the far wall is flush
    rect(14.4,18,15,20,fill="#ddd",stroke="#222",sw=1); label(12.8,19.2,"built-in",8,False,"#555")
    # bath
    # bath (photos 13, 14): from the east-end door, vanity left (south wall), tub right (north wall, end at the door), toilet under the west window
    rect(4,12,9,14.5,fill="#eee",stroke="#222",sw=1); label(6.5,13.5,"tub",9,False)
    rect(3,15.5,9,17,fill="#eee",stroke="#222",sw=1); label(6,16.5,"vanity",8,False)
    e=P(1.4,14.6); out.append(f'<ellipse cx="{e[0]}" cy="{e[1]}" rx="{1*S}" ry="{0.7*S}" fill="#fff" stroke="#222" stroke-width="1"/>')
    if proposed:
        label(11,13.9,"furnace out",7,False,"#1a7a3c"); label(11,14.8,"mini-splits in",7,False,"#1a7a3c")
    else:
        rect(10,13.2,12,14.6,fill="#888",stroke="#222",sw=1); label(11,15.4,"floor furnace",7,False,"#555")
    label(5.5,15.2,"BATH",11); label(10.7,16.6,"HALL",10)

    if not proposed:
        # bedroom 2 rear-left with slider; bedroom 1 rear-right; kitchen front-right (per Keith, Sept 9)
        door(12.5,0.4,2.5,'e'); door(20,0,2.5,'n')          # door to the back room is in the rear corner (photo 18)
        line(7.5,0,12,0,stroke="#fbfaf7",sw=6); line(7.5,0,12,0,stroke="#3a7bd5",sw=5); label(9.75,-0.6,"sliding glass door",8,False,"#3a7bd5"); window(1.5,0,3.5,0)
        label(6.25,5.5,"BEDROOM 2",14); label(6.25,7,"≈ 12' × 12'",11,False,"#555")
        label(19.5,5.5,"BEDROOM 1",14); label(19.5,7,"≈ 13' × 12' · door to rear porch",10,False,"#555")
        # kitchen fixtures, front-right room
        rect(24,15,26,24,fill="#eee",stroke="#222",sw=1); label(25,22.2,"tile",8,False); label(25,23.1,"counter",8,False)
        rect(24,17.5,26,20.5,fill="#ddd",stroke="#222",sw=1); label(25,19.2,"sink",8,False)
        rect(18,12.2,20.5,14.2,fill="#ddd",stroke="#222",sw=1); label(19.25,13.4,"range",8,False)
        rect(15.2,22,17.7,24.5,fill="#ddd",stroke="#222",sw=1); label(16.45,23.5,"fridge",8,False)
        circle(24.9,25,0.8); label(24.9,25.3,"WH",7,False)
    else:
        # kitchen rear-left, eat-in, opens to deck; bedroom 2 rear-right
        line(7,0,12,0,stroke="#fbfaf7",sw=6); line(7,0,12,0,stroke="#3a7bd5",sw=5); label(9.5,-0.6,"sliding / French door to deck",8,False,"#3a7bd5"); window(1.5,0,3.5,0)
        rect(0.2,1.5,2,11.8,fill="#eee",stroke="#222",sw=1); label(1.1,3.4,"counter",7,False)
        rect(0.2,4.5,2,7,fill="#ddd",stroke="#222",sw=1); label(1.1,5.9,"sink",7,False)
        rect(0.2,8,2.2,10.5,fill="#ddd",stroke="#222",sw=1); label(1.2,9.4,"range",7,False)
        rect(3,9.5,5.5,11.8,fill="#ddd",stroke="#222",sw=1); label(4.25,10.8,"fridge",8,False)
        rect(4.5,2.5,9.5,5.5,fill="#f4e9d0",stroke="#8a6a3a",sw=1); label(7,4.3,"table / island",8,False,"#555")
        label(7.2,7.6,"KITCHEN (eat-in)",14); label(7.2,9,"≈ 12' × 12' · opens to deck",10,False,"#555")
        # bedroom 2 (was bedroom 1; gains a closet)
        door(12.5,0.4,2.5,'e')                                  # kitchen -> bedroom 2, existing corner door
        line(12.5,9,15.5,9); line(15.5,9,15.5,12); opening(15.5,9.3,15.5,11.7); label(14,10.7,"closet",8,False)
        door(22,0,2.5,'n')                                      # bedroom 2 -> laundry/mudroom
        label(19.5,6,"BEDROOM 2",13); label(19.5,7.4,"≈ 13' × 12' · closet added",10,False,"#555")
        label(23.8,-0.7,"WH moves here",7,False,"#a33")
    # shared: bedroom 1, living room, doors
    door(9,14.5,2.5,'w'); opening(22,14.5,25,14.5); door(15,26.5,2.5,'e')
    window(0,3,0,7); window(0,13,0,15.5); window(0,19,0,22); window(3,30,9,30); window(26,17,26,21); window(26,8,26,10)
    if proposed:
        label(19.5,18.5,"BEDROOM 1",14); label(19.5,20,"≈ 11' × 12' · former kitchen",10,False,"#555"); label(23.5,13.4,"closet",8,False)
    else:
        label(19.5,18.5,"KITCHEN",14); label(19.5,20,"≈ 11' × 12' · tile counters",10,False,"#555"); label(23.5,13.4,"closet / pantry",8,False)
    label(7.5,23,"LIVING ROOM",15); label(7.5,24.6,"≈ 15' × 13' · fireplace + built-ins",10,False,"#555")
    # dims / north / street / legend
    line(-9.3,0,-9.3,30,stroke="#777",sw=1); p=P(-10.1,15)
    out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(-90)" font-size="10" text-anchor="middle" fill="#555">house ≈ 30 ft</text>')
    line(30,-27,30,46,stroke="#777",sw=1); p=P(30.9,9.5)
    out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(90)" font-size="10" text-anchor="middle" fill="#555">lot ≈ 73 ft (2,613 sq ft ÷ 36 ft, assumed)</text>')
    line(-8,-29.5,28,-29.5,stroke="#777",sw=1); label(10,-30.2,"lot ≈ 36 ft",10,False,"#555")
    p=P(33,-22); out.append(f'<g transform="translate({p[0]},{p[1]})"><polygon points="0,-18 6,4 0,0 -6,4" fill="#222"/><text x="0" y="18" font-size="11" text-anchor="middle" font-weight="bold">N</text></g>')
    label(10,49.2,'"N" is drawn as away from the street, not true north · lot edges are estimates from photos',8,False,"#555")
    ly=OY+50.4*S
    out.append(f'<line x1="40" y1="{ly}" x2="70" y2="{ly}" stroke="#3a7bd5" stroke-width="2.5"/><text x="78" y="{ly+4}" font-size="11" fill="#555">window / glass</text>')
    out.append(f'<line x1="190" y1="{ly}" x2="220" y2="{ly}" stroke="#999" stroke-width="1" stroke-dasharray="4,4"/><text x="228" y="{ly+4}" font-size="11" fill="#555">cased opening</text>')
    out.append(f'<text x="340" y="{ly+4}" font-size="11" fill="#555">arc = door swing · FP = brick fireplace · WH = water heater</text>')
    out.append('</svg>')
    return '\n'.join(out), W, H

import os
here = os.path.dirname(os.path.abspath(__file__))
for v in ("existing", "proposed"):
    svg, W, H = build(v)
    open(os.path.join(here, f"{v}.svg"), "w").write(svg)
    print(v, W, H)
