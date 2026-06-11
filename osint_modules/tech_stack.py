import requests
from bs4 import BeautifulSoup

def get_tech_stack(domain: str):
    techs = []
    try:
        url = f"http://{domain}"
        response = requests.get(url, timeout=5)
        headers = response.headers
        
        # Check Headers
        if "Server" in headers:
            techs.append(f"Server: {headers['Server']}")
        if "X-Powered-By" in headers:
            techs.append(f"Powered-By: {headers['X-Powered-By']}")
            
        # Parse HTML for common signs
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check generators
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            techs.append(f"Generator: {generator['content']}")
            
        # Basic script checks
        scripts = [script.get('src', '').lower() for script in soup.find_all('script') if script.get('src')]
        if any('wp-content' in src for src in scripts):
            techs.append("CMS: WordPress")
        if any('react' in src for src in scripts):
            techs.append("Framework: React")
        if any('vue' in src for src in scripts):
            techs.append("Framework: Vue.js")
            
    except Exception:
        pass
        
    return {"tech_stack": list(set(techs))}
