"""Schematics drawn to look like they came out of PowerPoint.

Office theme colours in their pastel tints: fill is the theme colour at
"Lighter 60%", the outline is the base accent, the text is "Darker 50%". That
combination is a stock PowerPoint shape style, so the result reads as a slide
rather than as a hand-drawn figure.
"""
import os
OUT = "/home/claude/site/assets/fig"
os.makedirs(OUT, exist_ok=True)

SLIDE = "#fcfcfb"      # matches the figure panels on the pink page
SOIL = "#edebe6"
TXT = "#3b3838"      # Text 1, lighter 25%
TXT2 = "#6b6764"     # quieter caption grey
LINE = "#8c8c8c"     # connector grey
HAIR = "#bfbfbf"     # leader lines

FONT = "Aptos, Calibri, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

# fill / outline / title / subtitle, per Office accent
PAL = {
    "blue":   dict(fill="#b4c7e7", line="#4472c4", tx="#1f3864", sx="#2f5597"),
    "pale":   dict(fill="#deebf7", line="#5b9bd5", tx="#1f4e79", sx="#2e75b6"),
    "orange": dict(fill="#f8cbad", line="#ed7d31", tx="#833c0c", sx="#c55a11"),
    "green":  dict(fill="#c5e0b4", line="#70ad47", tx="#375623", sx="#548235"),
    "grey":   dict(fill="#ededed", line="#a5a5a5", tx="#3b3838", sx="#595959"),
}


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{title}" style="font-family:{FONT}">'
        f'<defs>'
        f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
        f'<path d="M0.5,1.2 L9.4,5 L0.5,8.8 Z" fill="{LINE}"/></marker>'
        f'<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
        f'<path d="M0.5,1.2 L9.4,5 L0.5,8.8 Z" fill="#2f5597"/></marker>'
        f'<filter id="sh" x="-30%" y="-30%" width="170%" height="190%">'
        f'<feDropShadow dx="0" dy="1.3" stdDeviation="2.1" flood-color="#1f2328" '
        f'flood-opacity="0.16"/></filter>'
        f'</defs>'
        f'<rect width="{w}" height="{h}" fill="{SLIDE}"/>{body}</svg>')


def shape(x, y, w, h, label, sub=None, tone="pale", rx=5, size=15):
    """A filled PowerPoint block. `label` splits on | for extra lines."""
    c = PAL[tone]
    o = (f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" '
         f'rx="{rx}" fill="{c["fill"]}" stroke="{c["line"]}" '
         f'stroke-width="1.25"/></g>')
    lines = label.split("|")
    n = len(lines)
    step = size + 4
    cy = y + h / 2 - (n - 1) * step / 2 - (6 if sub else 0)
    for i, ln in enumerate(lines):
        o += (f'<text x="{x+w/2}" y="{cy + i*step}" text-anchor="middle" '
              f'font-size="{size}" fill="{c["tx"]}" '
              f'dominant-baseline="central">{ln}</text>')
    if sub:
        o += (f'<text x="{x+w/2}" y="{cy + n*step - 1}" text-anchor="middle" '
              f'font-size="{size-3}" fill="{c["sx"]}" '
              f'dominant-baseline="central">{sub}</text>')
    return o


def conn(x1, y1, x2, y2, col=LINE, marker="ah", w=1.5):
    return (f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="{w}" '
            f'fill="none" marker-end="url(#{marker})" stroke-linecap="round"/>')


def elbow(x1, y1, x2, y2, r=9, col=LINE, w=1.5):
    """Right-angle connector with a softened corner."""
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    return (f'<path d="M{x1},{y1} L{x2-sx*r},{y1} Q{x2},{y1} {x2},{y1+sy*r} '
            f'L{x2},{y2}" stroke="{col}" stroke-width="{w}" fill="none" '
            f'marker-end="url(#ah)" stroke-linecap="round"/>')


def leader(x1, y1, x2, y2):
    return (f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{HAIR}" '
            f'stroke-width="1" fill="none"/>')


