
import os
import requests

ABUSE_API_KEY = os.getenv("ABUSEIPDB_API_KEY")


def check_abuse_ip(ip):
    if not ABUSE_API_KEY:
        print("[ERROR] AbuseIPDB API key is missing.")
        return 0, 0

    url = "https://api.abuseipdb.com/api/v2/check"

    headers = {
        "Key": ABUSE_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()["data"]

        confidence = data["abuseConfidenceScore"]
        reports = data["totalReports"]

        return confidence, reports

    except requests.RequestException as e:
        print("[API ERROR]", e)
        return 0, 0
    except (KeyError, ValueError, TypeError) as e:
        print("[DATA ERROR]", e)
        return 0, 0


def enrich_threat(ip, confidence, reports, behavior=None, is_vpn=False):

    risk_score = 0

    # AbuseIPDB
    risk_score += confidence * 0.4
    risk_score += min(reports, 50) * 0.2

    # Behavior
    if behavior == "ATTACKER":
        risk_score += 20

    # VPN / Proxy
    if is_vpn:
        risk_score += 15

    # Normalize
    risk_score = min(risk_score, 100)

    return {
        "risk_score": risk_score
    }
