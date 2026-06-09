from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import pptx.oxml.ns as nsmap
from lxml import etree
import copy

# ── Color Palette ────────────────────────────────────────────────────────────
BG_COLOR     = RGBColor(0x1A, 0x1A, 0x1A)   # near-black charcoal
ACCENT_COLOR = RGBColor(0x00, 0x8B, 0x8B)   # deep teal
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY   = RGBColor(0xC8, 0xC8, 0xC8)
DIM_GRAY     = RGBColor(0x88, 0x88, 0x88)
ACCENT_PALE  = RGBColor(0x00, 0xBF, 0xBF)   # lighter teal for sub-items

# ── Slide dimensions (16:9) ───────────────────────────────────────────────────
W = Inches(13.333)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK_LAYOUT = prs.slide_layouts[6]  # truly blank


# ── Helpers ───────────────────────────────────────────────────────────────────

def fill_bg(slide, color=BG_COLOR):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, l, t, w, h, color):
    shape = slide.shapes.add_shape(
        pptx.enum.shapes.MSO_SHAPE_TYPE.AUTO_SHAPE if False else 1,
        l, t, w, h
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_text_box(slide, text, l, t, w, h,
                 font_size=24, bold=False, color=WHITE,
                 align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txb = slide.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = wrap
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size   = Pt(font_size)
    run.font.bold   = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name   = "Helvetica Neue"
    return txb


def add_multiline_tb(slide, lines, l, t, w, h,
                     font_size=24, color=WHITE, align=PP_ALIGN.LEFT,
                     line_spacing_pt=None):
    """lines = list of (text, bold, color_override_or_None)"""
    txb = slide.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = True
    tf  = txb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(lines):
        text, bold, col = item
        col = col or color
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = align
        if line_spacing_pt:
            p.line_spacing = Pt(line_spacing_pt)
        run = p.add_run()
        run.text = text
        run.font.size  = Pt(font_size)
        run.font.bold  = bold
        run.font.color.rgb = col
        run.font.name  = "Helvetica Neue"
    return txb


def accent_rule(slide, y_top, width_frac=0.12):
    """Horizontal teal rule under a heading."""
    add_rect(slide,
             Inches(0.5), y_top,
             Inches(13.333 * width_frac), Inches(0.045),
             ACCENT_COLOR)


def slide_number(slide, n, total=14):
    add_text_box(slide, f"{n} / {total}",
                 Inches(11.9), Inches(7.05), Inches(1.2), Inches(0.35),
                 font_size=13, color=DIM_GRAY, align=PP_ALIGN.RIGHT)


def big_number(slide, number_str, label_str, l, t, w=Inches(3.5)):
    """Stacked big number + small label."""
    add_text_box(slide, number_str, l, t, w, Inches(0.9),
                 font_size=52, bold=True, color=ACCENT_COLOR, align=PP_ALIGN.LEFT)
    add_text_box(slide, label_str, l, t + Inches(0.85), w, Inches(0.45),
                 font_size=18, color=LIGHT_GRAY, align=PP_ALIGN.LEFT)


def heading(slide, text, t=Inches(0.42)):
    add_text_box(slide, text,
                 Inches(0.5), t, Inches(12.3), Inches(0.85),
                 font_size=40, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    accent_rule(slide, t + Inches(0.88))


def bullet_block(slide, items, t_start, font_size=24, indent=Inches(0.5)):
    """items = list of (text, is_accent)"""
    for i, (text, is_accent) in enumerate(items):
        col = ACCENT_COLOR if is_accent else LIGHT_GRAY
        add_text_box(slide,
                     f"• {text}",
                     indent, t_start + Inches(i * 0.62), Inches(12.1), Inches(0.6),
                     font_size=font_size, color=col)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

# Teal left accent bar
add_rect(s, Inches(0), Inches(0), Inches(0.18), H, ACCENT_COLOR)

# Club name
add_text_box(s, "Kids Creativity", Inches(0.55), Inches(1.5), Inches(12), Inches(1.2),
             font_size=64, bold=True, color=WHITE)
add_text_box(s, "Confidence Club", Inches(0.55), Inches(2.6), Inches(12), Inches(1.2),
             font_size=64, bold=True, color=ACCENT_COLOR)

# Rule
add_rect(s, Inches(0.55), Inches(3.75), Inches(3.5), Inches(0.055), ACCENT_COLOR)

# Subtitle
add_text_box(s, "The Monthly Encouragement Subscription",
             Inches(0.55), Inches(3.9), Inches(10), Inches(0.65),
             font_size=26, color=LIGHT_GRAY)

# Author / date
add_text_box(s, "D. Long  ·  June 2026",
             Inches(0.55), Inches(6.7), Inches(6), Inches(0.45),
             font_size=18, color=DIM_GRAY)

slide_number(s, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — The Problem
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "Kids Stop Creating")

# Icon-like large text symbol
add_text_box(s, "✦", Inches(10.8), Inches(1.8), Inches(2), Inches(2),
             font_size=110, color=RGBColor(0x00, 0x4A, 0x4A), align=PP_ALIGN.CENTER)

items = [
    ("Ages 3–7: kids create constantly — no fear, no comparison.", False),
    ("Ages 8–10: they stop. They compare. They lose encouragement.", True),
    ("No product exists to keep them creating.", False),
]
bullet_block(s, items, Inches(1.65))

# Callout stat
add_text_box(s, "The drop-off happens before middle school.",
             Inches(0.5), Inches(5.8), Inches(10), Inches(0.55),
             font_size=20, color=DIM_GRAY, italic=True)

slide_number(s, 2)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Why Parents Care
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "Parents Spend Billions on Confidence")

# Three big numbers
big_number(s, "$1,500–3,000", "per family / year on enrichment", Inches(0.5), Inches(1.9))
big_number(s, "20M+",         "households in target market",       Inches(4.8), Inches(1.9))
big_number(s, "$0",           "products for creative confidence",  Inches(9.0), Inches(1.9))

# Rule divider
add_rect(s, Inches(0.5), Inches(3.6), Inches(12.3), Inches(0.04), RGBColor(0x33, 0x33, 0x33))

items = [
    ("Parents already budget heavily for enrichment activities.", False),
    ("They need something confidence-focused, not just skill-based.", False),
    ("Creative confidence = gap nobody has filled.", True),
]
bullet_block(s, items, Inches(3.8), font_size=22)

slide_number(s, 3)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — The Idea (Flow Diagram)
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "Here's What We Do")

# Flow diagram nodes
nodes = [
    ("Kid\nCreates", Inches(0.6)),
    ("Kid\nSubmits", Inches(3.3)),
    ("Kid Gets\nCelebrated", Inches(6.0)),
    ("Kid Creates\nAgain", Inches(8.7)),
]

node_w = Inches(2.1)
node_h = Inches(1.7)
node_t = Inches(2.3)

for label, left in nodes:
    # Box
    box = s.shapes.add_shape(1, left, node_t, node_w, node_h)
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0x0D, 0x3D, 0x3D)
    box.line.color.rgb = ACCENT_COLOR
    box.line.width = Pt(1.5)
    tf = box.text_frame
    tf.word_wrap = True
    p  = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    run.font.size  = Pt(22)
    run.font.bold  = True
    run.font.color.rgb = WHITE
    run.font.name  = "Helvetica Neue"

    # Auto-vertical center via XML margin
    from pptx.oxml.ns import qn
    txBody = tf._txBody
    bodyPr = txBody.find(qn('a:bodyPr'))
    if bodyPr is not None:
        bodyPr.set('anchor', 'ctr')

