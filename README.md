# 📰 Indian News Aggregation System

An intelligent, automated news aggregation pipeline that collects trending news from Indian Reddit communities, processes them using a local LLM (Qwen), and archives media to Google Drive.

---

## ✨ Features

- **Multi-Subreddit Monitoring** – Tracks 15+ Indian subreddits including `india`, `IndiaSpeaks`, `IndiaTech`, `ISRO`, and more.
- **External Content Extraction** – Scrapes article text from external links for richer context.
- **Media Pipeline** – Downloads images/videos via `yt-dlp` and uploads to Google Drive.
- **AI-Powered Processing** – Uses a local Qwen LLM to generate headlines, summaries, and detailed explanations.
- **Structured JSON Output** – Maintains a clean, timestamped database with automatic 7-day pruning.
- **Hourly Automation** – Designed to run on a scheduled loop.

---

## 🗂️ Project Structure

```
News/
├── main.py            # Entry point & orchestration
├── scraper.py         # Reddit data fetching & external content scraping
├── processor.py       # LLM integration (Qwen) for content analysis
├── uploader.py        # Google Drive media upload logic
├── storage.py         # JSON database & state management
├── config.py          # Configuration constants
├── setup_auth.py      # Google OAuth setup helper
├── requirements.txt   # Python dependencies
└── data/
    ├── Prompt.txt     # Agentic prompt documentation
    └── (runtime files ignored by git)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Google Cloud Project with Drive API enabled
- Local LLM setup (Qwen model)
- `yt-dlp` installed for media downloads

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/indian-news-aggregator.git
   cd indian-news-aggregator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/macOS
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Drive credentials**
   - Download your OAuth `credentials.json` from the Google Cloud Console.
   - Place it in the project root.
   - Run `python setup_auth.py` to generate `token.json`.

5. **Configure environment variables**
   Create a `.env` file:
   ```env
   REDDIT_USER_AGENT=your-user-agent-string
   ```

---

## ⚙️ Usage

Run the aggregator:

```bash
python main.py
```

For continuous hourly execution, set up a task scheduler (Windows Task Scheduler / `cron`).

---

## Output Schema

Each news entry in `indian_news_data.json` includes:

| Field           | Description                                      |
|-----------------|--------------------------------------------------|
| `id`            | Unique ID prefixed with `red-`                   |
| `headline`      | Cleaned, objective title                         |
| `description`   | 2-3 sentence summary (20-100 words)              |
| `explanation`   | Detailed reporter-style analysis (100-300 words) |
| `topic`         | Category (Politics, Tech, Sports, etc.)          |
| `datePosted`    | ISO 8601 timestamp                               |
| `dateOfConduct` | Actual event date                                |
| `subreddit`     | Source subreddit                                 |
| `post_url`      | Reddit permalink                                 |
| `news_url`      | External article link (if available)             |
| `media_name`    | Filename in Google Drive                         |
| `media_link`    | Web view link to media                           |

---

## 🔒 Security Notes

> ⚠️ **Never commit credentials or tokens to version control.**

The `.gitignore` is configured to exclude:
- `credentials.json` / `credentials2.json`
- `token.json`
- `.env`
- Runtime data files (`state.json`, `indian_news_data.json`)

---

## 📜 License

This project is licensed under **CC BY-NC 4.0** (Creative Commons Attribution-NonCommercial).

- ✅ **Free for**: Personal use, educational use, cloning, modification, sharing
- ❌ **Requires permission for**: Commercial or market use

See the [LICENSE](./LICENSE) file for details. For commercial licensing inquiries, contact the author.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.
