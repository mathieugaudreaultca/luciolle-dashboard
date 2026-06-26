import streamlit as st
import feedparser
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Luciolle Dashboard", layout="wide")

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
# FUNCTIONS
# -----------------------------
def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries:
            articles.append({
                "title": entry.get("title", "No title"),
                "summary": entry.get("summary", "No summary available"),
                "link": entry.get("link", "#")
            })

        return articles

    except Exception as e:
        st.error(f"Error fetching feed: {e}")
        return []


def is_relevant(article):
    text = (article["title"] + article["summary"]).lower()
    return any(keyword in text for keyword in KEYWORDS)


def generate_brief(article):
    return f"""
### {article['title']}

**Summary:**  
{article['summary'][:300]}...

**Implications:**  
- Potential policy or funding initiative  
- Possible impact on stakeholders or industry  
- Signals government priorities  

{article['link']}
"""


# -----------------------------
# UI
# -----------------------------
st.title("🟢 Luciolle — Government Intelligence Dashboard")

st.sidebar.header("Filters")

selected_source = st.sidebar.selectbox(
    "Select Source",
    list(SOURCES.keys())
)

keyword_filter = st.sidebar.text_input(
    "Keyword filter (optional)",
)

max_items = st.sidebar.slider(
    "Number of briefs", 
    min_value=5, 
    max_value=20, 
    value=10
)

# -----------------------------
# LOAD DATA
# -----------------------------
with st.spinner("Collecting government announcements..."):
    articles = fetch_feed(SOURCES[selected_source])

# Filter relevant articles
relevant = [a for a in articles if is_relevant(a)]

# Apply keyword filter
if keyword_filter:
    relevant = [
        a for a in relevant
        if keyword_filter.lower() in (a["title"] + a["summary"]).lower()
    ]

# Limit results
relevant = relevant[:max_items]

# -----------------------------
# DISPLAY
# -----------------------------
st.subheader(f"📊 Executive Briefs — {selected_source}")

if not relevant:
    st.warning("No relevant announcements found.")
else:
    for article in relevant:
        st.markdown(generate_brief(article))
        st.markdown("---")

# Optional raw data view
if st.checkbox("Show raw data"):
    df = pd.DataFrame(relevant)
    st.dataframe(df)
