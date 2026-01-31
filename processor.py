from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import logging
from datetime import datetime
from config import TOPICS

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global model/tokenizer to avoid reloading per post
_tokenizer = None
_model = None

def get_model_and_tokenizer():
    global _tokenizer, _model
    if _model is None:
        logging.info("Loading Qwen model...")
        model_name = "Qwen/Qwen3-0.6B"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForCausalLM.from_pretrained(model_name)
        # Move to GPU if available
        if torch.cuda.is_available():
            _model = _model.to("cuda")
    return _tokenizer, _model

def clean_json_string(json_str):
    """
    Cleans the model response to extract just the JSON part.
    """
    json_str = json_str.strip()
    # Try to find the first '{' and last '}'
    start_idx = json_str.find('{')
    end_idx = json_str.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        json_str = json_str[start_idx:end_idx+1]
        
    return json_str

def process_post(post, external_content=""):
    """
    Sends post data to local Qwen model to generate structured news entry.
    """
    tokenizer, model = get_model_and_tokenizer()
    
    # Enrich content if external text is available
    content_context = post['selftext'][:1000]
    if external_content:
        content_context += f"\n\n[External Article Context]: {external_content[:1500]}"
    
    prompt = f"""
    You are a news aggregation AI. Analyze the following Reddit post and context to create a news database entry.
    
    Subreddit: r/{post['subreddit']}
    Title: {post['title']}
    Content: {content_context}... (truncated)
    Post URL: {post['url']}
    Posted Date (UTC timestamp): {post['created_utc']}
    
    REQUIRED JSON FORMAT:
    {{
        "headline": "Cleaned up title, objective tone",
        "explanation": "Provide detailed 500 word explanation of the event/news as if you are reporting. Provide context and background.",
        "datePosted": "ISO 8601 format",
        "dateOfConduct": "Estimated date of event (ISO 8601) or same as datePosted",
        "topic": "One of: {', '.join(TOPICS)}",
        "subreddit": "{post['subreddit']}",
        "post_url": "https://www.reddit.com{post['permalink']}",
        "news_url": "{post['url'] if 'reddit.com' not in post['url'] else ''}"
    }}
    
    Output ONLY the valid JSON object. Do not add any markdown formatting or extra text.
    """
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
        
        # Move inputs to same device as model
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        outputs = model.generate(**inputs, max_new_tokens=1024, temperature=0.7)
        # Decode only the new tokens
        response_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
        
        logging.info(f"Raw model response: {response_text[:100]}...")

        clean_text = clean_json_string(response_text)
        data = json.loads(clean_text)
        
        # Enforce consistency / Default values if model missed them
        if 'datePosted' not in data:
            dt = datetime.fromtimestamp(post['created_utc'])
            data['datePosted'] = dt.isoformat()
            
        if 'topic' not in data:
            data['topic'] = 'Other'

        # Ensure new fields are present even if model hallucinated omitting them
        if 'subreddit' not in data:
            data['subreddit'] = post['subreddit']
        if 'post_url' not in data:
            data['post_url'] = f"https://www.reddit.com{post['permalink']}"
        if 'news_url' not in data:
            data['news_url'] = post['url'] if 'reddit.com' not in post['url'] else ''
            
        return data
        
    except Exception as e:
        logging.error(f"Error processing post {post['id']}: {e}")
        return None