#!/usr/bin/env python3
"""
Build the Utility Inspection Intelligence Command Center Excel workbook.
Output: /home/user/sales/Utility_Inspection_Intelligence_Command_Center.xlsx
"""

import datetime
from openpyxl import Workbook
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

# ─────────────────────────────────────────────────────────────────────────────
# COLOR CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
HEADER_BG      = "1F3864"   # dark navy
HEADER_FG      = "FFFFFF"   # white text
TIER1_FILL     = "C6EFCE"   # light green
TIER2_FILL     = "FFEB9C"   # light yellow
TIER3_FILL     = "FFCC99"   # light orange
PARTNER_FILL   = "BDD7EE"   # light blue
COMP_FILL      = "FFC7CE"   # light red
SECTION_FILL   = "D9D9D9"   # medium gray
ALT_ROW_FILL   = "F2F2F2"   # very light gray
WHITE_FILL     = "FFFFFF"
TITLE_BG       = "1F3864"
SUBTITLE_BG    = "2E5090"

TODAY_STR = datetime.date.today().isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FACTORIES
# ─────────────────────────────────────────────────────────────────────────────

def make_fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def thin_border() -> Border:
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)


def header_font(size=10, bold=True, color=HEADER_FG) -> Font:
    return Font(name="Calibri", size=size, bold=bold, color=color)


def body_font(size=9, bold=False, color="000000") -> Font:
    return Font(name="Calibri", size=size, bold=bold, color=color)


def apply_header_row(ws, row_num: int, cols: list[str],
                     bg=HEADER_BG, fg=HEADER_FG, height=20):
    """Write column headers with dark background and white bold text."""
    for col_idx, label in enumerate(cols, start=1):
        cell = ws.cell(row=row_num, column=col_idx, value=label)
        cell.fill = make_fill(bg)
        cell.font = Font(name="Calibri", size=10, bold=True, color=fg)
        cell.alignment = Alignment(horizontal="center", vertical="center",
                                   wrap_text=True)
        cell.border = thin_border()
    ws.row_dimensions[row_num].height = height


def section_header(ws, row_num: int, text: str, col_span: int,
                   bg=SECTION_FILL, font_size=11):
    """Write a merged section header cell."""
    cell = ws.cell(row=row_num, column=1, value=text)
    cell.fill = make_fill(bg)
    cell.font = Font(name="Calibri", size=font_size, bold=True, color="000000")
    cell.alignment = Alignment(horizontal="left", vertical="center")
    cell.border = thin_border()
    if col_span > 1:
        ws.merge_cells(start_row=row_num, start_column=1,
                       end_row=row_num, end_column=col_span)
    ws.row_dimensions[row_num].height = 18


