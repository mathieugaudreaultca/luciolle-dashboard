import streamlit as st
import feedparser
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Luciolle Agent", layout="wide")

# -----------------------------
# DATA SOURCES
# -----------------------------
SOURCES = {
    "Federal (Canada)": "https://www.canada.ca/en/news/web-feeds/all.atom.xml",
    "BC Government": "https://news.gov.bc.ca/en/feed",
    "Ontario Government": "https://news.ontario.ca/feed/en",
    "CBC News": "https://www.cbc.ca/cmlink/rss-topstories"
}

KEYWORDS = [
    "funding", "policy", "regulation", "announces",
    "investment", "program", "legislation", "strategy",
    "housing", "energy", "infrastructure"
]

# -----------------------------
# STATE (CHAT MEMORY)
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "reference_text" not in st.session_state:
    st.session_state.reference_text = ""

# -----------------------------
# FUNCTIONS
# -----------------------------
def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries:
            articles.append({
                "title": entry.get("title", "No title"),
                "summary": entry.get("summary", "No summary"),
                "link": entry.get("link", "#")
            })

        return articles
    except:
        return []


def is_relevant(article):
    text = (article["title"] + article["summary"]).lower()
    return any(keyword in text for keyword in KEYWORDS)


def generate_brief(article, reference_text):
    return f"""
### {article['title']}

**Context (from your uploaded document):**  
{reference_text[:300] if reference_text else "No reference uploaded."}

**Summary:**  
{article['summary'][:300]}...

**Implications:**  
- Policy or funding signal  
- Stakeholder impact  
- Government priority indicator  

{article['link']}
"""


def luciolle_chat(user_input, articles, reference_text):
    context = "\n\n".join([a["title"] + ": " + a["summary"] for a in articles[:5]])

    reply = f"""
**Luciolle Analysis**

User question: {user_input}

Relevant recent signals:
{context[:800]}

Reference briefing style:
{reference_text[:400] if reference_text else "No reference provided."}

🧠 Insight:
- This question relates to current policy developments
- Key risks and opportunities should be monitored

✅ Recommended takeaway:
Continue monitoring announcements related to this topic
"""

    return reply


# -----------------------------
# UI
# -----------------------------
st.title("🟢 Luciolle — Policy Intelligence Agent")

# Sidebar controls
st.sidebar.header("Monitoring Controls")

selected_source = st.sidebar.selectbox(
    "Select Source",
    list(SOURCES.keys())
)

keyword_filter = st.sidebar.text_input("Keyword filter")
max_items = st.sidebar.slider("Number of briefs", 5, 20, 10)

# -----------------------------
# FILE UPLOAD
# -----------------------------
st.sidebar.header("📄 Upload Reference Brief")

uploaded_file = st.sidebar.file_uploader(
    "Upload briefing sample (txt or pdf)",
    type=["txt", "pdf"]
)

if uploaded_file is not None:
    try:
        file_content = uploaded_file.read()
        st.session_state.reference_text = file_content.decode("utf-8", errors="ignore")
        st.sidebar.success("Reference uploaded ✅")
    except:
        st.sidebar.error("Could not read file")

# -----------------------------
# FETCH DATA
# -----------------------------
with st.spinner("Collecting government announcements..."):
    articles = fetch_feed(SOURCES[selected_source])

relevant_articles = [a for a in articles if is_relevant(a)]

if keyword_filter:
    relevant_articles = [
        a for a in relevant_articles
        if keyword_filter.lower() in (a["title"] + a["summary"]).lower()
    ]

relevant_articles = relevant_articles[:max_items]

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["📊 Executive Briefs", "💬 Ask Luciolle"])

# -----------------------------
# TAB 1: BRIEFS
# -----------------------------
with tab1:
    st.subheader("Executive Briefings")

    if not relevant_articles:
        st.warning("No relevant announcements found.")
    else:
        for article in relevant_articles:
            st.markdown(generate_brief(article, st.session_state.reference_text))
            st.markdown("---")

# -----------------------------
# TAB 2: CHAT
# -----------------------------
with tab2:
    st.subheader("Ask Luciolle")

    user_input = st.text_input("Ask a question about policy or announcements")

    if st.button("Submit"):
        if user_input:
            response = luciolle_chat(
                user_input,
                relevant_articles,
                st.session_state.reference_text
            )

            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Luciolle", response))

    # Display chat
    for speaker, message in st.session_state.chat_history:
        st.markdown(f"**{speaker}:** {message}")
