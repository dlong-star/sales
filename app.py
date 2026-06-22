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
    page_title="Spanish Conversation Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & base ─────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.main .block-container {
  padding: 1.5rem 2rem 4rem;
  max-width: 1100px;
}

/* ── Background ───────────────────────────────────────── */
.stApp { background: #080b14; }
section[data-testid="stSidebar"] { background: #0d1017 !important; border-right: 1px solid #1e2535; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

/* ── Sidebar brand ────────────────────────────────────── */
.sidebar-brand {
  display: flex; align-items: center; gap: .6rem;
  padding: 0 1rem 1.5rem;
  border-bottom: 1px solid #1e2535;
  margin-bottom: 1.5rem;
}
.sidebar-brand .icon { font-size: 1.4rem; }
.sidebar-brand .name { color: #f1f5f9; font-size: .95rem; font-weight: 700; line-height: 1.2; }
.sidebar-brand .sub  { color: #64748b; font-size: .72rem; letter-spacing: .04em; }

.sidebar-label {
  color: #475569; font-size: .68rem; font-weight: 600;
  letter-spacing: .1em; text-transform: uppercase;
  padding: 0 1rem; margin-bottom: .4rem;
}
.sidebar-divider { border: none; border-top: 1px solid #1e2535; margin: 1.25rem 0; }

/* ── Upload card ──────────────────────────────────────── */
.upload-card {
  background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
  border: 1.5px dashed #2d3f6b;
  border-radius: 20px;
  padding: 2.5rem 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
  transition: border-color .25s, background .25s;
  position: relative;
  overflow: hidden;
}
.upload-card::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(99,102,241,.08) 0%, transparent 70%);
  pointer-events: none;
}
.upload-card:hover { border-color: #6366f1; }
.upload-icon { font-size: 2.5rem; margin-bottom: .75rem; }
.upload-title { color: #f1f5f9; font-size: 1.15rem; font-weight: 600; margin-bottom: .35rem; }
.upload-sub   { color: #64748b; font-size: .82rem; }

/* override Streamlit uploader to blend in */
.stFileUploader > div { background: transparent !important; border: none !important; }
.stFileUploader label { display: none !important; }

/* ── Step progress ────────────────────────────────────── */
.progress-track {
  display: flex; align-items: center; gap: 0;
  background: #0d1117;
  border: 1px solid #1e2535;
  border-radius: 14px;
  padding: .85rem 1.5rem;
  margin-bottom: 1.75rem;
}
.step-item {
  display: flex; align-items: center; gap: .5rem;
  flex: 1;
}
.step-item:not(:last-child)::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #1e2535;
  margin: 0 .5rem;
}
.step-dot {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .75rem; font-weight: 700;
  flex-shrink: 0;
}
.step-dot.done    { background: #6366f1; color: white; }
.step-dot.active  { background: linear-gradient(135deg,#6366f1,#8b5cf6); color: white; box-shadow: 0 0 12px rgba(99,102,241,.6); }
.step-dot.pending { background: #1e2535; color: #475569; }
.step-text { font-size: .78rem; font-weight: 500; white-space: nowrap; }
.step-text.done    { color: #818cf8; }
.step-text.active  { color: #f1f5f9; }
.step-text.pending { color: #475569; }

/* ── Section cards ────────────────────────────────────── */
.s-card {
  background: linear-gradient(160deg, #0d1117 0%, #111827 100%);
  border: 1px solid #1e2535;
  border-radius: 16px;
  padding: 1.5rem 1.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 12px rgba(0,0,0,.35);
  transition: border-color .2s, box-shadow .2s;
}
.s-card:hover { border-color: #2d3f6b; box-shadow: 0 4px 24px rgba(0,0,0,.5); }

.s-card-header {
  display: flex; align-items: center; gap: .6rem;
  margin-bottom: 1.1rem;
  padding-bottom: .8rem;
  border-bottom: 1px solid #1e2535;
}
.s-card-icon {
  width: 34px; height: 34px;
  background: linear-gradient(135deg,#1e1b4b,#2e1065);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.s-card-title { color: #f1f5f9; font-size: .92rem; font-weight: 600; }
.s-card-sub   { color: #64748b; font-size: .75rem; margin-top: .1rem; }

/* ── Metric grid ──────────────────────────────────────── */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(120px,1fr)); gap: .75rem; margin-bottom: 1rem; }
.metric-tile {
  background: #0a0e18;
  border: 1px solid #1e2535;
  border-radius: 12px;
  padding: .85rem 1rem;
  text-align: center;
}
.metric-tile .m-label { color: #475569; font-size: .65rem; text-transform: uppercase; letter-spacing: .09em; font-weight: 600; margin-bottom: .35rem; }
.metric-tile .m-value { color: #f1f5f9; font-size: 1.25rem; font-weight: 700; line-height: 1; }
.metric-tile .m-sub   { color: #64748b; font-size: .68rem; margin-top: .25rem; }

/* ── Score bars ───────────────────────────────────────── */
.score-row { margin: .55rem 0; }
.score-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: .3rem; }
.score-meta span:first-child { color: #94a3b8; font-size: .8rem; }
.score-meta span:last-child  { font-size: .8rem; font-weight: 700; }
.score-track { background: #1e2535; border-radius: 99px; height: 6px; overflow: hidden; }
.score-fill  { height: 6px; border-radius: 99px; transition: width .7s cubic-bezier(.4,0,.2,1); }

/* ── Tags / badges ────────────────────────────────────── */
.badge {
  display: inline-flex; align-items: center; gap: .3rem;
  padding: .25rem .7rem;
  border-radius: 99px;
  font-size: .72rem; font-weight: 600;
  margin: .15rem;
}
.badge-violet  { background: rgba(139,92,246,.15); color: #a78bfa; border: 1px solid rgba(139,92,246,.25); }
.badge-blue    { background: rgba(99,102,241,.15);  color: #818cf8; border: 1px solid rgba(99,102,241,.25); }
.badge-green   { background: rgba(52,211,153,.12);  color: #6ee7b7; border: 1px solid rgba(52,211,153,.25); }
.badge-amber   { background: rgba(251,191,36,.12);  color: #fcd34d; border: 1px solid rgba(251,191,36,.25); }
.badge-red     { background: rgba(239,68,68,.12);   color: #fca5a5; border: 1px solid rgba(239,68,68,.25); }
.badge-slate   { background: rgba(100,116,139,.12); color: #94a3b8; border: 1px solid rgba(100,116,139,.25); }

/* ── Alert cards ──────────────────────────────────────── */
.alert {
  border-radius: 12px; padding: .85rem 1.1rem;
  font-size: .83rem; line-height: 1.6; margin-bottom: .85rem;
  display: flex; align-items: flex-start; gap: .6rem;
}
.alert-icon { font-size: 1rem; flex-shrink: 0; margin-top: .05rem; }
.alert-body { flex: 1; }
.alert-title { font-weight: 600; margin-bottom: .15rem; }
.alert-info    { background: rgba(99,102,241,.08); border: 1px solid rgba(99,102,241,.2); color: #a5b4fc; }
.alert-success { background: rgba(52,211,153,.08); border: 1px solid rgba(52,211,153,.2); color: #6ee7b7; }
.alert-warn    { background: rgba(251,191,36,.08); border: 1px solid rgba(251,191,36,.2); color: #fcd34d; }
.alert-danger  { background: rgba(239,68,68,.08);  border: 1px solid rgba(239,68,68,.2);  color: #fca5a5; }

/* ── Transcript boxes ─────────────────────────────────── */
.transcript-box {
  background: #0a0e18;
  border: 1px solid #1e2535;
  border-radius: 12px;
  padding: 1.1rem 1.25rem;
  color: #cbd5e1;
  font-size: .85rem;
  line-height: 1.75;
  max-height: 280px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: 'Inter', monospace;
}
.transcript-box::-webkit-scrollbar { width: 4px; }
.transcript-box::-webkit-scrollbar-track { background: transparent; }
.transcript-box::-webkit-scrollbar-thumb { background: #2d3f6b; border-radius: 99px; }

/* ── Flag rows ────────────────────────────────────────── */
.flag-row {
  background: #0a0e18;
  border: 1px solid #1e2535;
  border-radius: 10px;
  padding: .7rem 1rem;
  margin: .4rem 0;
  display: flex; align-items: flex-start; gap: .75rem;
}
.flag-row .flag-sev { flex-shrink: 0; }
.flag-row .flag-name { color: #f1f5f9; font-weight: 600; font-size: .85rem; }
.flag-row .flag-detail { color: #64748b; font-size: .78rem; margin-top: .2rem; }

/* ── Signal rows ──────────────────────────────────────── */
.signal-row {
  background: #0a0e18;
  border-left: 3px solid #6366f1;
  border-radius: 0 10px 10px 0;
  padding: .75rem 1rem;
  margin: .5rem 0;
}
.signal-name   { color: #818cf8; font-weight: 600; font-size: .85rem; margin-bottom: .3rem; }
.signal-quote  { color: #94a3b8; font-size: .8rem; font-style: italic; margin-bottom: .3rem; }
.signal-impl   { color: #e2e8f0; font-size: .82rem; }

/* ── Verification rows ────────────────────────────────── */
.verify-row {
  border-radius: 10px;
  padding: .75rem 1rem;
  margin: .45rem 0;
  border: 1px solid;
}
.verify-high   { background: rgba(239,68,68,.07);  border-color: rgba(239,68,68,.25); }
.verify-medium { background: rgba(251,191,36,.07); border-color: rgba(251,191,36,.25); }
.verify-low    { background: rgba(52,211,153,.07); border-color: rgba(52,211,153,.25); }
.verify-item   { font-weight: 600; font-size: .85rem; color: #f1f5f9; margin-bottom: .25rem; }
.verify-reason { font-size: .79rem; color: #94a3b8; }

/* ── Buttons ──────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  padding: .55rem 1.4rem !important;
  font-size: .85rem !important;
  font-weight: 600 !important;
  letter-spacing: .01em !important;
  transition: opacity .2s, box-shadow .2s !important;
  box-shadow: 0 2px 12px rgba(99,102,241,.3) !important;
}
.stButton > button:hover {
  opacity: .88 !important;
  box-shadow: 0 4px 20px rgba(99,102,241,.45) !important;
}
div[data-testid="stDownloadButton"] button {
  background: #131a2a !important;
  border: 1px solid #2d3f6b !important;
  color: #94a3b8 !important;
  box-shadow: none !important;
}
div[data-testid="stDownloadButton"] button:hover {
  border-color: #6366f1 !important;
  color: #f1f5f9 !important;
}

/* ── Copy button ──────────────────────────────────────── */
.copy-btn {
  display: inline-flex; align-items: center; gap: .4rem;
  background: #131a2a;
  color: #94a3b8;
  border: 1px solid #2d3f6b;
  border-radius: 10px;
  padding: .5rem 1.1rem;
  font-size: .82rem; font-weight: 600;
  cursor: pointer;
  transition: border-color .2s, color .2s;
  font-family: inherit;
}
.copy-btn:hover { border-color: #6366f1; color: #f1f5f9; }

/* ── Tabs ─────────────────────────────────────────────── */
div[data-testid="stTabs"] button {
  color: #475569 !important;
  font-size: .83rem !important;
  font-weight: 500 !important;
  border-radius: 8px 8px 0 0 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
  color: #818cf8 !important;
  border-bottom-color: #6366f1 !important;
}

/* ── Accordion ────────────────────────────────────────── */
details {
  background: #0d1117;
  border: 1px solid #1e2535;
  border-radius: 12px;
  margin-bottom: .6rem;
  overflow: hidden;
}
details[open] { border-color: #2d3f6b; }
summary {
  padding: .85rem 1.2rem;
  color: #e2e8f0;
  font-size: .88rem;
  font-weight: 600;
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  gap: .5rem;
  user-select: none;
}
summary::-webkit-details-marker { display: none; }
summary::after {
  content: '›';
  margin-left: auto;
  color: #475569;
  font-size: 1.1rem;
  transition: transform .2s;
}
details[open] summary::after { transform: rotate(90deg); }
details .accordion-body { padding: 0 1.2rem 1rem; border-top: 1px solid #1e2535; }

/* ── Spinner ──────────────────────────────────────────── */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── Text inputs ──────────────────────────────────────── */
.stTextInput input, .stTextArea textarea {
  background: #0a0e18 !important;
  border: 1px solid #1e2535 !important;
  border-radius: 10px !important;
  color: #e2e8f0 !important;
  font-size: .83rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,.1) !important;
}

/* ── File uploader tweak ──────────────────────────────── */
div[data-testid="stFileUploader"] {
  background: #0d1117;
  border: 1.5px dashed #2d3f6b;
  border-radius: 16px;
  padding: 1.5rem;
  transition: border-color .2s;
}
div[data-testid="stFileUploader"]:hover { border-color: #6366f1; }
div[data-testid="stFileUploader"] section { background: transparent !important; border: none !important; }

/* ── Expander ─────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: #0d1117 !important;
  border-radius: 10px !important;
  border: 1px solid #1e2535 !important;
  color: #e2e8f0 !important;
}

/* ── Risk level banner ────────────────────────────────── */
.risk-banner {
  display: flex; align-items: center; justify-content: space-between;
  background: #0a0e18;
  border-radius: 12px;
  padding: .9rem 1.2rem;
  margin-bottom: 1rem;
  border: 1px solid #1e2535;
}
.risk-level { font-size: 1.5rem; font-weight: 800; letter-spacing: -.01em; }
.risk-low      { color: #6ee7b7; }
.risk-medium   { color: #fcd34d; }
.risk-high     { color: #fca5a5; }
.risk-critical { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
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
        st.error("OPENAI_API_KEY not set. Add it to your .env file or paste it in the sidebar.")
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
    return {".m4a": "audio/mp4", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".mp4": "video/mp4"}.get(suffix, "audio/mpeg")


def analyze_transcript(client: openai.OpenAI, transcript: str, context: str = "") -> dict:
    user_content = f"Transcript:\n{transcript}"
    if context.strip():
        user_content = f"Additional context:\n{context}\n\n{user_content}"
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
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw)


def pct(val: float) -> str:
    return f"{int(round(val * 100))}%"


def score_color(val: float) -> str:
    if val >= 0.8:  return "#6ee7b7"
    if val >= 0.6:  return "#fcd34d"
    if val >= 0.4:  return "#fb923c"
    return "#fca5a5"


def sev_badge(s: str) -> str:
    cls = {"Low": "badge-green", "Medium": "badge-amber", "High": "badge-red"}.get(s, "badge-slate")
    return f'<span class="badge {cls}">{s}</span>'


def pri_badge(p: str) -> str:
    cls = {"Low": "badge-green", "Medium": "badge-amber", "High": "badge-red"}.get(p, "badge-slate")
    return f'<span class="badge {cls}">{p} Priority</span>'


def score_bar_html(label: str, val: float) -> str:
    color = score_color(val)
    w = int(val * 100)
    return f"""
    <div class="score-row">
      <div class="score-meta">
        <span>{label}</span>
        <span style="color:{color}">{pct(val)}</span>
      </div>
      <div class="score-track">
        <div class="score-fill" style="width:{w}%;background:linear-gradient(90deg,{color}cc,{color})"></div>
      </div>
    </div>"""


def risk_class(level: str) -> str:
    return {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high", "Critical": "risk-critical"}.get(level, "risk-low")


# ── Step tracker ───────────────────────────────────────────────────────────────

def render_steps(active: int):
    steps = ["Upload", "Transcribe", "Analyze", "Report Ready"]
    items = []
    for i, s in enumerate(steps, 1):
        if i < active:
            cls = "done"
            dot = "✓"
        elif i == active:
            cls = "active"
            dot = str(i)
        else:
            cls = "pending"
            dot = str(i)

        connector = "" if i == len(steps) else ""
        items.append(f"""
        <div class="step-item">
          <div class="step-dot {cls}">{dot}</div>
          <span class="step-text {cls}">{s}</span>
        </div>""")

    st.markdown(f'<div class="progress-track">{"".join(items)}</div>', unsafe_allow_html=True)


# ── Export ─────────────────────────────────────────────────────────────────────

def build_markdown(data: dict, filename: str) -> str:
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M")
    tcs = data.get("transcript_confidence_summary", {})
    arr = data.get("audio_risk_report", {})
    cs  = data.get("confidence_scores", {})
    era = data.get("emotional_relationship_analysis", {})

    score_labels = {
        "transcription_accuracy": "Transcription Accuracy",
        "translation_accuracy": "Translation Accuracy",
        "emotional_analysis": "Emotional Analysis",
        "contextual_interpretation": "Contextual Interpretation",
        "overall_reliability": "Overall Reliability",
    }

    lines = [
        "# Spanish Conversation Intelligence Report",
        f"**File:** {filename}  |  **Generated:** {ts}",
        "",
        "---",
        "",
        "## Transcript Confidence Summary",
        f"- **Overall Confidence:** {pct(tcs.get('overall_confidence', 0))}",
        f"- **Clarity:** {tcs.get('clarity_rating', '—')}",
        f"- **Noise Level:** {tcs.get('noise_level', '—')}",
        f"- **Estimated Speakers:** {tcs.get('speaker_count_estimate', '—')}",
        f"- **Language Detected:** {tcs.get('language_detected', '—')}",
        f"- **Notes:** {tcs.get('notes', '—')}",
        "",
        "## Audio Risk Report",
        f"**Risk Level:** {arr.get('overall_risk_level', '—')}  |  **Score:** {pct(arr.get('risk_score', 0))}",
        "",
        arr.get("summary", ""),
        "",
        "### Risk Flags",
    ]
    for flag in arr.get("flags", []):
        lines.append(f"- **[{flag.get('severity')}]** {flag.get('flag')}: {flag.get('detail')}")
    lines += [
        "", "## Original Transcript", data.get("original_transcript", ""),
        "", "## Literal English Translation", data.get("literal_english_translation", ""),
        "", "## Natural English Meaning", data.get("natural_english_meaning", ""),
        "", "## Contextual Meaning", data.get("contextual_meaning", ""),
        "", "## Emotional / Relationship Analysis",
        f"- **Primary Emotion:** {era.get('primary_emotion', '—')}",
        f"- **Secondary Emotions:** {', '.join(era.get('secondary_emotions', []))}",
        f"- **Tone:** {era.get('tone', '—')}",
        f"- **Relationship Dynamic:** {era.get('relationship_dynamic', '—')}",
        f"- **Power Dynamic:** {era.get('power_dynamic', '—')}",
        "", era.get("analysis", ""),
        "", "## Important Relationship Signals",
    ]
    for sig in data.get("important_relationship_signals", []):
        lines.append(f"- **{sig.get('signal')}**: \"{sig.get('evidence')}\" → {sig.get('implication')}")
    lines += ["", "## Verification Required"]
    for v in data.get("verification_required", []):
        lines.append(f"- **[{v.get('priority')}]** {v.get('item')}: {v.get('reason')}")
    lines += ["", "## Confidence Scores", "| Dimension | Score |", "|---|---|"]
    for key, label in score_labels.items():
        lines.append(f"| {label} | {pct(cs.get(key, 0))} |")
    return "\n".join(lines)


def build_txt(data: dict, filename: str) -> str:
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M")
    tcs = data.get("transcript_confidence_summary", {})
    arr = data.get("audio_risk_report", {})
    cs  = data.get("confidence_scores", {})
    era = data.get("emotional_relationship_analysis", {})

    sep = "=" * 60
    lines = [
        "SPANISH CONVERSATION INTELLIGENCE REPORT",
        f"File: {filename}  |  Generated: {ts}",
        sep,
        "",
        "TRANSCRIPT CONFIDENCE SUMMARY",
        f"  Overall Confidence : {pct(tcs.get('overall_confidence', 0))}",
        f"  Clarity            : {tcs.get('clarity_rating', '—')}",
        f"  Noise Level        : {tcs.get('noise_level', '—')}",
        f"  Speakers Estimated : {tcs.get('speaker_count_estimate', '—')}",
        f"  Language Detected  : {tcs.get('language_detected', '—')}",
        f"  Notes              : {tcs.get('notes', '—')}",
        "",
        "AUDIO RISK REPORT",
        f"  Risk Level : {arr.get('overall_risk_level', '—')}",
        f"  Risk Score : {pct(arr.get('risk_score', 0))}",
        f"  Summary    : {arr.get('summary', '—')}",
        "  Flags:",
    ]
    for flag in arr.get("flags", []):
        lines.append(f"    [{flag.get('severity')}] {flag.get('flag')}: {flag.get('detail')}")
    lines += [
        "", "ORIGINAL TRANSCRIPT", data.get("original_transcript", ""),
        "", "LITERAL ENGLISH TRANSLATION", data.get("literal_english_translation", ""),
        "", "NATURAL ENGLISH MEANING", data.get("natural_english_meaning", ""),
        "", "CONTEXTUAL MEANING", data.get("contextual_meaning", ""),
        "", "EMOTIONAL / RELATIONSHIP ANALYSIS",
        f"  Primary Emotion     : {era.get('primary_emotion', '—')}",
        f"  Secondary Emotions  : {', '.join(era.get('secondary_emotions', []))}",
        f"  Tone                : {era.get('tone', '—')}",
        f"  Relationship Dynamic: {era.get('relationship_dynamic', '—')}",
        f"  Power Dynamic       : {era.get('power_dynamic', '—')}",
        f"  Analysis: {era.get('analysis', '—')}",
        "", "IMPORTANT RELATIONSHIP SIGNALS",
    ]
    for sig in data.get("important_relationship_signals", []):
        lines.append(f"  [{sig.get('signal')}] \"{sig.get('evidence')}\" -> {sig.get('implication')}")
    lines += ["", "VERIFICATION REQUIRED"]
    for v in data.get("verification_required", []):
        lines.append(f"  [{v.get('priority')}] {v.get('item')}: {v.get('reason')}")
    score_labels = {
        "transcription_accuracy": "Transcription Accuracy",
        "translation_accuracy": "Translation Accuracy",
        "emotional_analysis": "Emotional Analysis",
        "contextual_interpretation": "Contextual Interpretation",
        "overall_reliability": "Overall Reliability",
    }
    lines += ["", "CONFIDENCE SCORES"]
    for key, label in score_labels.items():
        lines.append(f"  {label:<30} {pct(cs.get(key, 0))}")
    return "\n".join(lines)


def build_pdf(markdown_text: str) -> bytes | None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        ACC = colors.HexColor("#6366f1")
        FG  = colors.HexColor("#e2e8f0")
        MUT = colors.HexColor("#94a3b8")
        h1  = ParagraphStyle("H1", parent=styles["Heading1"], textColor=ACC, fontSize=18, spaceAfter=6)
        h2  = ParagraphStyle("H2", parent=styles["Heading2"], textColor=ACC, fontSize=13, spaceBefore=14, spaceAfter=4)
        body   = ParagraphStyle("Body",   parent=styles["Normal"], textColor=FG,  fontSize=9,  leading=14)
        bullet = ParagraphStyle("Bullet", parent=styles["Normal"], textColor=FG,  fontSize=9,  leading=14, leftIndent=12)
        story = []
        for line in markdown_text.split("\n"):
            s = line.strip()
            if not s:
                story.append(Spacer(1, 5))
            elif s.startswith("# "):
                story.append(Paragraph(s[2:], h1))
            elif s.startswith("## "):
                story.append(HRFlowable(width="100%", thickness=.5, color=ACC, spaceAfter=3))
                story.append(Paragraph(s[3:], h2))
            elif s.startswith("- "):
                story.append(Paragraph(f"• {s[2:]}", bullet))
            elif s.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=.5, color=MUT, spaceAfter=3))
            elif s.startswith("|"):
                pass
            else:
                story.append(Paragraph(s, body))
        doc.build(story)
        return buf.getvalue()
    except ImportError:
        return None


# ── Sidebar ────────────────────────────────────────────────────────────────────

def sidebar() -> str:
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
          <div class="icon">🎙️</div>
          <div>
            <div class="name">Spanish Conversation<br>Intelligence</div>
            <div class="sub">Powered by GPT-4o</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">API Configuration</div>', unsafe_allow_html=True)
        key = st.text_input("OpenAI API Key", type="password",
                            value=os.getenv("OPENAI_API_KEY", ""),
                            placeholder="sk-…",
                            label_visibility="collapsed")
        if key:
            os.environ["OPENAI_API_KEY"] = key

        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-label">Analysis Context</div>', unsafe_allow_html=True)
        context = st.text_area(
            "Context",
            placeholder="Optional: describe the situation, speakers, or language (e.g. 'Phone call between two people arguing in Mexican Spanish')",
            height=130,
            label_visibility="collapsed",
        )

        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        st.markdown("""
        <div style="padding: 0 .5rem">
          <div class="sidebar-label" style="margin-bottom:.75rem">Supported formats</div>
          <div>
            <span class="badge badge-slate">.m4a</span>
            <span class="badge badge-slate">.mp3</span>
            <span class="badge badge-slate">.wav</span>
            <span class="badge badge-slate">.mp4</span>
          </div>
          <div style="color:#475569;font-size:.72rem;margin-top:.75rem">Max size: 25 MB</div>
        </div>
        """, unsafe_allow_html=True)
    return context


# ── Report sections ────────────────────────────────────────────────────────────

def confidence_section(tcs: dict):
    conf = tcs.get("overall_confidence", 0)
    color = score_color(conf)
    st.markdown(f"""
    <div class="s-card">
      <div class="s-card-header">
        <div class="s-card-icon">📊</div>
        <div>
          <div class="s-card-title">Transcript Confidence Summary</div>
          <div class="s-card-sub">Audio quality and transcription reliability</div>
        </div>
      </div>
      <div class="metric-grid">
        <div class="metric-tile">
          <div class="m-label">Confidence</div>
          <div class="m-value" style="color:{color}">{pct(conf)}</div>
        </div>
        <div class="metric-tile">
          <div class="m-label">Clarity</div>
          <div class="m-value">{tcs.get('clarity_rating','—')}</div>
        </div>
        <div class="metric-tile">
          <div class="m-label">Noise</div>
          <div class="m-value">{tcs.get('noise_level','—')}</div>
        </div>
        <div class="metric-tile">
          <div class="m-label">Speakers</div>
          <div class="m-value">{tcs.get('speaker_count_estimate','—')}</div>
          <div class="m-sub">estimated</div>
        </div>
      </div>
      <div style="margin-bottom:.6rem">
        <span class="badge badge-violet">🌐 {tcs.get('language_detected','Unknown')}</span>
      </div>
      <p style="color:#64748b;font-size:.82rem;margin:0;line-height:1.6">{tcs.get('notes','')}</p>
    </div>
    """, unsafe_allow_html=True)


def risk_section(arr: dict):
    level = arr.get("overall_risk_level", "Low")
    score = arr.get("risk_score", 0)
    rc = risk_class(level)
    risk_color = score_color(1 - score)

    flags_html = ""
    for flag in arr.get("flags", []):
        flags_html += f"""
        <div class="flag-row">
          <div class="flag-sev">{sev_badge(flag.get('severity',''))}</div>
          <div>
            <div class="flag-name">{flag.get('flag','')}</div>
            <div class="flag-detail">{flag.get('detail','')}</div>
          </div>
        </div>"""

    st.markdown(f"""
    <div class="s-card">
      <div class="s-card-header">
        <div class="s-card-icon">⚠️</div>
        <div>
          <div class="s-card-title">Audio Risk Report</div>
          <div class="s-card-sub">Detected risk factors and severity flags</div>
        </div>
      </div>
      <div class="risk-banner">
        <div>
          <div style="color:#64748b;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.25rem">Overall Risk</div>
          <div class="risk-level {rc}">{level}</div>
        </div>
        <div style="text-align:right">
          <div style="color:#64748b;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.25rem">Risk Score</div>
          <div style="font-size:1.5rem;font-weight:800;color:{score_color(score)}">{pct(score)}</div>
        </div>
      </div>
      <p style="color:#94a3b8;font-size:.83rem;line-height:1.65;margin-bottom:1rem">{arr.get('summary','')}</p>
      {flags_html}
    </div>
    """, unsafe_allow_html=True)


def transcript_accordion(title: str, icon: str, content: str, open_default: bool = False):
    open_attr = "open" if open_default else ""
    safe = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(f"""
    <details {open_attr}>
      <summary>{icon} {title}</summary>
      <div class="accordion-body" style="padding-top:.85rem">
        <div class="transcript-box">{safe}</div>
      </div>
    </details>
    """, unsafe_allow_html=True)


def emotional_section(era: dict):
    primary = era.get("primary_emotion", "—")
    secondary = era.get("secondary_emotions", [])
    tags = f'<span class="badge badge-violet">{primary}</span>'
    for e in secondary:
        tags += f' <span class="badge badge-blue">{e}</span>'
    st.markdown(f"""
    <div class="s-card">
      <div class="s-card-header">
        <div class="s-card-icon">💭</div>
        <div>
          <div class="s-card-title">Emotional / Relationship Analysis</div>
          <div class="s-card-sub">Detected emotions, tone, and relationship dynamics</div>
        </div>
      </div>
      <div style="margin-bottom:1rem">{tags}</div>
      <div class="metric-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:1rem">
        <div class="metric-tile">
          <div class="m-label">Tone</div>
          <div class="m-value" style="font-size:.95rem;padding-top:.1rem">{era.get('tone','—')}</div>
        </div>
        <div class="metric-tile" style="grid-column:span 2">
          <div class="m-label">Relationship Dynamic</div>
          <div class="m-value" style="font-size:.9rem;padding-top:.1rem">{era.get('relationship_dynamic','—')}</div>
        </div>
      </div>
      <div class="metric-tile" style="text-align:left;margin-bottom:1rem">
        <div class="m-label">Power Dynamic</div>
        <div style="color:#f1f5f9;font-size:.9rem;font-weight:600;margin-top:.3rem">{era.get('power_dynamic','—')}</div>
      </div>
      <p style="color:#94a3b8;font-size:.83rem;line-height:1.7;margin:0">{era.get('analysis','')}</p>
    </div>
    """, unsafe_allow_html=True)


def signals_section(signals: list):
    rows = ""
    for sig in signals:
        rows += f"""
        <div class="signal-row">
          <div class="signal-name">{sig.get('signal','')}</div>
          <div class="signal-quote">"{sig.get('evidence','')}"</div>
          <div class="signal-impl">→ {sig.get('implication','')}</div>
        </div>"""
    st.markdown(f"""
    <div class="s-card">
      <div class="s-card-header">
        <div class="s-card-icon">🔍</div>
        <div>
          <div class="s-card-title">Important Relationship Signals</div>
          <div class="s-card-sub">Key indicators found in the conversation</div>
        </div>
      </div>
      {rows}
    </div>
    """, unsafe_allow_html=True)


def verification_section(items: list):
    rows = ""
    for v in items:
        pri = v.get("priority", "Low")
        vcls = {"High": "verify-high", "Medium": "verify-medium", "Low": "verify-low"}.get(pri, "verify-low")
        rows += f"""
        <div class="verify-row {vcls}">
          <div class="verify-item">{pri_badge(pri)} {v.get('item','')}</div>
          <div class="verify-reason">{v.get('reason','')}</div>
        </div>"""
    st.markdown(f"""
    <div class="s-card">
      <div class="s-card-header">
        <div class="s-card-icon">✅</div>
        <div>
          <div class="s-card-title">Verification Required</div>
          <div class="s-card-sub">Items that need human review</div>
        </div>
      </div>
      {rows}
    </div>
    """, unsafe_allow_html=True)


def scores_section(cs: dict):
    score_labels = {
        "transcription_accuracy": "Transcription Accuracy",
        "translation_accuracy": "Translation Accuracy",
        "emotional_analysis": "Emotional Analysis",
        "contextual_interpretation": "Contextual Interpretation",
        "overall_reliability": "Overall Reliability",
    }
    bars = "".join(score_bar_html(label, cs.get(key, 0)) for key, label in score_labels.items())
    overall = cs.get("overall_reliability", 0)
    color = score_color(overall)
    st.markdown(f"""
    <div class="s-card">
      <div class="s-card-header">
        <div class="s-card-icon">📈</div>
        <div>
          <div class="s-card-title">Confidence Scores</div>
          <div class="s-card-sub">Per-dimension reliability assessment</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.25rem">
        <div style="font-size:2.5rem;font-weight:800;color:{color}">{pct(overall)}</div>
        <div style="color:#64748b;font-size:.8rem">Overall<br>Reliability</div>
      </div>
      {bars}
    </div>
    """, unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    context = sidebar()

    # Header
    st.markdown("""
    <div style="margin-bottom:1.75rem">
      <h1 style="color:#f1f5f9;font-size:1.6rem;font-weight:800;margin:0 0 .3rem;letter-spacing:-.02em">
        Spanish Conversation Intelligence
      </h1>
      <p style="color:#475569;font-size:.88rem;margin:0">
        Upload an audio recording to receive a full linguistic, emotional, and risk intelligence report.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Step tracker — initial state
    if "step" not in st.session_state:
        st.session_state.step = 1

    render_steps(st.session_state.step)

    # Upload
    uploaded = st.file_uploader(
        "Audio file",
        type=["m4a", "mp3", "wav", "mp4"],
        label_visibility="collapsed",
    )

    if uploaded is None:
        st.session_state.step = 1
        st.markdown("""
        <div class="alert alert-info" style="margin-top:1rem">
          <div class="alert-icon">ℹ️</div>
          <div class="alert-body">
            <div class="alert-title">Ready to analyze</div>
            Drop an audio file above (.m4a, .mp3, .wav, .mp4 — max 25 MB). Add context in the sidebar to improve accuracy.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    file_bytes = uploaded.read()
    file_mb = len(file_bytes) / (1024 * 1024)

    if file_mb > MAX_FILE_MB:
        st.markdown(f"""
        <div class="alert alert-danger">
          <div class="alert-icon">🚫</div>
          <div class="alert-body">
            <div class="alert-title">File too large</div>
            {file_mb:.1f} MB exceeds the 25 MB limit.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.session_state.step = 2

    col_info, col_run, col_clear = st.columns([3, 1, 1])
    with col_info:
        st.markdown(f"""
        <div style="color:#64748b;font-size:.82rem;padding:.55rem 0;display:flex;align-items:center;gap:.5rem">
          <span class="badge badge-slate">📎</span>
          <b style="color:#e2e8f0">{uploaded.name}</b> — {file_mb:.2f} MB
        </div>
        """, unsafe_allow_html=True)
    with col_run:
        run = st.button("🔍 Analyze", use_container_width=True)
    with col_clear:
        if st.button("✕ Clear", use_container_width=True):
            st.session_state.pop("last_result", None)
            st.session_state.step = 1
            st.rerun()

    if not run and "last_result" not in st.session_state:
        return

    if run:
        client = get_client()

        st.session_state.step = 2
        render_steps(st.session_state.step)

        with st.spinner("Transcribing with gpt-4o-transcribe…"):
            try:
                transcript = transcribe_audio(client, file_bytes, uploaded.name)
            except Exception as e:
                st.error(f"Transcription error: {e}")
                return

        st.session_state.step = 3
        render_steps(st.session_state.step)

        with st.spinner("Analyzing with GPT-4.5…"):
            try:
                result = analyze_transcript(client, transcript, context)
                result["_filename"] = uploaded.name
                st.session_state["last_result"] = result
                st.session_state.step = 4
            except json.JSONDecodeError as e:
                st.error(f"Analysis returned invalid JSON: {e}")
                return
            except Exception as e:
                st.error(f"Analysis error: {e}")
                return

    data = st.session_state.get("last_result")
    if not data:
        return

    st.session_state.step = 4
    fname = data.get("_filename", uploaded.name)

    st.markdown("""
    <div class="alert alert-success" style="margin-top:.5rem">
      <div class="alert-icon">✓</div>
      <div class="alert-body"><div class="alert-title">Analysis complete — report ready below</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Export bar ──────────────────────────────────────────────────────────
    md_report  = build_markdown(data, fname)
    txt_report = build_txt(data, fname)
    pdf_bytes  = build_pdf(md_report)

    stem = Path(fname).stem
    escaped = md_report.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    ecols = st.columns([1, 1, 1, 2])
    with ecols[0]:
        st.download_button("⬇️ Markdown", data=md_report.encode(), file_name=f"{stem}_report.md",
                           mime="text/markdown", use_container_width=True)
    with ecols[1]:
        st.download_button("⬇️ TXT", data=txt_report.encode(), file_name=f"{stem}_report.txt",
                           mime="text/plain", use_container_width=True)
    with ecols[2]:
        if pdf_bytes:
            st.download_button("⬇️ PDF", data=pdf_bytes, file_name=f"{stem}_report.pdf",
                               mime="application/pdf", use_container_width=True)
        else:
            st.markdown('<span style="color:#475569;font-size:.75rem">PDF: install reportlab</span>', unsafe_allow_html=True)
    with ecols[3]:
        st.markdown(f"""
        <button class="copy-btn"
          onclick="navigator.clipboard.writeText(`{escaped}`)
            .then(()=>{{this.textContent='✓ Copied to clipboard';setTimeout(()=>this.textContent='📋 Copy Report',2000)}})
            .catch(()=>this.textContent='Copy failed')">
          📋 Copy Report
        </button>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Report ──────────────────────────────────────────────────────────────
    confidence_section(data.get("transcript_confidence_summary", {}))
    risk_section(data.get("audio_risk_report", {}))

    st.markdown("---")
    st.markdown('<p style="color:#818cf8;font-size:.75rem;font-weight:600;letter-spacing:.09em;text-transform:uppercase;margin-bottom:.75rem">Transcript & Translations</p>', unsafe_allow_html=True)
    transcript_accordion("Original Transcript", "📝", data.get("original_transcript", ""), open_default=True)
    transcript_accordion("Literal English Translation", "🔤", data.get("literal_english_translation", ""))
    transcript_accordion("Natural English Meaning", "💬", data.get("natural_english_meaning", ""))
    transcript_accordion("Contextual Meaning", "🧠", data.get("contextual_meaning", ""))

    st.markdown("---")
    emotional_section(data.get("emotional_relationship_analysis", {}))
    signals_section(data.get("important_relationship_signals", []))
    verification_section(data.get("verification_required", []))
    scores_section(data.get("confidence_scores", {}))


if __name__ == "__main__":
    main()
