CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
  padding-top: 1.25rem;
  max-width: 1080px;
}

.hero-title {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #F4F7FB;
  margin-bottom: 0.35rem;
}

.hero-subtitle {
  color: #8B98A8;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.scope-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: linear-gradient(135deg, #1a2744 0%, #152238 100%);
  border: 1px solid #2d4a7a;
  color: #7eb8ff;
  border-radius: 999px;
  padding: 0.35rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 600;
  margin: 0.5rem 0 1rem 0;
}

.scope-badge.warn {
  background: linear-gradient(135deg, #2a2218 0%, #1f1a14 100%);
  border-color: #5c4a2a;
  color: #e8c170;
}

section[data-testid="stSidebar"] {
  background: #0c1017;
  border-right: 1px solid #1e2a3d;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
  font-size: 0.72rem !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6b7d94 !important;
  font-weight: 600 !important;
}

.doc-card {
  background: #141b26;
  border: 1px solid #243041;
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.45rem;
  font-size: 0.82rem;
  color: #c8d4e0;
  line-height: 1.35;
}

.doc-card .doc-type {
  display: inline-block;
  background: #1e3050;
  color: #6ea8ff;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  margin-right: 0.4rem;
  text-transform: uppercase;
}

div[data-testid="stFileUploader"] section {
  border: 1px dashed #2d4b73 !important;
  border-radius: 12px !important;
  background: #10151d !important;
}

.stChatMessage {
  border: 1px solid #1e2a3d !important;
  border-radius: 14px !important;
  background: #111820 !important;
  padding: 0.25rem 0.5rem !important;
}

.stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  border-color: #3d2a2a !important;
}

.stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
  border-color: #1e3a5f !important;
}

.citation-chip {
  display: inline-block;
  background: #152238;
  color: #8fb8ff;
  border: 1px solid #2a4570;
  border-radius: 999px;
  padding: 0.22rem 0.7rem;
  margin: 0.2rem 0.3rem 0.2rem 0;
  font-size: 0.76rem;
  font-weight: 500;
}

.sources-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6b7d94;
  margin: 0.75rem 0 0.35rem 0;
  font-weight: 600;
}

.answer-card {
  background: #121a28;
  border: 1px solid #243041;
  border-left: 3px solid #4f8cff;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  margin: 0.65rem 0 1rem 0;
}

.answer-card-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #8fb8ff;
  margin-bottom: 0.45rem;
  letter-spacing: 0.01em;
}

.answer-card-body {
  font-size: 0.9rem;
  color: #c8d4e0;
  line-height: 1.55;
  white-space: pre-wrap;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
