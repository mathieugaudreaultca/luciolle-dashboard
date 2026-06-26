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
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        articles.append({
            "title": entry.title,
