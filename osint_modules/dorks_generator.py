import urllib.parse

def generate_dorks(domain: str):
    """
    Generates a dictionary of useful Google Dorks for the target domain.
    These URLs will be clickable from the dashboard.
    """
    dorks = {
        "Exposed Documents": f"site:{domain} ext:doc | ext:docx | ext:odt | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv",
        "Directory Listing": f"site:{domain} intitle:index.of",
        "Configuration Files": f"site:{domain} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini | ext:env",
        "Database Files": f"site:{domain} ext:sql | ext:dbf | ext:mdb",
        "Log Files": f"site:{domain} ext:log",
        "Backup and Old Files": f"site:{domain} ext:bkf | ext:bkp | ext:bak | ext:old | ext:backup",
        "Login Pages": f"site:{domain} inurl:login | inurl:signin | intitle:Login | intitle:\"sign in\" | inurl:auth",
        "SQL Errors": f"site:{domain} intext:\"sql syntax near\" | intext:\"syntax error has occurred\" | intext:\"incorrect syntax near\" | intext:\"unexpected end of SQL command\" | intext:\"Warning: mysql_connect()\" | intext:\"Warning: mysql_query()\" | intext:\"Warning: pg_connect()\"",
        "Publicly Exposed Documents (PDF)": f"site:{domain} ext:pdf",
        "WordPress Admin": f"site:{domain} inurl:wp-admin | inurl:wp-content"
    }
    
    # Generate Google Search URLs
    dork_links = {}
    for title, dork_query in dorks.items():
        encoded_query = urllib.parse.quote_plus(dork_query)
        dork_links[title] = f"https://www.google.com/search?q={encoded_query}"
        
    return {
        "dorks_queries": dorks,
        "dorks_links": dork_links
    }
