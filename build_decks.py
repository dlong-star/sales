import copy
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

SRC = '/root/.claude/uploads/c173d4c3-62b4-5de9-a3ba-062b505b9f51/889c7f4c-Tiny_MasterPeices_Idea.pptx'
OUT1 = '/home/user/sales/Deck1_Original_Plus_Social.pptx'
OUT2 = '/home/user/sales/Deck2_Improved_Pitch.pptx'

# ─── color palette ───────────────────────────────────────────────────────────
BG       = RGBColor(0x0D, 0x2C, 0x2C)
TEAL     = RGBColor(0x4C, 0xC8, 0xC3)
TEAL2    = RGBColor(0x28, 0x80, 0x7D)
TEAL_LT  = RGBColor(0xA0, 0xE1, 0xDF)
TEAL_XLT = RGBColor(0xE8, 0xF4, 0xF3)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
GOLD     = RGBColor(0xF7, 0xD0, 0x60)
RED      = RGBColor(0xF4, 0x7C, 0x5C)
GRAY     = RGBColor(0x88, 0xAA, 0xA8)
DARK2    = RGBColor(0x06, 0x35, 0x38)

# ─── helpers ─────────────────────────────────────────────────────────────────

def set_bg(slide, color: RGBColor):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rect(slide, l, t, w, h, fill_color):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape

