# 🛡️ DecoyShield

### A Deception-Based Framework for Proactive Threat Detection and Cyber Defense

DecoyShield is a Python-based cybersecurity project that explores **honeypot technology and cyber deception** to monitor suspicious network activity, collect attack-related information, and analyze potential attacker behavior in a controlled environment.

The framework uses simulated network services to attract suspicious connections and observe interactions, demonstrating how deception-based techniques can support proactive threat monitoring.

---

## 📌 Project Overview

Traditional security mechanisms often focus on detecting threats through conventional security controls and monitoring systems. DecoyShield explores an additional layer of defense through deception-based techniques.

The project focuses on:

- Network activity monitoring
- Attacker behavior analysis
- Threat classification and risk scoring
- Attack information logging
- Threat intelligence enrichment
- Security event visualization

## ✨ Key Features

- **Multi-Port Honeypot:** Simulates network services on decoy ports to observe incoming connections.
- **Behavioral Analysis:** Examines connection patterns and suspicious network activity.
- **Threat Classification:** Uses risk scoring to categorize suspicious activity into LOW, MEDIUM, and HIGH levels.
- **Adaptive Deception:** Explores simulated service responses and controlled interactive environments.
- **Threat Intelligence Integration:** Supports AbuseIPDB-based IP reputation enrichment when a valid API key is configured.
- **Attack Logging:** Uses SQLite to store attack-related information.
- **Email Alerts:** Supports email notifications for security events using environment-based configuration.
- **Desktop Dashboard:** Provides a PyQt5 graphical interface for monitoring attack activity and displaying security information.
- **Attack Map Visualization:** Uses Folium to visualize honeypot and attack-source locations based on available geographic information.

*Note: Features described in the proposed framework and research documentation may differ from the functionality implemented in individual project versions. Some integrations require additional configuration.*

## 🧰 Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Desktop GUI | PyQt5 |
| Database | SQLite |
| Data Visualization | Matplotlib |
| Attack Map Visualization | Folium |
| Networking | Python Socket Programming |
| Network Testing | Nmap, Netcat |
| Threat Intelligence | AbuseIPDB API |
| Notifications | SMTP Email Alerts |
| Platform | Windows |

## 🏗️ System Architecture

The proposed DecoyShield framework consists of six major layers:

1. **Network and Access Layer** – Handles incoming network connections.
2. **Intelligence API Layer** – Retrieves external threat intelligence.
3. **Analytics and Decision Engine** – Analyzes activity and calculates risk scores.
4. **Deception Layer** – Provides simulated services and controlled interactions.
5. **Storage and Alerting Layer** – Maintains attack records and security notifications.
6. **User Interface Layer** – Presents monitoring information through the PyQt5 desktop dashboard.

## 🔍 Threat Intelligence and Risk Scoring

DecoyShield supports AbuseIPDB integration to enrich suspicious IP addresses with external reputation information.

The integration can retrieve:

- Abuse confidence score
- Total reported incidents

A custom risk-scoring mechanism considers reputation information and observed behavior to calculate a risk score.

The AbuseIPDB integration requires an API key supplied through the `ABUSEIPDB_API_KEY` environment variable. API access is not available when the key is missing.

## 🧪 Testing and Evaluation

The project is evaluated through controlled testing scenarios, including:

- Network port scanning using Nmap
- Service probing
- Connection attempts using Netcat
- Simulated command-based interactions

These scenarios help evaluate the system's ability to observe suspicious network activity and analyze attacker interactions.

## 📸 Dashboard Screenshots

### 1. Live Threat Dashboard

![Live Threat Dashboard](screenshots/live-threat-dashboard.png)

### 2. Dashboard Overview

![Dashboard Overview](screenshots/dashboard-overview.png)

## 📁 Repository Structure

```text
DecoyShield/
│
├── src/
│   ├── main.py
│   ├── gui_dashboard.py
│   ├── dashboard.py
│   ├── background_monitor.py
│   ├── database.py
│   ├── ports.py
│   ├── alerts.py
│   ├── attacker_profile.py
│   ├── behavior_engine.py
│   ├── intel_engine.py
│   ├── intent_engine.py
│   ├── threat_intel.py
│   ├── icon.ico
│   └── icon.png
│
├── screenshots/
│   ├── live-threat-dashboard.png
│   └── dashboard-overview.png
│
├── .gitignore
└── README.md
```

## 🚀 Future Enhancements

- AI-based threat detection and behavioral analysis
- Automated incident response
- SIEM and firewall integration
- Cloud-based deployment
- Enhanced threat intelligence enrichment

## 👩‍💻 Contributors

Developed as an academic cybersecurity project by students of the Department of Computer Science and Engineering (Cyber Security).

**Vimal Jyothi Engineering College**  
Chemperi, Kannur, Kerala, India.

## ⚠️ Disclaimer

DecoyShield is developed for educational and cybersecurity research purposes. It must only be deployed and tested in authorized, controlled environments. The project must not be used to monitor or interact with systems without permission.
