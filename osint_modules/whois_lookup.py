import whois

def get_whois_info(domain: str):
    try:
        w = whois.whois(domain)
        # return basic info
        return {
            "registrar": w.registrar,
            "creation_date": str(w.creation_date[0]) if isinstance(w.creation_date, list) else str(w.creation_date),
            "expiration_date": str(w.expiration_date[0]) if isinstance(w.expiration_date, list) else str(w.expiration_date),
            "name_servers": w.name_servers,
            "emails": w.emails
        }
    except Exception as e:
        return {"error": str(e)}