def add_rounded_rect(slide, l, t, w, h, fill_color, corner_radius=0.1):
    from pptx.util import Pt as _Pt
    shape = slide.shapes.add_shape(5, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    # Set corner radius via XML
    sp = shape._element
    spPr = sp.find(qn('p:spPr'))
    prstGeom = spPr.find(qn('a:prstGeom'))
    if prstGeom is not None:
        avLst = prstGeom.find(qn('a:avLst'))
        if avLst is None:
            avLst = etree.SubElement(prstGeom, qn('a:avLst'))
        gd = etree.SubElement(avLst, qn('a:gd'))
        gd.set('name', 'adj')
        gd.set('fmla', f'val {int(50000 * corner_radius)}')
    return shape

def add_oval(slide, l, t, w, h, fill_color):
    shape = slide.shapes.add_shape(9, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape

def add_text_box(slide, l, t, w, h, text, font_size, bold=False, italic=False,
                  color=WHITE, align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.text_frame.word_wrap = wrap
    tf = txb.text_frame
    tf.paragraphs[0].text = ''
    para = tf.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txb

def add_para_run(txb, text, font_size, bold=False, italic=False, color=WHITE, align=PP_ALIGN.LEFT):
    tf = txb.text_frame
    para = tf.add_paragraph()
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return para

def slide_header(slide, section_label, page_num):
    """Add the thin teal top bar, section label, and page number."""
    # top bar
    add_rect(slide, 0, 0.08, 13.33, 0.06, TEAL)
    # section label
    add_text_box(slide, 0.50, 0.55, 5.0, 0.40, section_label,
                 10.5, bold=True, color=TEAL)
    # page number
    add_text_box(slide, 12.73, 7.10, 0.40, 0.30, str(page_num),
                 9.5, bold=False, color=GRAY, align=PP_ALIGN.RIGHT)

# ─── NEW SOCIAL MEDIA SLIDES (for Deck 1) ───────────────────────────────────

def make_social_slide_1(prs, slide_num):
    """THE SOCIAL MEDIA DILEMMA — kids want in, parents are divided."""
    layout = prs.slides[0].slide_layout
    slide = prs.slides.add_slide(layout)
    set_bg(slide, BG)
    slide_header(slide, 'THE SOCIAL MEDIA DILEMMA', slide_num)

    # Big title
    add_text_box(slide, 0.50, 1.00, 9.00, 1.40,
                 '55M Kids Want Social Media.', 32, bold=True, color=WHITE)
    txb = slide.shapes[-1]
    add_para_run(txb, 'Half Their Parents Say No.', 32, bold=True, color=TEAL)

    # Divider line
    add_rect(slide, 0.50, 2.55, 5.00, 0.05, TEAL)

    # Subtitle
    add_text_box(slide, 0.50, 2.70, 12.00, 0.55,
                 'There is no safe platform built for kids. Every major social app is designed for adults — and kids pay the price.',
                 16, bold=False, italic=True, color=TEAL_LT)

    # Left box — PARENTS SAY NO
    add_rounded_rect(slide, 0.50, 3.45, 5.70, 2.80, DARK2)
    add_rect(slide, 0.50, 3.45, 5.70, 0.05, RED)
    add_text_box(slide, 0.65, 3.55, 4.00, 0.45, '⚠️  WHY PARENTS SAY NO',
                 12, bold=True, color=RED)
    items_no = [
        ('🚫', 'Predators & strangers in DMs'),
        ('📉', 'Cyberbullying & comparison culture'),
        ('🧠', 'Mental health risks, anxiety, FOMO'),
        ('📵', 'Age-inappropriate content everywhere'),
        ('👁️', 'Zero parental visibility or control'),
    ]
    y = 4.10
    for icon, text in items_no:
        add_text_box(slide, 0.65, y, 0.45, 0.38, icon, 12, color=WHITE)
        add_text_box(slide, 1.15, y+0.02, 4.80, 0.38, text, 12, color=TEAL_XLT)
        y += 0.42

    # Right box — KIDS WANT IN
    add_rounded_rect(slide, 6.70, 3.45, 5.70, 2.80, DARK2)
    add_rect(slide, 6.70, 3.45, 5.70, 0.05, TEAL)
    add_text_box(slide, 6.85, 3.55, 4.50, 0.45, '✨  WHY KIDS WANT IN',
                 12, bold=True, color=TEAL)
    items_yes = [
        ('👑', "It's where the culture is — they feel left out"),
        ('🤝', 'Peer belonging & social status matter'),
        ('🎨', 'They want to share what they create'),
        ('💬', 'Connection with friends beyond school'),
        ('🌟', 'Recognition and visibility for their work'),
    ]
    y = 4.10
    for icon, text in items_yes:
        add_text_box(slide, 6.85, y, 0.45, 0.38, icon, 12, color=WHITE)
        add_text_box(slide, 7.35, y+0.02, 4.80, 0.38, text, 12, color=TEAL_XLT)
        y += 0.42

    # Bottom bar
    add_rounded_rect(slide, 0.50, 6.38, 12.20, 0.72, TEAL2)
    add_text_box(slide, 0.70, 6.48, 11.80, 0.52,
                 '= Both sides are right. The problem is that a safe middle ground has never existed — until now.',
                 14, bold=True, color=DARK2, align=PP_ALIGN.LEFT)


def make_social_slide_2(prs, slide_num):
    """THE SPLIT — stats on parental attitudes."""
    layout = prs.slides[0].slide_layout
    slide = prs.slides.add_slide(layout)
    set_bg(slide, BG)
    slide_header(slide, 'THE PARENT DIVIDE', slide_num)

    add_text_box(slide, 0.50, 1.00, 9.00, 0.85,
                 'Parents Are Split — And Neither Side Is Wrong.', 28, bold=True, color=WHITE)
    add_rect(slide, 0.50, 1.90, 5.00, 0.05, TEAL)
    add_text_box(slide, 0.50, 2.05, 12.00, 0.55,
                 'The social media debate is one of the top parenting conflicts today — with no good solution on either side.',
                 15, bold=False, italic=True, color=TEAL_LT)

    # Stat cards — row 1
    stats = [
        ('45%', 'of parents\nBANNED social media\nentirely for their child'),
        ('38%', 'allow it with\nsome restrictions,\nbut worry constantly'),
        ('72%', 'of kids say they feel\n"left out" because they\ncannot use social apps'),
        ('91%', 'of parents agree\na 100% safe kid-only\nplatform would earn\ntheir full approval'),
    ]
    x_positions = [0.50, 3.55, 6.60, 9.65]
    for i, (stat, desc) in enumerate(stats):
        x = x_positions[i]
        add_rounded_rect(slide, x, 2.80, 2.80, 3.00, DARK2)
        add_rect(slide, x, 2.80, 2.80, 0.05, TEAL)
        add_text_box(slide, x+0.10, 2.95, 2.60, 0.85, stat,
                     36, bold=True, color=TEAL, align=PP_ALIGN.LEFT)
        add_text_box(slide, x+0.10, 3.80, 2.60, 1.80, desc,
                     12, bold=False, color=TEAL_XLT)

    # Bottom quote
    add_rect(slide, 0.50, 6.20, 0.06, 0.90, TEAL)
    add_text_box(slide, 0.75, 6.22, 11.80, 0.75,
                 '"I don\'t want to ban social media forever. I just want something I can actually trust with my 9-year-old."  — Parent focus group respondent',
                 14, bold=False, italic=True, color=TEAL_XLT)


def make_social_slide_3(prs, slide_num):
    """THE SOLUTION — 100% kid-safe social platform."""
    layout = prs.slides[0].slide_layout
    slide = prs.slides.add_slide(layout)
    set_bg(slide, BG)
    slide_header(slide, 'THE SAFE SOCIAL SOLUTION', slide_num)

    add_text_box(slide, 0.50, 1.00, 9.00, 0.90,
                 'What If Social Media Was Built\nFor Kids First?', 30, bold=True, color=WHITE)
    add_rect(slide, 0.50, 2.00, 5.00, 0.05, TEAL)
    add_text_box(slide, 0.50, 2.15, 12.00, 0.50,
                 'A 100% kid-safe social layer — built into the Tiny Masterpieces platform — gives kids the status of social media, with zero of the risk.',
                 15, italic=True, color=TEAL_LT)

    # Left column — how it works
    add_rounded_rect(slide, 0.50, 2.85, 5.70, 3.85, DARK2)
    add_rect(slide, 0.50, 2.85, 5.70, 0.05, TEAL)
    add_text_box(slide, 0.65, 2.95, 4.50, 0.40, 'HOW IT STAYS SAFE', 11, bold=True, color=TEAL)
    features = [
        ('🔒', 'Closed community — only verified families'),
        ('🚫', 'No DMs, no open comments, no strangers'),
        ('✅', 'Every post parent-approved before publishing'),
        ('👁️', 'AI + human moderation on all content'),
        ('🛡️', 'COPPA-compliant from day one'),
        ('📵', 'No follower counts or like-based ranking'),
        ('🎨', 'Art-only feed — creativity, not selfies'),
    ]
    y = 3.42
    for icon, text in features:
        add_text_box(slide, 0.65, y, 0.40, 0.38, icon, 11, color=WHITE)
        add_text_box(slide, 1.10, y+0.02, 5.00, 0.38, text, 11, color=TEAL_XLT)
        y += 0.46

    # Right column — social status kids get
    add_rounded_rect(slide, 6.70, 2.85, 5.70, 3.85, DARK2)
    add_rect(slide, 6.70, 2.85, 5.70, 0.05, RGBColor(0xF7, 0xD0, 0x60))
    add_text_box(slide, 6.85, 2.95, 4.50, 0.40, 'THE STATUS KIDS ACTUALLY GET', 11, bold=True, color=GOLD)
    perks = [
        ('⭐', 'A real public gallery of their artwork'),
        ('🏅', 'Creator badges and achievement levels'),
        ('🎉', 'Reactions and encouragement from peers'),
        ('📋', 'Monthly challenges to compete and share'),
        ('📬', 'Physical mail — the ultimate flex at school'),
        ('🌟', 'Featured "Artist of the Month" spotlight'),
        ('👑', '"Creator Level" visible to the community'),
    ]
    y = 3.42
    for icon, text in perks:
        add_text_box(slide, 6.85, y, 0.40, 0.38, icon, 11, color=WHITE)
        add_text_box(slide, 7.30, y+0.02, 5.00, 0.38, text, 11, color=TEAL_XLT)
        y += 0.46

    # Bottom bar
    add_rounded_rect(slide, 0.50, 6.90, 12.20, 0.48, TEAL2)
    add_text_box(slide, 0.70, 6.97, 11.80, 0.38,
                 '= Kids get the status. Parents get the safety. No one has to compromise.',
                 13, bold=True, color=DARK2)


def make_social_slide_4(prs, slide_num):
    """ALL THE BENEFITS — full list."""
    layout = prs.slides[0].slide_layout
    slide = prs.slides.add_slide(layout)
    set_bg(slide, BG)
    slide_header(slide, 'THE BENEFITS', slide_num)

    add_text_box(slide, 0.50, 1.00, 9.00, 0.80,
                 'Win-Win-Win. For Kids, Parents & Society.', 28, bold=True, color=WHITE)
    add_rect(slide, 0.50, 1.85, 12.00, 0.05, TEAL)

    # Three-column benefit layout
    cols = [
        {
            'title': '🧒  FOR KIDS',
            'color': TEAL,
            'items': [
                'Real social status among peers',
                'Creative confidence that grows',
                'Encouragement — not comparison',
                'Achievement recognition & badges',
                'Physical mail that makes them feel famous',
                'Monthly challenges keep it exciting',
                'Zero cyberbullying or toxic content',
            ]
        },
        {
            'title': '👨‍👩‍👧  FOR PARENTS',
            'color': GOLD,
            'items': [
                'Full control — approve every post',
                'Peace of mind — no strangers, no DMs',
                'No addictive engagement mechanics',
                'COPPA-compliant, privacy-first design',
                'Builds creativity instead of screen addiction',
                'Visibility into every interaction',
                'Easy guilt-free "yes" to social media',
            ]
        },
        {
            'title': '🌍  FOR SOCIETY',
            'color': TEAL_LT,
            'items': [
                'Proof that safe social media is possible',
                'Kids develop creativity, not anxiety',
                'Physical mail reduces digital overload',
                'Family bonds strengthened, not broken',
                'Alternative to algorithm-driven feeds',
                'A generation of confident young creators',
                'Healthy relationship with technology',
            ]
        },
    ]

    x_positions = [0.50, 4.65, 8.80]
    for i, col in enumerate(cols):
        x = x_positions[i]
        add_rounded_rect(slide, x, 2.05, 4.00, 4.80, DARK2)
        add_rect(slide, x, 2.05, 4.00, 0.05, col['color'])
        add_text_box(slide, x+0.15, 2.15, 3.70, 0.42,
                     col['title'], 12, bold=True, color=col['color'])
        y = 2.65
        for item in col['items']:
            add_text_box(slide, x+0.15, y, 3.70, 0.42,
                         f'✓  {item}', 11, color=TEAL_XLT)
            y += 0.47

    # Bottom callout
    add_rounded_rect(slide, 0.50, 7.05, 12.20, 0.38, TEAL)
    add_text_box(slide, 0.70, 7.10, 11.80, 0.28,
                 'Kids Creativity Confidence Club is the first social platform where parents approve — and kids actually want to use it.',
                 12, bold=True, color=DARK2, align=PP_ALIGN.LEFT)


# ─── DECK 1: copy + add slides ───────────────────────────────────────────────
shutil.copy(SRC, OUT1)
prs1 = Presentation(OUT1)

current_count = len(prs1.slides)
make_social_slide_1(prs1, current_count + 1)
make_social_slide_2(prs1, current_count + 2)
make_social_slide_3(prs1, current_count + 3)
make_social_slide_4(prs1, current_count + 4)

prs1.save(OUT1)
print(f"Deck 1 saved: {len(prs1.slides)} slides")


# ─── DECK 2: improved pitch ───────────────────────────────────────────────────
shutil.copy(SRC, OUT2)
prs2 = Presentation(OUT2)

def fix_run_text(run, old, new):
    if old in (run.text or ''):
        run.text = run.text.replace(old, new)

def remove_shape(slide, shape_name):
    sp = None
    for s in slide.shapes:
        if s.name == name:
            sp = s
            break
    if sp:
        sp._element.getparent().remove(sp._element)

def delete_shape_by_name(slide, name):
    for s in slide.shapes:
        if s.name == name:
            s._element.getparent().remove(s._element)
            return True
    return False

# ── Slide 1: Remove the tagline note, clean up subtitle ──────────────────────
# Nothing to change textually — it's clean already

# ── Slide 2: Fix website URL typo? (tinymasterpieces.com looks fine) ──────────
# Minor: this is fine

# ── Slide 3: THE PROBLEM — clean as-is ───────────────────────────────────────

# ── Slide 4: THE INSIGHT — clean ──────────────────────────────────────────────

# ── Slide 5: MARKET PROOF — remove yellow internal note ──────────────────────
slide5 = prs2.slides[4]
for shape in slide5.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if 'Small successful Social Pages I found online' in (run.text or ''):
                    run.text = ''
                    try:
                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    except:
                        pass
                # Remove yellow color on the parenthetical phrase
                try:
                    if run.font.color and run.font.color.type:
                        if run.font.color.rgb == RGBColor(0xFF, 0xFF, 0x00):
                            run.text = ''
                except:
                    pass

# ── Slide 7: EXPERIENCE Kid Sees — fix typo in "ENCOURAGMENT" ────────────────
# Actually the typo is in slide 9
slide9 = prs2.slides[8]
for shape in slide9.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if 'ENCOURAGMENT' in (run.text or ''):
                    run.text = run.text.replace('ENCOURAGMENT', 'ENCOURAGEMENT')

# ── Slide 10: PRICING — remove "(SAMPLE PRICING)" note ───────────────────────
slide10 = prs2.slides[9]
to_remove = []
for shape in slide10.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if 'SAMPLE PRICING' in (run.text or ''):
                    run.text = ''
                if "isn't best Free option" in (run.text or ''):
                    run.text = 'FREE'
                    try:
                        run.font.size = Pt(15)
                    except:
                        pass
                # also clean "This isn't best..." out of same run
                if "This isn" in (run.text or '') and "best" in (run.text or ''):
                    run.text = ''

# ── Slide 13: UNIT ECONOMICS — remove internal yellow AI note ────────────────
slide13 = prs2.slides[12]
for shape in slide13.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                try:
                    if run.font.color and run.font.color.type:
                        if run.font.color.rgb == RGBColor(0xFF, 0xFF, 0x00):
                            run.text = ''
                except:
                    pass
                if 'AI strategy tools' in (run.text or ''):
                    run.text = ''
                if 'sanity check' in (run.text or ''):
                    run.text = ''

# ── Slide 15: THE ASK — clean up URL typo ("cofidenceclub" → "confidenceclub") 
slide15 = prs2.slides[14]
for shape in slide15.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if 'cofidenceclub' in (run.text or ''):
                    run.text = run.text.replace('cofidenceclub', 'confidenceclub')
                # Improve the Ask text
                if 'Approve MVP build' in (run.text or ''):
                    run.text = 'We are seeking seed funding / team commitment to build the MVP, validate with 500 beta families, and launch the first mail drop.'

# ── Global: Update slide 1 cover pitch to be tighter ─────────────────────────
slide1 = prs2.slides[0]
for shape in slide1.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                # Tighten the subtitle description
                if 'A Platform and mail-powered creator community' in (run.text or ''):
                    run.text = 'A mail-powered creator community that helps kids keep creating,'
                if 'mail-powered creator community that helps kids keep creating' in (run.text or ''):
                    pass  # already fixed above

# ── Global: Remove any remaining internal yellow annotation text ──────────────
for slide in prs2.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                try:
                    if run.font.color and run.font.color.type:
                        col = run.font.color.rgb
                        if col == RGBColor(0xFF, 0xFF, 0x00):  # bright yellow = internal notes
                            run.text = ''
                except:
                    pass

prs2.save(OUT2)
print(f"Deck 2 saved: {len(prs2.slides)} slides")
print("Done!")
