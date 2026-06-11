import requests

def scan_vulnerabilities(domain: str):
    results = {
        "missing_headers": [],
        "warnings": [],
        "robots_txt": "Not Found"
    }
    
    url = f"http://{domain}"
    try:
        # Check HTTP Headers
        response = requests.get(url, timeout=10, allow_redirects=True)
        headers = {k.lower(): v for k, v in response.headers.items()}
        
        security_headers = {
            "strict-transport-security": "HSTS (Strict-Transport-Security) is missing. The site may be vulnerable to downgrade attacks.",
            "x-frame-options": "X-Frame-Options is missing. The site may be vulnerable to Clickjacking.",
            "content-security-policy": "CSP (Content-Security-Policy) is missing. The site may be vulnerable to XSS attacks.",
            "x-content-type-options": "X-Content-Type-Options is missing. The site may be vulnerable to MIME sniffing."
        }
        
        for header, warning in security_headers.items():
            if header not in headers:
                results["missing_headers"].append(header)
                results["warnings"].append(warning)
                
        # Check for Server signature
        server = headers.get('server', '')
        x_powered_by = headers.get('x-powered-by', '')
        
        if server:
            results["warnings"].append(f"Server header exposes version: {server}")
        if x_powered_by:
            results["warnings"].append(f"X-Powered-By header exposes framework: {x_powered_by}")

        # Check robots.txt
        robots_url = f"{response.url.rstrip('/')}/robots.txt"
        robots_resp = requests.get(robots_url, timeout=5)
        if robots_resp.status_code == 200:
            lines = robots_resp.text.split('\\n')
            disallowed = [line for line in lines if line.lower().startswith('disallow')]
            results["robots_txt"] = f"Found ({len(disallowed)} disallowed paths)"
            
    except Exception as e:
        results["error"] = str(e)
        
    return results
