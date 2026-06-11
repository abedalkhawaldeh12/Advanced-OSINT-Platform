from concurrent.futures import ThreadPoolExecutor, as_completed
from osint_modules.dns_resolver import get_dns_records
from osint_modules.whois_lookup import get_whois_info
from osint_modules.subdomain_enum import get_subdomains
from osint_modules.ip_geo import get_ip_geo
from osint_modules.port_scanner import scan_ports
from osint_modules.tech_stack import get_tech_stack
from osint_modules.ssl_analyzer import get_ssl_info
from osint_modules.wayback_urls import get_wayback_urls
from osint_modules.social_extractor import extract_social_links
from osint_modules.vuln_scanner import scan_vulnerabilities
from osint_modules.dorks_generator import generate_dorks
from osint_modules.email_hunter import harvest_emails
from osint_modules.breach_scanner import scan_breaches
from osint_modules.takeover_scanner import scan_takeovers

def analyze_target(domain: str, api_keys: dict = None):
    if api_keys is None:
        api_keys = {}
        
    results = {}
    
    # Run initial tasks concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(get_dns_records, domain): "dns",
            executor.submit(get_whois_info, domain): "whois",
            executor.submit(get_subdomains, domain): "subdomains",
            executor.submit(get_tech_stack, domain): "tech_stack",
            executor.submit(get_ssl_info, domain): "ssl",
            executor.submit(get_wayback_urls, domain): "wayback",
            executor.submit(extract_social_links, domain): "social",
            executor.submit(scan_vulnerabilities, domain): "vulns",
            executor.submit(generate_dorks, domain): "dorks",
            executor.submit(harvest_emails, domain, api_keys.get("hunter")): "emails"
        }
        
        for future in as_completed(futures):
            module_name = futures[future]
            try:
                results[module_name] = future.result()
            except Exception as e:
                results[module_name] = {"error": str(e)}

    # Secondary tasks that depend on first round
    ips = results.get("dns", {}).get("A", [])
    geo_results = {}
    port_results = {}
    
    emails = results.get("emails", {}).get("emails", [])
    subs = results.get("subdomains", {}).get("subdomains", [])
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        geo_futures = {executor.submit(get_ip_geo, ip): ip for ip in ips}
        port_futures = {executor.submit(scan_ports, ip): ip for ip in ips[:2]} 
        breach_future = executor.submit(scan_breaches, emails, api_keys.get("hibp"))
        takeover_future = executor.submit(scan_takeovers, subs)
        
        for future in as_completed(geo_futures):
            ip = geo_futures[future]
            res = future.result()
            # حفظ النتيجة فقط إذا كانت تحتوي على خطوط طول وعرض صحيحة
            if res and not "error" in res and res.get("lat") and res.get("lon"):
                geo_results[ip] = res
            
        for future in as_completed(port_futures):
            ip = port_futures[future]
            port_results[ip] = future.result()
            
        try:
            results["breaches"] = breach_future.result()
        except Exception as e:
            results["breaches"] = {"error": str(e)}
            
        try:
            results["takeovers"] = takeover_future.result()
        except Exception as e:
            results["takeovers"] = {"error": str(e)}
            
    results["geo"] = geo_results
    results["ports"] = port_results
    
    # Transform results to Graph Nodes and Edges
    nodes = []
    edges = []
    
    # Root Node
    nodes.append({"id": domain, "label": domain, "group": "target"})
    
    # DNS Nodes
    for idx, ip in enumerate(ips):
        node_id = f"ip_{idx}"
        nodes.append({"id": node_id, "label": f"IP: {ip}", "group": "ip"})
        edges.append({"from": domain, "to": node_id})
        
        geo = geo_results.get(ip, {})
        if geo and "country" in geo:
            geo_id = f"geo_{idx}"
            nodes.append({"id": geo_id, "label": f"{geo.get('country')}, {geo.get('city')}", "group": "geo"})
            edges.append({"from": node_id, "to": geo_id})
            
        ports = port_results.get(ip, {}).get("open_ports", [])
        if ports:
            ports_id = f"ports_{idx}"
            nodes.append({"id": ports_id, "label": f"Ports: {', '.join(map(str, ports))}", "group": "port"})
            edges.append({"from": node_id, "to": ports_id})
            
    # Subdomains
    for idx, sub in enumerate(subs[:15]):
        sub_id = f"sub_{idx}"
        nodes.append({"id": sub_id, "label": sub, "group": "subdomain"})
        edges.append({"from": domain, "to": sub_id})
        
    # Tech Stack
    techs = results.get("tech_stack", {}).get("tech_stack", [])
    for idx, tech in enumerate(techs):
        tech_id = f"tech_{idx}"
        nodes.append({"id": tech_id, "label": tech, "group": "tech"})
        edges.append({"from": domain, "to": tech_id})
        
    # Social Links
    socials = results.get("social", {}).get("social_links", [])
    for idx, link in enumerate(socials):
        soc_id = f"soc_{idx}"
        nodes.append({"id": soc_id, "label": link, "group": "social"})
        edges.append({"from": domain, "to": soc_id})

    # SSL Info
    ssl_info = results.get("ssl", {})
    if ssl_info and "issuer" in ssl_info:
        ssl_id = "ssl_0"
        nodes.append({"id": ssl_id, "label": f"SSL Issuer: {ssl_info['issuer']}", "group": "ssl"})
        edges.append({"from": domain, "to": ssl_id})

    # WHOIS Info
    whois_info = results.get("whois", {})
    if whois_info and "registrar" in whois_info and whois_info["registrar"]:
        reg_id = "whois_reg"
        nodes.append({"id": reg_id, "label": f"Registrar: {whois_info['registrar']}", "group": "whois"})
        edges.append({"from": domain, "to": reg_id})

    # DNS MX & TXT
    mx_records = results.get("dns", {}).get("MX", [])
    if mx_records:
        for idx, mx in enumerate(mx_records[:3]):
            mx_id = f"mx_{idx}"
            nodes.append({"id": mx_id, "label": f"MX: {mx}", "group": "dns_mx"})
            edges.append({"from": domain, "to": mx_id})

    txt_records = results.get("dns", {}).get("TXT", [])
    if txt_records:
        for idx, txt in enumerate(txt_records[:2]):
            txt_id = f"txt_{idx}"
            short_txt = txt[:30] + "..." if len(txt) > 30 else txt
            nodes.append({"id": txt_id, "label": f"TXT: {short_txt}", "group": "dns_txt"})
            edges.append({"from": domain, "to": txt_id})

    # Wayback URLs
    wayback = results.get("wayback", {}).get("archived_urls", [])
    if wayback:
        for idx, url in enumerate(wayback[:5]):
            wb_id = f"wb_{idx}"
            short_url = url.split("?")[0][:40]
            nodes.append({"id": wb_id, "label": short_url, "group": "wayback"})
            edges.append({"from": domain, "to": wb_id})

    # Vulnerabilities (Warnings)
    warnings = results.get("vulns", {}).get("warnings", [])
    if warnings:
        for idx, warning in enumerate(warnings[:4]):
            vuln_id = f"vuln_{idx}"
            nodes.append({"id": vuln_id, "label": f"Alert: {warning[:15]}...", "group": "vuln"})
            edges.append({"from": domain, "to": vuln_id})
            
    # Dorks
    dorks_queries = results.get("dorks", {}).get("dorks_queries", {})
    if dorks_queries:
        dork_id = "dork_main"
        nodes.append({"id": dork_id, "label": "Google Dorks", "group": "dork"})
        edges.append({"from": domain, "to": dork_id})
        
    # Emails
    if emails:
        email_id = "emails_main"
        nodes.append({"id": email_id, "label": f"{len(emails)} Emails Found", "group": "social"})
        edges.append({"from": domain, "to": email_id})

    # Breaches
    breached_emails = results.get("breaches", {}).get("breached_emails", {})
    if breached_emails:
        breach_id = "breach_main"
        nodes.append({"id": breach_id, "label": "Data Breaches Found!", "group": "vuln"})
        edges.append({"from": domain, "to": breach_id})
        
    # Takeovers
    takeovers = results.get("takeovers", {}).get("vulnerable", [])
    if takeovers:
        tk_id = "takeover_main"
        nodes.append({"id": tk_id, "label": "Subdomain Takeover Alert!", "group": "vuln"})
        edges.append({"from": domain, "to": tk_id})

    return {"nodes": nodes, "edges": edges, "raw_data": results}