# Arrows between nodes
arrow_t = node_t + Inches(0.75)
arrow_lefts = [Inches(2.72), Inches(5.42), Inches(8.12)]
for al in arrow_lefts:
    add_text_box(s, "→", al, arrow_t, Inches(0.55), Inches(0.55),
                 font_size=30, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)

# Loop arrow hint
add_text_box(s, "↺  Every month. Recurring.",
             Inches(0.5), Inches(4.3), Inches(12), Inches(0.55),
             font_size=22, bold=True, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)

# Sub-note
add_text_box(s, "No product development. The child creates the product.",
             Inches(0.5), Inches(5.1), Inches(12), Inches(0.5),
             font_size=19, color=DIM_GRAY, align=PP_ALIGN.CENTER)

slide_number(s, 4)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — What's Inside the Box
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "What Kid Gets Each Month")

# Left column: icon + item cards
items_left = [
    ("✉", "Personalized encouragement letter\n(addressed to the child by name)"),
    ("🖼", "Printed reproduction or keepsake\nof their submitted work"),
]
items_right = [
    ("🎯", "Creative challenge card\nfor next month"),
    ("⭐", "Milestone rewards over time\n(streaks, certificates, surprises)"),
]

card_w = Inches(5.5)
card_h = Inches(1.55)
gap    = Inches(0.25)
left_x = Inches(0.5)
right_x= Inches(7.0)
top_y  = Inches(1.65)

