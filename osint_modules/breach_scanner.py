import requests
import time

def scan_breaches(emails: list, api_key: str = None):
    results = {"breached_emails": {}, "error": None}
    
    if not api_key:
        results["error"] = "No API key provided. Add HaveIBeenPwned key in Settings to scan emails."
        return results

    if not emails:
        results["error"] = "No emails found to scan for breaches."
        return results

    headers = {
        "hibp-api-key": api_key,
        "user-agent": "OSINT-Dashboard-Agent"
    }

    try:
        # Check only up to 5 emails to avoid rate limits
        for email_obj in emails[:5]:
            email = email_obj.get("value") if isinstance(email_obj, dict) else email_obj
            if not email: continue

            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                breaches = response.json()
                results["breached_emails"][email] = []
                for b in breaches:
                    results["breached_emails"][email].append({
                        "Name": b.get("Name"),
                        "Title": b.get("Title"),
                        "BreachDate": b.get("BreachDate"),
                        "DataClasses": b.get("DataClasses")
                    })
            elif response.status_code == 404:
                # 404 means no breach found, which is good!
                pass
            else:
                results["error"] = f"HIBP API Error: {response.status_code}"
                break
            
            # HIBP rate limit requires 1.5s delay between requests
            time.sleep(1.6)
            
    except Exception as e:
        results["error"] = str(e)

    return results
