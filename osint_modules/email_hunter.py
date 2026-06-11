import requests
import re
import urllib.parse

def harvest_emails(domain: str, api_key: str = None):
    results = {"emails": [], "pattern": None, "source": "hunter.io", "error": None}
    
    # محاولة استخدام Hunter.io إذا توفر المفتاح
    if api_key:
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                results["pattern"] = data.get("pattern")
                
                emails = data.get("emails", [])
                for email in emails:
                    results["emails"].append({
                        "value": email.get("value"),
                        "type": email.get("type"),
                        "position": email.get("position"),
                        "department": email.get("department")
                    })
                return results
            else:
                results["error"] = f"API Error: {response.status_code}. جاري تفعيل البحث المجاني..."
        except Exception as e:
            results["error"] = str(e)
            
    # الخطة البديلة: البحث المجاني (Free Scraping) عبر DuckDuckGo
    results["source"] = "Free Web Scraping"
    try:
        query = urllib.parse.quote(f'"{domain}" email OR contact "@{domain}"')
        url = f"https://html.duckduckgo.com/html/?q={query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            email_pattern = r'[a-zA-Z0-9._%+-]+@' + re.escape(domain)
            found_emails = set(re.findall(email_pattern, html, re.IGNORECASE))
            
            for email in found_emails:
                results["emails"].append({
                    "value": email.lower(),
                    "type": "Scraped",
                    "position": "Unknown",
                    "department": "Unknown"
                })
        else:
            if not results["error"]:
                results["error"] = "Free scraping blocked by search engine."
            
    except Exception as e:
        if not results["error"]:
            results["error"] = f"Scraping error: {str(e)}"
        
    return results