def item_card(slide, icon, text, l, t, w, h):
    box = slide.shapes.add_shape(1, l, t, w, h)
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0x26, 0x26, 0x26)
    box.line.color.rgb = RGBColor(0x38, 0x38, 0x38)
    box.line.width = Pt(0.75)
    # icon
    add_text_box(slide, icon, l + Inches(0.15), t + Inches(0.25), Inches(0.6), Inches(0.9),
                 font_size=30, color=ACCENT_COLOR)
    # text
    add_text_box(slide, text, l + Inches(0.85), t + Inches(0.1), w - Inches(1.0), h - Inches(0.15),
                 font_size=20, color=LIGHT_GRAY)

for i, (icon, text) in enumerate(items_left):
    item_card(s, icon, text, left_x, top_y + i*(card_h + gap), card_w, card_h)

for i, (icon, text) in enumerate(items_right):
    item_card(s, icon, text, right_x, top_y + i*(card_h + gap), card_w, card_h)

# Bottom note
add_text_box(s, "Fully personalized. Mailed or digital delivery depending on tier.",
             Inches(0.5), Inches(5.6), Inches(12.3), Inches(0.5),
             font_size=18, color=DIM_GRAY, italic=True)

slide_number(s, 5)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — What We're Actually Selling
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "It's Not Art. It's Confidence.")

add_text_box(s, "We're selling:", Inches(0.5), Inches(1.65), Inches(5), Inches(0.5),
             font_size=22, color=DIM_GRAY)

words = ["Confidence", "Recognition", "Encouragement", "A lasting memory"]
for i, w_text in enumerate(words):
    add_text_box(s, w_text,
                 Inches(0.5), Inches(2.25) + Inches(i * 0.72),
                 Inches(7), Inches(0.65),
                 font_size=32, bold=True, color=ACCENT_COLOR)

# Quote card
qbox = s.shapes.add_shape(1, Inches(7.3), Inches(1.65), Inches(5.7), Inches(3.2))
qbox.fill.solid()
qbox.fill.fore_color.rgb = RGBColor(0x0D, 0x3D, 0x3D)
qbox.line.fill.background()

add_text_box(s, "“A child getting mail that says\n‘We loved your imagination’\nchanges something.”",
             Inches(7.55), Inches(1.9), Inches(5.2), Inches(2.8),
             font_size=21, color=WHITE, italic=True, align=PP_ALIGN.LEFT)

# Rule
add_rect(s, Inches(0.5), Inches(5.5), Inches(12.3), Inches(0.04), RGBColor(0x33, 0x33, 0x33))

add_text_box(s, "The product is validation. The box is delivery.",
             Inches(0.5), Inches(5.65), Inches(12), Inches(0.5),
             font_size=19, color=DIM_GRAY, italic=True)

slide_number(s, 6)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Pricing Tiers
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "Three Entry Points")

tiers = [
    ("Starter",  "$9.99",  ["Digital feedback", "Gallery feature", "Monthly prompt"]),
    ("Standard", "$17.99", ["↑ Everything above", "Printed card", "Keepsake item"]),
    ("Premium",  "$29.99", ["↑ Everything above", "Framed print", "Rewards program"]),
    ("Family",   "$39.99", ["Up to 3 kids", "All Standard features", "Shared gallery"]),
]

