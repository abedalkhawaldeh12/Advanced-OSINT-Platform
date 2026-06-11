import requests
from bs4 import BeautifulSoup
import re

def extract_social_links(domain: str):
    social_links = []
    social_platforms = {
        "twitter.com", "facebook.com", "linkedin.com", 
        "github.com", "instagram.com", "youtube.com"
    }
    
    try:
        url = f"http://{domain}"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            for platform in social_platforms:
                if platform in href:
                    social_links.append(href)
                    
    except Exception:
        pass
        
    return {"social_links": list(set(social_links))}
