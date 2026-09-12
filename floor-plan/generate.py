#!/usr/bin/env python3
"""Floor plans for 1645 9th St, Berkeley — existing and proposed. Run: python3 generate.py

Units are feet. x runs west→east (0 = outside face of the west wall); y runs rear→front
(0 = outside face of the main rear wall, growing toward 9th St). "N" on the drawing means
away from the street, not true north.

The model is centerline walls with real thickness, standard-width doors with swings, windows,
and fixtures. All sizes are DRAFT ESTIMATES from Keith's Freeform sketch (Sept 2026, one grid
dot ≈ 1 ft) reconciled with the 21 listing photos. Nothing has been measured on site.
"""
import math, os

S = 20                                  # px per foot
EXT = 0.5                               # exterior wall: 2x4 + siding + lath & plaster ≈ 6"
INT = 5 / 12                            # interior wall: 2x4 + plaster both sides ≈ 5"
D28, D26, D30, SLIDER = 2 + 8 / 12, 2.5, 3.0, 6.0   # standard door leaves (ft)

WOOD, TILE, SOFT, PORCH, DECK, PAGE = "#f7f0e3", "#eef1f4", "#f4f0e8", "#f1ede4", "#e8dcc8", "#fbfaf7"
WALL, NEW, GONE, GLASS = "#222", "#1a7a3c", "#c0392b", "#3a7bd5"

# drawing extents (ft): x -6..27, y -8..41.5
OX, OY = 40 + 6 * S, 120 + 8 * S
W = OX + 27 * S + 180


def ftin(v):
    t = int(round(v * 12)); f, i = divmod(t, 12)
    return f"{f}′-{i}″" if i else f"{f}′"