card_w  = Inches(2.9)
card_h  = Inches(4.2)
card_t  = Inches(1.65)
gap_x   = Inches(0.28)
start_x = Inches(0.5)

for i, (name, price, features) in enumerate(tiers):
    lx = start_x + i * (card_w + gap_x)
    is_featured = (name == "Standard")

    box = s.shapes.add_shape(1, lx, card_t, card_w, card_h)
    if is_featured:
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(0x0D, 0x3D, 0x3D)
        box.line.color.rgb = ACCENT_COLOR
        box.line.width = Pt(2)
    else:
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(0x26, 0x26, 0x26)
        box.line.color.rgb = RGBColor(0x44, 0x44, 0x44)
        box.line.width = Pt(1)

    # Tier name
    add_text_box(s, name, lx + Inches(0.15), card_t + Inches(0.18),
                 card_w - Inches(0.3), Inches(0.45),
                 font_size=20, bold=True,
                 color=ACCENT_COLOR if is_featured else LIGHT_GRAY,
                 align=PP_ALIGN.CENTER)

    # Price
    add_text_box(s, price, lx + Inches(0.1), card_t + Inches(0.65),
                 card_w - Inches(0.2), Inches(0.75),
                 font_size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    add_text_box(s, "/ month", lx + Inches(0.1), card_t + Inches(1.35),
                 card_w - Inches(0.2), Inches(0.35),
                 font_size=14, color=DIM_GRAY, align=PP_ALIGN.CENTER)

    # Divider
    add_rect(s, lx + Inches(0.2), card_t + Inches(1.8),
             card_w - Inches(0.4), Inches(0.03),
             RGBColor(0x44, 0x44, 0x44))

    # Features
    for j, feat in enumerate(features):
        add_text_box(s, f"• {feat}",
                     lx + Inches(0.18), card_t + Inches(1.95) + Inches(j * 0.58),
                     card_w - Inches(0.36), Inches(0.55),
                     font_size=16, color=LIGHT_GRAY)

    # "Popular" badge for featured
    if is_featured:
        add_text_box(s, "MOST POPULAR", lx, card_t - Inches(0.38),
                     card_w, Inches(0.35),
                     font_size=12, bold=True, color=ACCENT_COLOR,
                     align=PP_ALIGN.CENTER)

slide_number(s, 7)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Who Wants This
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "Multiple Customer Anchors")

segments = [
    ("👨‍👩‍👧", "Parents",            "20M+\nhouseholds",   "Confidence-building for their child"),
    ("👴",    "Grandparents",       "35M+\nhouseholds",   "Meaningful gifts that celebrate grandkids"),
    ("📚",    "Homeschool\nFamilies","5M+\nhouseholds",    "Screen-free creative engagement"),
]

col_w  = Inches(3.8)
col_h  = Inches(4.1)
col_t  = Inches(1.65)
gaps   = [Inches(0.55), Inches(4.5), Inches(8.45)]

