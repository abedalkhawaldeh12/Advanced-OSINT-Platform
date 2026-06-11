import requests

def get_wayback_urls(domain: str):
    urls = []
    try:
        # Limit to 50 results to keep the graph clean
        url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&collapse=urlkey&output=json&limit=50"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # The first item is the header ['urlkey', 'timestamp', 'original', 'mimetype', 'statuscode', 'digest', 'length']
            if len(data) > 1:
                for row in data[1:]:
                    original_url = row[2]
                    urls.append(original_url)
    except Exception as e:
        pass
        
    return {"archived_urls": urls}