def txt(x, y, s, anchor="middle", size=13, col=TXT, weight="400"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{col}" font-weight="{weight}">{s}</text>')


# ======================================================= 1. vine deployment
def vine():
    W, H = 900, 322
    GROUND = 52
    TOP, BOT, MID = 112, 172, 142
    b = ""
    # soil
    b += f'<rect x="0" y="{GROUND}" width="{W}" height="{H-GROUND}" fill="{SOIL}"/>'
    b += f'<path d="M0,{GROUND} L{W},{GROUND}" stroke="{HAIR}" stroke-width="1.4"/>'
    b += txt(W - 14, GROUND - 11, "Ground level", anchor="end", size=12.5,
             col=TXT2)

    # access chamber
    b += ('<g filter="url(#sh)"><rect x="30" y="52" width="90" height="160" '
          f'rx="3" fill="{PAL["grey"]["fill"]}" stroke="{PAL["grey"]["line"]}" '
          'stroke-width="1.25"/></g>')
    b += txt(75, 234, "Access", size=13, col=TXT)
    b += txt(75, 251, "chamber", size=13, col=TXT)

    # duct: straight run, then a swept bend down towards the next chamber.
    # Centreline radius 70 about (560, 212); walls are that radius +/- 30.
    b += ('<g filter="url(#sh)"><path d="M120,112 L560,112 '
          'A100,100 0 0 1 660,212 L660,254 L600,254 L600,212 '
          'A40,40 0 0 0 560,172 L120,172 Z" '
          f'fill="#ffffff" stroke="{PAL["grey"]["line"]}" '
          'stroke-width="1.6" stroke-linejoin="round"/></g>')
    b += (f'<path d="M600,254 L600,280 M660,254 L660,280" '
          f'stroke="{PAL["grey"]["line"]}" stroke-width="1.6" '
          'stroke-dasharray="5 5" opacity="0.75"/>')
    b += txt(690, 220, "90&#176; bend to", anchor="start", size=12.5, col=TXT2)
    b += txt(690, 237, "next chamber", anchor="start", size=12.5, col=TXT2)

    # silt ahead of the tip
    for cx, cy, r in ((548, 150, 11), (568, 156, 9), (538, 159, 7),
                      (562, 135, 7)):
        b += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#dbdbdb" '
              f'stroke="{PAL["grey"]["line"]}" stroke-width="1"/>')

    # robot: everted body, fibre running inside it, tip at the front
    b += ('<g filter="url(#sh)"><rect x="120" y="132" width="360" height="21" '
          f'rx="10.5" fill="{PAL["blue"]["fill"]}" '
          f'stroke="{PAL["blue"]["line"]}" stroke-width="1.25"/></g>')
    b += (f'<path d="M132,{MID+0.5} L462,{MID+0.5}" stroke="#ed7d31" '
          'stroke-width="1.6" stroke-linecap="round" opacity="0.95"/>')
    b += ('<g filter="url(#sh)"><circle cx="482" cy="{}" r="14" '
          'fill="#8eaadb" stroke="{}" stroke-width="1.25"/></g>'
          .format(MID, PAL["blue"]["line"]))
    b += conn(502, MID, 530, MID, col="#2f5597", marker="ahb", w=2)

    # callouts
    b += leader(262, 130, 262, 96)
    b += txt(262, 88, "Everted body, stationary against duct wall", size=13)
    b += leader(516, 126, 516, 96)
    b += txt(516, 88, "Advancing tip", size=13)
    b += leader(220, 155, 220, 202)
    b += txt(220, 218, "Fibre drawn in behind tip", size=13)
    b += leader(552, 174, 516, 202)
    b += txt(516, 218, "Silt, partial blockage", size=13)

    # extent bar
    b += (f'<path d="M120,288 L640,288 M120,282 L120,294 M640,282 L640,294" '
          f'stroke="{HAIR}" stroke-width="1.3"/>')
    b += txt(380, 311, "Single run, chamber to chamber", size=12.5, col=TXT2)

    open(f"{OUT}/vine-deployment.svg", "w").write(
        svg(W, H, b, "Vine robot deploying through a buried duct"))