for icon, title, stat, desc in zip(
        [x[0] for x in segments],
        [x[1] for x in segments],
        [x[2] for x in segments],
        [x[3] for x in segments]):
    lx = gaps[segments.index((icon, title, stat, desc))]

    box = s.shapes.add_shape(1, lx, col_t, col_w, col_h)
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0x26, 0x26, 0x26)
    box.line.color.rgb = RGBColor(0x38, 0x38, 0x38)

    add_text_box(s, icon, lx, col_t + Inches(0.2), col_w, Inches(0.75),
                 font_size=40, align=PP_ALIGN.CENTER)
    add_text_box(s, title, lx, col_t + Inches(0.95), col_w, Inches(0.7),
                 font_size=24, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(s, stat, lx, col_t + Inches(1.65), col_w, Inches(0.85),
                 font_size=30, bold=True, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)
    add_text_box(s, desc, lx + Inches(0.15), col_t + Inches(2.6), col_w - Inches(0.3), Inches(1.0),
                 font_size=18, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

add_text_box(s, "Not betting on one customer type.",
             Inches(0.5), Inches(6.05), Inches(12.3), Inches(0.5),
             font_size=20, bold=True, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)

slide_number(s, 8)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Competition
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "Who Else Does This?")

rows = [
    ("Artkive",           "Parent storage problem",    "Not ours"),
    ("Art Supply Boxes",  "Send supplies",             "Not celebration"),
    ("Art Contests",      "Winners only",              "Not recurring"),
]

col_xs = [Inches(0.5), Inches(4.8), Inches(9.0)]
col_ws = [Inches(4.0), Inches(3.9), Inches(3.9)]
row_h  = Inches(0.75)
header_t = Inches(1.62)

# Header row
headers = ["Competitor", "What They Do", "Why It's Different"]
for j, (hdr, lx, lw) in enumerate(zip(headers, col_xs, col_ws)):
    add_text_box(s, hdr, lx, header_t, lw, Inches(0.45),
                 font_size=17, bold=True, color=DIM_GRAY)

add_rect(s, Inches(0.5), header_t + Inches(0.45), Inches(12.3), Inches(0.03), RGBColor(0x44,0x44,0x44))

for i, (comp, what, diff) in enumerate(rows):
    row_t = header_t + Inches(0.52) + Inches(i * 1.0)
    # Row bg alternating
    if i % 2 == 0:
        add_rect(s, Inches(0.5), row_t, Inches(12.3), row_h, RGBColor(0x22,0x22,0x22))

    add_text_box(s, comp, col_xs[0], row_t + Inches(0.1), col_ws[0], row_h,
                 font_size=22, bold=True, color=WHITE)
    add_text_box(s, what, col_xs[1], row_t + Inches(0.1), col_ws[1], row_h,
                 font_size=20, color=LIGHT_GRAY)
    add_text_box(s, diff, col_xs[2], row_t + Inches(0.1), col_ws[2], row_h,
                 font_size=20, color=ACCENT_COLOR)

# Callout box
cbox = s.shapes.add_shape(1, Inches(0.5), Inches(5.05), Inches(12.3), Inches(1.15))
cbox.fill.solid()
cbox.fill.fore_color.rgb = RGBColor(0x0D, 0x3D, 0x3D)
cbox.line.fill.background()

add_text_box(s, "The gap: Nobody celebrates to the CHILD, every month.",
             Inches(0.8), Inches(5.2), Inches(11.7), Inches(0.75),
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

slide_number(s, 9)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Unit Economics
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "The Math Works")

# Left: metrics table
metrics = [
    ("Average price",    "$17.99"),
    ("COGS estimate",    "$4–5"),
    ("Gross margin",     "50%+  at scale"),
    ("1,000 customers",  "$9K MRR"),
    ("Customer LTV",     "$200–500+"),
]

for i, (label, val) in enumerate(metrics):
    row_t = Inches(1.65) + Inches(i * 0.92)
    add_rect(s, Inches(0.5), row_t, Inches(7.5), Inches(0.78),
             RGBColor(0x22, 0x22, 0x22) if i % 2 == 0 else RGBColor(0x1A, 0x1A, 0x1A))
    add_text_box(s, label, Inches(0.7), row_t + Inches(0.12), Inches(4.0), Inches(0.6),
                 font_size=21, color=LIGHT_GRAY)
    add_text_box(s, val,   Inches(4.9), row_t + Inches(0.12), Inches(3.0), Inches(0.6),
                 font_size=21, bold=True, color=ACCENT_COLOR, align=PP_ALIGN.RIGHT)

# Right: churn note
add_text_box(s, "If churn stays\nbelow 3%/month",
             Inches(8.8), Inches(1.65), Inches(4.2), Inches(0.9),
             font_size=19, color=DIM_GRAY, align=PP_ALIGN.CENTER)

add_text_box(s, "$500+",
             Inches(8.8), Inches(2.7), Inches(4.2), Inches(1.1),
             font_size=72, bold=True, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)

add_text_box(s, "customer LTV",
             Inches(8.8), Inches(3.75), Inches(4.2), Inches(0.5),
             font_size=22, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

add_text_box(s, "Margin compounds fast once fulfillment ops are dialed in.",
             Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.5),
             font_size=18, color=DIM_GRAY, italic=True)

slide_number(s, 10)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Why We Win
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "Why We Win")

