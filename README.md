# 🎙️ Audio Intelligence Analyzer

Transcribe and deeply analyze audio recordings using **gpt-4o-transcribe** and **GPT-4.5**.

## What it generates

| Section | Description |
|---|---|
| Transcript Confidence Summary | Clarity, noise level, speaker count, language |
| Audio Risk Report | Risk flags with severity levels |
| Original Transcript | Verbatim transcription |
| Literal English Translation | Word-for-word translation |
| Natural English Meaning | Fluent English rendering |
| Contextual Meaning | Subtext and implied intent |
| Emotional / Relationship Analysis | Emotions, tone, power dynamics |
| Important Relationship Signals | Key signals with evidence |
| Verification Required | Items needing human review |
| Confidence Scores | Per-dimension reliability scores |

## Setup

### 1. Clone and enter the directory
```bash
git clone <repo-url>
cd sales
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
```bash
cp .env.example .env
# Open .env and set OPENAI_API_KEY=sk-your-key-here
```

Alternatively, paste the key directly into the sidebar when the app is running.

## Run locally
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**.

## Exports

- **Markdown** — full structured report as `.md`
- **PDF** — formatted PDF via ReportLab (included in requirements)
- **Copy to Clipboard** — one-click copy of the full report

## Supported audio formats

`.m4a` · `.mp3` · `.wav` · `.mp4` (max **25 MB**)

## File structure

```
sales/
├── app.py              # Main Streamlit application
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```