class Plan:
    LAYERS = ("floor", "fix", "wall", "cut", "sym", "text", "dim")

    def __init__(self, proposed):
        self.p = proposed
        self.L = {k: [] for k in self.LAYERS}
        self.rooms = []

    # ---------------------------------------------------------------- primitives
    @staticmethod
    def px(x, y): return OX + x * S, OY + y * S

    def rect(self, layer, x1, y1, x2, y2, fill, stroke="none", sw=1, dash=None):
        a, b = self.px(min(x1, x2), min(y1, y2)), self.px(max(x1, x2), max(y1, y2))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.L[layer].append(f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0]-a[0]:.1f}" height="{b[1]-a[1]:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, layer, x1, y1, x2, y2, stroke=WALL, sw=1, dash=None):
        a, b = self.px(x1, y1), self.px(x2, y2)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.L[layer].append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="square"{d}/>')

    def poly(self, layer, pts, stroke=WALL, sw=1, fill="none"):
        p = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.px(x, y) for x, y in pts))
        self.L[layer].append(f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, layer, x, y, t, size=11, bold=False, fill=WALL, anchor="middle", rot=0):
        a = self.px(x, y)
        tr = f' transform="rotate({rot} {a[0]:.1f} {a[1]:.1f})"' if rot else ""
        self.L[layer].append(f'<text x="{a[0]:.1f}" y="{a[1]:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{"bold" if bold else "normal"}"{tr}>{t}</text>')

    def circle(self, layer, x, y, r, fill="#ddd", stroke=WALL):
        a = self.px(x, y)
        self.L[layer].append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="{r*S:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')

    # ---------------------------------------------------------------- model
    def wall(self, x1, y1, x2, y2, t=INT, state="keep"):
        """Axis-aligned centerline segment. state: keep | new | removed."""
        if x1 == x2: r = (x1 - t / 2, min(y1, y2), x1 + t / 2, max(y1, y2))
        else: r = (min(x1, x2), y1 - t / 2, max(x1, x2), y1 + t / 2)
        if state == "keep": self.rect("wall", *r, WALL)
        elif state == "new": self.rect("wall", *r, NEW)
        else: self.rect("sym", *r, "none", GONE, 1.5, "5,4")

    def room(self, name, x1, y1, x2, y2, fill=WOOD, sub=None, at=None, size=12, dims=True):
        self.rect("floor", x1, y1, x2, y2, fill)
        w, h = x2 - x1, y2 - y1
        cx, cy = at or ((x1 + x2) / 2, (y1 + y2) / 2)
        self.text("text", cx, cy - 0.25, name, size, True)
        if dims: self.text("text", cx, cy + 0.45, f"{ftin(w)} × {ftin(h)} · {round(w*h)} sf", 9, False, "#555")
        if sub: self.text("text", cx, cy + 1.05, sub, 8, False, "#777")
        self.rooms.append((name, w, h))

    def door(self, x, y, w, axis, hinge, swing, t=INT, arc=True):
        """Opening starts at (x,y) and runs w along axis ('x' or 'y'). hinge 0 = at start, 1 = at end.
        swing: +1 toward +axis-normal (x: toward the street/south; y: toward east), -1 opposite."""
        if axis == "x":
            self.rect("cut", x, y - t / 2, x + w, y + t / 2, "#fff")
            hx, jx = (x, x + w) if hinge == 0 else (x + w, x)
            Hp, Jp, Ep = (hx, y), (jx, y), (hx, y + swing * w)
        else:
            self.rect("cut", x - t / 2, y, x + t / 2, y + w, "#fff")
            hy, jy = (y, y + w) if hinge == 0 else (y + w, y)
            Hp, Jp, Ep = (x, hy), (x, jy), (x + swing * w, hy)
        self.line("sym", *Hp, *Ep, "#333", 1.6)
        if arc:
            Lv, Jv = (Ep[0] - Hp[0], Ep[1] - Hp[1]), (Jp[0] - Hp[0], Jp[1] - Hp[1])
            pts = [(Hp[0] + math.cos(a) * Lv[0] + math.sin(a) * Jv[0], Hp[1] + math.cos(a) * Lv[1] + math.sin(a) * Jv[1])
                   for a in (i * math.pi / 32 for i in range(17))]
            self.poly("sym", pts, "#888", 0.9)

    def slider(self, x, y, w, t=EXT):
        self.rect("cut", x, y - t / 2, x + w, y + t / 2, "#fff")
        self.line("sym", x, y - 0.1, x + w / 2 + 0.15, y - 0.1, GLASS, 2.2)
        self.line("sym", x + w / 2 - 0.15, y + 0.1, x + w, y + 0.1, GLASS, 2.2)

    def opening(self, x1, y1, x2, y2, t=INT):
        if y1 == y2: self.rect("cut", x1, y1 - t / 2, x2, y1 + t / 2, "#fff")
        else: self.rect("cut", x1 - t / 2, y1, x1 + t / 2, y2, "#fff")
        self.line("sym", x1, y1, x2, y2, "#999", 1, "4,3")

    def window(self, x1, y1, x2, y2, t=EXT):
        if y1 == y2: self.rect("cut", x1, y1 - t / 2, x2, y1 + t / 2, "#fff", "#555", 0.8)
        else: self.rect("cut", x1 - t / 2, y1, x1 + t / 2, y2, "#fff", "#555", 0.8)
        self.line("sym", x1, y1, x2, y2, GLASS, 2)

    def fix(self, x1, y1, x2, y2, label=None, fill="#e4e4e4", size=8, rot=0):
        self.rect("fix", x1, y1, x2, y2, fill, "#444", 0.8)
        if label: self.text("text", (x1 + x2) / 2, (y1 + y2) / 2 + 0.15, label, size, False, "#333", rot=rot)

    def dimh(self, x1, x2, y, label=None):
        self.line("dim", x1, y, x2, y, "#666", 0.8)
        for x in (x1, x2): self.line("dim", x, y - 0.25, x, y + 0.25, "#666", 0.8)
        self.text("dim", (x1 + x2) / 2, y - 0.3, label or ftin(x2 - x1), 9.5, False, "#444")

    def dimv(self, y1, y2, x, label=None):
        self.line("dim", x, y1, x, y2, "#666", 0.8)
        for y in (y1, y2): self.line("dim", x - 0.25, y, x + 0.25, y, "#666", 0.8)
        self.text("dim", x - 0.3, (y1 + y2) / 2, label or ftin(y2 - y1), 9.5, False, "#444", rot=-90)

    # ---------------------------------------------------------------- output
    def svg(self, title, subtitle, notes):
        import textwrap
        notes = [ln for n in notes for ln in textwrap.wrap(n, 150)]
        y = int(OY + (YMAX + 0.8) * S); H = y + 15 * len(notes) + 30
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
             f'<rect width="{W}" height="{H}" fill="{PAGE}"/>',
             f'<text x="40" y="44" font-size="22" font-weight="bold" fill="{WALL}">1645 9th St, Berkeley — {title}</text>',
             f'<text x="40" y="66" font-size="12.5" fill="#555">{subtitle}</text>',
             f'<text x="40" y="84" font-size="11.5" fill="#a33">Sept 12, 2026 · Keith\'s sketch scaled to the measured rooms [M]; the rest estimated</text>',
             f'<text x="40" y="100" font-size="11.5" fill="#a33">walls 6″ exterior / 5″ interior · doors 2′-8″ (bath 2′-6″, closets 2′-0″ [M]) · front door 3′-0″ · slider 5′-5″ [M]</text>']
        for k in self.LAYERS: o += self.L[k]
        for n in notes:
            o.append(f'<text x="40" y="{y}" font-size="10.5" fill="#444">{n}</text>'); y += 15
        o.append("</svg>")
        return "\n".join(o)


