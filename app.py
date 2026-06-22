import streamlit as st
import openai
import os
import json
import tempfile
import io
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Audio Intelligence Analyzer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: #0f1117; }

  .hero-banner {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #2d3561;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
  }
  .hero-banner h1 { color: #e2e8f0; font-size: 2rem; font-weight: 700; margin: 0 0 .5rem; }
  .hero-banner p  { color: #94a3b8; margin: 0; font-size: 1rem; }

  .section-card {
    background: #1e2330;
    border: 1px solid #2d3561;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: border-color .2s;
  }
  .section-card:hover { border-color: #4f63d2; }

  .section-title {
    color: #818cf8;
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin-bottom: .75rem;
  }

  .metric-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
  .metric-box {
    background: #0f1117;
    border: 1px solid #2d3561;
    border-radius: 10px;
    padding: .75rem 1.25rem;
    flex: 1;
    min-width: 120px;
    text-align: center;
  }
  .metric-box .label { color: #64748b; font-size: .7rem; text-transform: uppercase; letter-spacing: .08em; }
  .metric-box .value { color: #e2e8f0; font-size: 1.4rem; font-weight: 700; margin-top: .25rem; }

  .score-bar-wrap { margin: .4rem 0; }
  .score-label { color: #94a3b8; font-size: .82rem; margin-bottom: .2rem; display: flex; justify-content: space-between; }
  .score-bar-bg { background: #2d3561; border-radius: 99px; height: 8px; }
  .score-bar-fill { border-radius: 99px; height: 8px; transition: width .6s ease; }

  .risk-high   { color: #f87171; }
  .risk-medium { color: #fb923c; }
  .risk-low    { color: #4ade80; }

  .tag {
    display: inline-block;
    padding: .2rem .65rem;
    border-radius: 99px;
    font-size: .72rem;
    font-weight: 600;
    margin: .2rem .15rem;
  }
  .tag-red    { background: rgba(248,113,113,.15); color: #f87171; border: 1px solid rgba(248,113,113,.3); }
  .tag-amber  { background: rgba(251,146,60,.15);  color: #fb923c; border: 1px solid rgba(251,146,60,.3); }
  .tag-green  { background: rgba(74,222,128,.15);  color: #4ade80; border: 1px solid rgba(74,222,128,.3); }
  .tag-blue   { background: rgba(129,140,248,.15); color: #818cf8; border: 1px solid rgba(129,140,248,.3); }

  .transcript-box {
    background: #0f1117;
    border: 1px solid #2d3561;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: #cbd5e1;
    font-size: .88rem;
    line-height: 1.7;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
  }

  .copy-btn {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    background: #4f63d2;
    color: white;
    border: none;
    border-radius: 8px;
    padding: .5rem 1.1rem;
    font-size: .82rem;
    font-weight: 600;
    cursor: pointer;
    transition: background .2s;
  }
  .copy-btn:hover { background: #4051b5; }

  .stButton > button {
    background: linear-gradient(135deg, #4f63d2, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    transition: opacity .2s !important;
  }
  .stButton > button:hover { opacity: .88 !important; }

  .stFileUploader > div { border: 2px dashed #2d3561 !important; border-radius: 12px !important; background: #1a1f2e !important; }

  div[data-testid="stSidebar"] { background: #141824 !important; border-right: 1px solid #2d3561; }
  div[data-testid="stSidebar"] .stMarkdown h3 { color: #818cf8; }

  .stSpinner > div { border-top-color: #818cf8 !important; }

  .alert-box {
    border-radius: 10px;
    padding: .85rem 1.1rem;
    margin-bottom: 1rem;
    font-size: .85rem;
  }
  .alert-info    { background: rgba(129,140,248,.1); border: 1px solid rgba(129,140,248,.3); color: #a5b4fc; }
  .alert-success { background: rgba(74,222,128,.1);  border: 1px solid rgba(74,222,128,.3);  color: #86efac; }
  .alert-warning { background: rgba(251,146,60,.1);  border: 1px solid rgba(251,146,60,.3);  color: #fdba74; }
  .alert-danger  { background: rgba(248,113,113,.1); border: 1px solid rgba(248,113,113,.3); color: #fca5a5; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
SUPPORTED_FORMATS = [".m4a", ".mp3", ".wav", ".mp4"]
MAX_FILE_MB = 25

ANALYSIS_SYSTEM_PROMPT = """You are an expert linguistic analyst specializing in audio transcript analysis.
Your job is to deeply analyze a transcript and return a structured JSON report.

Always return ONLY valid JSON with this exact schema (no markdown fences, no extra text):

{
  "transcript_confidence_summary": {
    "overall_confidence": <float 0-1>,
    "clarity_rating": "<Excellent|Good|Fair|Poor>",
    "noise_level": "<Low|Moderate|High>",
    "speaker_count_estimate": <int>,
    "language_detected": "<language name>",
    "notes": "<brief notes on audio quality>"
  },
  "audio_risk_report": {
    "overall_risk_level": "<Low|Medium|High|Critical>",
    "risk_score": <float 0-1>,
    "flags": [
      {"flag": "<flag name>", "severity": "<Low|Medium|High>", "detail": "<explanation>"}
    ],
    "summary": "<paragraph summary of risks>"
  },
  "original_transcript": "<verbatim transcript text>",
  "literal_english_translation": "<word-for-word translation preserving original structure>",
  "natural_english_meaning": "<fluent, natural English rendering of the content>",
  "contextual_meaning": "<what the speaker likely means in context, including subtext>",
  "emotional_relationship_analysis": {
    "primary_emotion": "<dominant emotion>",
    "secondary_emotions": ["<emotion1>", "<emotion2>"],
    "tone": "<formal|informal|hostile|warm|neutral|distressed|etc>",
    "relationship_dynamic": "<description of the apparent relationship>",
    "power_dynamic": "<balanced|dominant speaker A|dominant speaker B|unclear>",
    "analysis": "<detailed paragraph>"
  },
  "important_relationship_signals": [
    {"signal": "<signal name>", "evidence": "<quote or observation>", "implication": "<what it suggests>"}
  ],
  "verification_required": [
    {"item": "<thing to verify>", "reason": "<why verification is needed>", "priority": "<High|Medium|Low>"}
  ],
  "confidence_scores": {
    "transcription_accuracy": <float 0-1>,
    "translation_accuracy": <float 0-1>,
    "emotional_analysis": <float 0-1>,
    "contextual_interpretation": <float 0-1>,
    "overall_reliability": <float 0-1>
  }
}"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_client() -> openai.OpenAI:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        st.error("OPENAI_API_KEY not set. Add it to your .env file or environment.")
        st.stop()
    return openai.OpenAI(api_key=key)


def transcribe_audio(client: openai.OpenAI, file_bytes: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=(filename, f, _mime(suffix)),
                response_format="text",
            )
        return str(response)
    finally:
        os.unlink(tmp_path)


def _mime(suffix: str) -> str:
    return {
        ".m4a": "audio/mp4",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".mp4": "video/mp4",
    }.get(suffix, "audio/mpeg")


def analyze_transcript(client: openai.OpenAI, transcript: str, context: str = "") -> dict:
    user_content = f"Transcript:\n{transcript}"
    if context.strip():
        user_content = f"Additional context from user:\n{context}\n\n{user_content}"

    response = client.chat.completions.create(
        model="gpt-4.5-preview",
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    raw = response.choices[0].message.content.strip()
    # strip markdown code fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw)


def pct(val: float) -> str:
    return f"{int(round(val * 100))}%"


def score_color(val: float) -> str:
    if val >= 0.8:
        return "#4ade80"
    if val >= 0.6:
        return "#facc15"
    if val >= 0.4:
        return "#fb923c"
    return "#f87171"


def risk_class(level: str) -> str:
    return {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high", "Critical": "risk-high"}.get(level, "")


def severity_tag(sev: str) -> str:
    cls = {"Low": "tag-green", "Medium": "tag-amber", "High": "tag-red"}.get(sev, "tag-blue")
    return f'<span class="tag {cls}">{sev}</span>'


def priority_tag(p: str) -> str:
    cls = {"Low": "tag-green", "Medium": "tag-amber", "High": "tag-red"}.get(p, "tag-blue")
    return f'<span class="tag {cls}">{p}</span>'


def score_bar(label: str, val: float) -> str:
    color = score_color(val)
    width = int(val * 100)
    return f"""
    <div class="score-bar-wrap">
      <div class="score-label"><span>{label}</span><span style="color:{color};font-weight:600">{pct(val)}</span></div>
      <div class="score-bar-bg"><div class="score-bar-fill" style="width:{width}%;background:{color}"></div></div>
    </div>"""


# ── Export helpers ─────────────────────────────────────────────────────────────

def build_markdown_report(data: dict, filename: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    tcs = data.get("transcript_confidence_summary", {})
    arr = data.get("audio_risk_report", {})
    cs  = data.get("confidence_scores", {})
    era = data.get("emotional_relationship_analysis", {})

    lines = [
        f"# Audio Intelligence Report",
        f"**File:** {filename}  |  **Generated:** {ts}",
        "",
        "---",
        "",
        "## Transcript Confidence Summary",
        f"- **Overall Confidence:** {pct(tcs.get('overall_confidence', 0))}",
        f"- **Clarity:** {tcs.get('clarity_rating', '—')}",
        f"- **Noise Level:** {tcs.get('noise_level', '—')}",
        f"- **Speakers Estimated:** {tcs.get('speaker_count_estimate', '—')}",
        f"- **Language Detected:** {tcs.get('language_detected', '—')}",
        f"- **Notes:** {tcs.get('notes', '—')}",
        "",
        "## Audio Risk Report",
        f"**Risk Level:** {arr.get('overall_risk_level', '—')}  |  **Risk Score:** {pct(arr.get('risk_score', 0))}",
        "",
        arr.get("summary", ""),
        "",
        "### Risk Flags",
    ]
    for flag in arr.get("flags", []):
        lines.append(f"- **[{flag.get('severity')}]** {flag.get('flag')}: {flag.get('detail')}")
    lines += [
        "",
        "## Original Transcript",
        data.get("original_transcript", ""),
        "",
        "## Literal English Translation",
        data.get("literal_english_translation", ""),
        "",
        "## Natural English Meaning",
        data.get("natural_english_meaning", ""),
        "",
        "## Contextual Meaning",
        data.get("contextual_meaning", ""),
        "",
        "## Emotional / Relationship Analysis",
        f"- **Primary Emotion:** {era.get('primary_emotion', '—')}",
        f"- **Secondary Emotions:** {', '.join(era.get('secondary_emotions', []))}",
        f"- **Tone:** {era.get('tone', '—')}",
        f"- **Relationship Dynamic:** {era.get('relationship_dynamic', '—')}",
        f"- **Power Dynamic:** {era.get('power_dynamic', '—')}",
        "",
        era.get("analysis", ""),
        "",
        "## Important Relationship Signals",
    ]
    for sig in data.get("important_relationship_signals", []):
        lines.append(f"- **{sig.get('signal')}**: {sig.get('evidence')} → _{sig.get('implication')}_")
    lines += [
        "",
        "## Verification Required",
    ]
    for v in data.get("verification_required", []):
        lines.append(f"- **[{v.get('priority')}]** {v.get('item')}: {v.get('reason')}")
    lines += [
        "",
        "## Confidence Scores",
        f"| Dimension | Score |",
        f"|-----------|-------|",
    ]
    score_labels = {
        "transcription_accuracy": "Transcription Accuracy",
        "translation_accuracy": "Translation Accuracy",
        "emotional_analysis": "Emotional Analysis",
        "contextual_interpretation": "Contextual Interpretation",
        "overall_reliability": "Overall Reliability",
    }
    for key, label in score_labels.items():
        lines.append(f"| {label} | {pct(cs.get(key, 0))} |")
    return "\n".join(lines)


def build_pdf_bytes(markdown_text: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib.enums import TA_LEFT
        import re

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        )

        styles = getSampleStyleSheet()
        BG = colors.HexColor("#0f1117")
        FG = colors.HexColor("#e2e8f0")
        ACC = colors.HexColor("#818cf8")
        MUT = colors.HexColor("#94a3b8")

        h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=ACC, fontSize=18, spaceAfter=6)
        h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=ACC, fontSize=13, spaceBefore=14, spaceAfter=4)
        body = ParagraphStyle("Body", parent=styles["Normal"], textColor=FG, fontSize=9, leading=14)
        meta = ParagraphStyle("Meta", parent=styles["Normal"], textColor=MUT, fontSize=8, leading=12)
        bullet = ParagraphStyle("Bullet", parent=styles["Normal"], textColor=FG, fontSize=9, leading=14, leftIndent=12)

        story = []
        for line in markdown_text.split("\n"):
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 6))
            elif stripped.startswith("# "):
                story.append(Paragraph(stripped[2:], h1))
            elif stripped.startswith("## "):
                story.append(HRFlowable(width="100%", thickness=0.5, color=ACC, spaceAfter=4))
                story.append(Paragraph(stripped[3:], h2))
            elif stripped.startswith("### "):
                story.append(Paragraph(f"<b>{stripped[4:]}</b>", body))
            elif stripped.startswith("- "):
                txt = stripped[2:].replace("**", "<b>", 1).replace("**", "</b>", 1).replace("_", "<i>", 1).replace("_", "</i>", 1)
                story.append(Paragraph(f"• {txt}", bullet))
            elif stripped.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=0.5, color=MUT, spaceAfter=4))
            elif stripped.startswith("|"):
                pass  # skip markdown tables in PDF (scores already in bars)
            else:
                txt = stripped.replace("**", "<b>", 1).replace("**", "</b>", 1)
                story.append(Paragraph(txt, body if not stripped.startswith("**") else meta))

        doc.build(story)
        return buf.getvalue()
    except ImportError:
        return None


# ── Sidebar ────────────────────────────────────────────────────────────────────

def sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        api_key = st.text_input("OpenAI API Key", type="password",
                                value=os.getenv("OPENAI_API_KEY", ""),
                                placeholder="sk-…",
                                help="Overrides OPENAI_API_KEY env var for this session")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        st.markdown("---")
        st.markdown("### 📋 Context")
        context = st.text_area("Optional context for analysis",
                               placeholder="e.g. 'This is a phone call between a debt collector and a customer in Spanish'",
                               height=120)

        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("""
**Audio Intelligence Analyzer**

Transcribes audio with `gpt-4o-transcribe` and performs deep linguistic, emotional, and risk analysis with GPT.

Supported formats: `.m4a` `.mp3` `.wav` `.mp4`

Max file size: **25 MB**
        """)
    return context


# ── Result panels ──────────────────────────────────────────────────────────────

def render_confidence_summary(tcs: dict):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Transcript Confidence Summary</div>', unsafe_allow_html=True)

    conf = tcs.get("overall_confidence", 0)
    color = score_color(conf)

    cols = st.columns(4)
    metrics = [
        ("Confidence", pct(conf)),
        ("Clarity", tcs.get("clarity_rating", "—")),
        ("Noise Level", tcs.get("noise_level", "—")),
        ("Speakers", str(tcs.get("speaker_count_estimate", "—"))),
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-box">
              <div class="label">{label}</div>
              <div class="value" style="color:{color if label=='Confidence' else '#e2e8f0'}">{value}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:.75rem">
      <span class="tag tag-blue">🌐 {tcs.get('language_detected','Unknown')}</span>
    </div>
    <p style="color:#94a3b8;font-size:.85rem;margin-top:.75rem">{tcs.get('notes','')}</p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_risk_report(arr: dict):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚠️ Audio Risk Report</div>', unsafe_allow_html=True)

    level = arr.get("overall_risk_level", "Low")
    score = arr.get("risk_score", 0)
    rc = risk_class(level)

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
      <div style="font-size:2rem;font-weight:700" class="{rc}">{level}</div>
      <div style="color:#94a3b8;font-size:.85rem">Risk Score: <b style="color:#e2e8f0">{pct(score)}</b></div>
    </div>
    <p style="color:#94a3b8;font-size:.85rem;margin-bottom:1rem">{arr.get('summary','')}</p>
    """, unsafe_allow_html=True)

    for flag in arr.get("flags", []):
        st.markdown(f"""
        <div style="background:#0f1117;border:1px solid #2d3561;border-radius:8px;padding:.6rem 1rem;margin:.4rem 0">
          {severity_tag(flag.get('severity',''))}
          <span style="color:#e2e8f0;font-weight:600;margin-left:.5rem">{flag.get('flag','')}</span>
          <div style="color:#94a3b8;font-size:.8rem;margin-top:.3rem">{flag.get('detail','')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_transcript_section(title: str, icon: str, content: str, key: str):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{icon} {title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="transcript-box">{content}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_emotional_analysis(era: dict):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💭 Emotional / Relationship Analysis</div>', unsafe_allow_html=True)

    primary = era.get("primary_emotion", "—")
    secondary = era.get("secondary_emotions", [])
    tone = era.get("tone", "—")
    power = era.get("power_dynamic", "—")

    tags = f'<span class="tag tag-blue">{primary}</span>'
    for e in secondary:
        tags += f' <span class="tag tag-amber">{e}</span>'

    st.markdown(f"""
    <div style="margin-bottom:1rem">{tags}</div>
    <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-bottom:1rem">
      <div><span style="color:#64748b;font-size:.75rem">TONE</span><br><span style="color:#e2e8f0;font-weight:600">{tone}</span></div>
      <div><span style="color:#64748b;font-size:.75rem">RELATIONSHIP</span><br><span style="color:#e2e8f0;font-weight:600">{era.get('relationship_dynamic','—')}</span></div>
      <div><span style="color:#64748b;font-size:.75rem">POWER DYNAMIC</span><br><span style="color:#e2e8f0;font-weight:600">{power}</span></div>
    </div>
    <p style="color:#94a3b8;font-size:.85rem;line-height:1.7">{era.get('analysis','')}</p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_signals(signals: list):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 Important Relationship Signals</div>', unsafe_allow_html=True)
    for sig in signals:
        st.markdown(f"""
        <div style="background:#0f1117;border:1px solid #2d3561;border-radius:8px;padding:.75rem 1rem;margin:.5rem 0">
          <div style="color:#818cf8;font-weight:600;font-size:.88rem">{sig.get('signal','')}</div>
          <div style="color:#94a3b8;font-size:.8rem;margin:.3rem 0"><i>"{sig.get('evidence','')}"</i></div>
          <div style="color:#e2e8f0;font-size:.82rem">→ {sig.get('implication','')}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_verification(items: list):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✅ Verification Required</div>', unsafe_allow_html=True)
    for v in items:
        st.markdown(f"""
        <div style="background:#0f1117;border:1px solid #2d3561;border-radius:8px;padding:.75rem 1rem;margin:.5rem 0">
          <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem">
            {priority_tag(v.get('priority',''))}
            <span style="color:#e2e8f0;font-weight:600;font-size:.88rem">{v.get('item','')}</span>
          </div>
          <div style="color:#94a3b8;font-size:.8rem">{v.get('reason','')}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_confidence_scores(cs: dict):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Confidence Scores</div>', unsafe_allow_html=True)
    labels = {
        "transcription_accuracy": "Transcription Accuracy",
        "translation_accuracy": "Translation Accuracy",
        "emotional_analysis": "Emotional Analysis",
        "contextual_interpretation": "Contextual Interpretation",
        "overall_reliability": "Overall Reliability",
    }
    bars = "".join(score_bar(label, cs.get(key, 0)) for key, label in labels.items())
    st.markdown(bars, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    context = sidebar()

    st.markdown("""
    <div class="hero-banner">
      <h1>🎙️ Audio Intelligence Analyzer</h1>
      <p>Transcribe, translate, and deeply analyze audio recordings using GPT-4o and GPT-4.5</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your audio file here",
        type=["m4a", "mp3", "wav", "mp4"],
        help="Max 25 MB. Supported: .m4a, .mp3, .wav, .mp4",
    )

    if uploaded is None:
        st.markdown("""
        <div class="alert-box alert-info">
          Upload an audio file above to begin analysis. The app will transcribe it and generate a full intelligence report.
        </div>
        """, unsafe_allow_html=True)
        return

    file_bytes = uploaded.read()
    file_mb = len(file_bytes) / (1024 * 1024)

    if file_mb > MAX_FILE_MB:
        st.markdown(f'<div class="alert-box alert-danger">File too large ({file_mb:.1f} MB). Maximum is {MAX_FILE_MB} MB.</div>', unsafe_allow_html=True)
        return

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'<div style="color:#94a3b8;font-size:.85rem;padding:.5rem 0">📎 <b style="color:#e2e8f0">{uploaded.name}</b> — {file_mb:.2f} MB</div>', unsafe_allow_html=True)
    with col2:
        run = st.button("🔍 Analyze Audio", use_container_width=True)
    with col3:
        if "last_result" in st.session_state and st.session_state.last_result:
            st.button("🗑️ Clear Results", on_click=lambda: st.session_state.pop("last_result", None), use_container_width=True)

    if not run and "last_result" not in st.session_state:
        return

    if run:
        client = get_client()

        with st.spinner("Step 1/2 — Transcribing audio with gpt-4o-transcribe…"):
            try:
                transcript = transcribe_audio(client, file_bytes, uploaded.name)
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                return

        with st.spinner("Step 2/2 — Analyzing transcript with GPT-4.5…"):
            try:
                result = analyze_transcript(client, transcript, context)
                result["_filename"] = uploaded.name
                st.session_state["last_result"] = result
            except json.JSONDecodeError as e:
                st.error(f"Analysis returned invalid JSON: {e}")
                return
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                return

    data = st.session_state.get("last_result")
    if not data:
        return

    fname = data.get("_filename", uploaded.name)
    st.markdown('<div class="alert-box alert-success">✓ Analysis complete.</div>', unsafe_allow_html=True)

    # ── Export buttons ──────────────────────────────────────────────────────
    md_report = build_markdown_report(data, fname)

    ecol1, ecol2, ecol3 = st.columns([1, 1, 2])
    with ecol1:
        st.download_button(
            "⬇️ Download Markdown",
            data=md_report.encode("utf-8"),
            file_name=f"report_{Path(fname).stem}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with ecol2:
        pdf_bytes = build_pdf_bytes(md_report)
        if pdf_bytes:
            st.download_button(
                "⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"report_{Path(fname).stem}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.markdown('<div class="alert-box alert-warning" style="font-size:.75rem">Install <code>reportlab</code> for PDF export.</div>', unsafe_allow_html=True)
    with ecol3:
        # Copy-to-clipboard via JS
        escaped = md_report.replace("`", "\\`").replace("\\", "\\\\").replace("${", "\\${")
        st.markdown(f"""
        <button class="copy-btn" onclick="navigator.clipboard.writeText(`{escaped}`).then(()=>this.innerText='✓ Copied!').catch(()=>this.innerText='Copy failed')">
          📋 Copy Report to Clipboard
        </button>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Sections ────────────────────────────────────────────────────────────
    render_confidence_summary(data.get("transcript_confidence_summary", {}))
    render_risk_report(data.get("audio_risk_report", {}))

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Transcript & Translation", "💭 Emotional Analysis", "🔍 Signals & Verification", "📈 Scores"])

    with tab1:
        render_transcript_section("Original Transcript", "📝", data.get("original_transcript", ""), "orig")
        render_transcript_section("Literal English Translation", "🔤", data.get("literal_english_translation", ""), "lit")
        render_transcript_section("Natural English Meaning", "💬", data.get("natural_english_meaning", ""), "nat")
        render_transcript_section("Contextual Meaning", "🧠", data.get("contextual_meaning", ""), "ctx")

    with tab2:
        render_emotional_analysis(data.get("emotional_relationship_analysis", {}))

    with tab3:
        render_signals(data.get("important_relationship_signals", []))
        render_verification(data.get("verification_required", []))

    with tab4:
        render_confidence_scores(data.get("confidence_scores", {}))


if __name__ == "__main__":
    main()