wins = [
    ("Zero product development",    "The kid creates it. We package and celebrate."),
    ("Recurring revenue model",      "Monthly subscriptions = predictable cash flow."),
    ("Multiple customer anchors",    "Parents, grandparents, homeschoolers — not a niche."),
    ("Defensible brand moat",        "Trust, recognition, and emotional loyalty compound."),
    ("Expandable platform",          "Stories, inventions, science projects — same model."),
]

for i, (title, sub) in enumerate(wins):
    row_t = Inches(1.65) + Inches(i * 0.97)
    # Teal number
    add_text_box(s, str(i + 1), Inches(0.5), row_t, Inches(0.5), Inches(0.72),
                 font_size=28, bold=True, color=ACCENT_COLOR)
    add_text_box(s, title, Inches(1.1), row_t, Inches(5.5), Inches(0.4),
                 font_size=22, bold=True, color=WHITE)
    add_text_box(s, sub,   Inches(1.1), row_t + Inches(0.4), Inches(11.5), Inches(0.45),
                 font_size=18, color=LIGHT_GRAY)

slide_number(s, 11)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Risks
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "What Could Kill This")

# Left: risks
risks = [
    ("Churn risk",                 "Parents forget to submit artwork"),
    ("Personalization at scale",   "Manual effort doesn't scale past ~500 subs"),
    ("Fulfillment logistics",      "Physical delivery adds cost and complexity"),
]

# Right: mitigations
mitigations = [
    "Auto-reminders + monthly challenge prompts drive submission habit.",
    "AI-assisted encouragement letters + human review system.",
    "Fulfillment ops partner locked in before scaling past 200 subs.",
]

add_text_box(s, "RISKS", Inches(0.5), Inches(1.65), Inches(5.5), Inches(0.42),
             font_size=16, bold=True, color=DIM_GRAY)
add_text_box(s, "MITIGATIONS", Inches(7.2), Inches(1.65), Inches(5.6), Inches(0.42),
             font_size=16, bold=True, color=DIM_GRAY)

add_rect(s, Inches(0.5), Inches(2.08), Inches(5.5), Inches(0.03), RGBColor(0x55,0x00,0x00))
add_rect(s, Inches(7.2), Inches(2.08), Inches(5.6), Inches(0.03), ACCENT_COLOR)

for i, ((risk, sub), mit) in enumerate(zip(risks, mitigations)):
    row_t = Inches(2.18) + Inches(i * 1.4)
    # Risk
    rbox = s.shapes.add_shape(1, Inches(0.5), row_t, Inches(5.5), Inches(1.2))
    rbox.fill.solid()
    rbox.fill.fore_color.rgb = RGBColor(0x30, 0x18, 0x18)
    rbox.line.color.rgb = RGBColor(0x66, 0x22, 0x22)
    add_text_box(s, risk, Inches(0.7), row_t + Inches(0.08), Inches(5.1), Inches(0.42),
                 font_size=20, bold=True, color=RGBColor(0xFF, 0x88, 0x88))
    add_text_box(s, sub,  Inches(0.7), row_t + Inches(0.5),  Inches(5.1), Inches(0.55),
                 font_size=17, color=LIGHT_GRAY)

    # Arrow
    add_text_box(s, "→", Inches(6.1), row_t + Inches(0.3), Inches(0.8), Inches(0.55),
                 font_size=28, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)

    # Mitigation
    mbox = s.shapes.add_shape(1, Inches(7.2), row_t, Inches(5.6), Inches(1.2))
    mbox.fill.solid()
    mbox.fill.fore_color.rgb = RGBColor(0x0D, 0x3D, 0x3D)
    mbox.line.color.rgb = RGBColor(0x00, 0x6B, 0x6B)
    add_text_box(s, mit, Inches(7.4), row_t + Inches(0.15), Inches(5.2), Inches(0.95),
                 font_size=17, color=LIGHT_GRAY)

slide_number(s, 12)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — The Test
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

heading(s, "We Don't Build. We Test First.")