YMAX = 44.0   # bottom of the drawing area (ft)

def build(proposed):
    P = Plan(proposed)
    # ------------------------------------------------------------------ key lines (ft); [M] = measured by Keith, Sept 12
    # Topology is Keith's Freeform sketch: one straight partition between the west rooms (bedroom 2, bath+hall, living)
    # and the east rooms (closet strip, bedroom 1, kitchen, porch). Deck and laundry side by side behind, same depth.
    h = INT / 2
    B2W = (29.5 + 65 + 27) / 12           # [M] bedroom 2 rear wall: 29½″ wall + 5′-5″ slider + 27″ wall = 10′-2″ (deck the same)
    B1W, B1D = 8 + 2 / 12, 8 + 9 / 12     # [M] bedroom 1: 8′-2″ wide × 8′-9″ deep
    XW = 0
    X2 = 0.5 + B2W + h                    # the partition (bedroom 2 / bedroom 1, living / kitchen — fireplace wall)
    XE = X2 + h + B1W + 0.5               # east face  →  house ≈19′-9″ wide (derived from the two bedrooms)
    X2W, X2E = X2 - h, X2 + h
    HALLC = 3.0                           # hall clear width (guess)
    XB = X2 - HALLC - INT                 # bath east wall
    XBW, XBE = XB - h, XB + h
    B2D = 9 + 2 / 12                      # [M] bedroom 2 depth 9′-2″ (closet door on its east wall 25½″ from the rear corner; hall door at the south-east corner)
    Y2 = 0.5 + B2D + h                    # bedroom 2 south wall
    CD = 3 + 5 / 12                       # [M] closet strip depth: bedroom 2's closet is 3′-5″ north-south
    YS = 0.5 + CD + h                     # closet strip / bedroom 1 wall
    Y1 = YS + h + B1D + h                 # bedroom 1 / kitchen wall
    XC = X2E + 4 + 11 / 12 + h            # [M] bedroom 2's closet is 4′-11″ east-west; bedroom 1's closet gets the rest of the strip
    YB = Y2 + INT + 7.6                   # bath + hall / living wall (bath 7′-7″ deep — guess)
    YF = YB + h + 12.7 + 0.5              # front face, west half (living room 12′-8″ deep — guess)
    YP = YF + 3.0                         # porch front face (porch projects 3′ — guess)
    YKP = YP - 0.5 - 7.5 - h              # kitchen / porch wall (porch 7′-6″ deep — guess)
    LD = 6.0                              # deck and laundry depth (guess)

    # ------------------------------------------------------------------ deck + laundry
    P.room("DECK", 0.5, -LD, X2W, 0, DECK, "10′-2″ wide [M] · ≈2′ above grade", size=11)
    for i in range(1, 10): P.line("floor", i, -LD, i, 0, "#cfb98f", 0.8)
    P.rect("floor", -5, -5, 0, -2, DECK, "#8a6a3a", 1)
    for i in range(1, 5): P.line("floor", -i, -5, -i, -2, "#8a6a3a", 1)
    P.text("text", -2.5, -0.9, "stairs down", 8, False, "#666")
    if not proposed:
        P.room("LAUNDRY / SHED", X2E, -LD + 0.21, XE - 0.42, 0, PORCH, "unfinished · east door only", at=((X2E + XE) / 2, -3.2), size=10)
    else:
        P.room("LAUNDRY / SHED", X2E, -LD + 0.21, XE - 0.42, 0, PORCH, "W/D · tankless WH · east door only", at=((X2E + XE) / 2, -2.2), size=10)
        P.fix(X2E + 0.4, -LD + 0.45, X2E + 2.7, -LD + 2.75, "W", "#ddd", 8); P.fix(X2E + 2.9, -LD + 0.45, X2E + 5.2, -LD + 2.75, "D", "#ddd", 8)
        P.fix(X2E + 5.8, -LD + 0.45, X2E + 7.0, -LD + 1.2, None, NEW); P.text("text", X2E + 6.4, -LD + 1.8, "tankless", 6.5, False, NEW); P.text("text", X2E + 6.4, -LD + 2.35, "WH", 6.5, False, NEW)

    # ------------------------------------------------------------------ rooms
    ECX = (X2E + XE - 0.5) / 2
    P.room("BEDROOM 2", 0.5, 0.5, X2W, Y2 - h, WOOD, "measured · slider · closet door on east wall", at=(5.6, 6.0))
    P.room("BATH", 0.5, Y2 + h, XBW, YB - h, TILE, "door past the tub", at=(3.9, Y2 + 4.5), size=11)
    P.room("HALL", XBE, Y2 + h, X2W, YB - h, WOOD, at=((XBE + X2W) / 2, Y2 + 1.2), size=9, dims=False)
    P.text("text", (XBE + X2W) / 2, Y2 + 1.7, ftin(HALLC) + " wide", 7.5, False, "#666")
    P.room("LIVING ROOM", 0.5, YB + h, X2W, YF - 0.5, WOOD, "fireplace · built-in · picture rail", at=(5.6, YB + 6.4))
    P.room("closet", X2E, 0.5, XC - h, YS - h, SOFT, None, at=((X2E + XC) / 2 + 0.4, 1.8), size=8, dims=False)
    P.text("text", (X2E + XC) / 2 + 0.4, 2.45, "bed 2 · 4′-11″ × 3′-5″ [M]", 6.5, False, "#666")
    P.room("closet", XC + h, 0.5, XE - 0.5, YS - h, SOFT, None, at=((XC + XE - 0.5) / 2, 1.8), size=7, dims=False)
    P.text("text", (XC + XE - 0.5) / 2, 2.45, "bed 1", 6.5, False, "#666")
    P.room("BEDROOM 1", X2E, YS + h, XE - 0.5, Y1 - h, WOOD, "measured · closet above · window east", at=(ECX, YS + 4.2))
    P.room("KITCHEN", X2E, Y1 + h, XE - 0.5, YKP - h, TILE, "fridge · range · WH on fireplace wall" if not proposed else "same layout · WH → counter", at=(ECX + 0.7, Y1 + 8.4), size=11)
    P.room("FRONT PORCH", X2E, YKP + h, XE - 0.5, YP - 0.5, PORCH, "enclosed entry · windows 3 sides", at=(ECX, YKP + 3.9), size=10.5)

    # ------------------------------------------------------------------ walls
    P.wall(0.25, 0, 0.25, YF, EXT); P.wall(XW, 0.25, XE, 0.25, EXT); P.wall(XE - 0.25, 0, XE - 0.25, YP, EXT)
    P.wall(XW, YF - 0.25, X2 + 0.25, YF - 0.25, EXT); P.wall(X2, YF - 0.5, X2, YP, EXT); P.wall(X2, YP - 0.25, XE, YP - 0.25, EXT)
    P.wall(X2, -LD, X2, 0, INT); P.wall(X2, -LD + 0.21, XE, -LD + 0.21, INT); P.wall(XE - 0.21, -LD, XE - 0.21, 0, INT)   # laundry box
    P.wall(X2, 0.5, X2, YF - 0.5, INT)                  # the partition / fireplace line
    P.wall(0.5, Y2, X2, Y2, INT); P.wall(0.5, YB, X2, YB, INT)   # bedroom 2 / bath+hall, bath+hall / living
    P.wall(XB, Y2, XB, YB, INT)                         # bath / hall
    P.wall(X2, YS, XE, YS, INT); P.wall(XC, 0.5, XC, YS, INT)    # closet strip, divider
    P.wall(X2, Y1, XE, Y1, INT); P.wall(X2, YKP, XE, YKP, INT)   # bedroom 1 / kitchen, kitchen / porch

    # ------------------------------------------------------------------ doors
    P.door(XE - 4.75, YP - 0.25, D30, "x", 1, -1, EXT)  # front door
    P.door(X2, YF - 0.5 - 0.3 - D28, D28, "y", 1, -1, INT)     # porch → living, south of the fireplace
    P.door(X2, 0.75, 2.0, "y", 0, +1, INT)             # [M] bedroom 2 closet door, 24″, at the rear corner (25½″ from the slider jamb = the corner)
    P.door(X2W - 0.3 - D28, Y2, D28, "x", 1, -1, INT)   # [M] bedroom 2 → hall: south wall at the east corner, swings into the bedroom
    P.door(XB, Y2 + h + 2.6, D26, "y", 0, -1, INT)      # bath → hall, past the tub, swings into the bath
    P.door(X2, Y1 - h - 0.2 - D28, D28, "y", 1, +1, INT)       # hall → bedroom 1, south end of its west wall (sketch)
    P.door(X2, Y1 + h + 0.3, D28, "y", 0, +1, INT)      # hall → kitchen, north end of its west wall (sketch, photo 12)
    P.door(XE - 0.25, Y1 + h + 0.3, D28, "y", 0, -1, EXT)      # kitchen side door, in line with the hall door
    P.opening(XBE, YB, X2W, YB)                         # hall → living room, cased opening
    P.door(XC + h + 0.35, YS, 2.0, "x", 1, -1, INT)     # bedroom 1 closet door (north wall)
    P.door(XE - 0.25, -LD + 1.4, D28, "y", 0, -1, EXT)  # laundry side door (east)
    P.slider(0.5 + 29.5 / 12, 0.25, 65 / 12)            # [M] slider 5′-5″, 29½″ from the west corner, 27″ to the east corner

    # ------------------------------------------------------------------ windows
    P.window(0.25, 3.5, 0.25, 6.5); P.window(0.25, Y2 + 2.9, 0.25, Y2 + 4.9); P.window(0.25, YB + 4.5, 0.25, YB + 8.5)
    P.window(3.5, YF - 0.25, 8.0, YF - 0.25)
    P.window(XE - 0.25, YS + 3, XE - 0.25, YS + 6); P.window(XE - 0.25, Y1 + 5.5, XE - 0.25, Y1 + 8.5)
    P.window(X2, YKP + 0.75, X2, YKP + 3.75); P.window(XE - 0.25, YKP + 0.75, XE - 0.25, YKP + 3.75)
    P.window(X2E + 0.4, YP - 0.25, X2E + 3.6, YP - 0.25)
    P.window(X2E + 1, -LD + 0.21, X2E + 4, -LD + 0.21, INT); P.window(X2E + 4.7, -LD + 0.21, X2E + 7.7, -LD + 0.21, INT); P.window(X2, -LD + 1, X2, -LD + 4, INT)
    P.window(X2E + 0.6, YKP, X2E + 2.6, YKP, INT)       # small 6-lite window above the WH → front porch

    # ------------------------------------------------------------------ fixtures
    FPY = YF - 0.5 - 0.3 - D28 - 0.9 - 4.5
    P.fix(X2W - 1.1, FPY, X2 + 0.4, FPY + 4.5, None, "#c0553f"); P.fix(X2W - 1.9, FPY, X2W - 1.1, FPY + 4.5, None, "#d9b9a8")
    P.text("text", X2 - 0.8, FPY + 2.4, "FP", 8, True, "#fff")
    P.fix(X2W - 0.45, YB + h + 0.4, X2E, YB + h + 2.4, None, "#ddd"); P.text("text", X2W - 1.4, YB + h + 1.5, "built-in", 7, False, "#555")
    P.line("fix", X2E + 0.3, YS - h - 0.3, XC - h - 0.3, YS - h - 0.3, "#888", 0.8, "2,2")   # bedroom 2 closet rod (back wall)
    P.line("fix", XC + h + 0.3, 1.3, XE - 0.8, 1.3, "#888", 0.8, "2,2")               # bedroom 1 closet rod
    P.fix(XBW - 5, Y2 + h, XBW, Y2 + h + 2.5, "tub", "#fff"); P.text("text", XBW - 0.3, Y2 + h + 1.25, "shower", 6, False, "#666", rot=-90)
    P.fix(XBW - 3, YB - h - 1.8, XBW, YB - h, "vanity", "#e8e8e8")
    P.circle("fix", 1.55, YB - h - 1.2, 0.55, "#fff"); P.fix(0.5, YB - h - 1.85, 1.15, YB - h - 0.55, None, "#fff")   # toilet
    if not proposed:
        P.fix(XBE + 0.3, YB - h - 2.9, X2W - 0.3, YB - h - 0.2, "floor furnace", "#999", 7)
        P.text("text", (XBE + X2W) / 2, YB - h - 0.9, "(red-tagged)", 6.5, False, "#333")
    else:
        P.text("text", (XBE + X2W) / 2, YB - h - 1.6, "furnace", 6.5, False, NEW); P.text("text", (XBE + X2W) / 2, YB - h - 1.0, "removed", 6.5, False, NEW)
        for (mx, my, mw, mh) in ((0.5, YB + 2.0, 0.35, 2.6), (XE - 0.85, YS + 6.6, 0.35, 2.0), (0.5, 0.9, 0.35, 2.6)):   # mini-split heads: living, bedroom 1, bedroom 2
            P.fix(mx, my, mx + mw, my + mh, None, NEW); P.text("text", mx + 0.9, my + 1.5, "MS", 6.5, False, NEW)
    P.fix(XE - 2.5, Y1 + 3.4, XE - 0.5, YKP - h - 0.3, None, "#e8e8e8"); P.fix(XE - 2.3, Y1 + 5.5, XE - 0.7, Y1 + 8.5, "sink", "#fff", 7)
    P.text("text", XE - 1.5, Y1 + 10.3, "tile", 7, False, "#555"); P.text("text", XE - 1.5, Y1 + 10.9, "counter", 7, False, "#555")
    P.fix(X2E, Y1 + h + 3.4, X2E + 2.8, Y1 + h + 6.2, "fridge", "#ddd", 7); P.fix(X2E, Y1 + h + 6.4, X2E + 2.5, Y1 + h + 8.9, "range", "#ddd", 7)
    if not proposed:
        P.circle("fix", X2E + 0.8, YKP - h - 0.8, 0.7); P.text("text", X2E + 0.8, YKP - h - 0.6, "WH", 6.5)
    else:
        P.fix(X2E, Y1 + h + 9.1, X2E + 2.0, YKP - h - 0.2, None, "#e8e8e8"); P.text("text", X2E + 1.0, YKP - h - 1.3, "counter", 6.5, False, "#555")

    # ------------------------------------------------------------------ site + dims
    P.fix(XE - 5, YP, XE - 1.5, YP + 2.4, None, "#e0e0e0"); [P.line("fix", XE - 5, YP + 0.8 * i, XE - 1.5, YP + 0.8 * i, "#999", 0.8) for i in (1, 2)]
    P.text("text", XE - 3.25, YP + 3.1, "concrete steps", 8, False, "#666")
    P.dimh(XW, XE, YP + 4.4, ftin(XE) + " (from the two bedrooms)"); P.dimh(0.5, X2W, -LD - 1.4, "bedroom 2 + deck " + ftin(B2W) + " [M]"); P.dimh(X2E, XE - 0.5, -LD - 1.4, "bedroom 1 " + ftin(B1W) + " [M]")
    P.dimv(0, YF, -2.4); P.dimv(-LD, YP, XE + 2.4); P.dimv(0.5, Y2 - h, -0.7, "bed 2 " + ftin(Y2 - h - 0.5) + " [M]"); P.dimv(YS + h, Y1 - h, XE + 1.1, "bed 1 " + ftin(B1D) + " [M]")
    P.text("text", XE / 2, YP + 5.6, "9th Street (front)", 10, False, "#555")
    a = P.px(-4, YF + 1.5)
    P.L["dim"].append(f'<g transform="translate({a[0]:.0f},{a[1]:.0f})"><polygon points="0,-20 6,4 0,0 -6,4" fill="{WALL}"/><text x="0" y="18" font-size="11" text-anchor="middle" font-weight="bold">N</text><text x="0" y="31" font-size="7.5" text-anchor="middle" fill="#666">away from street</text></g>')
    P.line("dim", -5, YP + 1.5, 0, YP + 1.5, WALL, 2); [P.line("dim", i, YP + 1.2, i, YP + 1.8, WALL, 1) for i in range(-5, 1)]
    P.text("dim", -2.5, YP + 2.4, "0        5 ft", 8.5, False, "#444")
    lx, ly = 0, YMAX - 0.3
    P.line("dim", lx, ly, lx + 1.5, ly, GLASS, 2); P.text("dim", lx + 1.9, ly + 0.15, "window / glass", 8.5, False, "#555", "start")
    P.line("dim", lx + 5.5, ly, lx + 7, ly, "#999", 1, "4,3"); P.text("dim", lx + 7.4, ly + 0.15, "cased opening", 8.5, False, "#555", "start")
    P.text("dim", lx + 11, ly + 0.15, "[M] = measured by Keith, Sept 12", 8.5, False, "#555", "start")
    if proposed:
        P.rect("dim", lx + 21, ly - 0.25, lx + 22.5, ly + 0.25, NEW); P.text("dim", lx + 22.9, ly + 0.15, "new / changed", 8.5, False, "#555", "start")
    return P


