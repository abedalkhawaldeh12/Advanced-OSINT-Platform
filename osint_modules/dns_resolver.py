import dns.resolver

def get_dns_records(domain: str):
    records = {"A": [], "MX": [], "TXT": []}
    try:
        # A records (IPv4)
        a_records = dns.resolver.resolve(domain, 'A')
        records["A"] = [r.to_text() for r in a_records]
    except Exception:
        pass

    try:
        # MX records (Mail)
        mx_records = dns.resolver.resolve(domain, 'MX')
        records["MX"] = [r.exchange.to_text() for r in mx_records]
    except Exception:
        pass

    try:
        # TXT records
        txt_records = dns.resolver.resolve(domain, 'TXT')
        records["TXT"] = [r.to_text() for r in txt_records]
    except Exception:
        pass

    return records
