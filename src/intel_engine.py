import requests
import socket

def get_ip_intelligence(ip):

    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=3)
        data = response.json()

        country = data.get("country", "Unknown")
        city = data.get("city", "Unknown")

    except:
        country = "Unknown"
        city = "Unknown"

    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        hostname = "Unknown"

    return country, city, hostname