NOTES_EXISTING = [
    "Keith's sketch, scaled to measurements. Measured [M]: bedroom 2 10′-2″ × 9′-2″ (rear wall 29½″ + 5′-5″ slider + 27″); bedroom 2's closet 4′-11″ × 3′-5″ with its 24″ door at the rear corner of the east wall; bedroom 1 8′-2″ × 8′-9″; deck 10′-2″ wide. The two bedroom widths make the house ≈19′-9″ wide.",
    "One straight partition (the fireplace wall) runs the full depth. West: bedroom 2, bath with the 3′ hall beside it, living room. East: closet strip (3′-5″ deep), bedroom 1, kitchen, front porch. Deck and laundry/shed side by side behind the house. The hall is only the strip in front of the bath; the bath door faces the bedroom doors (bedroom 2's at the hall's north end, bedroom 1's on its east side); kitchen door at the north end of its west wall with the side door opposite; living room through a cased opening at the hall's south end.",
    "Unmeasured (drawn from the sketch): hall 3′ wide (so bath 6′-8″); bedroom 1's closet 2′-10″ (rest of the strip); bath 7′-7″ deep; living room 12′-8″ deep; kitchen 12′-5″; porch 7′-6″ deep projecting 3′; deck and laundry 6′ deep; windows.",
]
NOTES_PROPOSED = [
    "Same plan as existing — no rooms move and no walls change. Kitchen stays where it is.",
    "Water heater leaves the kitchen: a tankless unit goes on the wall in the laundry / shed (gas + vent + cold/hot lines run from there), and the freed corner by the range becomes counter. Washer and dryer stay in the shed; it keeps its outside-only east door.",
    "Floor furnace (red-tagged) comes out; the hall floor is patched. Heat by ductless mini-splits: heads marked MS in the living room and both bedrooms, outdoor unit on the east side by the shed.",
    "Not shown: 200 A panel and rewire, EV charger, driveway, finishes. Bearing: nothing is removed on the partition.",
]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for v, proposed, notes, title, sub in (
        ("existing", False, NOTES_EXISTING, "Existing Layout", "2 bed · 1 bath · 734 sq ft listed · built 1919 · 2,613 sq ft lot · single-story bungalow · drawn at 20 px/ft"),
        ("proposed", True, NOTES_PROPOSED, "Proposed Layout", "same rooms · water heater out of the kitchen → tankless in the shed · floor furnace out → mini-splits · laundry stays in the shed"),
    ):
        P = build(proposed)
        open(os.path.join(here, f"{v}.svg"), "w").write(P.svg(title, sub, notes))
        print(v)
        for name, w, hh in P.rooms:
            if w * hh > 15: print(f"  {name:20s} {ftin(w):>8s} × {ftin(hh):<8s} {round(w*hh):4d} sf")
