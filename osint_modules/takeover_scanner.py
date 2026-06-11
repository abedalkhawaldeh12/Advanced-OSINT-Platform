import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

TAKEOVER_SIGNATURES = {
    "GitHub Pages": "There isn't a GitHub Pages site here.",
    "AWS S3": "NoSuchBucket",
    "Heroku": "No such app",
    "Shopify": "Sorry, this shop is currently unavailable.",
    "Tumblr": "Whatever you were looking for doesn't currently exist at this address.",
    "Ghost": "The thing you were looking for is no longer here",
    "Pantheon": "The excessively resolved domain",
    "Surge.sh": "project not found",
    "Strikingly": "page not found"
}

def check_subdomain(subdomain):
    # Check both HTTP and HTTPS
    protocols = ['http://', 'https://']
    for proto in protocols:
        try:
            url = f"{proto}{subdomain}"
            # Short timeout to keep it fast
            response = requests.get(url, timeout=3, allow_redirects=True)
            body = response.text
            
            for service, signature in TAKEOVER_SIGNATURES.items():
                if signature in body:
                    return {"subdomain": subdomain, "service": service, "status": "Vulnerable"}
        except:
            # Ignore timeouts and connection errors
            continue
    return None

def scan_takeovers(subdomains: list):
    results = {"vulnerable": [], "error": None}
    
    if not subdomains:
        return results
        
    # Limit to first 30 subdomains to prevent very long scans
    targets = subdomains[:30]
    
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(check_subdomain, sub): sub for sub in targets}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    results["vulnerable"].append(res)
    except Exception as e:
        results["error"] = str(e)
        
    return results