def write_cell(ws, row, col, value, bold=False, bg=None, fg="000000",
               size=9, wrap=False, h_align="left", v_align="top",
               border=True, num_format=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Calibri", size=size, bold=bold, color=fg)
    cell.alignment = Alignment(horizontal=h_align, vertical=v_align,
                               wrap_text=wrap)
    if bg:
        cell.fill = make_fill(bg)
    if border:
        cell.border = thin_border()
    if num_format:
        cell.number_format = num_format
    return cell


def set_col_widths(ws, widths: dict):
    """widths: {col_letter_or_index: width_in_chars}"""
    for col, w in widths.items():
        if isinstance(col, int):
            col = get_column_letter(col)
        ws.column_dimensions[col].width = w


def add_dropdown(ws, col_letter: str, start_row: int, end_row: int,
                 formula: str, title="Select", prompt="Choose a value"):
    dv = DataValidation(
        type="list",
        formula1=formula,
        allow_blank=True,
        showDropDown=False,
    )
    dv.prompt = prompt
    dv.promptTitle = title
    ws.add_data_validation(dv)
    dv.sqref = f"{col_letter}{start_row}:{col_letter}{end_row}"


def blank_data_rows(ws, start_row: int, num_rows: int, num_cols: int,
                    alt=True):
    """Write alternating-color blank rows."""
    for r in range(start_row, start_row + num_rows):
        bg = ALT_ROW_FILL if (alt and (r - start_row) % 2 == 1) else WHITE_FILL
        for c in range(1, num_cols + 1):
            cell = ws.cell(row=r, column=c)
            cell.fill = make_fill(bg)
            cell.border = thin_border()
            cell.font = body_font()
            cell.alignment = Alignment(wrap_text=True, vertical="top")


def write_data_row(ws, row_num: int, values: list, tier_col: int = None,
                   alt: bool = False):
    """Write a row of data with optional tier-based fill."""
    tier_map = {
        "T1": TIER1_FILL, "T2": TIER2_FILL, "T3": TIER3_FILL,
        "T4": PARTNER_FILL, "T5": COMP_FILL, "T6": SECTION_FILL,
        "T7": ALT_ROW_FILL,
    }
    bg = ALT_ROW_FILL if alt else WHITE_FILL
    if tier_col and tier_col <= len(values):
        tier_val = str(values[tier_col - 1])
        bg = tier_map.get(tier_val, bg)

    for col_idx, val in enumerate(values, start=1):
        cell = ws.cell(row=row_num, column=col_idx, value=val)
        cell.fill = make_fill(bg)
        cell.font = body_font(size=9)
        cell.alignment = Alignment(wrap_text=True, vertical="top",
                                   horizontal="left")
        cell.border = thin_border()
    ws.row_dimensions[row_num].height = 45


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 1 — "00 - START HERE"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_00(wb: Workbook):
    ws = wb.active
    ws.title = "00 - START HERE"
    ws.sheet_view.showGridLines = False

    def mw(col, width):
        ws.column_dimensions[get_column_letter(col)].width = width

    mw(1, 34); mw(2, 50); mw(3, 28)

    cur_row = 1

    # ── Title block ───────────────────────────────────────────────────────────
    ws.merge_cells(f"A{cur_row}:C{cur_row}")
    tc = ws.cell(row=cur_row, column=1,
                 value="UTILITY INSPECTION INTELLIGENCE COMMAND CENTER")
    tc.fill = make_fill(HEADER_BG)
    tc.font = Font(name="Calibri", size=16, bold=True, color=HEADER_FG)
    tc.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 36
    cur_row += 1

    ws.merge_cells(f"A{cur_row}:C{cur_row}")
    sc = ws.cell(row=cur_row, column=1,
                 value="Market Intelligence & Sales Operations Platform")
    sc.fill = make_fill(SUBTITLE_BG)
    sc.font = Font(name="Calibri", size=12, bold=False, color=HEADER_FG)
    sc.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 22
    cur_row += 1

    ws.merge_cells(f"A{cur_row}:C{cur_row}")
    dc = ws.cell(row=cur_row, column=1,
                 value=f"Last Updated: {TODAY_STR}")
    dc.fill = make_fill("2E5090")
    dc.font = Font(name="Calibri", size=10, italic=True, color=HEADER_FG)
    dc.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 18
    cur_row += 2  # blank gap

    # ── PURPOSE ───────────────────────────────────────────────────────────────
    section_header(ws, cur_row, "PURPOSE", 3, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    ws.merge_cells(f"A{cur_row}:C{cur_row}")
    pc = ws.cell(row=cur_row, column=1,
                 value=("This workbook identifies the best buyers, partners, RFP opportunities, "
                        "and competitive intelligence in the utility inspection, drone inspection, "
                        "EPC, and infrastructure analytics market. Use it to prioritize outreach, "
                        "track live RFPs, and brief leadership on top opportunities."))
    pc.font = body_font(size=9)
    pc.alignment = Alignment(wrap_text=True, vertical="top")
    pc.fill = make_fill(WHITE_FILL)
    pc.border = thin_border()
    ws.row_dimensions[cur_row].height = 52
    cur_row += 2

    # ── SHEET MAP ─────────────────────────────────────────────────────────────
    section_header(ws, cur_row, "SHEET MAP", 3, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    apply_header_row(ws, cur_row,
                     ["Sheet Name", "Purpose", "Primary User"],
                     bg="2E5090", fg=HEADER_FG, height=18)
    cur_row += 1
    sheet_map = [
        ("00 - START HERE",        "Orientation, legend, glossary",                              "All users"),
        ("01 - EXEC DASHBOARD",    "Top 25 accounts, hot RFPs, Monday morning calls",            "Leadership"),
        ("02 - TOP ACCOUNTS",      "All scored utility targets, ranked",                         "Sales, Research"),
        ("03 - RFP + RFI TRACKER", "Live procurement opportunities with deadlines",              "Sales, BD"),
        ("04 - CONTACTS",          "Decision makers, outreach status, last touch",               "Sales"),
        ("05 - INSPECTION VENDORS","Competitors, partners, watchlist companies",                 "Strategy"),
        ("06 - CHANNEL PARTNERS",  "EPC firms, drone vendors, GIS integrators",                 "BD, Partnerships"),
        ("07 - COOPERATIVES",      "NRECA co-ops and public power targets",                      "Sales"),
        ("08 - MARKET INTELLIGENCE","News signals, competitor moves, conference intel",          "Strategy"),
        ("09 - SCORING MODEL",     "Score definitions, weights, calibration",                   "All users"),
        ("10 - DATA SOURCES",      "Procurement portals, monitoring feeds, refresh schedule",   "Research"),
    ]
    for i, (sn, pu, usr) in enumerate(sheet_map):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col, val in enumerate([sn, pu, usr], start=1):
            c = ws.cell(row=cur_row, column=col, value=val)
            c.fill = make_fill(bg); c.font = body_font(9)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = thin_border()
        ws.row_dimensions[cur_row].height = 15
        cur_row += 1
    cur_row += 1

    # ── COLOR LEGEND ─────────────────────────────────────────────────────────
    section_header(ws, cur_row, "COLOR LEGEND", 3, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    legend = [
        (TIER1_FILL,    "GREEN fill",  "Tier 1 (Active Now — call this week)"),
        (TIER2_FILL,    "YELLOW fill", "Tier 2 (High fit, nurture)"),
        (TIER3_FILL,    "ORANGE fill", "Tier 3 (Active RFP, lower fit)"),
        (PARTNER_FILL,  "BLUE fill",   "Partner opportunity"),
        (COMP_FILL,     "RED fill",    "Competitor / watchlist"),
        (SECTION_FILL,  "GRAY fill",   "Archive / ignore"),
    ]
    for fill_hex, label, meaning in legend:
        c1 = ws.cell(row=cur_row, column=1, value=label)
        c1.fill = make_fill(fill_hex); c1.font = body_font(9, bold=True)
        c1.alignment = Alignment(vertical="center")
        c1.border = thin_border()
        ws.merge_cells(f"B{cur_row}:C{cur_row}")
        c2 = ws.cell(row=cur_row, column=2, value=meaning)
        c2.fill = make_fill(fill_hex); c2.font = body_font(9)
        c2.alignment = Alignment(vertical="center")
        c2.border = thin_border()
        ws.row_dimensions[cur_row].height = 16
        cur_row += 1
    cur_row += 1

    # ── TIER DEFINITIONS ─────────────────────────────────────────────────────
    section_header(ws, cur_row, "TIER DEFINITIONS", 3, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    tiers = [
        ("T1 — Active Now",          "High fit + active RFP/capital signal. Outreach within 7 days.",      TIER1_FILL),
        ("T2 — High Fit, No Signal", "Strong buyer, no current trigger. Quarterly nurture.",               TIER2_FILL),
        ("T3 — Active RFP, Low Fit", "Open bid but misaligned. Bid only if strategic.",                   TIER3_FILL),
        ("T4 — Partner",             "Channel relationship, not direct buyer.",                            PARTNER_FILL),
        ("T5 — Competitive Intel",   "Competitor to monitor only.",                                        COMP_FILL),
        ("T6 — Watchlist",           "Unclear role, review quarterly.",                                    SECTION_FILL),
        ("T7 — Ignore",              "Confirmed low fit. Archive.",                                        ALT_ROW_FILL),
    ]
    for tier_label, tier_def, fill_hex in tiers:
        c1 = ws.cell(row=cur_row, column=1, value=tier_label)
        c1.fill = make_fill(fill_hex); c1.font = body_font(9, bold=True)
        c1.alignment = Alignment(vertical="center")
        c1.border = thin_border()
        ws.merge_cells(f"B{cur_row}:C{cur_row}")
        c2 = ws.cell(row=cur_row, column=2, value=tier_def)
        c2.fill = make_fill(fill_hex); c2.font = body_font(9)
        c2.alignment = Alignment(wrap_text=True, vertical="top")
        c2.border = thin_border()
        ws.row_dimensions[cur_row].height = 16
        cur_row += 1
    cur_row += 1

    # ── SCORING MODEL SUMMARY ─────────────────────────────────────────────────
    section_header(ws, cur_row, "SCORING MODEL SUMMARY  (full definitions in Sheet 09 - SCORING MODEL)",
                   3, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    apply_header_row(ws, cur_row, ["Signal", "Weight", ""],
                     bg="2E5090", fg=HEADER_FG, height=16)
    cur_row += 1
    scoring = [
        ("Drone Program Maturity",   "15%"),
        ("Data Volume / Pain Signal","15%"),
        ("Budget Signal",            "15%"),
        ("Active RFP / RFI",         "15%"),
        ("Technology Fit",           "10%"),
        ("Urgency Driver",           "10%"),
        ("Ease of Entry",            "10%"),
        ("Revenue Potential",        "5%"),
        ("Competitive Exposure",     "5%"),
        ("Partner Potential",        "0% (bonus multiplier)"),
    ]
    for i, (sig, wt) in enumerate(scoring):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col, val in enumerate([sig, wt, ""], start=1):
            c = ws.cell(row=cur_row, column=col, value=val)
            c.fill = make_fill(bg); c.font = body_font(9)
            c.alignment = Alignment(vertical="center")
            c.border = thin_border()
        ws.row_dimensions[cur_row].height = 15
        cur_row += 1
    cur_row += 1

    # ── GLOSSARY ──────────────────────────────────────────────────────────────
    section_header(ws, cur_row, "GLOSSARY", 3, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    glossary = [
        ("IOU",             "Investor-Owned Utility"),
        ("DSP",             "Drone Service Provider"),
        ("EPC",             "Engineering, Procurement, Construction"),
        ("TIC",             "Testing, Inspection, Certification"),
        ("BVLOS",           "Beyond Visual Line of Sight"),
        ("DLR",             "Dynamic Line Rating"),
        ("WMP",             "Wildfire Mitigation Plan"),
        ("SRP",             "System Resilience Plan"),
        ("GRIP",            "Grid Resilience and Innovation Partnerships (DOE grant program)"),
        ("FEMA BRIC",       "Building Resilient Infrastructure and Communities"),
        ("HMGP",            "Hazard Mitigation Grant Program"),
        ("MSA",             "Master Service Agreement"),
        ("OMNIA/Sourcewell/NASPO", "Cooperative purchasing vehicles"),
    ]
    for i, (term, defn) in enumerate(glossary):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        c1 = ws.cell(row=cur_row, column=1, value=term)
        c1.fill = make_fill(bg); c1.font = body_font(9, bold=True)
        c1.alignment = Alignment(vertical="center")
        c1.border = thin_border()
        ws.merge_cells(f"B{cur_row}:C{cur_row}")
        c2 = ws.cell(row=cur_row, column=2, value=defn)
        c2.fill = make_fill(bg); c2.font = body_font(9)
        c2.alignment = Alignment(wrap_text=True, vertical="top")
        c2.border = thin_border()
        ws.row_dimensions[cur_row].height = 15
        cur_row += 1


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 2 — "01 - EXEC DASHBOARD"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_01(wb: Workbook):
    ws = wb.create_sheet("01 - EXEC DASHBOARD")
    ws.sheet_view.showGridLines = False

    # Column widths
    col_widths = {1: 6, 2: 28, 3: 8, 4: 20, 5: 45, 6: 52, 7: 42, 8: 14, 9: 14}
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    cur_row = 1

    # ─── Title ────────────────────────────────────────────────────────────────
    ws.merge_cells(f"A{cur_row}:I{cur_row}")
    t = ws.cell(row=cur_row, column=1, value="01 — EXEC DASHBOARD")
    t.fill = make_fill(HEADER_BG); t.font = Font(name="Calibri", size=14, bold=True, color=HEADER_FG)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 30
    cur_row += 2

    # ─── Section A: TOP 10 PRIORITY ACCOUNTS ─────────────────────────────────
    section_header(ws, cur_row, "SECTION A — TOP 10 PRIORITY ACCOUNTS — Update Weekly", 9,
                   bg=SECTION_FILL, font_size=11)
    cur_row += 1
    a_cols = ["Rank", "Company", "Score", "Type", "Why Now", "Pitch Angle",
              "Next Action", "Owner", "Due Date"]
    apply_header_row(ws, cur_row, a_cols, bg=HEADER_BG, fg=HEADER_FG, height=22)
    cur_row += 1

    top10 = [
        (1, "Oncor Electric Delivery", 94, "Utility - IOU",
         "$47.5B capital plan 2026-30; actively purchased 2800mi drone + 20000mi LiDAR imagery Q2 2025; House Bill 5247 UTM compliance",
         "Lead with: data organization and retrieval — they are acquiring massive imagery volumes with no unified intelligence layer",
         "Schedule intro call with VP Grid Operations", "", ""),
        (2, "Pacific Gas & Electric", 91, "Utility - IOU",
         "Wildfire regulation pressure; 220000 poles inspected 2024; multiple drone platforms (Skydio + DJI); aerial span inspection pilot 2026-28; $3.3B undergrounding",
         "Lead with: multi-vendor data fragmentation — they run Skydio, DJI Matrice, AirData simultaneously with no unified layer",
         "Identify drone program lead via LinkedIn", "", ""),
        (3, "Florida Power & Light", 89, "Utility - IOU",
         "5.9M customers; 20+ drone fleet; Percepto AIM + Osmose + LiDAR running in parallel; 2026 Storm Protection Plan",
         "Lead with: storm documentation and FEMA evidence — they have annual storm exposure and massive field verification needs",
         "Research current inspection software vendor", "", ""),
        (4, "Ameren", 87, "Utility - IOU",
         "Publicly stated: 'we were finding more data than we could ingest'; 18 drone pilots; 200000+ poles; 600mi transmission LiDAR; DistribuTECH presence",
         "Lead with: data ingestion and retrieval — use their own public quote as the opener",
         "Find contact from DistribuTECH attendance", "", ""),
        (5, "Georgia Power", 85, "Utility - IOU",
         "Most mature in-house UAS program in U.S.; 160+ pilots, 200+ aircraft; expanding from transmission to distribution; massive data center load growth driving grid expansion",
         "Lead with: scaling analytics to match program maturity — they have the data; they need the intelligence layer",
         "Identify UAS program director", "", ""),
        (6, "Burns & McDonnell", 82, "EPC / Channel Partner",
         "$7.3B revenue; 14000 employees; uses drone inspection services; engineering-led culture open to analytics tools; ESOP ownership = partnership-friendly",
         "Lead with: analytics layer for their drone inspection deliverables — you make their reports more valuable to utility clients",
         "BD intro via engineering conference", "", ""),
        (7, "Quanta Services", 80, "EPC / Channel Partner",
         "$28.48B revenue; 59000 employees; recent acquisitions (Dynamic Systems 2025, Cupertino Electric 2024); largest utility contractor in U.S.",
         "Lead with: proof-of-work documentation and closeout packages for their utility clients — they need better field verification tools",
         "Research Quanta digital/technology division", "", ""),
        (8, "CPS Energy", 76, "Utility - Municipal",
         "$3B revenue; 920000 customers; largest U.S. municipal gas+electric utility; drone program documented; major data center and TX manufacturing load growth",
         "Lead with: drone data organization for a rapidly growing urban utility with capital expansion underway",
         "Identify technology or operations contact", "", ""),
        (9, "Salt River Project", 74, "Utility - Public Power",
         "Consolidated drone into Flight Services (140 poles/day); 2025-35 ISP; retiring 1300+ MW coal; data center load boom in AZ",
         "Lead with: consolidated fleet = consolidated data need; they are mature enough to need analytics not just imagery",
         "Research SRP drone program lead", "", ""),
        (10, "Black & Veatch", 72, "EPC / Channel Partner",
         "$4.3B revenue; 10000 employees; major utility engineering firm; private ESOP; analytical culture; potential reseller of inspection analytics to utility clients",
         "Lead with: partnership to embed analytics in their utility inspection deliverables",
         "Identify VP of Digital or Innovation", "", ""),
    ]
    for i, row_data in enumerate(top10):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.fill = make_fill(bg)
            cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top",
                                       horizontal="center" if col_idx in (1, 3) else "left")
            cell.border = thin_border()
        ws.row_dimensions[cur_row].height = 60
        cur_row += 1
    cur_row += 2

    # ─── Section B: HOT RFPs ──────────────────────────────────────────────────
    section_header(ws, cur_row,
                   "SECTION B — HOT RFPs — Active Opportunities (Update Weekly)", 9,
                   bg=SECTION_FILL, font_size=11)
    cur_row += 1
    b_cols = ["Opportunity Name", "Issuer", "Type", "Deadline",
              "Fit (1-5)", "Status", "Link", "Owner"]
    # merge last 2 cols into 9 total
    apply_header_row(ws, cur_row, b_cols, bg=HEADER_BG, fg=HEADER_FG, height=22)
    # adjust widths for section B display in 8 of 9 cols
    cur_row += 1
    rfp_rows = [
        ("EXAMPLE — Drone Inspection Services", "[Issuer TBD]", "RFP",
         "[Date TBD]", 5, "Monitoring", "[SAM.gov link]", "[Owner]"),
        ("EXAMPLE — Vegetation Management Analytics", "[Issuer TBD]", "RFI",
         "[Date TBD]", 4, "Qualifying", "[State portal]", "[Owner]"),
        ("EXAMPLE — Grid Resilience Documentation", "[Issuer TBD]", "Grant",
         "[Date TBD]", 5, "Researching", "[DOE GRIP portal]", "[Owner]"),
    ]
    for i, rd in enumerate(rfp_rows):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col_idx, val in enumerate(rd, start=1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[cur_row].height = 22
        cur_row += 1
    cur_row += 2

    # ─── Section C: MONDAY MORNING ────────────────────────────────────────────
    section_header(ws, cur_row,
                   "SECTION C — MONDAY MORNING — 5 CALLS THIS WEEK", 9,
                   bg=SECTION_FILL, font_size=11)
    cur_row += 1
    c_cols = ["Priority", "Name", "Company", "Reason to Call",
              "What to Say", "Phone/Email", "Status", "", ""]
    apply_header_row(ws, cur_row, c_cols, bg=HEADER_BG, fg=HEADER_FG, height=22)
    cur_row += 1
    blank_data_rows(ws, cur_row, 5, 9)
    cur_row += 6

    # ─── Section D: INTENT SIGNALS ────────────────────────────────────────────
    section_header(ws, cur_row,
                   "SECTION D — INTENT SIGNALS THIS WEEK", 9,
                   bg=SECTION_FILL, font_size=11)
    cur_row += 1
    d_cols = ["Company", "Signal", "Source", "Date Spotted",
              "Recommended Action", "", "", "", ""]
    apply_header_row(ws, cur_row, d_cols, bg=HEADER_BG, fg=HEADER_FG, height=22)
    cur_row += 1
    blank_data_rows(ws, cur_row, 5, 9)
    cur_row += 6

    # ─── Section E: COMPETITOR ALERTS ────────────────────────────────────────
    section_header(ws, cur_row,
                   "SECTION E — COMPETITOR ALERTS", 9,
                   bg=SECTION_FILL, font_size=11)
    cur_row += 1
    e_cols = ["Competitor", "Event", "Date", "Implication", "Our Response",
              "", "", "", ""]
    apply_header_row(ws, cur_row, e_cols, bg=HEADER_BG, fg=HEADER_FG, height=22)
    cur_row += 1
    competitors = [
        ("Zeitview",
         "Raised $60M Series D (Mar 2025); acquired Consilience Jul 2025, Clearsight 2024",
         "2025",
         "Most aggressive acquirer in market; expanding beyond solar into utility",
         "Differentiate on data organization vs. image capture; they are hardware/capture-focused"),
        ("Optelos",
         "19 employees; GIS/EAM/ServiceNow integrations; claims 70% reduction in remediation time",
         "2025",
         "Smallest but most technically aligned competitor; deepest integration story",
         "Monitor for utility wins; their integration depth is the strongest competitive threat"),
        ("Sharper Shape",
         "~$35M revenue; Living Digital Twin + Asset Insights AI; Volatus partnership",
         "2025",
         "Revenue-generating competitor with temporal comparison story but dependent on Volatus (distress)",
         "Volatus restructuring may destabilize Sharper Shape's delivery model — watch for customer churn"),
        ("HUVRdata",
         "Acquired by Technical Toolboxes Jan 2026",
         "Jan 2026",
         "Validates consolidation thesis; TT has strong utility relationships",
         "Research which utilities used HUVRdata — they may now be open to alternatives"),
        ("PrecisionHawk",
         "Chapter 7 bankruptcy Dec 2023; $136M+ raised; assets auctioned ~$150k",
         "Dec 2023",
         "Massive cautionary tale; their utility customers are now without a vendor",
         "Target former PrecisionHawk utility customers immediately — they are actively looking"),
    ]
    for i, rd in enumerate(competitors):
        bg = COMP_FILL if i % 2 == 0 else ALT_ROW_FILL
        for col_idx, val in enumerate(rd, start=1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        # fill remaining cols
        for col_idx in range(len(rd) + 1, 10):
            cell = ws.cell(row=cur_row, column=col_idx)
            cell.fill = make_fill(bg); cell.border = thin_border()
        ws.row_dimensions[cur_row].height = 52
        cur_row += 1


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 3 — "02 - TOP ACCOUNTS"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_02(wb: Workbook):
    ws = wb.create_sheet("02 - TOP ACCOUNTS")

    headers = [
        "#", "Company", "Tier", "Fit Score", "Lead Type", "Utility Type",
        "Revenue (approx)", "Employees", "Customers", "HQ", "States Served",
        "Transmission Miles", "Distribution Miles", "Drone Maturity (0-5)",
        "Known Drone Vendors", "Data Pain Signal", "Budget Signal",
        "Wildfire Zone", "Storm FEMA Risk", "Asset Mgmt System", "GIS Platform",
        "Veg Mgmt Contractor", "Active RFP/RFI", "Pitch Angle",
        "Contact Name", "Contact Title", "Contact Email", "Contact Phone",
        "Last Outreach", "Next Action", "Action Owner", "Due Date",
        "Deal Stage", "Source URL", "Last Verified", "Confidence (1-3)", "Notes"
    ]
    num_cols = len(headers)

    col_widths = {
        1: 5, 2: 28, 3: 8, 4: 8, 5: 16, 6: 14,
        7: 14, 8: 10, 9: 18, 10: 18, 11: 14,
        12: 14, 13: 14, 14: 8,
        15: 22, 16: 40, 17: 30,
        18: 12, 19: 14, 20: 18, 21: 14,
        22: 18, 23: 14, 24: 48,
        25: 20, 26: 22, 27: 24, 28: 16,
        29: 14, 30: 36, 31: 14, 32: 14,
        33: 14, 34: 32, 35: 12, 36: 12, 37: 38,
    }
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    # Row 1: headers
    apply_header_row(ws, 1, headers, bg=HEADER_BG, fg=HEADER_FG, height=30)
    ws.freeze_panes = "D2"  # freeze top row + first 3 columns

    # Row 2: maturity scale note
    note_cell = ws.cell(row=2, column=1,
                        value="NOTE — Drone Maturity Scale: 0=None | 1=Pilot | 2=Active | 3=Expanding | 4=Consolidated | 5=Mature")
    note_cell.fill = make_fill("EEEEEE")
    note_cell.font = Font(name="Calibri", size=8, italic=True, color="555555")
    note_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.merge_cells(f"A2:{get_column_letter(num_cols)}2")
    ws.row_dimensions[2].height = 14

    # Data rows (row 3 onwards)
    accounts = [
        [1, "Oncor Electric Delivery", "T1", 94, "Utility - IOU", "T&D", "$6.5B", 5000,
         "4M+ meters (13M people)", "Dallas TX", "TX", "143000+ mi", "", 4,
         "Internal fleet",
         "Very High — Q2 2025 purchased 2800mi drone imagery + 20000mi LiDAR; actively integrating data",
         "$47.5B capital plan 2026-30; $3B SRP; ERCOT 765kV STEP",
         "Moderate", "High", "Unknown", "Esri (likely)", "Unknown",
         "Likely — SRP procurement 2025",
         "Lead with data organization and retrieval at scale — they are buying massive volumes with no unified intelligence layer",
         "", "VP Grid Operations (TBD)", "", "", "",
         "Research VP Grid Operations and UAS program lead on LinkedIn", "", "",
         "Research", "https://www.oncor.com", "2025-Q2", 2, ""],
        [2, "Pacific Gas & Electric", "T1", 91, "Utility - IOU", "T&D", "$24B", 29000,
         "5.5M accounts (16M people)", "Oakland CA", "Northern/Central CA", "", "", 5,
         "Skydio + DJI Matrice + AirData",
         "Very High — multiple platforms running in parallel; 220000 poles inspected 2024; 4000+ flights Kern County 2024",
         "2026-28 WMP; $3.3B undergrounding 1077 mi; 700+ mi overhead hardening",
         "Very High (CPUC Tier 3)", "High", "Unknown", "Unknown", "Unknown",
         "Yes — aerial span inspection pilot 2026-28",
         "Lead with multi-vendor data fragmentation and wildfire evidence documentation — regulatory pressure demands better asset data",
         "", "VP Wildfire Operations or UAS Program Lead (TBD)", "", "", "",
         "Identify drone program lead via LinkedIn + utility press", "", "",
         "Research", "https://www.pge.com", "2025-Q2", 2, ""],
        [3, "Florida Power & Light", "T1", 89, "Utility - IOU", "T&D", "$20B+", 9000,
         "5.9M accounts (12M people)", "Juno Beach FL", "FL", "", "", 5,
         "Percepto AIM + Osmose + LiDAR + FPLAir One fixed-wing",
         "High — 20+ drone fleet; autonomous substation robot; daily inspections; multiple systems running in parallel",
         "2026 Storm Protection Plan; annual T/D/vegetation programs",
         "Low", "Very High (hurricane zone)", "Unknown", "Esri (likely)", "Unknown",
         "Yes — annual storm/vegetation programs",
         "Lead with storm documentation and FEMA evidence packets — annual hurricane exposure creates recurring proof-of-work demand",
         "", "", "", "", "",
         "Research current inspection analytics vendor", "", "",
         "Research", "https://www.fpl.com", "2025-Q2", 2, ""],
        [4, "Ameren", "T1", 87, "Utility - IOU", "T&D", "$7.6B", 9000,
         "3.3M (electric + gas)", "St. Louis MO", "MO/IL", "600mi LiDAR documented", "", 4,
         "Internal (18 pilots)",
         "Critical — publicly stated 'we were finding more data than we could ingest'",
         "IL/MO Smart Energy Plan; MISO investments; DistribuTECH 2025 presence",
         "Low-Moderate", "Moderate", "Unknown", "Unknown", "Unknown",
         "Likely — grid mod procurement 2025-26",
         "Use their own public quote: 'we were finding more data than we could ingest' — position as the intelligence layer on top of their existing acquisition",
         "", "Innovation or UAS Program Lead (TBD)", "", "", "",
         "Find contact from DistribuTECH 2025 agenda", "", "",
         "Research", "https://www.ameren.com", "2025-Q2", 2, ""],
        [5, "Georgia Power", "T1", 85, "Utility - IOU", "T&D", "$10B+", 6800,
         "2.7M+", "Atlanta GA", "GA", "11855 mi", "78583 mi", 5,
         "Internal (Southern Company UAS; 160+ pilots 200+ aircraft)",
         "High — most mature in-house program in U.S.; expanding transmission to distribution; scaling data volume rapidly",
         "Data center/AI load boom; massive grid expansion; Vogtle nuclear online",
         "Low", "Moderate", "Unknown", "Unknown", "Unknown",
         "Likely — distribution inspection expansion 2025-26",
         "Lead with scaling analytics to match program maturity — they have more data than any other utility program; they need the intelligence layer",
         "", "UAS Program Director or Chief Digital Officer (TBD)", "", "", "",
         "Research Southern Company UAS team structure", "", "",
         "Research", "https://www.georgiapower.com", "2025-Q2", 2, ""],
        [6, "Eversource Energy", "T2", 78, "Utility - IOU", "T&D", "$11.9B", 10000,
         "4.4M", "Hartford CT", "CT/MA/NH", "", "", 3,
         "Internal (among first FAA approval 2014; BVLOS NH pilot)",
         "Moderate — 200+ test flights on transmission; offshore wind exit frees capital for grid focus",
         "NE grid modernization; offshore wind exit capital redeployment",
         "Low", "Moderate", "Unknown", "Unknown", "Unknown",
         "Monitor",
         "Lead with grid data organization as they redeploy offshore wind capital into transmission analytics",
         "", "", "", "", "",
         "Quarterly nurture — watch for capital plan RFP", "", "",
         "Nurture", "https://www.eversource.com", "2025-Q2", 2, ""],
        [7, "Puget Sound Energy", "T2", 74, "Utility - IOU", "T&D + Gas", "$3.7B", 3300,
         "2.1M", "Bellevue WA", "WA", "", "", 3,
         "Internal + Osmose + Heimdall Power DLR sensors (Oct 2025)",
         "Moderate — remote area transmission poles; DLR pilot expanding sensor data",
         "Grid modernization; WA decarbonization (CETA)",
         "Moderate", "High (wind/ice storms)", "Unknown", "Unknown", "Unknown",
         "Monitor",
         "Lead with sensor data integration — they are now running DLR sensors + drones + Osmose; fragmentation is building",
         "", "", "", "", "",
         "Watch for RFP tied to CETA compliance", "", "",
         "Nurture", "https://www.pse.com", "2025-Q2", 2, ""],
        [8, "Rocky Mountain Power", "T2", 72, "Utility - IOU", "T&D", "$6.5B (PacifiCorp)", "610 (segment)",
         "1.2M (RMP) / 2M (PacifiCorp)", "Salt Lake City UT", "UT/WY/ID", "", "", 3,
         "Internal",
         "High — wildfire litigation driving asset evidence demand; difficult western terrain",
         "Energy Gateway transmission capital; wildfire mitigation capital",
         "Very High (western)", "Moderate", "Unknown", "Unknown", "Unknown",
         "Monitor",
         "Lead with wildfire evidence documentation and litigation support data — Berkshire/PacifiCorp wildfire liability makes asset data a legal necessity",
         "", "", "", "", "",
         "Watch for wildfire mitigation procurement notices", "", "",
         "Nurture", "https://www.rockymountainpower.net", "2025-Q2", 2, ""],
        [9, "CPS Energy", "T2", 76, "Utility - Municipal", "T&D + Gas", "$3B", 3600,
         "920000 electric", "San Antonio TX", "TX", "", "", 2,
         "Internal (documented; vendor TBD)",
         "Moderate — drone program active but analytics vendor unclear",
         "Capital plan + resiliency; load growth (data centers + TX manufacturing)",
         "Low", "Moderate", "Unknown", "Unknown", "Unknown",
         "Monitor",
         "Lead with drone data analytics for a rapidly growing municipal utility — data center boom in TX is driving grid expansion faster than inspection programs can scale",
         "", "", "", "", "",
         "Research procurement contact", "", "",
         "Nurture", "https://www.cpsenergy.com", "2025-Q2", 2, ""],
        [10, "Salt River Project", "T2", 74, "Utility - Public Power", "T&D", "$4B", 5400,
         "1.1M electric", "Tempe AZ", "AZ", "", "", 4,
         "Internal (Flight Services consolidated; 140 poles/day)",
         "Moderate — consolidated program = consolidated data need; they are mature enough for analytics",
         "2025-35 ISP; +2000 MW gas additions; coal retirement; AZ data center load",
         "Moderate", "Moderate", "Unknown", "Esri (likely)", "Unknown",
         "Monitor",
         "Lead with analytics maturity to match fleet maturity — they have consolidated operations; now they need consolidated intelligence",
         "", "", "", "", "",
         "Research SRP Flight Services program lead", "", "",
         "Nurture", "https://www.srpnet.com", "2025-Q2", 2, ""],
        [11, "Austin Energy", "T2", 65, "Utility - Municipal", "T&D", "$1.7B", 1900,
         "600000", "Austin TX", "TX", "", "", 2,
         "Internal (since 2016 research pilot)",
         "Low-Moderate — early program; N. Austin transmission inspection",
         "Grid modernization + Austin growth; carbon goals",
         "Low", "Moderate", "Unknown", "Unknown", "Unknown",
         "Monitor",
         "Lead with growing into analytics as they scale their drone program",
         "", "", "", "", "",
         "Research technology or grid operations contact", "", "",
         "Nurture", "https://austinenergy.com", "2025-Q2", 2, ""],
    ]

    for i, row_data in enumerate(accounts):
        data_row_num = 3 + i
        tier_val = str(row_data[2])
        tier_fills = {"T1": TIER1_FILL, "T2": TIER2_FILL, "T3": TIER3_FILL}
        bg = tier_fills.get(tier_val, WHITE_FILL)
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=data_row_num, column=col_idx, value=val)
            cell.fill = make_fill(bg)
            cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top",
                                       horizontal="center" if col_idx in (1, 3, 4, 14) else "left")
            cell.border = thin_border()
        ws.row_dimensions[data_row_num].height = 80


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 4 — "03 - RFP + RFI TRACKER"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_03(wb: Workbook):
    ws = wb.create_sheet("03 - RFP + RFI TRACKER")

    headers = [
        "#", "Opportunity Name", "Issuer", "Issuer Type", "Opportunity Type",
        "NAICS Code", "Source Portal", "Link", "Issue Date", "Deadline",
        "Days Remaining", "Estimated Value", "Scope Summary", "Key Requirements",
        "Fit Score (1-5)", "Fit Notes", "Incumbent Vendor", "Our Angle",
        "Teaming Partners", "Status", "Owner", "Submission Notes", "Outcome",
        "Last Updated"
    ]

    col_widths = {
        1: 5, 2: 40, 3: 28, 4: 16, 5: 14, 6: 10,
        7: 18, 8: 36, 9: 12, 10: 12, 11: 12,
        12: 14, 13: 42, 14: 36, 15: 8, 16: 36,
        17: 22, 18: 38, 19: 22, 20: 14, 21: 14,
        22: 38, 23: 16, 24: 14,
    }
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    apply_header_row(ws, 1, headers, bg=HEADER_BG, fg=HEADER_FG, height=30)
    ws.freeze_panes = "B2"

    # Row 2: dropdown notes
    note = ("Opportunity Type: RFP | RFI | Bid | Grant | Co-op | Pilot | IDIQ | BPA    |    "
            "Status: Monitoring | Qualifying | Bidding | Submitted | Won | Lost | Skipped | Expired")
    nc = ws.cell(row=2, column=1, value=note)
    nc.fill = make_fill("EEEEEE")
    nc.font = Font(name="Calibri", size=8, italic=True, color="555555")
    nc.alignment = Alignment(horizontal="left", vertical="center")
    ws.merge_cells(f"A2:{get_column_letter(len(headers))}2")
    ws.row_dimensions[2].height = 14

    rfp_data = [
        [1, "[SAM.gov search: drone inspection utility]", "DOE / Utility TBD", "Federal/IOU", "RFP",
         "541360", "SAM.gov", "https://sam.gov", "", "", "",
         "", "Aerial drone inspection services for transmission and distribution infrastructure",
         "Drone inspection, data delivery, reporting", 5,
         "Perfect fit — monitor SAM.gov NAICS 541360 541519 237130 weekly",
         "Unknown", "Lead with AI-organized data delivery vs. raw image dumps",
         "", "Monitoring", "",
         "Set up SAM.gov email alert for these NAICS codes immediately", "", ""],
        [2, "[DOE GRIP Grant Round]", "U.S. Department of Energy", "Federal", "Grant",
         "", "DOE GRIP portal",
         "https://www.energy.gov/gdo/grid-resilience-and-innovation-partnerships-grip-program",
         "", "", "", "Up to $10M",
         "Grid resilience infrastructure improvement with data and analytics component",
         "Inspection analytics, documentation, asset data", 4,
         "Strong fit if scoped toward inspection analytics and documentation",
         "N/A", "Lead with inspection data organization as core grid resilience capability",
         "", "Researching", "",
         "Check current GRIP round open dates; partner with utility for application", "", ""],
        [3, "[FEMA BRIC / HMGP — Storm Documentation]", "FEMA / State EM Agency", "Federal", "Grant",
         "", "FEMA BRIC portal",
         "https://www.fema.gov/grants/mitigation/building-resilient-infrastructure-communities",
         "", "", "", "Varies by state",
         "Hazard mitigation planning; infrastructure documentation and resilience",
         "Storm documentation, proof-of-work, FEMA reimbursement support", 4,
         "Strong fit — inspection closeout documentation and FEMA evidence packets",
         "N/A", "Lead with FEMA reimbursement documentation tool for storm-affected utilities",
         "", "Researching", "",
         "Target utilities in hurricane and tornado corridors; FL, TX, LA, MS, AL, GA", "", ""],
        [4, "[Cooperative Purchasing — OMNIA Partners]", "OMNIA Partners", "Co-op Vehicle", "Co-op",
         "", "OMNIA Partners portal", "https://www.omniapartners.com",
         "", "", "", "Multi-year",
         "Inspection analytics and drone data management software",
         "Software, SaaS, analytics, inspection", 5,
         "Single award covers hundreds of member utilities and municipalities",
         "Unknown", "Position as inspection intelligence platform for cooperative members",
         "", "Researching", "",
         "One cooperative vehicle award = access to 500+ utility members; highest leverage procurement path", "", ""],
        [5, "[Sourcewell Technology Contract]", "Sourcewell", "Co-op Vehicle", "Co-op",
         "", "Sourcewell portal", "https://www.sourcewell-mn.gov",
         "", "", "", "Multi-year",
         "Technology and software solutions for government and utility members",
         "Software, analytics, data management", 5,
         "Sourcewell members include hundreds of municipal utilities and cooperatives",
         "Unknown", "Position as the inspection data intelligence layer for Sourcewell utility members",
         "", "Researching", "",
         "Research current Sourcewell technology solicitation cycle; applications typically annual", "", ""],
    ]

    for i, row_data in enumerate(rfp_data):
        data_row = 3 + i
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=data_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[data_row].height = 65

    # Dropdown validations
    add_dropdown(ws, "E", 3, 102,
                 '"RFP,RFI,Bid,Grant,Co-op,Pilot,IDIQ,BPA"',
                 "Opportunity Type")
    add_dropdown(ws, "T", 3, 102,
                 '"Monitoring,Qualifying,Bidding,Submitted,Won,Lost,Skipped,Expired"',
                 "Status")


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 5 — "04 - CONTACTS"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_04(wb: Workbook):
    ws = wb.create_sheet("04 - CONTACTS")

    headers = [
        "#", "First Name", "Last Name", "Title", "Company", "Company Tier",
        "Email", "Direct Dial", "Mobile", "LinkedIn URL", "Contact Source",
        "Last Outreach Date", "Outreach Method", "Outreach Notes", "Response",
        "Next Action", "Next Action Date", "Owner", "Deal Stage",
        "Warm Intro Path", "Notes", "Last Verified", "Confidence (1-3)"
    ]

    col_widths = {
        1: 5, 2: 14, 3: 16, 4: 26, 5: 26, 6: 12,
        7: 28, 8: 14, 9: 14, 10: 36, 11: 18,
        12: 14, 13: 16, 14: 38, 15: 22,
        16: 36, 17: 14, 18: 14, 19: 14,
        20: 32, 21: 38, 22: 12, 23: 10,
    }
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    # Priority note
    note_row = 1
    ws.merge_cells(f"A{note_row}:{get_column_letter(len(headers))}{note_row}")
    nc = ws.cell(row=note_row, column=1,
                 value=("PRIORITY: Complete contact research for all Tier 1 accounts before next outreach cycle. "
                        "Use Apollo.io People Export + LinkedIn Sales Navigator. "
                        "Required fields: Name, Title, Email, LinkedIn URL, Last Verified."))
    nc.fill = make_fill(TIER2_FILL)
    nc.font = Font(name="Calibri", size=9, bold=True, color="7F6000")
    nc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    nc.border = thin_border()
    ws.row_dimensions[note_row].height = 28

    apply_header_row(ws, 2, headers, bg=HEADER_BG, fg=HEADER_FG, height=28)
    ws.freeze_panes = "B3"

    # Dropdown notes row
    dn_row = 3
    ws.merge_cells(f"A{dn_row}:{get_column_letter(len(headers))}{dn_row}")
    dc = ws.cell(row=dn_row, column=1,
                 value=("Outreach Method: Cold email | Cold call | LinkedIn | Warm intro | Conference | Referral | Event    |    "
                        "Response: No response | Bounced | Opened | Replied — interested | Replied — not now | Meeting booked | Declined"))
    dc.fill = make_fill("EEEEEE"); dc.font = Font(name="Calibri", size=8, italic=True, color="555555")
    dc.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[dn_row].height = 14

    blank_data_rows(ws, 4, 20, len(headers))

    add_dropdown(ws, "M", 4, 103,
                 '"Cold email,Cold call,LinkedIn,Warm intro,Conference,Referral,Event"',
                 "Outreach Method")
    add_dropdown(ws, "O", 4, 103,
                 '"No response,Bounced,Opened,Replied — interested,Replied — not now,Meeting booked,Declined"',
                 "Response")


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 6 — "05 - INSPECTION VENDORS"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_05(wb: Workbook):
    ws = wb.create_sheet("05 - INSPECTION VENDORS")

    headers = [
        "#", "Company", "Category", "Relationship Type", "Revenue (approx)",
        "Employees", "HQ", "Tech Stack", "Funding Total", "Last Round",
        "Status", "Why It Matters", "Competitive Threat Level",
        "Partnership Potential", "Acquisition Interest", "Known Utility Clients",
        "Website", "LinkedIn", "Last Verified", "Confidence", "Notes"
    ]

    col_widths = {
        1: 5, 2: 26, 3: 24, 4: 20, 5: 16, 6: 12,
        7: 22, 8: 40, 9: 14, 10: 18,
        11: 26, 12: 50, 13: 16,
        14: 16, 15: 16, 16: 28,
        17: 32, 18: 28, 19: 12, 20: 10, 21: 46,
    }
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    apply_header_row(ws, 1, headers, bg=HEADER_BG, fg=HEADER_FG, height=30)
    ws.freeze_panes = "B2"

    vendors = [
        [1, "Optelos", "Inspection Analytics Software", "Direct Competitor",
         "Early stage", 19, "Deer Park TX",
         "AI + computer vision; GIS/EAM/ServiceNow integrations",
         "Angel/undisclosed", "Unknown", "Active",
         "Deepest integration story in market; GIS/EAM/ServiceNow already integrated; claims 70% reduction in remediation time and 3x capacity",
         "Critical", "Low", "Monitor",
         "Utility clients (names TBD)", "https://optelos.com", "", "2025-Q2", 2,
         "Biggest technical threat; small team but strong integration depth; monitor closely for utility wins"],
        [2, "Zeitview (fka DroneBase)", "Inspection Software + DSP", "Direct Competitor",
         "$25-100M", "100-250", "Santa Monica CA",
         "Drone capture + AI analytics; acquired Consilience (AI analytics Jul 2025) Clearsight (2024) Heliolytics (solar 2023)",
         "$174M total", "$60M Series D Mar 2025", "Active — aggressive",
         "Most well-funded competitor; acquisitive strategy to build end-to-end; expanding from solar/wind into utility",
         "High", "Low", "No",
         "Unknown", "https://zeitview.com", "", "2025-Q2", 2,
         "Watch acquisition targets closely — they are buying capability gaps; Consilience acquisition (Jul 2025) adds AI analytics"],
        [3, "Sharper Shape", "Inspection Analytics Software", "Direct Competitor",
         "~$35M", "58-63", "Salt Lake City UT",
         "Living Digital Twin; Asset Insights AI (40+ components)",
         "~$23.4M raised", "Unknown", "Active",
         "Temporal comparison story; promises data organization over time; but dependent on Volatus (distress)",
         "High", "Low", "Monitor",
         "Unknown", "https://sharpershape.com", "", "2025-Q2", 2,
         "Volatus restructuring may destabilize delivery model — watch for customer churn opportunities"],
        [4, "Cyberhawk", "Inspection Analytics Software", "Direct Competitor",
         "Unknown", "Unknown", "UK + US",
         "Drone inspection + AI analytics; utility and oil & gas focus",
         "Unknown", "Unknown", "Active",
         "Established UK-origin competitor with U.S. utility presence",
         "Moderate", "Low", "Monitor",
         "Unknown", "https://www.cyberhawk.aero", "", "2025-Q2", 2,
         "UK origin gives international reference customers; watch for U.S. utility wins"],
        [5, "HUVRdata (acq. Technical Toolboxes)", "Inspection Data Platform", "Former Competitor",
         "Unknown", "Unknown", "Houston TX",
         "Inspection data management; acquired Jan 2026",
         "Unknown", "Acquired Jan 2026", "Acquired",
         "Validates consolidation thesis; Technical Toolboxes has strong utility relationships",
         "Moderate", "Research", "No",
         "Unknown", "https://huvr.com", "", "2026-Jan", 2,
         "Former HUVRdata utility customers may now be open to alternatives — target list TBD"],
        [6, "PrecisionHawk", "Drone Analytics Platform", "Defunct",
         "Defunct", 0, "Raleigh NC (formerly)",
         "Drone data analytics; utility and ag focus",
         "$136M+ raised", "Chapter 7 Dec 2023", "Bankrupt — assets auctioned ~$150k",
         "Largest cautionary tale in the market; their utility customers are now without a vendor",
         "None", "None", "No",
         "Unknown (major utility customer base)", "N/A", "", "2024", 3,
         "PRIORITY: Research which utilities used PrecisionHawk — they are actively looking for replacement vendors"],
        [7, "AgEagle / senseFly", "Drone Hardware + Software", "Watchlist",
         "Unknown", "Unknown", "Wichita KS",
         "Drone hardware; eBee fixed-wing; senseFly integration",
         "Unknown", "Unknown",
         "Distress — NYSE American below compliance since Apr 2025; delist deadline Oct 2026",
         "Below compliance signal = possible distress; watch for asset sale or shutdown",
         "Low", "No", "Monitor",
         "Unknown", "https://ageagle.com", "", "2025-Q2", 2,
         "If delisted, their customer relationships and software assets may become available"],
        [8, "Percepto", "Drone-in-a-Box Hardware", "Partner Candidate",
         "Unknown", 180, "Modiin Israel / Austin TX",
         "Autonomous Sparrow drone + AIM software + AI; $120M+ raised",
         "$120M+", "Unknown", "Active",
         "Percepto AIM software is deployed at FPL — they are a hardware/software stack that needs an analytics intelligence layer on top",
         "Low", "High", "No",
         "FPL (confirmed)", "https://percepto.co", "", "2025-Q2", 2,
         "Already inside FPL — if we can integrate with Percepto AIM, we get indirect access to FPL data"],
        [9, "Raptor Maps", "Solar Inspection Analytics", "Adjacent Competitor",
         "Unknown", 86, "Boston MA",
         "Solar inspection analytics; AI review; $62-65M raised",
         "$62-65M", "$35M Series C 2024", "Active",
         "Solar-focused but adjacent; Series C 2024 = growing; could expand into utility",
         "Low", "Monitor", "No",
         "Solar developers (not utility)", "https://raptormaps.com", "", "2025-Q2", 2,
         "Watch for pivot into utility inspection — their data organization model is adjacent to ours"],
        [10, "American Robotics (Ondas)", "Drone-in-a-Box Hardware", "Watchlist",
         "$3.5B market cap", 120, "Marlborough MA",
         "Automated drone station; Scout system; BVLOS-capable",
         "Public NASDAQ: ONDS", "Unknown", "Public — distress signals",
         "Hardware play; integration with inspection analytics platforms possible",
         "None", "Monitor", "No",
         "Unknown", "https://ondas.com", "", "2025-Q2", 2,
         "Hardware only — potential integration partnership if they need an analytics layer"],
        [11, "Skydio", "Drone Hardware", "Partner Candidate",
         "Unknown", "Unknown", "Redwood City CA",
         "AI-powered drone hardware; PG&E deployment confirmed",
         "Unknown", "Unknown", "Active",
         "PG&E uses Skydio — hardware partner that needs analytics layer; integration opportunity",
         "None", "High", "No",
         "PG&E (confirmed)", "https://www.skydio.com", "", "2025-Q2", 2,
         "Already inside PG&E — Skydio integration could give access to PG&E inspection data"],
        [12, "Volatus Aerospace", "Drone Services + Software", "Watchlist",
         "Unknown", "Unknown", "Canada + US",
         "Drone services; Sharper Shape partnership",
         "Unknown", "Unknown", "Distress / restructuring 2025",
         "Sharper Shape dependency creates customer risk; Volatus restructuring = opportunity",
         "None", "Low", "Monitor",
         "Unknown", "https://volatusaerospace.com", "", "2025-Q2", 2,
         "Volatus distress may create Sharper Shape customer churn — watch closely"],
        [13, "Intertek", "Testing Inspection Certification", "Partner Candidate",
         "£3.4B group", "320 US", "Arlington Heights IL",
         "TIC services; global testing labs",
         "Public LSE: ITRK", "N/A", "Active",
         "Global TIC firm with utility inspection services; could be a channel partner for analytics layer",
         "Low", "Moderate", "No",
         "Unknown", "https://www.intertek.com", "", "2025-Q2", 2,
         "Channel partner potential — they deliver inspection reports; we make those reports intelligent"],
        [14, "SGS North America", "Testing Inspection Certification", "Partner Candidate",
         "CHF 6.8B group", "230 US", "Rutherford NJ",
         "Global TIC; inspection and certification",
         "Public SIX: SGSN", "N/A", "Active",
         "Global TIC firm similar to Intertek; utility inspection presence",
         "Low", "Moderate", "No",
         "Unknown", "https://www.sgsgroup.us.com", "", "2025-Q2", 2,
         "Same channel partner thesis as Intertek"],
    ]

    rel_fills = {
        "Direct Competitor": COMP_FILL,
        "Former Competitor": "FFD9D9",
        "Defunct": SECTION_FILL,
        "Watchlist": ALT_ROW_FILL,
        "Partner Candidate": PARTNER_FILL,
        "Adjacent Competitor": TIER3_FILL,
    }

    for i, row_data in enumerate(vendors):
        data_row = 2 + i
        rel_type = str(row_data[3])
        bg = rel_fills.get(rel_type, WHITE_FILL)
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=data_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[data_row].height = 65

    add_dropdown(ws, "D", 2, 101,
                 '"Direct Competitor,Adjacent Competitor,Partner Candidate,Channel Partner,Acquisition Target,Watchlist,Ignore"',
                 "Relationship Type")
    add_dropdown(ws, "M", 2, 101,
                 '"Critical,High,Moderate,Low,None"',
                 "Competitive Threat Level")


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 7 — "06 - CHANNEL PARTNERS"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_06(wb: Workbook):
    ws = wb.create_sheet("06 - CHANNEL PARTNERS")

    headers = [
        "#", "Company", "Type", "Revenue (approx)", "Employees", "HQ",
        "Utility Relationships", "Tech Capabilities", "Partnership Angle",
        "Revenue Potential", "Effort to Close", "Priority",
        "Contact Name", "Contact Title", "Contact Email",
        "Website", "Next Action", "Owner", "Notes", "Last Verified"
    ]

    col_widths = {
        1: 5, 2: 26, 3: 22, 4: 14, 5: 10, 6: 20,
        7: 36, 8: 36, 9: 46, 10: 18, 11: 18, 12: 8,
        13: 18, 14: 24, 15: 28, 16: 30, 17: 38, 18: 12,
        19: 42, 20: 12,
    }
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    apply_header_row(ws, 1, headers, bg=HEADER_BG, fg=HEADER_FG, height=28)
    ws.freeze_panes = "B2"

    partners = [
        [1, "Burns & McDonnell", "EPC Firm", "~$7.3B", 14000, "Kansas City MO",
         "Extensive — T&D, substation, transmission; utility-focused",
         "Engineering, procurement, construction; uses drone inspection services",
         "Embed our analytics layer into their drone inspection deliverables — they capture data, we make it intelligent",
         "High — access to their entire utility client base",
         "Moderate — ESOP culture values partners", "T1",
         "", "SVP or VP of T&D", "", "https://www.burnsmcd.com",
         "Research innovation or digital division contact", "",
         "Major ESOP firm; partnership-friendly culture", "2025-Q2"],
        [2, "Quanta Services", "EPC Firm", "$28.48B", 59000, "Houston TX",
         "Largest U.S. utility contractor; nationwide",
         "Construction, maintenance, drone capabilities (Dynamic Systems acquisition 2025)",
         "Proof-of-work documentation and closeout packages for their utility clients",
         "Very High — 59000 field employees generating inspection data",
         "Hard — large public company; procurement complex", "T1",
         "", "VP Digital or Chief Digital Officer", "", "https://www.quantaservices.com",
         "Research Quanta digital/technology division", "",
         "Recent Dynamic Systems acquisition adds drone capability — perfect integration timing", "2025-Q2"],
        [3, "Black & Veatch", "EPC Firm", "~$4.3B", 10000, "Overland Park KS",
         "Strong — T&D planning, grid modernization, utility analytics",
         "Engineering, analytics, consulting; ESOP",
         "Analytics partnership for utility inspection deliverables",
         "High", "Moderate — analytical culture; ESOP", "T1",
         "", "VP of Digital or Innovation", "", "https://www.bv.com",
         "Research innovation or digital division", "",
         "ESOP like Burns & McDonnell — partnership-friendly", "2025-Q2"],
        [4, "HDR Inc.", "Engineering Consultant", "~$3.5B", "87 Apollo entity", "Omaha NE",
         "Broad — utilities, infrastructure, government",
         "Engineering, consulting, GIS",
         "Channel partner for analytics in utility inspection projects",
         "Moderate", "Moderate", "T2",
         "", "", "", "https://www.hdrinc.com",
         "Research utility practice lead", "",
         "ESOP engineering firm", "2025-Q2"],
        [5, "Skydio", "Drone Hardware", "Unknown", "Unknown", "Redwood City CA",
         "PG&E confirmed; expanding utility market",
         "AI-powered drone hardware; BVLOS capable",
         "Integration — Skydio captures; we organize and analyze",
         "High if integrated", "Low — technical integration required", "T1",
         "", "VP of Partnerships or Enterprise", "", "https://www.skydio.com",
         "Research partnerships team", "",
         "Already inside PG&E; technical integration unlocks FPL, Oncor via hardware path", "2025-Q2"],
        [6, "Percepto", "Drone-in-a-Box", "Unknown", 180, "Austin TX",
         "FPL confirmed; expanding utility market",
         "Autonomous drone hardware + AIM software",
         "Integration — Percepto captures; we provide intelligence layer on top of AIM",
         "High if integrated with AIM", "Moderate — they have own software (AIM)", "T2",
         "", "VP of Partnerships", "", "https://percepto.co",
         "Research Percepto partnerships team", "",
         "FPL uses Percepto AIM — integration gives indirect access to FPL inspection data", "2025-Q2"],
    ]

    tier_fills = {"T1": TIER1_FILL, "T2": TIER2_FILL, "T3": TIER3_FILL}
    for i, row_data in enumerate(partners):
        data_row = 2 + i
        tier_val = str(row_data[11])
        bg = tier_fills.get(tier_val, WHITE_FILL)
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=data_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[data_row].height = 65

    add_dropdown(ws, "C", 2, 101,
                 '"EPC Firm,Drone Service Provider,GIS Integrator,Vegetation Management,Engineering Consultant,Inspection Contractor,Software Integrator"',
                 "Type")


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 8 — "07 - COOPERATIVES"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_07(wb: Workbook):
    ws = wb.create_sheet("07 - COOPERATIVES")

    headers = [
        "#", "Cooperative Name", "Type", "Members", "HQ", "States",
        "Revenue (approx)", "Inspection Program", "Procurement Method",
        "Priority", "Contact", "Website", "Next Action", "Notes"
    ]

    col_widths = {
        1: 5, 2: 36, 3: 22, 4: 36, 5: 18, 6: 18,
        7: 14, 8: 22, 9: 30, 10: 8, 11: 16,
        12: 34, 13: 40, 14: 56,
    }
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    # Intro note
    note_text = ("Electric cooperatives represent 900+ distribution cooperatives (NRECA members) serving 42M people across 56% of U.S. land area. "
                 "They buy differently — cooperative purchasing vehicles (OMNIA, Sourcewell, NRECA programs) cover hundreds at once. "
                 "One cooperative vehicle contract = access to the entire membership. START HERE for fastest market entry.")
    ws.merge_cells(f"A1:{get_column_letter(len(headers))}1")
    nc = ws.cell(row=1, column=1, value=note_text)
    nc.fill = make_fill(PARTNER_FILL)
    nc.font = Font(name="Calibri", size=9, bold=True, color="002060")
    nc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    nc.border = thin_border()
    ws.row_dimensions[1].height = 48

    apply_header_row(ws, 2, headers, bg=HEADER_BG, fg=HEADER_FG, height=28)
    ws.freeze_panes = "B3"

    coops = [
        [1, "Dairyland Power Cooperative", "G&T Cooperative",
         "24 distribution co-ops; 600000+ consumers",
         "La Crosse WI", "WI/MN/IA/IL", "~$700M",
         "Unknown — research", "NRECA purchasing + direct", "T2", "",
         "https://www.dairylandpower.com",
         "Research inspection and operations contacts",
         "Midwest G&T; transmission-heavy; good candidate for transmission inspection analytics"],
        [2, "Tri-State Generation and Transmission", "G&T Cooperative",
         "45 member co-ops; 1.5M consumers",
         "Westminster CO", "CO/NE/NM/WY", "~$1.5B",
         "Unknown — research", "NRECA + direct", "T2", "",
         "https://www.tristate.coop",
         "Research operations and grid modernization contacts",
         "Large western G&T; wildfire exposure in CO/NM"],
        [3, "Associated Electric Cooperative (AECI)", "G&T Cooperative",
         "6 regional co-ops; 51 distribution co-ops; 910000 meters",
         "Springfield MO", "MO/IA/KS/NE/OK", "~$1.5B",
         "Unknown — research", "NRECA + direct", "T2", "",
         "https://www.aeci.org",
         "Research grid operations contact",
         "One of the largest G&T cooperatives in the U.S."],
        [4, "Basin Electric Power Cooperative", "G&T Cooperative",
         "130+ member systems; 3M consumers",
         "Bismarck ND", "ND/SD/WY/MT/NE/MN/WI/MI/IA", "~$2B",
         "Unknown — research", "NRECA + direct", "T2", "",
         "https://www.basinelectric.com",
         "Research operations and technology contacts",
         "Large G&T with extensive transmission network; storm exposure (Great Plains)"],
        [5, "Seminole Electric Cooperative", "G&T Cooperative",
         "8 distribution co-ops; 2M+ consumers",
         "Tampa FL", "FL", "~$1B",
         "Unknown — research", "NRECA + direct", "T2", "",
         "https://www.seminole-electric.com",
         "Research operations contact",
         "FL storm exposure; hurricane documentation need"],
        [6, "Old Dominion Electric Cooperative", "G&T Cooperative",
         "11 distribution co-ops; 500000+ consumers",
         "Glen Allen VA", "VA/MD/DE", "~$800M",
         "Unknown — research", "NRECA + direct", "T2", "",
         "https://www.odec.com",
         "Research operations contact",
         "Mid-Atlantic; transmission-heavy"],
        [7, "NRECA (National Rural Electric Cooperative Assoc.)", "Association / Co-op Vehicle",
         "900+ member cooperatives",
         "Arlington VA", "National", "N/A",
         "N/A", "NRECA group purchasing program", "T1", "",
         "https://www.electric.coop",
         "Research NRECA cooperative purchasing program manager",
         "A cooperative vehicle contract with NRECA covers 900+ member co-ops — single most important cooperative procurement path"],
        [8, "Sourcewell (formerly NJPA)", "Cooperative Vehicle",
         "50000+ member agencies",
         "Staples MN", "National", "N/A",
         "N/A", "Competitive solicitation; annual cycles", "T1", "",
         "https://www.sourcewell-mn.gov",
         "Research current technology solicitation cycle and application process",
         "Sourcewell members include hundreds of municipal utilities; single contract covers all"],
        [9, "OMNIA Partners", "Cooperative Vehicle",
         "100000+ members",
         "Franklin TN", "National", "N/A",
         "N/A", "Competitive solicitation", "T1", "",
         "https://www.omniapartners.com",
         "Research technology/software category solicitation",
         "Largest cooperative purchasing organization; utility members + government"],
        [10, "NASPO ValuePoint", "Cooperative Vehicle",
         "All 50 states + territories",
         "Lexington KY", "National", "N/A",
         "N/A", "State-led competitive solicitation", "T1", "",
         "https://www.naspovaluepoint.org",
         "Research technology category master agreements",
         "State-led; strong in western states where many cooperatives and public power utilities operate"],
    ]

    tier_fills = {"T1": TIER1_FILL, "T2": TIER2_FILL}
    for i, row_data in enumerate(coops):
        data_row = 3 + i
        tier_val = str(row_data[9])
        bg = tier_fills.get(tier_val, WHITE_FILL)
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=data_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[data_row].height = 52

    add_dropdown(ws, "C", 3, 102,
                 '"Distribution Co-op,G&T Cooperative,Public Power,Municipal Utility,Joint Action Agency"',
                 "Type")


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 9 — "08 - MARKET INTELLIGENCE"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_08(wb: Workbook):
    ws = wb.create_sheet("08 - MARKET INTELLIGENCE")

    headers = [
        "#", "Date", "Category", "Company/Source", "Signal/Event",
        "Implication", "Recommended Action", "Priority", "Owner",
        "Status", "Source URL", "Date Added"
    ]

    col_widths = {
        1: 5, 2: 10, 3: 22, 4: 22, 5: 56, 6: 48, 7: 48,
        8: 10, 9: 12, 10: 14, 11: 36, 12: 12,
    }
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    apply_header_row(ws, 1, headers, bg=HEADER_BG, fg=HEADER_FG, height=28)
    ws.freeze_panes = "B2"

    intel_data = [
        [1, "2026-01", "Acquisition", "HUVRdata / Technical Toolboxes",
         "HUVRdata acquired by Technical Toolboxes Jan 2026",
         "Validates consolidation thesis in inspection data market; TT has strong utility relationships",
         "Target former HUVRdata utility customers — they may be open to alternatives post-acquisition",
         "High", "", "Research", "", "2026-06"],
        [2, "2025-03", "Funding Event", "Zeitview",
         "Raised $60M Series D Mar 2025; $174M total raised",
         "Most well-funded competitor; will accelerate product development and sales hiring",
         "Accelerate competitive differentiation; identify Zeitview's product gaps",
         "High", "", "Monitor", "", "2026-06"],
        [3, "2025-07", "Acquisition", "Zeitview / Consilience",
         "Zeitview acquired Consilience (AI analytics) Jul 2025",
         "Zeitview is buying AI analytics capability — confirms this is the battleground",
         "Differentiate on data organization and indexing vs. AI defect detection; Zeitview is heavy on detection not indexing",
         "High", "", "Monitor", "", "2026-06"],
        [4, "2023-12", "Distress Signal", "PrecisionHawk",
         "Chapter 7 bankruptcy Dec 2023; $136M+ raised; assets auctioned ~$150k",
         "Largest failure in drone analytics market; major utility customer base now without vendor",
         "PRIORITY: Research which utilities used PrecisionHawk — these are warm prospects",
         "Critical", "", "Research", "", "2026-06"],
        [5, "2025-04", "Distress Signal", "Volatus Aerospace",
         "Restructuring/distress 2025; Sharper Shape dependency",
         "Sharper Shape delivery model at risk; their utility clients may be looking for alternatives",
         "Monitor for Sharper Shape customer churn; position as stable alternative",
         "High", "", "Monitor", "", "2026-06"],
        [6, "2025-04", "Distress Signal", "AgEagle / senseFly",
         "NYSE American below compliance since Apr 2025; delist deadline Oct 2026",
         "Potential asset sale or shutdown; customer relationships may become available",
         "Monitor for asset sale announcement; their drone hardware customers may need new analytics partner",
         "Moderate", "", "Monitor", "", "2026-06"],
        [7, "2025-Q2", "Utility Announcement", "Oncor Electric Delivery",
         "Purchased 2800mi drone imagery + 20000mi LiDAR data Q2 2025; $47.5B capital plan",
         "They are buying data at massive scale — the intelligence layer opportunity is live now",
         "Prioritize Oncor outreach immediately; they have the data and the budget",
         "Critical", "", "Pursue", "", "2026-06"],
        [8, "2025", "Utility Announcement", "Ameren",
         "Publicly stated 'we were finding more data than we could ingest' at industry conference",
         "Best public proof-of-concept statement for our value proposition",
         "Use this quote in sales materials and as direct opener with similar utilities",
         "Critical", "", "Use in sales", "", "2026-06"],
        [9, "2025-Q4", "Technology Launch", "Puget Sound Energy",
         "Heimdall Power DLR sensors deployed Oct 2025",
         "PSE is adding sensor types to their grid monitoring stack — fragmentation is increasing",
         "Pitch PSE as a multi-source data integration customer",
         "Moderate", "", "Nurture", "", "2026-06"],
        [10, "2025-03", "Regulatory Filing", "Pacific Gas & Electric",
         "2026-28 Wildfire Mitigation Plan filed; aerial span inspection pilot included",
         "PG&E is committing to aerial inspection at scale for 2026-28 — active buying signal",
         "Identify PG&E drone program lead and WMP procurement contacts",
         "High", "", "Research", "", "2026-06"],
    ]

    priority_fills = {
        "Critical": COMP_FILL,
        "High": TIER3_FILL,
        "Moderate": TIER2_FILL,
        "Low": ALT_ROW_FILL,
    }
    cat_fills = {
        "Distress Signal": COMP_FILL,
        "Funding Event": PARTNER_FILL,
        "Acquisition": TIER3_FILL,
        "Utility Announcement": TIER1_FILL,
        "Technology Launch": TIER2_FILL,
        "Regulatory Filing": PARTNER_FILL,
    }

    for i, row_data in enumerate(intel_data):
        data_row = 2 + i
        priority_val = str(row_data[7])
        bg = priority_fills.get(priority_val, WHITE_FILL)
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=data_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[data_row].height = 65

    cat_formula = ('"Competitor Move,Funding Event,Acquisition,RFP Published,Utility Announcement,'
                   'Leadership Change,Technology Launch,Storm/Disaster Event,Regulatory Filing,'
                   'Conference Signal,Hiring Signal,Grant Award,Distress Signal"')
    add_dropdown(ws, "C", 2, 201, cat_formula, "Category")
    add_dropdown(ws, "H", 2, 201,
                 '"Critical,High,Moderate,Low"', "Priority")
    add_dropdown(ws, "J", 2, 201,
                 '"Research,Monitor,Pursue,Use in sales,Archive,Done"', "Status")


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 10 — "09 - SCORING MODEL"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_09(wb: Workbook):
    ws = wb.create_sheet("09 - SCORING MODEL")
    ws.sheet_view.showGridLines = False

    col_widths = {1: 28, 2: 10, 3: 26, 4: 26, 5: 26, 6: 26, 7: 26, 8: 44}
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    cur_row = 1

    # Title
    ws.merge_cells(f"A{cur_row}:H{cur_row}")
    t = ws.cell(row=cur_row, column=1, value="FIT SCORE DEFINITIONS AND CALIBRATION")
    t.fill = make_fill(HEADER_BG); t.font = Font(name="Calibri", size=14, bold=True, color=HEADER_FG)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 32
    cur_row += 1

    ws.merge_cells(f"A{cur_row}:H{cur_row}")
    s = ws.cell(row=cur_row, column=1,
                value="Use this sheet to understand how scores are calculated. Update weights quarterly based on win/loss patterns.")
    s.fill = make_fill(SUBTITLE_BG); s.font = Font(name="Calibri", size=10, italic=True, color=HEADER_FG)
    s.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 20
    cur_row += 2

    # ── Signal Definitions ────────────────────────────────────────────────────
    section_header(ws, cur_row, "SCORING SIGNAL DEFINITIONS", 8, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    sig_headers = ["Signal", "Weight", "Score 1 (Low)", "Score 2", "Score 3", "Score 4",
                   "Score 5 (High)", "Scoring Notes"]
    apply_header_row(ws, cur_row, sig_headers, bg=HEADER_BG, fg=HEADER_FG, height=22)
    cur_row += 1

    signals = [
        ("Drone Program Maturity", "15%",
         "No drone program",
         "Pilot/one-off test",
         "Active recurring flights",
         "Expanding program; multiple pilots",
         "Consolidated fleet operation; daily inspections",
         "Higher maturity = more data = more need for analytics layer"),
        ("Data Volume / Pain Signal", "15%",
         "No evidence of data volume issue",
         "Some imagery collected",
         "Active program; data accumulating",
         "Evidence of data management friction",
         "Public statement of data overload (like Ameren quote)",
         "The pain signal is the strongest buy indicator"),
        ("Budget Signal", "15%",
         "No capital plan evidence",
         "Small capital plan (<$500M)",
         "Moderate capital plan ($500M-$2B)",
         "Large capital plan ($2B-$10B)",
         "Massive capital plan (>$10B) or active grid modernization program",
         "Active grid mod spending = inspection budget"),
        ("Active RFP / RFI", "15%",
         "No procurement activity",
         "Watchlist only",
         "RFI issued",
         "RFP issued",
         "RFP with inspection/drone analytics scope",
         "Active procurement = immediate revenue opportunity"),
        ("Technology Fit", "10%",
         "Single-vendor closed system",
         "Proprietary stack; limited integration",
         "Mixed vendors; some API capability",
         "Multi-vendor + GIS + asset management system",
         "Multi-vendor fragmented stack + stated analytics need",
         "More fragmentation = more need for unifying layer"),
        ("Urgency Driver", "10%",
         "No urgency",
         "Mild (routine grid work)",
         "Moderate (grid modernization)",
         "High (wildfire/storm exposure; regulatory deadline)",
         "Critical (active wildfire litigation; FEMA reimbursement need; compliance deadline)",
         "Litigation and FEMA needs create immediate urgency"),
        ("Ease of Entry", "10%",
         "No contact path",
         "Cold outreach only",
         "Industry connection available",
         "Warm intro possible",
         "Direct relationship or existing vendor relationship",
         "Partner relationships dramatically improve ease of entry"),
        ("Revenue Potential", "5%",
         "<100K customers",
         "100K-500K customers",
         "500K-1M customers",
         "1M-3M customers",
         ">3M customers or major EPC/channel with 10+ utility clients",
         "Proxy for inspection program scale and budget size"),
        ("Competitive Exposure", "5%",
         "Competitor firmly entrenched",
         "Competitor likely present",
         "Unknown vendor status",
         "Competitor present but dissatisfied signals",
         "No competitor; open field",
         "Lower competitive exposure = easier to win"),
        ("Partner Potential (bonus)", "Bonus",
         "No partner value",
         "Possible future partner",
         "Moderate partner opportunity",
         "Strong channel potential (5+ utility clients)",
         "Dominant channel (50+ utility clients or cooperative vehicle)",
         "Partners multiply revenue without direct sales cost"),
    ]

    for i, row_data in enumerate(signals):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top",
                                       horizontal="center" if col_idx == 2 else "left")
            cell.border = thin_border()
        ws.row_dimensions[cur_row].height = 62
        cur_row += 1
    cur_row += 1

    # ── Score Interpretation ──────────────────────────────────────────────────
    section_header(ws, cur_row, "SCORE INTERPRETATION", 8, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    interp = [
        ("90-100",    TIER1_FILL,  "Tier 1 — Active pursuit; outreach within 7 days"),
        ("75-89",     TIER1_FILL,  "Tier 1/2 boundary — Strong opportunity; qualify within 30 days"),
        ("60-74",     TIER2_FILL,  "Tier 2 — High fit; quarterly nurture; watch for triggers"),
        ("40-59",     TIER3_FILL,  "Tier 2/3 — Marginal fit or low urgency; watch list"),
        ("Below 40",  SECTION_FILL,"Tier 3-7 — Low priority; archive or competitive intel only"),
    ]
    for score_range, fill_hex, meaning in interp:
        c1 = ws.cell(row=cur_row, column=1, value=score_range)
        c1.fill = make_fill(fill_hex); c1.font = body_font(9, bold=True)
        c1.alignment = Alignment(vertical="center", horizontal="center")
        c1.border = thin_border()
        ws.merge_cells(f"B{cur_row}:H{cur_row}")
        c2 = ws.cell(row=cur_row, column=2, value=meaning)
        c2.fill = make_fill(fill_hex); c2.font = body_font(9)
        c2.alignment = Alignment(vertical="center", wrap_text=True)
        c2.border = thin_border()
        ws.row_dimensions[cur_row].height = 18
        cur_row += 1
    cur_row += 1

    # ── Calibration Log ───────────────────────────────────────────────────────
    section_header(ws, cur_row, "CALIBRATION LOG — Update Quarterly Based on Win/Loss Data",
                   8, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    cal_headers = ["Date", "Change Made", "Reason", "Win/Loss Data Driving Change",
                   "", "", "", ""]
    apply_header_row(ws, cur_row, cal_headers, bg=HEADER_BG, fg=HEADER_FG, height=20)
    cur_row += 1
    blank_data_rows(ws, cur_row, 10, 8)
    cur_row += 11

    # ── RFP Opportunity Score ─────────────────────────────────────────────────
    section_header(ws, cur_row,
                   "RFP OPPORTUNITY SCORE — Score each dimension 1-5, max 25",
                   8, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    rfp_score_headers = ["Dimension", "Score (1-5)", "Score 1", "Score 2", "Score 3",
                         "Score 4", "Score 5", "Notes"]
    apply_header_row(ws, cur_row, rfp_score_headers, bg=HEADER_BG, fg=HEADER_FG, height=20)
    cur_row += 1
    rfp_dims = [
        ("Technical Fit", "",
         "No match", "Partial match", "Good match", "Strong match", "Perfect scope match",
         "Does the scope match what you do exactly?"),
        ("Competitive Position", "",
         "Entrenched incumbent", "Heavily competed", "Competitive field", "Light competition", "Open field",
         "Are you differentiated vs. likely bidders?"),
        ("Relationship Access", "",
         "No contacts", "Cold only", "Industry connection", "Warm intro path", "Direct relationship",
         "Do you know anyone at the issuing organization?"),
        ("Revenue Size", "",
         "<$50K", "$50K-$250K", "$250K-$1M", "$1M-$5M", ">$5M or multi-year",
         "Is the contract worth the bid investment?"),
        ("Win Probability", "",
         "<10%", "10-25%", "25-50%", "50-75%", ">75%",
         "Realistic chance given timeline, incumbents, requirements?"),
    ]
    for i, row_data in enumerate(rfp_dims):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[cur_row].height = 40
        cur_row += 1
    cur_row += 1

    # Decision guide
    decision = [
        ("Score ≥ 18", TIER1_FILL,  "Pursue aggressively"),
        ("Score 12-17", TIER2_FILL, "Qualify further before committing"),
        ("Score < 12",  SECTION_FILL,"Skip unless strategically important"),
    ]
    for score_range, fill_hex, guidance in decision:
        c1 = ws.cell(row=cur_row, column=1, value=score_range)
        c1.fill = make_fill(fill_hex); c1.font = body_font(9, bold=True)
        c1.alignment = Alignment(vertical="center", horizontal="center")
        c1.border = thin_border()
        ws.merge_cells(f"B{cur_row}:H{cur_row}")
        c2 = ws.cell(row=cur_row, column=2, value=guidance)
        c2.fill = make_fill(fill_hex); c2.font = body_font(9)
        c2.alignment = Alignment(vertical="center")
        c2.border = thin_border()
        ws.row_dimensions[cur_row].height = 16
        cur_row += 1


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 11 — "10 - DATA SOURCES"
# ─────────────────────────────────────────────────────────────────────────────

def build_sheet_10(wb: Workbook):
    ws = wb.create_sheet("10 - DATA SOURCES")
    ws.sheet_view.showGridLines = False

    col_widths = {1: 36, 2: 56, 3: 56, 4: 14, 5: 28, 6: 14}
    for c, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c)].width = w

    cur_row = 1

    # Title
    ws.merge_cells(f"A{cur_row}:F{cur_row}")
    t = ws.cell(row=cur_row, column=1, value="MONITORING FEEDS AND RESEARCH SOURCES")
    t.fill = make_fill(HEADER_BG); t.font = Font(name="Calibri", size=14, bold=True, color=HEADER_FG)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 32
    cur_row += 1

    ws.merge_cells(f"A{cur_row}:F{cur_row}")
    s = ws.cell(row=cur_row, column=1,
                value=("Set up these alerts and check these sources on the schedule shown. "
                       "Last column = date last checked."))
    s.fill = make_fill(SUBTITLE_BG); s.font = Font(name="Calibri", size=10, italic=True, color=HEADER_FG)
    s.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[cur_row].height = 20
    cur_row += 2

    # ── RFP and Procurement Sources ───────────────────────────────────────────
    section_header(ws, cur_row, "RFP AND PROCUREMENT SOURCES", 6, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    proc_headers = ["Source", "URL", "Search Terms / NAICS", "Check Frequency",
                    "Alert Setup", "Last Checked"]
    apply_header_row(ws, cur_row, proc_headers, bg=HEADER_BG, fg=HEADER_FG, height=22)
    cur_row += 1

    procurement_sources = [
        ("SAM.gov (Federal)",
         "https://sam.gov",
         "NAICS: 541360 541519 237130 238210; Keywords: drone inspection aerial inspection UAS vegetation management asset inspection",
         "Weekly", "Set up email alerts for each NAICS code", ""),
        ("State of Texas SmartBuy",
         "https://www.txsmartbuy.gov",
         "drone inspection utility inspection aerial inspection",
         "Weekly", "RSS or email alert", ""),
        ("California eProcure",
         "https://caleprocure.ca.gov",
         "drone inspection wildfire inspection aerial inspection utility",
         "Weekly", "Email alert", ""),
        ("Florida MyFloridaMarketPlace",
         "https://vendor.myfloridamarketplace.com",
         "drone inspection utility inspection aerial",
         "Weekly", "Email alert", ""),
        ("Georgia Procurement Registry",
         "https://ssl.doas.state.ga.us/PRSapp",
         "drone inspection utility aerial inspection",
         "Weekly", "Email alert", ""),
        ("Washington WEBS",
         "https://pr-webs-vendor.des.wa.gov",
         "drone inspection utility aerial",
         "Weekly", "Email alert", ""),
        ("BidNet Direct",
         "https://www.bidnetdirect.com",
         "drone inspection utility inspection",
         "Weekly", "Email alert subscription", ""),
        ("DemandStar",
         "https://network.demandstar.com",
         "drone inspection utility inspection aerial",
         "Weekly", "Email alert", ""),
        ("Periscope Holdings / IonWave",
         "https://www.ionwave.net",
         "drone inspection utility inspection",
         "Weekly", "Email alert", ""),
        ("OMNIA Partners",
         "https://www.omniapartners.com",
         "Technology software inspection analytics",
         "Monthly", "Check solicitation calendar", ""),
        ("Sourcewell",
         "https://www.sourcewell-mn.gov",
         "Technology software inspection",
         "Monthly", "Check solicitation calendar", ""),
        ("NASPO ValuePoint",
         "https://www.naspovaluepoint.org",
         "Technology software analytics",
         "Monthly", "Check master agreement calendar", ""),
        ("NRECA Purchasing",
         "https://www.electric.coop",
         "Inspection analytics software",
         "Monthly", "Contact NRECA purchasing", ""),
        ("DOE GRIP Portal",
         "https://www.energy.gov/gdo/grid-resilience-and-innovation-partnerships-grip-program",
         "Grid resilience inspection analytics",
         "Monthly", "Check grant round calendar", ""),
        ("FEMA BRIC Portal",
         "https://www.fema.gov/grants/mitigation/building-resilient-infrastructure-communities",
         "Infrastructure documentation storm resilience",
         "Monthly", "Check grant cycle calendar", ""),
        ("FERC eLibrary",
         "https://elibrary.ferc.gov",
         "Inspection capital plan transmission",
         "Monthly", "RSS feed for utility docket filings", ""),
    ]

    for i, row_data in enumerate(procurement_sources):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[cur_row].height = 38
        cur_row += 1
    cur_row += 1

    # ── Intelligence and News Sources ─────────────────────────────────────────
    section_header(ws, cur_row, "INTELLIGENCE AND NEWS SOURCES", 6, bg=SECTION_FILL, font_size=11)
    cur_row += 1
    intel_headers = ["Source", "URL", "What to Watch", "Check Frequency",
                     "Alert Setup", "Last Checked"]
    apply_header_row(ws, cur_row, intel_headers, bg=HEADER_BG, fg=HEADER_FG, height=22)
    cur_row += 1

    intel_sources = [
        ("Google Alerts — Competitors",
         "https://alerts.google.com",
         "Zeitview Optelos Sharper Shape Cyberhawk HUVRdata drone inspection analytics",
         "Daily", "Set up one alert per competitor", ""),
        ("Google Alerts — Target Utilities",
         "https://alerts.google.com",
         "Oncor PG&E FPL Ameren Georgia Power + drone OR inspection OR RFP",
         "Weekly", "Set up per Tier 1 utility", ""),
        ("Utility Dive",
         "https://www.utilitydive.com",
         "Grid modernization drone inspection vegetation management asset management",
         "Weekly", "Email newsletter", ""),
        ("T&D World",
         "https://www.tdworld.com",
         "Drone inspection transmission distribution utility technology",
         "Weekly", "Email newsletter", ""),
        ("Electric Light & Power",
         "https://www.elp.com",
         "Utility technology inspection drone",
         "Weekly", "Email newsletter", ""),
        ("Crunchbase",
         "https://www.crunchbase.com",
         "Funding rounds for: Zeitview Optelos Sharper Shape Raptor Maps Percepto",
         "Monthly", "Set up company alerts", ""),
        ("LinkedIn Job Posts",
         "https://www.linkedin.com/jobs",
         "UAS operator drone program manager inspection data analyst GIS analyst at target utilities",
         "Weekly", "Sales Navigator alerts", ""),
        ("DistribuTECH Conference",
         "https://www.distributech.com",
         "Exhibitor list attendee agenda drone inspection analytics",
         "Annual (Jan)", "Register; review exhibitor list before show", ""),
        ("IEEE T&D Conference",
         "https://ieee-td.org",
         "Drone inspection paper presentations utility technology",
         "Annual", "Review program for target utility names", ""),
        ("FEMA Disaster Declarations",
         "https://www.fema.gov/disaster/declarations",
         "Major disaster declarations in utility service territories",
         "Weekly", "RSS feed", ""),
        ("NIFC Fire Season Outlook",
         "https://www.nifc.gov",
         "Western fire season outlook; states with high risk utilities",
         "Monthly (Mar-Oct)", "Check monthly during fire season", ""),
    ]

    for i, row_data in enumerate(intel_sources):
        bg = ALT_ROW_FILL if i % 2 else WHITE_FILL
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.fill = make_fill(bg); cell.font = body_font(9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border()
        ws.row_dimensions[cur_row].height = 38
        cur_row += 1


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    wb = Workbook()

    print("Building Sheet 00 — START HERE...")
    build_sheet_00(wb)

    print("Building Sheet 01 — EXEC DASHBOARD...")
    build_sheet_01(wb)

    print("Building Sheet 02 — TOP ACCOUNTS...")
    build_sheet_02(wb)

    print("Building Sheet 03 — RFP + RFI TRACKER...")
    build_sheet_03(wb)

    print("Building Sheet 04 — CONTACTS...")
    build_sheet_04(wb)

    print("Building Sheet 05 — INSPECTION VENDORS...")
    build_sheet_05(wb)

    print("Building Sheet 06 — CHANNEL PARTNERS...")
    build_sheet_06(wb)

    print("Building Sheet 07 — COOPERATIVES...")
    build_sheet_07(wb)

    print("Building Sheet 08 — MARKET INTELLIGENCE...")
    build_sheet_08(wb)

    print("Building Sheet 09 — SCORING MODEL...")
    build_sheet_09(wb)

    print("Building Sheet 10 — DATA SOURCES...")
    build_sheet_10(wb)

    # Set first sheet as active
    wb.active = wb["00 - START HERE"]

    output_path = "/home/user/sales/Utility_Inspection_Intelligence_Command_Center.xlsx"
    wb.save(output_path)
    print(f"\nWorkbook saved: {output_path}")
    print(f"Sheets: {[ws.title for ws in wb.worksheets]}")


if __name__ == "__main__":
    main()
