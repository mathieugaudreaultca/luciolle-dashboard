import streamlit as st
import feedparser
import pandas as pd
from io import StringIO

# PDF + Word support
from PyPDF2 import PdfReader
import docx

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Luciolle Copilot", layout="wide")

# -----------------------------
# DATA SOURCES
# -----------------------------
SOURCES = {
    "Federal (Canada)": "https://www.canada.ca/en/news/web-feeds/all.atom.xml",
    "BC Government": "https://news.gov.bc.ca/en/feed",
    "Ontario Government": "https://news.ontario.ca/feed/en"
}

KEYWORDS = [
    "funding", "policy", "regulation", "announces",
    "investment", "program", "legislation", "strategy",
    "housing", "energy", "infrastructure"
]

# -----------------------------
# SESSION STATE
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""

# -----------------------------
# FILE PROCESSING
# -----------------------------
def read_pdf(file):
    text = ""
    reader = PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# -----------------------------
# DATA FETCHING
# -----------------------------
def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link", "")
            })

        return articles
    except:
        return []

def is_relevant(article):
    text = (article["title"] + article["summary"]).lower()
    return any(k in text for k in KEYWORDS)

# -----------------------------
# COPILOT RESPONSE
# -----------------------------
def luciolle_response(query, articles, knowledge):
    context = "\n\n".join(
        [f"{a['title']}: {a['summary']}" for a in articles[:5]]
    )

    response = f"""
### Luciolle Analysis

**Your Question:**  
{query}

---

### Relevant Government Signals
{context[:1000]}

---

### Learned Briefing Style / Knowledge
{knowledge[:1000] if knowledge else "No documents uploaded yet."}

---

### Insight
- Key developments suggest evolving policy direction
- Potential implications for stakeholders and funding access
- Alignment with government priorities should be assessed

### Recommended Executive Takeaway
Monitor closely and align internal strategy with emerging signals.
"""

    return response

# -----------------------------
# UI LAYOUT (COPILOT STYLE)
# -----------------------------
st.title("🟢 Luciolle Copilot")

col1, col2 = st.columns([2, 1])

# -----------------------------
# LEFT SIDE: CHAT
# -----------------------------
with col1:
    st.subheader("💬 Ask Luciolle")

    user_query = st.text_area("Type your question here")

    if st.button("Run Analysis"):
        articles = fetch_feed(list(SOURCES.values())[0])
        relevant = [a for a in articles if is_relevant(a)]

        answer = luciolle_response(
            user_query,
            relevant,
            st.session_state.knowledge_base
        )

        st.session_state.chat_history.append(("You", user_query))
        st.session_state.chat_history.append(("Luciolle", answer))

    # Show chat history
    for sender, message in reversed(st.session_state.chat_history):
        if sender == "You":
            st.markdown(f"**🧑 You:** {message}")
        else:
            st.markdown(f"{message}")
        st.markdown("---")

# -----------------------------
# RIGHT SIDE: DOCUMENT UPLOAD
# -----------------------------
with col2:
    st.subheader("📄 Upload Documents")

    uploaded_files = st.file_uploader(
        "Drag & drop PDF or Word files",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt"]
    )

    if uploaded_files:
        combined_text = ""

        for file in uploaded_files:
            if file.type == "application/pdf":
                combined_text += read_pdf(file)

            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                combined_text += read_docx(file)

            else:
                combined_text += StringIO(file.getvalue().decode("utf-8")).read()

        st.session_state.knowledge_base = combined_text
        st.success("Documents processed ✅")

    if st.session_state.knowledge_base:
        st.subheader("📚 Learned Context")
        st.write(st.session_state.knowledge_base[:1000])

# -----------------------------
# FOOTER MONITORING VIEW
# -----------------------------
st.subheader("📊 Latest Relevant Announcements")

articles = fetch_feed(list(SOURCES.values())[0])
relevant_articles = [a for a in articles if is_relevant(a)][:5]

for article in relevant_articles:
    st.markdown(f"### {article['title']}")
    st.write(article["summary"][:200] + "...")
    st.markdown(article["link"])
    st.markdown("---")
``
