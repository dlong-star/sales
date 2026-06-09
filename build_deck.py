from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import math

# ── Color palette from reference deck ──────────────────────────────────────
BG        = RGBColor(0x0D, 0x2C, 0x2C)   # very dark teal-charcoal bg
TEAL      = RGBColor(0x4C, 0xC8, 0xC3)   # deep teal accent
TEAL_DIM  = RGBColor(0x28, 0x80, 0x7D)   # dimmer teal
TEAL_LITE = RGBColor(0xA0, 0xE1, 0xDF)   # light teal
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
OFFWHITE  = RGBColor(0xE8, 0xF4, 0xF3)
GREY      = RGBColor(0x88, 0xAA, 0xA8)
YELLOW    = RGBColor(0xF7, 0xD0, 0x60)
CORAL     = RGBColor(0xF4, 0x7C, 0x5C)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

# ── Helper utilities ────────────────────────────────────────────────────────

def blank_slide(prs):
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    return slide

def set_bg(slide, color=BG):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, x, y, w, h, color, alpha=None):
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    return shape

def txt(slide, text, x, y, w, h, size=24, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb

def add_para(tf, text, size=20, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
             italic=False, space_before=0):
    from pptx.util import Pt as pt2
    p = tf.add_paragraph()
    p.alignment = align
    if space_before:
        p.space_before = Pt(space_before)
    run = p.add_run()
    run.text = text
    run.font.size = pt2(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color

def accent_bar(slide, y=Inches(0.08), h=Inches(0.06)):
    box(slide, 0, y, W, h, TEAL)

def slide_num(slide, n):
    txt(slide, str(n), W-Inches(0.6), H-Inches(0.4), Inches(0.4), Inches(0.3),
        size=10, color=GREY, align=PP_ALIGN.RIGHT)

def icon_circle(slide, x, y, r, color, label=None, label_color=WHITE, lsize=28):
    d = r*2
    shape = slide.shapes.add_shape(9, x-r, y-r, d, d)  # 9=oval
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if label:
        txt(slide, label, x-r, y-r, d, d, size=lsize, bold=True,
            color=label_color, align=PP_ALIGN.CENTER)

def rounded_box(slide, x, y, w, h, color, corner=Inches(0.15)):
    from pptx.util import Emu
    shape = slide.shapes.add_shape(5, x, y, w, h)  # 5=rounded rectangle
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    try:
        shape.adjustments[0] = 0.08
    except: pass
    return shape

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 – Title
# ─────────────────────────────────────────────────────────────────────────────
def slide1(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)
    
    # Large teal circle graphic top-right
    icon_circle(sl, Inches(10.5), Inches(3.2), Inches(2.8), TEAL_DIM)
    icon_circle(sl, Inches(10.5), Inches(3.2), Inches(2.2), RGBColor(0x12,0x3A,0x3A))
    
    # Inner art palette icon (emoji-style text)
    txt(sl, "🎨", Inches(9.6), Inches(2.3), Inches(1.8), Inches(1.8), size=72,
        align=PP_ALIGN.CENTER)
    
    # Star / sparkle accents
    for sx, sy, ss in [(1.0, 1.1, 18), (1.8, 6.2, 14), (5.5, 0.6, 12),
                        (0.4, 5.5, 22), (7.2, 1.0, 10)]:
        txt(sl, "✦", Inches(sx), Inches(sy), Inches(0.5), Inches(0.5),
            size=ss, color=TEAL)

    # Envelope icon strip bottom
    for i, emoji in enumerate(["✉️","📬","🖍️","⭐","📮"]):
        txt(sl, emoji, Inches(0.5 + i*1.05), Inches(6.4), Inches(1.0), Inches(0.7),
            size=28, align=PP_ALIGN.CENTER)

    # Main title
    txt(sl, "Kids Creativity\nConfidence Club", Inches(0.6), Inches(1.4),
        Inches(7.8), Inches(2.8), size=58, bold=True, color=WHITE)

    # Teal underline
    box(sl, Inches(0.6), Inches(4.1), Inches(5.2), Inches(0.05), TEAL)

    # Tagline
    txt(sl, "A mail-powered creator community that helps kids keep creating —",
        Inches(0.6), Inches(4.3), Inches(8.0), Inches(0.5), size=18,
        color=TEAL_LITE)
    txt(sl, "turning imagination into encouragement, recognition, and real keepsakes.",
        Inches(0.6), Inches(4.75), Inches(8.0), Inches(0.5), size=18,
        color=TEAL_LITE)

    # Sub badges
    for i, badge in enumerate(["🔒 Parent-Controlled", "📬 Real Mail", "🌟 Community"]):
        bx = Inches(0.6 + i * 2.55)
        rounded_box(sl, bx, Inches(5.55), Inches(2.35), Inches(0.48), TEAL_DIM)
        txt(sl, badge, bx + Inches(0.1), Inches(5.57), Inches(2.2), Inches(0.44),
            size=13, bold=True, color=WHITE)

    slide_num(sl, 1)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 – Problem: Kids Stop Creating
# ─────────────────────────────────────────────────────────────────────────────
def slide2(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    # Faded left panel
    box(sl, 0, 0, Inches(4.8), H, RGBColor(0x08,0x1E,0x1E))

    txt(sl, "THE PROBLEM", Inches(0.5), Inches(0.55), Inches(4.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "Kids Stop\nCreating.", Inches(0.5), Inches(1.0), Inches(4.0), Inches(2.0),
        size=48, bold=True, color=WHITE)
    box(sl, Inches(0.5), Inches(3.0), Inches(3.0), Inches(0.05), TEAL)

    # Stats on left
    for i, (num, label) in enumerate([
        ("72%", "of kids aged 10–14 say they\nfeel \"not creative enough\""),
        ("1 in 3", "kids stop making art by\nmiddle school"),
        ("0", "safe platforms built\naround a child's artwork"),
    ]):
        y = Inches(3.3 + i * 1.2)
        txt(sl, num, Inches(0.5), y, Inches(1.4), Inches(0.6),
            size=30, bold=True, color=TEAL)
        txt(sl, label, Inches(1.9), y, Inches(2.7), Inches(0.75),
            size=13, color=OFFWHITE)

    # Right panel – visual story
    # Broken crayon icon area
    txt(sl, "🖍️", Inches(5.3), Inches(1.0), Inches(1.5), Inches(1.5), size=60,
        align=PP_ALIGN.CENTER)
    
    # Arrow down
    txt(sl, "↓", Inches(5.8), Inches(2.4), Inches(0.8), Inches(0.6),
        size=36, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    txt(sl, "\"I'm not good\nenough.\"", Inches(4.9), Inches(3.0), Inches(3.8), Inches(1.2),
        size=34, bold=True, color=YELLOW, italic=True)

    # 3 root-cause cards
    causes = [
        ("No audience", "Nobody sees their work"),
        ("No feedback", "Silence kills motivation"),
        ("No continuity", "No reason to create again"),
    ]
    for i, (head, sub) in enumerate(causes):
        bx = Inches(5.0 + i * 2.7)
        rounded_box(sl, bx, Inches(5.3), Inches(2.45), Inches(1.0), TEAL_DIM)
        txt(sl, head, bx+Inches(0.12), Inches(5.36), Inches(2.2), Inches(0.4),
            size=13, bold=True, color=WHITE)
        txt(sl, sub, bx+Inches(0.12), Inches(5.72), Inches(2.2), Inches(0.5),
            size=11, color=TEAL_LITE)

    slide_num(sl, 2)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 – Core Insight
# ─────────────────────────────────────────────────────────────────────────────
def slide3(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "THE INSIGHT", Inches(0.5), Inches(0.55), Inches(6.0), Inches(0.4),
        size=11, bold=True, color=TEAL)

    txt(sl, "Mail makes encouragement feel real.", Inches(0.5), Inches(1.1),
        Inches(9.0), Inches(1.4), size=44, bold=True, color=WHITE)

    box(sl, Inches(0.5), Inches(2.5), Inches(5.0), Inches(0.05), TEAL)

    txt(sl, "The community keeps kids creating.\nThe mail makes the recognition tangible.",
        Inches(0.5), Inches(2.7), Inches(7.5), Inches(0.9), size=20, color=TEAL_LITE)

    # Two big concept boxes
    concepts = [
        ("💻", "Digital Community", "Safe space to share art,\nget reactions, join challenges"),
        ("📬", "Physical Mail", "Real postcards & keepsakes\ndelivered to their door"),
    ]
    for i, (icon, head, body) in enumerate(concepts):
        bx = Inches(0.5 + i * 6.1)
        rounded_box(sl, bx, Inches(3.8), Inches(5.7), Inches(2.8), TEAL_DIM)
        txt(sl, icon, bx + Inches(0.2), Inches(3.95), Inches(1.0), Inches(0.9),
            size=44, align=PP_ALIGN.CENTER)
        txt(sl, head, bx + Inches(1.15), Inches(4.05), Inches(4.3), Inches(0.5),
            size=18, bold=True, color=WHITE)
        txt(sl, body, bx + Inches(1.15), Inches(4.55), Inches(4.3), Inches(0.85),
            size=14, color=OFFWHITE)

    # PLUS connector
    txt(sl, "+", Inches(5.8), Inches(4.8), Inches(0.7), Inches(0.7),
        size=48, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    # Result banner
    rounded_box(sl, Inches(0.5), Inches(6.3), Inches(11.7), Inches(0.82), TEAL)
    txt(sl, "= A safe creator community powered by real mail that keeps kids creating.",
        Inches(0.7), Inches(6.38), Inches(11.3), Inches(0.7), size=17,
        bold=True, color=RGBColor(0x0D,0x2C,0x2C))

    slide_num(sl, 3)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 – Snail-Mail Proof  (named creators + community orgs)
# ─────────────────────────────────────────────────────────────────────────────
def slide4(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "MARKET PROOF", Inches(0.5), Inches(0.55), Inches(9.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "The mail revival is already a business.", Inches(0.5), Inches(0.92),
        Inches(10.5), Inches(0.72), size=38, bold=True, color=WHITE)
    box(sl, Inches(0.5), Inches(1.62), Inches(6.5), Inches(0.05), TEAL)

    # ── Top stat strip ──────────────────────────────────────────────────────
    highlights = [
        ("84%",    "of Americans now\nincorporating analog\nlifestyle choices"),
        ("150K+",  "TikTok posts\ntagged #snailmail"),
        ("~50%",   "of Gen Z mails\nsomething monthly\n(Stamps.com)"),
        ("63%",    "of Gen Z intentionally\ncutting screen time\n(Talker Research)"),
    ]
    hw = Inches(3.05)
    for i, (big, label) in enumerate(highlights):
        bx = Inches(0.5) + i * (hw + Inches(0.12))
        rounded_box(sl, bx, Inches(1.75), hw, Inches(1.3), RGBColor(0x10,0x32,0x32))
        box(sl, bx, Inches(1.75), hw, Inches(0.05), TEAL)
        txt(sl, big, bx + Inches(0.15), Inches(1.84), Inches(1.2), Inches(0.65),
            size=30, bold=True, color=TEAL)
        txt(sl, label, bx + Inches(1.35), Inches(1.82), Inches(1.6), Inches(1.1),
            size=10, color=OFFWHITE)

    # ── Section label ───────────────────────────────────────────────────────
    txt(sl, "REAL CREATORS  ·  REAL REVENUE  ·  ZERO PAID ADS",
        Inches(0.5), Inches(3.12), Inches(8.0), Inches(0.35),
        size=9, bold=True, color=TEAL)

    # ── Creator cards row (4 across) ───────────────────────────────────────
    creators = [
        ("✉️", "$45K/mo", "The Tiny Post",
         "Hannah Gustafson · Austin TX\n5,000 subs · $11/mo\n0 paid ads, 0 PR"),
        ("🏛️", "$18,300/mo", "The Architecture Club",
         "Trinity Shiroma · Orlando FL\n2,700 subs · $8.88/mo\n1,300 subs in first 3 months"),
        ("🍝", "4,000 subs", "Little Kitchen of Bo",
         "Bo Natakhin · Toronto\n$20/issue · first drop\ncooking zine via TikTok"),
        ("🚦", "$14K/mo", "The Cloud Report",
         "Christine Tyler Hill · Vermont\nCrossing guard → 2,000 subs\n3,600 on waitlist at launch"),
    ]
    cw = Inches(3.05)
    ch = Inches(2.05)
    for i, (icon, revenue, name, detail) in enumerate(creators):
        bx = Inches(0.5) + i * (cw + Inches(0.12))
        by = Inches(3.52)
        rounded_box(sl, bx, by, cw, ch, RGBColor(0x14,0x3E,0x3E))
        # teal top bar
        box(sl, bx, by, cw, Inches(0.05), TEAL)
        txt(sl, icon, bx + Inches(0.15), by + Inches(0.1), Inches(0.55), Inches(0.55),
            size=26)
        txt(sl, revenue, bx + Inches(0.72), by + Inches(0.1), Inches(2.2), Inches(0.55),
            size=22, bold=True, color=TEAL)
        txt(sl, name, bx + Inches(0.15), by + Inches(0.65), cw - Inches(0.3), Inches(0.4),
            size=13, bold=True, color=WHITE)
        txt(sl, detail, bx + Inches(0.15), by + Inches(1.05), cw - Inches(0.3), Inches(0.88),
            size=10, color=GREY)

    # ── Community orgs row (4 across) ──────────────────────────────────────
    txt(sl, "COMMUNITY PROOF  ·  PEOPLE ALREADY CHOOSE REAL MAIL",
        Inches(0.5), Inches(5.65), Inches(10.0), Inches(0.32),
        size=9, bold=True, color=TEAL)

    orgs = [
        ("📮", "806K members\n87M+ postcards", "Postcrossing"),
        ("💌", "1M+ letters\nCOVID-era strangers", "Letters Against Isolation"),
        ("🤝", "1M+ letters\n100+ chapters, 70+ mailboxes", "Love For Our Elders"),
        ("🌍", "All 50 states\n70+ countries active", "More Love Letters"),
    ]
    ow = Inches(3.05)
    oh = Inches(1.38)
    for i, (icon, stat, name) in enumerate(orgs):
        bx = Inches(0.5) + i * (ow + Inches(0.12))
        by = Inches(6.0)
        rounded_box(sl, bx, by, ow, oh, RGBColor(0x0E,0x28,0x28))
        txt(sl, icon, bx + Inches(0.12), by + Inches(0.15), Inches(0.6), Inches(0.6),
            size=24)
        txt(sl, stat, bx + Inches(0.75), by + Inches(0.1), Inches(2.15), Inches(0.72),
            size=12, bold=True, color=TEAL_LITE)
        txt(sl, name, bx + Inches(0.75), by + Inches(0.82), Inches(2.2), Inches(0.38),
            size=10, color=GREY)

    slide_num(sl, 4)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 – Product Loop
# ─────────────────────────────────────────────────────────────────────────────
def slide5(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "THE PRODUCT LOOP", Inches(0.5), Inches(0.55), Inches(6.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "Five steps. One flywheel.", Inches(0.5), Inches(1.0), Inches(7.0),
        Inches(0.7), size=38, bold=True, color=WHITE)

    # 5-step loop as connected boxes in a row
    steps = [
        ("🖍️", "CREATE", "Kid makes art"),
        ("📤", "UPLOAD", "Photo to app"),
        ("⭐", "ENCOURAGED", "Reactions + AI\nfeedback + peers"),
        ("📬", "MAILED", "Real postcard\narrives at home"),
        ("🎨", "CREATE\nAGAIN", "Cycle repeats"),
    ]

    bw = Inches(2.1)
    bh = Inches(3.0)
    by = Inches(2.5)
    gap = Inches(0.42)

    for i, (icon, head, body) in enumerate(steps):
        bx = Inches(0.5) + i * (bw + gap)
        # Card
        c = TEAL if i == 4 else TEAL_DIM
        rounded_box(sl, bx, by, bw, bh, c)
        # Step number circle
        icon_circle(sl, bx + Inches(0.38), by + Inches(0.35), Inches(0.28),
                    BG, label=str(i+1), lsize=13)
        txt(sl, icon, bx + Inches(0.55), by + Inches(0.1), Inches(1.0), Inches(0.9),
            size=40, align=PP_ALIGN.CENTER)
        txt(sl, head, bx + Inches(0.1), by + Inches(1.05), bw - Inches(0.2),
            Inches(0.65), size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, body, bx + Inches(0.1), by + Inches(1.65), bw - Inches(0.2),
            Inches(1.1), size=12, color=TEAL_LITE, align=PP_ALIGN.CENTER)

        # Arrow between cards
        if i < 4:
            ax = bx + bw + Inches(0.1)
            txt(sl, "→", ax, by + Inches(1.2), gap - Inches(0.05), Inches(0.5),
                size=22, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    # Loop-back arrow label
    txt(sl, "↩  The loop is the product. Mail closes it.",
        Inches(0.5), Inches(5.9), Inches(10.0), Inches(0.5),
        size=16, color=TEAL, italic=True)

    slide_num(sl, 5)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 – What the Kid Sees
# ─────────────────────────────────────────────────────────────────────────────
def slide6(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    box(sl, 0, 0, Inches(5.5), H, RGBColor(0x08,0x1E,0x1E))

    txt(sl, "EXPERIENCE", Inches(0.5), Inches(0.55), Inches(4.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "What the\nKid Sees", Inches(0.5), Inches(1.0), Inches(4.5), Inches(1.7),
        size=46, bold=True, color=WHITE)

    features = [
        ("🎨", "Their art gallery — front and center"),
        ("⭐", "Stars, hearts, and encouraging reactions"),
        ("📋", "Monthly challenge prompts to create"),
        ("🏅", "Milestone badges and creator level"),
        ("📬", "Mail tracker — \"Your postcard was mailed!\""),
    ]
    for i, (icon, label) in enumerate(features):
        y = Inches(2.9 + i * 0.78)
        txt(sl, icon, Inches(0.5), y, Inches(0.6), Inches(0.6), size=22)
        txt(sl, label, Inches(1.2), y + Inches(0.04), Inches(4.0), Inches(0.55),
            size=15, color=OFFWHITE)

    # Right: phone wireframe mockup
    # Phone outline
    rounded_box(sl, Inches(6.2), Inches(0.8), Inches(3.0), Inches(5.8),
                RGBColor(0x1A,0x4A,0x4A))
    box(sl, Inches(6.2), Inches(0.8), Inches(3.0), Inches(5.8),
        RGBColor(0x1A,0x4A,0x4A))
    # Screen area
    box(sl, Inches(6.45), Inches(1.1), Inches(2.5), Inches(5.0),
        RGBColor(0x0F,0x30,0x30))
    # Notch
    rounded_box(sl, Inches(7.3), Inches(0.95), Inches(0.8), Inches(0.2),
                RGBColor(0x0D,0x2C,0x2C))
    # Home button
    icon_circle(sl, Inches(7.7), Inches(6.8), Inches(0.2), RGBColor(0x28,0x60,0x60))

    # Screen content wireframe
    txt(sl, "🎨  My Art", Inches(6.55), Inches(1.25), Inches(2.3), Inches(0.35),
        size=13, bold=True, color=WHITE)
    box(sl, Inches(6.55), Inches(1.65), Inches(2.3), Inches(0.04), TEAL_DIM)
    # Art tile grid
    for r in range(2):
        for c in range(2):
            rounded_box(sl, Inches(6.55 + c*1.2), Inches(1.75 + r*1.05),
                        Inches(1.1), Inches(0.95), RGBColor(0x1E,0x50,0x50))
            txt(sl, ["🌈","🐶","🚀","🌸"][r*2+c],
                Inches(6.65 + c*1.2), Inches(1.82 + r*1.05),
                Inches(0.9), Inches(0.75), size=28, align=PP_ALIGN.CENTER)
    # Reactions row
    txt(sl, "⭐ 12   ❤️ 8   🎉 5", Inches(6.55), Inches(3.9), Inches(2.3), Inches(0.35),
        size=11, color=TEAL_LITE)
    # Mail tracker
    rounded_box(sl, Inches(6.55), Inches(4.35), Inches(2.3), Inches(0.65),
                RGBColor(0x28,0x80,0x7D))
    txt(sl, "📬  Postcard in transit!", Inches(6.65), Inches(4.45), Inches(2.1),
        Inches(0.45), size=12, bold=True, color=WHITE)

    # Right text panel
    txt(sl, "No open feeds.\nNo follower counts.\nJust their own creative world.",
        Inches(9.5), Inches(2.0), Inches(3.3), Inches(2.0), size=18,
        color=TEAL_LITE, italic=True)

    slide_num(sl, 6)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 – What the Parent Sees
# ─────────────────────────────────────────────────────────────────────────────
def slide7(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    box(sl, Inches(7.8), 0, Inches(5.53), H, RGBColor(0x08,0x1E,0x1E))

    txt(sl, "EXPERIENCE", Inches(0.5), Inches(0.55), Inches(5.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "What the\nParent Sees", Inches(0.5), Inches(1.0), Inches(7.0),
        Inches(1.7), size=46, bold=True, color=WHITE)

    features = [
        ("🔒", "Full approval control — nothing ships without parent OK"),
        ("👁️", "Private child profiles, no strangers can search"),
        ("💬", "Moderated reactions only — no open DMs"),
        ("📦", "Printed keepsake books — optional add-on"),
        ("📊", "Creativity streak tracker and milestone alerts"),
    ]
    for i, (icon, label) in enumerate(features):
        y = Inches(3.0 + i * 0.75)
        txt(sl, icon, Inches(0.5), y, Inches(0.6), Inches(0.6), size=22)
        txt(sl, label, Inches(1.2), y + Inches(0.04), Inches(6.3), Inches(0.55),
            size=14, color=OFFWHITE)

    # Right: parent dashboard wireframe
    # Laptop frame
    box(sl, Inches(8.1), Inches(1.0), Inches(4.7), Inches(3.4),
        RGBColor(0x1A,0x4A,0x4A))
    box(sl, Inches(8.25), Inches(1.15), Inches(4.4), Inches(3.05),
        RGBColor(0x0F,0x30,0x30))
    box(sl, Inches(7.8), Inches(4.4), Inches(5.53), Inches(0.22),
        RGBColor(0x28,0x60,0x60))

    # Dashboard content
    txt(sl, "Parent Dashboard", Inches(8.35), Inches(1.25), Inches(4.2), Inches(0.35),
        size=12, bold=True, color=WHITE)
    box(sl, Inches(8.35), Inches(1.6), Inches(4.2), Inches(0.03), TEAL_DIM)

    # Stats row
    for i, (num, lab) in enumerate([("12","artworks"),("🏅 3","badges"),("📬 2","mailed")]):
        bx2 = Inches(8.35 + i*1.45)
        rounded_box(sl, bx2, Inches(1.7), Inches(1.3), Inches(0.65),
                    RGBColor(0x1E,0x50,0x50))
        txt(sl, num, bx2+Inches(0.08), Inches(1.75), Inches(1.1), Inches(0.3),
            size=16, bold=True, color=TEAL)
        txt(sl, lab, bx2+Inches(0.08), Inches(2.03), Inches(1.15), Inches(0.25),
            size=9, color=GREY)

    # Pending approval
    rounded_box(sl, Inches(8.35), Inches(2.5), Inches(4.2), Inches(0.75),
                RGBColor(0x20,0x55,0x55))
    txt(sl, "⏳  Pending approval: 1 artwork", Inches(8.45), Inches(2.57),
        Inches(2.5), Inches(0.35), size=12, color=YELLOW)
    txt(sl, "Approve  |  Decline", Inches(10.6), Inches(2.62), Inches(1.7),
        Inches(0.35), size=11, color=TEAL)

    # Keepsake upsell
    rounded_box(sl, Inches(8.35), Inches(3.35), Inches(4.2), Inches(0.65),
                TEAL_DIM)
    txt(sl, "📦  Order keepsake book — $19.99", Inches(8.45), Inches(3.42),
        Inches(4.0), Inches(0.5), size=12, bold=True, color=WHITE)

    # Trust message
    txt(sl, "Parents are in control — always.", Inches(8.1), Inches(5.5),
        Inches(4.7), Inches(0.5), size=16, bold=True, color=TEAL,
        align=PP_ALIGN.CENTER)

    slide_num(sl, 7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 – What Grandparents See
# ─────────────────────────────────────────────────────────────────────────────
def slide8(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "EXPERIENCE", Inches(0.5), Inches(0.55), Inches(5.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "What Grandparents See", Inches(0.5), Inches(1.0), Inches(9.0),
        Inches(0.9), size=42, bold=True, color=WHITE)
    box(sl, Inches(0.5), Inches(1.9), Inches(4.5), Inches(0.05), TEAL)

    txt(sl, "No app required. No account.\nJust joy in the mailbox.",
        Inches(0.5), Inches(2.05), Inches(5.5), Inches(1.0), size=20,
        color=TEAL_LITE, italic=True)

    # Grandparent journey
    steps_g = [
        ("📬", "Postcard arrives", "Real mail with\nkid's original art"),
        ("💌", "QR code inside", "Scan to see the\nonline gallery"),
        ("📖", "Keepsake book", "Optional printed\nbook of all artwork"),
        ("🌟", "Reaction card", "Pre-stamped note\nback to the kid"),
    ]
    for i, (icon, head, body) in enumerate(steps_g):
        bx = Inches(0.5 + i * 3.1)
        by = Inches(3.3)
        rounded_box(sl, bx, by, Inches(2.8), Inches(2.5), RGBColor(0x12,0x3A,0x3A))
        txt(sl, icon, bx+Inches(0.1), by+Inches(0.15), Inches(0.9), Inches(0.75), size=38)
        txt(sl, head, bx+Inches(1.05), by+Inches(0.22), Inches(1.6), Inches(0.5),
            size=14, bold=True, color=WHITE)
        txt(sl, body, bx+Inches(0.1), by+Inches(0.9), Inches(2.55), Inches(1.3),
            size=13, color=TEAL_LITE)

    # Pull quote
    box(sl, Inches(0.5), Inches(6.2), Inches(0.06), Inches(0.9), TEAL)
    txt(sl, "\"Grandparents don't need an account.\nThey just get a letter from their grandkid.\"",
        Inches(0.75), Inches(6.22), Inches(10.0), Inches(0.75), size=15,
        color=OFFWHITE, italic=True)

    # Right side art
    txt(sl, "💌", Inches(10.5), Inches(2.5), Inches(2.3), Inches(2.3), size=96,
        align=PP_ALIGN.CENTER)
    txt(sl, "The best gift a grandparent\ncan receive — made by the kid.",
        Inches(9.8), Inches(4.8), Inches(3.2), Inches(1.0), size=13,
        color=GREY, align=PP_ALIGN.CENTER)

    slide_num(sl, 8)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 – Pricing Tiers
# ─────────────────────────────────────────────────────────────────────────────
def slide9(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "PRICING", Inches(0.5), Inches(0.55), Inches(5.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "Simple. Predictable. Family-Friendly.", Inches(0.5), Inches(1.0),
        Inches(9.0), Inches(0.7), size=38, bold=True, color=WHITE)

    tiers = [
        ("FREE", "$0/mo", "Starter", TEAL_DIM, [
            "✓  Upload up to 3 artworks/mo",
            "✓  Reactions from family only",
            "✓  Monthly challenge prompt",
            "✗  No mail included",
        ]),
        ("CREATOR", "$9/mo", "Most Popular", TEAL, [
            "✓  Unlimited uploads",
            "✓  1 postcard mailed/month",
            "✓  AI feedback + peer community",
            "✓  Milestone badges",
        ]),
        ("FAMILY", "$19/mo", "Best Value", RGBColor(0x28,0x80,0x7D), [
            "✓  Up to 3 kids",
            "✓  3 postcards/month total",
            "✓  Grandparent sharing",
            "✓  Annual keepsake book included",
        ]),
    ]

    for i, (name, price, badge, color, features) in enumerate(tiers):
        bx = Inches(0.5 + i * 4.2)
        bh = Inches(5.5)
        rounded_box(sl, bx, Inches(1.9), Inches(3.9), bh, RGBColor(0x10,0x32,0x32))
        # Top color bar
        box(sl, bx, Inches(1.9), Inches(3.9), Inches(0.06), color)
        # Badge
        rounded_box(sl, bx+Inches(0.1), Inches(2.05), Inches(1.5), Inches(0.35), color)
        txt(sl, badge, bx+Inches(0.15), Inches(2.08), Inches(1.4), Inches(0.3),
            size=10, bold=True, color=RGBColor(0x0D,0x2C,0x2C))
        txt(sl, name, bx+Inches(0.2), Inches(2.5), Inches(3.5), Inches(0.45),
            size=20, bold=True, color=color)
        txt(sl, price, bx+Inches(0.2), Inches(2.95), Inches(3.5), Inches(0.75),
            size=42, bold=True, color=WHITE)
        txt(sl, "per month", bx+Inches(0.2), Inches(3.65), Inches(2.0), Inches(0.3),
            size=11, color=GREY)
        box(sl, bx+Inches(0.2), Inches(4.0), Inches(3.5), Inches(0.03), TEAL_DIM)
        for j, feat in enumerate(features):
            c2 = OFFWHITE if feat.startswith("✓") else GREY
            txt(sl, feat, bx+Inches(0.2), Inches(4.1 + j*0.48),
                Inches(3.5), Inches(0.42), size=13, color=c2)

    # Add-ons row
    txt(sl, "Add-ons:", Inches(0.5), Inches(7.05), Inches(1.5), Inches(0.35),
        size=12, bold=True, color=TEAL)
    txt(sl, "Extra postcards: $2/ea   |   Keepsake book: $19.99   |   Grandparent bundle: $4.99/mo",
        Inches(2.1), Inches(7.05), Inches(10.7), Inches(0.35), size=12, color=GREY)

    slide_num(sl, 9)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 – Growth Loops
# ─────────────────────────────────────────────────────────────────────────────
def slide10(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "GROWTH", Inches(0.5), Inches(0.55), Inches(4.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "Built-In Growth Loops", Inches(0.5), Inches(1.0), Inches(8.0),
        Inches(0.7), size=40, bold=True, color=WHITE)

    loops = [
        ("👨‍👩‍👧", "Grandparent Referral",
         "Parent shares kid's art → Grandparent gets postcard → Grandparent asks for more → Parent upgrades"),
        ("🏫", "School Viral",
         "Kid shows postcard at school → Classmate wants one → Parent signs up → New paying family"),
        ("🎨", "Creator Challenge",
         "Monthly themes drive uploads → Leaderboards create friendly competition → Low churn"),
        ("📦", "Keepsake Upsell",
         "12 months of art → End-of-year book prompt → $19.99 add-on → High-margin revenue"),
    ]
    for i, (icon, head, body) in enumerate(loops):
        row = i // 2
        col = i % 2
        bx = Inches(0.5 + col * 6.3)
        by = Inches(2.0 + row * 2.55)
        rounded_box(sl, bx, by, Inches(6.0), Inches(2.2), RGBColor(0x12,0x3A,0x3A))
        txt(sl, icon, bx+Inches(0.15), by+Inches(0.2), Inches(0.85), Inches(0.85), size=38)
        txt(sl, head, bx+Inches(1.1), by+Inches(0.25), Inches(4.6), Inches(0.45),
            size=16, bold=True, color=TEAL)
        txt(sl, body, bx+Inches(1.1), by+Inches(0.75), Inches(4.6), Inches(1.2),
            size=13, color=OFFWHITE)

    txt(sl, "Organic growth is the strategy. Mail is the catalyst.",
        Inches(0.5), Inches(7.08), Inches(10.0), Inches(0.35), size=13,
        color=TEAL, italic=True)

    slide_num(sl, 10)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11 – Moat
# ─────────────────────────────────────────────────────────────────────────────
def slide11(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "COMPETITIVE MOAT", Inches(0.5), Inches(0.55), Inches(6.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "Hard to copy.\nHarder to leave.", Inches(0.5), Inches(1.0),
        Inches(6.5), Inches(1.6), size=44, bold=True, color=WHITE)

    moats = [
        ("🔗", "Emotional Lock-In",
         "A child's art history lives here. You don't delete the app that holds your kid's masterpieces."),
        ("📬", "Physical + Digital Fusion",
         "No tech-only competitor can replicate real mail. No mail company can replicate the community."),
        ("👨‍👩‍👧‍👦", "Family Network Effect",
         "Each family adds grandparents, aunts, uncles. Every connection deepens retention."),
        ("🛡️", "Trust Infrastructure",
         "COPPA-compliant from day one. No DMs, moderated content, parent approval. Trust is the product."),
        ("📊", "Creative Data",
         "Proprietary dataset of children's creative development = future personalization no one else has."),
    ]

    for i, (icon, head, body) in enumerate(moats):
        by = Inches(2.8 + i * 0.88)
        # Indicator dot
        icon_circle(sl, Inches(0.75), by + Inches(0.22), Inches(0.18), TEAL)
        txt(sl, icon, Inches(1.05), by, Inches(0.6), Inches(0.55), size=22)
        txt(sl, head, Inches(1.7), by + Inches(0.04), Inches(3.0), Inches(0.4),
            size=14, bold=True, color=WHITE)
        txt(sl, body, Inches(1.7), by + Inches(0.42), Inches(11.1), Inches(0.4),
            size=12, color=GREY)

    # Right side graphic
    # Concentric circles = moat visual
    for r_idx, (rad, col) in enumerate([(1.8, RGBColor(0x28,0x80,0x7D)),
                                         (1.3, TEAL_DIM),
                                         (0.8, TEAL),
                                         (0.4, WHITE)]):
        icon_circle(sl, Inches(10.9), Inches(4.0), Inches(rad), col)
    txt(sl, "K3C", Inches(10.35), Inches(3.7), Inches(1.1), Inches(0.6),
        size=18, bold=True, color=BG, align=PP_ALIGN.CENTER)

    slide_num(sl, 11)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12 – Unit Economics
# ─────────────────────────────────────────────────────────────────────────────
def slide12(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "UNIT ECONOMICS", Inches(0.5), Inches(0.55), Inches(5.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "The numbers work.", Inches(0.5), Inches(1.0), Inches(6.0),
        Inches(0.7), size=40, bold=True, color=WHITE)

    # Creator plan breakdown
    txt(sl, "Creator Plan  —  $9/month", Inches(0.5), Inches(1.9),
        Inches(6.0), Inches(0.45), size=18, bold=True, color=TEAL)

    costs = [
        ("Postcard printing + postage", "$1.80"),
        ("Platform / infra per user", "$0.60"),
        ("AI moderation cost", "$0.25"),
        ("Customer support allocation", "$0.35"),
        ("Total COGS", "$3.00"),
    ]
    for i, (label, val) in enumerate(costs):
        by = Inches(2.45 + i * 0.52)
        is_total = label.startswith("Total")
        c2 = TEAL if is_total else OFFWHITE
        bold = is_total
        if is_total:
            box(sl, Inches(0.5), by - Inches(0.05), Inches(5.8), Inches(0.03), TEAL_DIM)
        txt(sl, label, Inches(0.5), by, Inches(4.5), Inches(0.45),
            size=14, color=c2, bold=bold)
        txt(sl, val, Inches(5.0), by, Inches(1.2), Inches(0.45),
            size=14, bold=bold, color=c2, align=PP_ALIGN.RIGHT)

    # Margin box
    rounded_box(sl, Inches(0.5), Inches(5.2), Inches(5.8), Inches(1.0), TEAL_DIM)
    txt(sl, "Gross Margin:", Inches(0.7), Inches(5.32), Inches(3.0), Inches(0.55),
        size=18, bold=True, color=WHITE)
    txt(sl, "67%", Inches(3.8), Inches(5.25), Inches(2.3), Inches(0.75),
        size=42, bold=True, color=TEAL)

    # Right side key metrics
    metrics = [
        ("$38", "Avg monthly revenue\nper family (blended)"),
        ("18 mo", "Target payback period"),
        ("$680", "LTV estimate\n(18-month avg tenure)"),
        ("~$18", "Blended CAC target"),
    ]
    for i, (big, label) in enumerate(metrics):
        col = i % 2
        row = i // 2
        bx = Inches(7.0 + col * 3.0)
        by = Inches(1.8 + row * 2.5)
        rounded_box(sl, bx, by, Inches(2.7), Inches(2.0), RGBColor(0x12,0x3A,0x3A))
        txt(sl, big, bx+Inches(0.15), by+Inches(0.2), Inches(2.4), Inches(0.75),
            size=42, bold=True, color=TEAL)
        txt(sl, label, bx+Inches(0.15), by+Inches(1.0), Inches(2.4), Inches(0.8),
            size=13, color=OFFWHITE)

    slide_num(sl, 12)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 13 – Risks + Safety / Moderation
# ─────────────────────────────────────────────────────────────────────────────
def slide13(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    txt(sl, "RISKS + SAFETY", Inches(0.5), Inches(0.55), Inches(5.0), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "We've thought about the hard stuff.", Inches(0.5), Inches(1.0),
        Inches(8.5), Inches(0.7), size=36, bold=True, color=WHITE)

    # Left: risks
    txt(sl, "Known Risks", Inches(0.5), Inches(1.9), Inches(5.5), Inches(0.45),
        size=16, bold=True, color=CORAL)
    risks = [
        ("📉", "Churn risk", "Kids age out — mitigated by family plan / sibling continuity"),
        ("📦", "Mail ops complexity", "Partnering with print-on-demand + USPS bulk rate from day one"),
        ("⚖️", "COPPA compliance", "Children's privacy law built into architecture, not bolted on"),
        ("📱", "Screen time concerns", "Positioned as creative tool — parents already pay for art classes"),
    ]
    for i, (icon, head, body) in enumerate(risks):
        by = Inches(2.5 + i * 1.0)
        txt(sl, icon, Inches(0.5), by, Inches(0.55), Inches(0.55), size=22)
        txt(sl, head, Inches(1.1), by+Inches(0.04), Inches(2.2), Inches(0.4),
            size=13, bold=True, color=CORAL)
        txt(sl, body, Inches(1.1), by+Inches(0.44), Inches(5.4), Inches(0.48),
            size=12, color=OFFWHITE)

    # Divider
    box(sl, Inches(6.8), Inches(1.85), Inches(0.04), Inches(5.0), TEAL_DIM)

    # Right: safety infrastructure
    txt(sl, "Safety Infrastructure", Inches(7.1), Inches(1.9), Inches(5.7), Inches(0.45),
        size=16, bold=True, color=TEAL)
    safety = [
        ("🛡️", "No open DMs — ever"),
        ("👁️", "AI-assisted content moderation + human review queue"),
        ("🔒", "Private child profiles — not searchable"),
        ("✅", "Parent must approve every upload before it's visible"),
        ("📋", "COPPA-compliant data handling from day one"),
        ("🤖", "AI feedback is encouraging only — no negative scores"),
    ]
    for i, (icon, label) in enumerate(safety):
        by = Inches(2.5 + i * 0.76)
        txt(sl, icon, Inches(7.1), by, Inches(0.55), Inches(0.55), size=18)
        txt(sl, label, Inches(7.75), by+Inches(0.06), Inches(5.0), Inches(0.45),
            size=13, color=OFFWHITE)

    slide_num(sl, 13)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 14 – Test Plan + Ask
# ─────────────────────────────────────────────────────────────────────────────
def slide14(prs):
    sl = blank_slide(prs)
    set_bg(sl)
    accent_bar(sl)

    # Large teal bg shape top-right
    rounded_box(sl, Inches(8.0), Inches(0.5), Inches(5.0), Inches(6.5),
                RGBColor(0x12,0x3A,0x3A))
    icon_circle(sl, Inches(10.5), Inches(3.5), Inches(2.0), TEAL_DIM)
    txt(sl, "🚀", Inches(9.6), Inches(2.6), Inches(1.8), Inches(1.8), size=72,
        align=PP_ALIGN.CENTER)

    txt(sl, "TEST PLAN + ASK", Inches(0.5), Inches(0.55), Inches(5.5), Inches(0.4),
        size=11, bold=True, color=TEAL)
    txt(sl, "90-Day\nLaunch Plan", Inches(0.5), Inches(1.0), Inches(6.5),
        Inches(1.7), size=46, bold=True, color=WHITE)

    phases = [
        ("Phase 1", "Days 1–30", "Waitlist + Community",
         "Build email list of 500 families. Run parent Facebook group. Validate art upload flow with 20 beta kids."),
        ("Phase 2", "Days 31–60", "First Mail Drop",
         "50 paid Creator subscribers. Mail first round of postcards. Capture parent reactions + kid responses."),
        ("Phase 3", "Days 61–90", "Prove Retention",
         "Measure 30-day re-upload rate. Target: 60%+ kids upload again after receiving their first postcard."),
    ]
    for i, (phase, dates, head, body) in enumerate(phases):
        by = Inches(3.0 + i * 1.4)
        rounded_box(sl, Inches(0.5), by, Inches(7.2), Inches(1.18),
                    RGBColor(0x12,0x3A,0x3A))
        rounded_box(sl, Inches(0.5), by, Inches(1.05), Inches(1.18), TEAL_DIM)
        txt(sl, phase, Inches(0.55), by+Inches(0.1), Inches(0.95), Inches(0.4),
            size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, dates, Inches(0.55), by+Inches(0.52), Inches(0.95), Inches(0.45),
            size=9, color=TEAL_LITE, align=PP_ALIGN.CENTER)
        txt(sl, head, Inches(1.65), by+Inches(0.12), Inches(2.5), Inches(0.4),
            size=13, bold=True, color=TEAL)
        txt(sl, body, Inches(1.65), by+Inches(0.52), Inches(5.8), Inches(0.6),
            size=11, color=OFFWHITE)

    # The Ask
    rounded_box(sl, Inches(0.5), Inches(6.3), Inches(7.2), Inches(0.9), TEAL)
    txt(sl, "The Ask:", Inches(0.65), Inches(6.4), Inches(1.5), Inches(0.45),
        size=15, bold=True, color=BG)
    txt(sl, "$150K pre-seed  ·  12 months  ·  1,000 paying families",
        Inches(2.2), Inches(6.4), Inches(5.3), Inches(0.45), size=15,
        bold=True, color=BG)

    # Contact
    txt(sl, "dc.long123@gmail.com", Inches(8.2), Inches(6.3), Inches(4.6),
        Inches(0.4), size=13, color=TEAL_LITE, align=PP_ALIGN.CENTER)
    txt(sl, "kidscreativityconfidenceclub.com", Inches(8.2), Inches(6.7),
        Inches(4.6), Inches(0.35), size=12, color=GREY, align=PP_ALIGN.CENTER)

    slide_num(sl, 14)

# ── Build all slides ──────────────────────────────────────────────────────────
slide1(prs)
slide2(prs)
slide3(prs)
slide4(prs)
slide5(prs)
slide6(prs)
slide7(prs)
slide8(prs)
slide9(prs)
slide10(prs)
slide11(prs)
slide12(prs)
slide13(prs)
slide14(prs)

out = "/home/user/sales/K3C_Pitch_Deck.pptx"
prs.save(out)
print(f"Saved: {out}")
