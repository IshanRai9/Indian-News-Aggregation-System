import yt_dlp
import os
import uuid
import requests
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime

# ... (logging setup is same) ...

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def fetch_subreddit_posts(subreddit_name, limit=5):
    """
    Fetches latest posts. Adds 'red-' prefix to IDs.
    """
    url = f"https://www.reddit.com/r/{subreddit_name}/new.json?limit={limit}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            posts = []
            if 'data' in data and 'children' in data['data']:
                for child in data['data']['children']:
                    post_data = child['data']
                    
                    # PREFIX ID
                    original_id = post_data.get('id')
                    new_id = f"red-{original_id}"
                    
                    posts.append({
                        'id': new_id,
                        'original_id': original_id, # Keep ref if needed
                        'title': post_data.get('title'),
                        'selftext': post_data.get('selftext', ''),
                        'url': post_data.get('url', ''),
                        'created_utc': post_data.get('created_utc'),
                        'permalink': post_data.get('permalink'),
                        'subreddit': subreddit_name
                    })
            return posts
        elif response.status_code == 429:
            logging.warning(f"Rate limited on r/{subreddit_name}. Waiting...")
            time.sleep(5)
            return []
        else:
            logging.error(f"Failed to fetch r/{subreddit_name}: Status {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error scraping r/{subreddit_name}: {e}")
        return []

def download_media(url, post_id):
    """
    Downloads media from the URL using yt-dlp.
    Returns path to downloaded file or None.
    Prioritizes video, then image.
    """
    # Skip self-posts with no external URL
    if not url or 'reddit.com' in url and '/comments/' in url:
        return None

    try:
        # Unique filename to avoid collisions
        # We assume yt-dlp handles extension
        out_tmpl = os.path.join(DOWNLOAD_DIR, f"{post_id}_%(title)s.%(ext)s")
        
        ydl_opts = {
            'outtmpl': out_tmpl,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Prioritize MP4 video
            'quiet': True,
            'no_warnings': True,
            # 'max_filesize': 50 * 1024 * 1024, # Optional: Limit 50MB
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # yt-dlp sometimes merely returns the template or partial name depending on merges
            # We need to find the actual file if it differs, but prepare_filename is usually good.
            if os.path.exists(filename):
                logging.info(f"Downloaded media: {filename}")
                return filename
            else:
                logging.warning(f"Download reported success but file missing: {filename}")
                return None
                
    except Exception as e:
        logging.warning(f"Media download failed for {url}: {e}")
        return None

def scrape_external_url(url):
    """
    Attempts to scrape the main text content from a given URL.
    Returns truncated text or empty string on failure.
    """
    # Skip non-http/https or internal reddit / image links
    if not url.startswith('http') or 'reddit.com' in url or 'i.redd.it' in url or 'v.redd.it' in url or 'imgur' in url:
        return ""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        logging.info(f"Scraping external link: {url}")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from p tags
            paragraphs = soup.find_all('p')
            text_content = ' '.join([p.get_text() for p in paragraphs])
            
            # Clean up whitespace
            text_content = ' '.join(text_content.split())
            
            # Truncate to avoid huge context (approx 2000 chars)
            return text_content[:2000]
    except Exception as e:
        logging.warning(f"Failed to scrape external URL {url}: {e}")
    
    return ""
