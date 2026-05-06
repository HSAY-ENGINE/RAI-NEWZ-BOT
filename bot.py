import feedparser
import requests
import time
from google import genai
from dotenv import load_dotenv
import os
load_dotenv()

# ─── YOUR CREDENTIALS ───
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ─── SETUP GEMINI ───
client = genai.Client(api_key=GEMINI_API_KEY)

# ─── YOUR YOUTUBE CHANNELS ───
CHANNELS = [
    {"name": "AI Explained", "id": "UCNJ1Ymd5yFuUPtn21xtRbbw"},
    {"name": "Two Minute Papers", "id": "UCbfYPyITQ-7l4upoX8nvctg"},
    {"name": "Matt Wolfe", "id": "UChpleBmo18P08aKCIgti38g"},
    {"name": "Vaibhav Sisinty", "id": "UClXAalunTPaX1YV185DWUeg"},
    {"name": "Nate Herk - AI Automation", "id": "UC2ojq-nuP8ceeHqiroeKhBA"},
    {"name": "Hitesh Choudhary", "id": "UCXgGY0wkgOzynnHvSEVmE3A"},
    {"name": "Ishan Sharma", "id": "UCY6N8zZhs2V7gNTUxPuKWoQ"}
]

# ─── AI NEWS WEBSITES ───
NEWS_SOURCES = [
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml"
    },
    {
        "name": "Anthropic News",
        "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml"
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml"
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml"
    },
    {
        "name": "Meta AI",
        "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_meta_ai.xml"
    },
    {
        "name": "Simon Willison",
        "url": "https://simonwillison.net/atom/everything"
    },
    {
        "name": "n8n Blog",
        "url": "https://n8n.io/blog/rss"
    },
    {
        "name": "Replicate Blog",
        "url": "https://replicate.com/blog/rss"
    },
    {
        "name": "Inc42 AI",
        "url": "https://inc42.com/category/ai/feed"
    },
    {
        "name": "YourStory AI",
        "url": "https://yourstory.com/tag/artificial-intelligence/feed"
    }
]

# ─── SEND MESSAGE TO TELEGRAM ───
# ─── DUPLICATE CHECKER ───
def load_seen():
    try:
        with open("seen.txt", "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def mark_seen(link):
    with open("seen.txt", "a") as f:
        f.write(link + "\n")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=data)
    return response.json()

# ─── SUMMARIZE WITH GEMINI ───
def summarize_with_ai(title, description):
    try:
        prompt = f"""
You are an AI news assistant for a young AI builder in India.

Video Title: {title}
Video Description: {description}

Give me:
1. SUMMARY: 2-3 lines explaining what this video is about
2. KEY INSIGHT: The single most valuable thing to learn from this
3. VERDICT: Should I WATCH or SKIP this video?
   - WATCH if: directly teaches AI tools, automation, agents, making money with AI
   - SKIP if: too basic, not relevant to building AI systems

Keep it short and sharp. No fluff.
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI summary unavailable. Read directly."

# ─── FETCH YOUTUBE CHANNEL ───
def fetch_youtube(channel_id, channel_name):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(url)

    if len(feed.entries) == 0:
        return None

    latest = feed.entries[0]
    title = latest.title
    link = latest.link
    published = latest.published
    # ─── CHECK IF ALREADY SEEN ───
    seen = load_seen()
    if link in seen:
        return None

    # ─── MARK AS SEEN ───
    mark_seen(link)

    if hasattr(latest, 'summary'):
        description = latest.summary[:500]
    else:
        description = title

    ai_summary = summarize_with_ai(title, description)

    message = f"""
🎥 <b>{channel_name}</b>

📌 <b>{title}</b>
🔗 {link}
📅 {published[:10]}

🤖 <b>AI Analysis:</b>
{ai_summary}
"""
    return message

# ─── MAIN FUNCTION ───
# ─── FETCH NEWS ARTICLES ───
def fetch_news(source_url, source_name):
    feed = feedparser.parse(source_url)

    if len(feed.entries) == 0:
        return None

    latest = feed.entries[0]
    title = latest.title
    link = latest.link

    if hasattr(latest, 'published'):
        published = latest.published[:10]
    else:
        published = "Recent"

    seen = load_seen()
    if link in seen:
        return None

    mark_seen(link)

    if hasattr(latest, 'summary'):
        description = latest.summary[:500]
    else:
        description = title

    ai_summary = summarize_with_ai(title, description)

    message = f"""
📰 <b>{source_name}</b>

📌 <b>{title}</b>
🔗 {link}
📅 {published}

🤖 <b>AI Analysis:</b>
{ai_summary}
"""
    return message

def run_bot():
    send_message("🤖 <b>RAI NEWZ BOT</b> — Fetching your AI updates...")

    new_content = False

    # ─── YOUTUBE CHANNELS ───
    for channel in CHANNELS:
        message = fetch_youtube(channel["id"], channel["name"])
        if message:
            send_message(message)
            new_content = True
        time.sleep(15)

    # ─── NEWS WEBSITES ───
    for source in NEWS_SOURCES:
        message = fetch_news(source["url"], source["name"])
        if message:
            send_message(message)
            new_content = True
        time.sleep(15)

    if not new_content:
        send_message("✅ No new content since last check. You are up to date!")

    send_message("✅ <b>RAI NEWZ BOT</b> — All done! Stay ahead. 🚀")
# ─── RUN ───
run_bot()