# Timeline
steps = [
    ("Week 1",   "Landing page + targeted ads"),
    ("Week 2–3", "Presale push — drive paid signups"),
    ("Target",   "20–50 paid signups"),
    ("Budget",   "$2,500–3,000"),
    ("Decision", "20 paid? We build."),
]

bar_h = Inches(0.8)
bar_t = Inches(1.65)
bar_gap = Inches(0.18)

for i, (label, desc) in enumerate(steps):
    bt = bar_t + i * (bar_h + bar_gap)
    is_decision = (label == "Decision")
    bar_color = ACCENT_COLOR if is_decision else RGBColor(0x0D, 0x3D, 0x3D)
    bar = s.shapes.add_shape(1, Inches(0.5), bt, Inches(12.3), bar_h)
    bar.fill.solid()
    bar.fill.fore_color.rgb = bar_color
    bar.line.fill.background()

    add_text_box(s, label, Inches(0.7), bt + Inches(0.15), Inches(1.9), Inches(0.5),
                 font_size=19, bold=True,
                 color=WHITE if is_decision else ACCENT_COLOR)
    add_text_box(s, desc,  Inches(2.8), bt + Inches(0.15), Inches(9.8), Inches(0.5),
                 font_size=20, color=WHITE)

add_text_box(s, "Low risk. Fast signal. Clear decision point.",
             Inches(0.5), Inches(6.55), Inches(12.3), Inches(0.5),
             font_size=20, bold=True, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)

slide_number(s, 13)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — The Ask / Close
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK_LAYOUT)
fill_bg(s)

# Teal left bar (mirroring title slide)
add_rect(s, Inches(0), Inches(0), Inches(0.18), H, ACCENT_COLOR)

heading(s, "The Ask")

asks = [
    "$3,000 for the validation test",
    "2–3 weeks of your input and feedback",
    "One decision point: hit 20 paid? We build.",
]
for i, ask in enumerate(asks):
    add_text_box(s, f"• {ask}",
                 Inches(0.55), Inches(1.75) + Inches(i * 0.78),
                 Inches(8.5), Inches(0.65),
                 font_size=26, color=LIGHT_GRAY)

# Mockup placeholder — simple card wireframe
card_l = Inches(9.1)
card_t = Inches(1.45)
card_w = Inches(3.7)
card_h = Inches(4.0)

envelope = s.shapes.add_shape(1, card_l, card_t, card_w, card_h)
envelope.fill.solid()
envelope.fill.fore_color.rgb = RGBColor(0x0D, 0x3D, 0x3D)
envelope.line.color.rgb = ACCENT_COLOR
envelope.line.width = Pt(1.5)

add_text_box(s, "✉", card_l, card_t + Inches(0.5), card_w, Inches(1.0),
             font_size=52, color=ACCENT_COLOR, align=PP_ALIGN.CENTER)
add_text_box(s, "Dear Emma,",
             card_l + Inches(0.2), card_t + Inches(1.55), card_w - Inches(0.4), Inches(0.42),
             font_size=16, bold=True, color=WHITE)
add_text_box(s, "We loved your imagination.\nYour drawing made us smile.",
             card_l + Inches(0.2), card_t + Inches(1.95), card_w - Inches(0.4), Inches(0.9),
             font_size=14, color=LIGHT_GRAY, italic=True)
add_text_box(s, "PACKAGE MOCKUP",
             card_l, card_t + Inches(3.5), card_w, Inches(0.35),
             font_size=11, color=DIM_GRAY, align=PP_ALIGN.CENTER)

# Rule
add_rect(s, Inches(0.5), Inches(5.25), Inches(8.3), Inches(0.04), RGBColor(0x33,0x33,0x33))

# Closing line
add_text_box(s, "Let's find out if this market exists.",
             Inches(0.55), Inches(5.5), Inches(8.3), Inches(0.75),
             font_size=30, bold=True, color=ACCENT_COLOR)

slide_number(s, 14)


# ═══════════════════════════════════════════════════════════════════════════════
# Save
# ═══════════════════════════════════════════════════════════════════════════════
output_path = "/home/user/sales/kids_creativity_confidence_club_pitch.pptx"
prs.save(output_path)
print(f"Saved: {output_path}")
