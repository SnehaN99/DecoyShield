def analyze_behavior(ip, port):
    """
    Detect attacker behavior based on port targeting
    """

    # Common attack target ports
    high_risk_ports = [22, 23, 80, 443, 445]

    if port in high_risk_ports:
        return "ATTACKER"

    return "NORMAL"