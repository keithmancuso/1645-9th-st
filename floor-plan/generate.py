#!/usr/bin/env python3
"""Generate floor-plan SVGs for 1645 9th St. Run: python3 generate.py
Produces existing.svg and proposed.svg. Units are feet; y grows toward the street (south on the drawing)."""
S = 18
OX, OY = 80, 300

def build(variant):
    out = []
    W, H = OX*2 + 26*S + 60, OY + 37*S + 80
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
    out.append(f'<text x="{OX}" y="44" font-size="22" font-weight="bold" fill="#222">1645 9th St, Berkeley — {title}</text>')
    out.append(f'<text x="{OX}" y="68" font-size="13" fill="#555">2 bed · 1 bath · 734 sq ft · built 1919 · 2,613 sq ft lot · single-story bungalow</text>')
    if proposed:
        out.append(f'<text x="{OX}" y="86" font-size="12" fill="#1a7a3c">Change: kitchen moves from the front-right room to the rear-left room with the slider, opening onto the deck.</text>')
        out.append(f'<text x="{OX}" y="102" font-size="12" fill="#1a7a3c">Old kitchen → bedroom 1. Rear-right stays a bedroom (2), closet added. Furnace out, mini-splits in.</text>')
    else:
        out.append(f'<text x="{OX}" y="86" font-size="12" fill="#a33">From the listing photos; room positions corrected after the walkthrough. Sizes are estimates (±2 ft), not measured.</text>')

    # deck + stairs
    rect(3,-8,17,0,fill="#e8dcc8",stroke="#8a6a3a",sw=2)
    for i in range(1,14): line(3+i,-8,3+i,0,stroke="#c9b48f",sw=1)
    label(10,-4.2,"DECK",12); label(10,-2.6,"≈ 14' × 8'",11,False,"#555")
    rect(0,-8,3,-2,fill="#e8dcc8",stroke="#8a6a3a",sw=2)
    for i in range(1,6): line(0,-8+i,3,-8+i,stroke="#8a6a3a",sw=1)
    label(1.5,-0.8,"stairs",9,False,"#555")
    # rear porch bump-out
    rect(17,-6,26,0,fill="#f3efe6",stroke="#222",sw=3)
    if proposed:
        label(21.5,-3.8,"LAUNDRY / MUDROOM",10); label(21.5,-2.4,"existing rear porch · ≈ 9' × 6'",9,False,"#555")
    else:
        label(21.5,-3.8,"REAR PORCH",11); label(21.5,-2.4,"enclosed · ≈ 9' × 6'",10,False,"#555")
    window(19,-6,24,-6); door(17,-4.5,2.5,'e'); window(26,-4.5,26,-1.5)
    # main house
    rect(0,0,26,30,fill="#fff",stroke="#222",sw=4)
    rect(16,26,26,34,fill="#f3efe6",stroke="#222",sw=3)
    label(21,29.3,"FRONT PORCH",11); label(21,30.7,"enclosed entry · ≈ 10' × 8'",10,False,"#555")
    door(19,34,3,'n'); window(16,30.5,16,33.5); window(23,34,25.5,34)
    label(21,35.4,"concrete steps",9,False,"#555")
    # shared interior walls
    line(15,0,15,12); line(15,12,26,12)   # one wall between the rear rooms (the earlier draft had a 2 ft double wall here; no evidence for it)
    line(0,12,9,12); line(0,17,15,17); line(9,12,9,17)
    line(15,12,15,26)
    line(21,12,21,14.5); line(21,14.5,26,14.5)
    # fireplace / built-in
    rect(12.8,23.4,15,26.2,fill="#c0553f",stroke="#222",sw=1.5); label(13.9,25.2,"FP",9,True,"#fff")   # brick fireplace sits in the living room; the far wall is flush
    rect(14.4,21.2,15,23.1,fill="#ddd",stroke="#222",sw=1); label(12.6,22.4,"built-in",8,False,"#555")
    # inset doorway, living room -> front-right room (photo 04): a wall section projects into the living room at the NE corner
    rect(13.5,17,15,18.4,fill="#222",stroke="#222",sw=1)
    opening(15,18.8,15,21)
    # bath
    rect(0,15,5,17,fill="#eee",stroke="#222",sw=1); label(2.5,16.2,"tub",9,False)
    rect(4,12,9,13.5,fill="#eee",stroke="#222",sw=1); label(6.5,13,"vanity",8,False)
    e=P(1.5,13.2); out.append(f'<ellipse cx="{e[0]}" cy="{e[1]}" rx="{0.7*S}" ry="{1*S}" fill="#fff" stroke="#222" stroke-width="1"/>')
    if proposed:
        label(12,15.3,"floor furnace out · mini-splits",8,False,"#1a7a3c")
    else:
        rect(12.4,9,14.6,10.5,fill="#888",stroke="#222",sw=1); label(12.3,8.4,"floor furnace (red-tagged)",8,False,"#555")
    label(4.5,14.7,"BATH",13); label(12,12.4,"HALL",11)

    if not proposed:
        # bedroom 2 rear-left with slider; bedroom 1 rear-right; kitchen front-right (per Keith, Sept 9)
        door(15,0.4,2.5,'e'); door(20,0,2.5,'n')          # door to the back room is in the rear corner (photo 18)
        line(5,0,10,0,stroke="#fbfaf7",sw=6); line(5,0,10,0,stroke="#3a7bd5",sw=5); label(7.5,-0.6,"sliding glass door",8,False,"#3a7bd5")
        label(6,5.5,"BEDROOM 2",14); label(6,7,"≈ 15' × 12'",11,False,"#555")
        label(20.5,5.5,"BEDROOM 1",14); label(20.5,7,"≈ 11' × 12' · door to rear porch",10,False,"#555")
        # kitchen fixtures, front-right room
        rect(24,15,26,24,fill="#eee",stroke="#222",sw=1); label(25,22.2,"tile",8,False); label(25,23.1,"counter",8,False)
        rect(24,17.5,26,20.5,fill="#ddd",stroke="#222",sw=1); label(25,19.2,"sink",8,False)
        rect(18,12.2,20.5,14.2,fill="#ddd",stroke="#222",sw=1); label(19.25,13.4,"range",8,False)
        rect(15.2,22,17.7,24.5,fill="#ddd",stroke="#222",sw=1); label(16.45,23.5,"fridge",8,False)
        circle(24.9,25,0.8); label(24.9,25.3,"WH",7,False)
    else:
        # kitchen rear-left, eat-in, opens to deck; bedroom 2 rear-right
        line(4,0,11,0,stroke="#fbfaf7",sw=6); line(4,0,11,0,stroke="#3a7bd5",sw=5); label(7.5,-0.6,"sliding / French door to deck",8,False,"#3a7bd5")
        rect(0.2,0.2,2.7,2.7,fill="#ddd",stroke="#222",sw=1); label(1.45,1.7,"fridge",8,False)
        rect(0.2,3,2,11.5,fill="#eee",stroke="#222",sw=1); label(1.1,4.6,"counter",7,False)
        rect(0.2,5.5,2,8,fill="#ddd",stroke="#222",sw=1); label(1.1,6.9,"sink",7,False)
        rect(0.2,9,2.2,11.5,fill="#ddd",stroke="#222",sw=1); label(1.2,10.4,"range",7,False)
        rect(5,4,10,7,fill="#f4e9d0",stroke="#8a6a3a",sw=1); label(7.5,5.8,"table / island",8,False,"#555")
        label(7.5,9.6,"KITCHEN (eat-in)",14); label(7.5,11,"≈ 15' × 12' · opens to deck",10,False,"#555")
        # bedroom 2 (was bedroom 1; gains a closet)
        door(15,0.4,2.5,'e')                                    # kitchen -> bedroom 2, existing corner door
        line(15,9,18,9); line(18,9,18,12); opening(18,9.3,18,11.7); label(16.5,10.7,"closet",8,False)
        door(22,0,2.5,'n')                                      # bedroom 2 -> laundry/mudroom
        label(21,6,"BEDROOM 2",13); label(21,7.4,"≈ 11' × 12' · closet added",10,False,"#555")
        label(23.8,-0.7,"WH moves here",7,False,"#a33")
    # shared: bedroom 1, living room, doors
    door(9,13.5,2.5,'w'); door(15,13,2.5,'e'); opening(22,14.5,25,14.5); opening(10.5,17,13.2,17); door(15,27,2.5,'e')
    window(0,3,0,7); window(0,13,0,15.5); window(0,19,0,22); window(3,30,9,30); window(26,17,26,21); window(26,8,26,10)
    if proposed:
        label(19.5,18.5,"BEDROOM 1",14); label(19.5,20,"≈ 11' × 12' · former kitchen",10,False,"#555"); label(23.5,13.4,"closet",8,False)
    else:
        label(19.5,18.5,"KITCHEN",14); label(19.5,20,"≈ 11' × 12' · tile counters",10,False,"#555"); label(23.5,13.4,"closet / pantry",8,False)
    label(7.5,23,"LIVING ROOM",15); label(7.5,24.6,"≈ 15' × 13' · fireplace + built-ins",10,False,"#555")
    # dims / north / street / legend
    line(-1.5,0,-1.5,30,stroke="#777",sw=1); p=P(-2.1,15)
    out.append(f'<text transform="translate({p[0]},{p[1]}) rotate(-90)" font-size="10" text-anchor="middle" fill="#555">≈ 30 ft</text>')
    line(0,-9.5,26,-9.5,stroke="#777",sw=1); label(13,-10,"≈ 26 ft",10,False,"#555")
    p=P(24,-9.6); out.append(f'<g transform="translate({p[0]},{p[1]})"><polygon points="0,-18 6,4 0,0 -6,4" fill="#222"/><text x="0" y="18" font-size="11" text-anchor="middle" font-weight="bold">N</text></g>')
    label(8,32,'9th Street (front) — "N" is drawn as away from the street, not true north',10,False,"#555")
    ly=OY+36.5*S
    out.append(f'<line x1="{OX}" y1="{ly}" x2="{OX+30}" y2="{ly}" stroke="#3a7bd5" stroke-width="2.5"/><text x="{OX+38}" y="{ly+4}" font-size="11" fill="#555">window / glass</text>')
    out.append(f'<line x1="{OX+150}" y1="{ly}" x2="{OX+180}" y2="{ly}" stroke="#999" stroke-width="1" stroke-dasharray="4,4"/><text x="{OX+188}" y="{ly+4}" font-size="11" fill="#555">cased opening</text>')
    out.append(f'<text x="{OX+300}" y="{ly+4}" font-size="11" fill="#555">arc = door swing · FP = brick fireplace · WH = water heater</text>')
    out.append('</svg>')
    return '\n'.join(out), W, H

import os
here = os.path.dirname(os.path.abspath(__file__))
for v in ("existing", "proposed"):
    svg, W, H = build(v)
    open(os.path.join(here, f"{v}.svg"), "w").write(svg)
    print(v, W, H)
