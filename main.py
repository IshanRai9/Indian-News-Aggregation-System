import schedule
import time
import logging
import os
from dotenv import load_dotenv
from config import SUBREDDITS
from scraper import fetch_subreddit_posts, scrape_external_url, download_media
from processor import process_post
from storage import load_state, save_state, append_news_data, prune_data
from uploader import upload_file

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def job():
    logging.info("Starting scheduled job...")
    
    # Reload state
    state = load_state()
    processed_ids = set(state.get('processed_ids', []))
    
    new_entries = []
    
    for sub in SUBREDDITS:
        logging.info(f"Checking r/{sub}...")
        posts = fetch_subreddit_posts(sub)
        
        current_run_processed_ids = []
        for post in posts:
            if post['id'] in processed_ids:
                continue
            
            logging.info(f"Processing new post: {post['title']}")
            
            # 1. Scrape external text
            external_content = ""
            if post['url'] and 'reddit.com' not in post['url']:
                external_content = scrape_external_url(post['url'])
                if external_content:
                    logging.info(f"Scraped {len(external_content)} chars from external link")
            
            # 2. Download Media (Image/Video)
            media_path = download_media(post['url'], post['id'])
            uploaded_media_name = None
            uploaded_media_link = None
            
            # 3. Upload to Drive if downloaded
            if media_path:
                upload_result = upload_file(media_path)
                if upload_result:
                    uploaded_media_name, media_id, uploaded_media_link = upload_result
                    logging.info(f"Media uploaded: {uploaded_media_name}")
                
                # Cleanup local file
                try:
                    os.remove(media_path)
                except OSError:
                    pass

            # 4. Process with AI
            news_item = process_post(post, external_content)
            
            if news_item:
                # Add media fields
                if uploaded_media_name:
                    news_item['media_name'] = uploaded_media_name
                    news_item['media_link'] = uploaded_media_link
                
                new_entries.append(news_item)
                current_run_processed_ids.append(post['id'])
                processed_ids.add(post['id'])
            
            # Rate limit protection: Sleep between EACH post strictly
            time.sleep(4)
                
        if new_entries:
            append_news_data(new_entries)
            # Update state immediately
            state['processed_ids'] = list(processed_ids)
            save_state(state)
            logging.info(f"Saved {len(new_entries)} entries for r/{sub}")
            new_entries = [] # Reset for next batch
            
    logging.info("Job finished.")

def main():
    load_dotenv()
    
    # Gemini config removed/deprecated, using local model now
    # if not configure_gemini(): ...

    logging.info("Indian News Aggregator System Initialized")
    
    # Run immediately on startup
    job()
    
    # Schedule hourly
    schedule.every(1).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
