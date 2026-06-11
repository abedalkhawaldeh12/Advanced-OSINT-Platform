import requests

def get_subdomains(domain: str):
    subdomains = set()
    try:
        # استخدام HackerTarget كبديل أكثر استقراراً وسرعة
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200 and "error" not in response.text.lower():
            lines = response.text.split('\n')
            for line in lines:
                if ',' in line:
                    sub = line.split(',')[0].strip()
                    if sub.endswith(domain) and sub != domain:
                        subdomains.add(sub)
    except Exception as e:
        return {"error": str(e)}
    
    return {"subdomains": list(subdomains)}