# ===================================================== 2. VLA architecture
def vla():
    W, H = 900, 400
    b = ""
    b += shape(30, 40, 170, 54, "RGB observation", tone="pale")
    b += shape(30, 150, 170, 54, "Optical tactile", sub="raw contact image",
               tone="orange")
    b += shape(30, 306, 170, 54, "Task instruction", sub="natural language",
               tone="pale")

    names = ["As an image", "As language tokens", "Via a learned encoder"]
    ys = [141, 191, 241]
    for y, n in zip(ys, names):
        b += shape(250, y, 200, 40, n, tone="orange", size=14)
    b += txt(350, 126, "Three encoding strategies, the variable under test",
             size=12.5, col=PAL["orange"]["sx"], weight="600")

    b += shape(505, 145, 170, 132,
               "Vision&#8211;language&#8211;|action backbone",
               sub="LoRA fine-tuned", tone="blue")
    b += shape(725, 170, 150, 82, "Fold-direction|selection",
               sub="ABB YuMi, cloth", tone="green", size=14)

    b += elbow(200, 67, 590, 141)
    b += elbow(200, 333, 590, 281)
    for y, land in zip(ys, (175, 211, 247)):
        b += conn(200, 177, 246, y + 20)
        b += conn(450, y + 20, 501, land)
    b += conn(675, 211, 721, 211)

    b += txt(800, 272, "Evaluated per material", size=12.5, col=TXT2)
    b += txt(30, 386, "Backbone, task and sensor held constant; only the "
                      "tactile encoding varies.", anchor="start", size=12.5,
             col=TXT2)

    open(f"{OUT}/vla-architecture.svg", "w").write(
        svg(W, H, b, "Tactile encoding strategies for a "
                     "vision-language-action model"))


# ============================================================= 3. lap sim
def lapsim():
    W, H = 360, 536
    steps = [
        ("Proposed circuit|geometry", "centreline and width", "pale"),
        ("Track model", "curvature, elevation, surface", "pale"),
        ("Vehicle and|energy model", "Gen3 powertrain limits", "pale"),
        ("Lap simulation", "optimal speed trace", "blue"),
        ("Design read-out", "lap time, energy, overtaking", "green"),
    ]
    b = ""
    y = 14
    for i, (label, sub, tone) in enumerate(steps):
        h = 72
        b += shape(30, y, 300, h, label, sub=sub, tone=tone)
        if i < len(steps) - 1:
            b += conn(180, y + h + 5, 180, y + h + 22, w=1.8)
        y += h + 26
    b += txt(180, 512, "Iterated per candidate layout", size=12.5, col=TXT2)
    open(f"{OUT}/lapsim-pipeline.svg", "w").write(
        svg(W, H, b, "Lap simulation pipeline"))


# ======================================================= 4. race prediction
def prediction():
    W, H = 900, 244
    b = ""
    b += shape(25, 26, 180, 96, "Live race state", sub="timing and telemetry",
               tone="pale")
    b += shape(245, 26, 190, 96, "Engineered|features", tone="orange")
    b += shape(475, 26, 180, 96, "Gradient-boosted|classifier",
               sub="trained in-house", tone="blue")
    b += shape(695, 26, 180, 96, "Win probability", sub="on the world feed",
               tone="green")
    for x1 in (205, 435, 655):
        b += conn(x1, 74, x1 + 36, 74, w=1.8)

    b += leader(340, 124, 340, 138)
    b += txt(340, 154, "Four feature families", size=12.5,
             col=PAL["orange"]["sx"], weight="600")
    for i, t in enumerate(["battery advantage relative to nearby cars",
                           "driver and circuit historical priors",
                           "race progression",
                           "speed trend"]):
        b += txt(340, 174 + i * 17, t, size=12.5, col=TXT)

    open(f"{OUT}/prediction-pipeline.svg", "w").write(
        svg(W, H, b, "Race outcome prediction pipeline"))


vine(); vla(); lapsim(); prediction()
print("wrote 4 diagrams")
