import requests

def get_ip_geo(ip_address: str):
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "country": data.get("country"),
                    "city": data.get("city"),
                    "isp": data.get("isp"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon")
                }
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Could not fetch geo info"}
