import socket
import threading
import time
from datetime import datetime
from database import log_attack, update_commands,update_attacker_type
from ports import generate_ports
from intel_engine import get_ip_intelligence
from threat_intel import check_abuse_ip,enrich_threat
from behavior_engine import analyze_behavior
from attacker_profile import classify_attacker
from intent_engine import analyze_intent
knock_state = {}
authorized_ip = {}
knock_sequence = [1111, 2222, 3333]
active_ports = set()
attack_counter = {}
scan_tracker = {}
running = False
AUTH_WINDOW = 120

# -------------------------------
# SANDBOX (UNCHANGED)
# -------------------------------
def start_sandbox(client, ip, attack_id):
    commands = []
    try:
        client.settimeout(1.5)

        client.sendall(b"\nWelcome to Legacy Admin Console\n")
        client.sendall(b"login: ")

        username = client.recv(1024)
        if not username:
            return

        client.sendall(b"password: ")
        password = client.recv(1024)
        if not password:
            return

        client.sendall(b"\nLogin successful!\n")

        while True:
            client.sendall(b"root@server:~# ")

            try:
                data = client.recv(1024)
            except socket.timeout:
                break

            if not data:
                break

            command = data.decode(errors="ignore").strip()

            print(f"[SANDBOX CMD] {ip} -> {command}")
            commands.append(command)
            update_commands(attack_id, "\n".join(commands))

            if command == "exit":
                client.sendall(b"logout\n")
                break
            else:
                client.sendall(b"command not found\n")

    except Exception as e:
        if "10054" not in str(e):
            print("Sandbox error:", e)

    return "\n".join(commands) if commands else "no commands"


# -------------------------------
# FAKE BANNER
# -------------------------------
def send_fake_banner(client, attack_id):
    commands = []
    try:
        client.settimeout(2)

        client.sendall(b"\nUbuntu 20.04 LTS\n")
        client.sendall(b"Last login: Thu Mar 6 10:22:41\n")

        while True:
            client.sendall(b"root@decoy:~# ")

            try:
                data = client.recv(1024)
            except socket.timeout:
                break

            if not data:
                break

            command = data.decode(errors="ignore").strip()
            commands.append(command)

            update_commands(attack_id, "\n".join(commands))

            if command == "whoami":
                client.sendall(b"root\n")
            elif command == "pwd":
                client.sendall(b"/root\n")
            elif command == "ls":
                client.sendall(b"file.txt logs backup passwords.txt\n")
            elif command.startswith("cat"):
                if "passwords.txt" in command:
                    client.sendall(b"admin:admin123\nroot:toor\n")
                elif "file.txt" in command:
                    client.sendall(b"note: setup completed, need to check remote access\ntodo: clean old backup files\n")
                elif "logs" in command:
                    client.sendall(b"[2026-03-21 08:11:02] INFO: System boot completed\n[2026-03-21 08:15:33] INFO: User login - admin\n")
                else:
                    client.sendall("No data")        
            elif command == "exit":
                client.sendall(b"logout\n")
                break
            else:
                client.sendall(b"command not found\n")

    except Exception as e:
        print("Fake banner error:", e)

    return "\n".join(commands) if commands else "no commands"


# -------------------------------
# FORWARDING
# -------------------------------
def forward_to_real_service(client, port):
    try:
        real_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        real_server.connect(("127.0.0.1", port))

        def client_to_server():
            while True:
                try:
                    data = client.recv(4096)
                    if not data:
                        break
                    real_server.sendall(data)
                except:
                    break

        def server_to_client():
            while True:
                try:
                    data = real_server.recv(4096)
                    if not data:
                        break
                    client.sendall(data)
                except:
                    break

        t1 = threading.Thread(target=client_to_server)
        t2 = threading.Thread(target=server_to_client)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    except Exception as e:
        print("Forwarding error:", e)

    finally:
        try:
            real_server.close()
        except:
            pass


# -------------------------------
# MAIN MONITOR
# -------------------------------

def monitor_port(port):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", port))
    except OSError as e:
        print(f"[SKIPPED] Port {port}: {e}")
        server.close()
        return

    server.listen(5)
    server.settimeout(1.0)

    print(f"[MONITOR] Listening on {port}")

    try:
        while running:

            try:
                client, addr = server.accept()

            except socket.timeout:
                continue

            except OSError:
                break

            try:
                ip = addr[0]
                is_vpn = False

                # -------------------------------
                # ABSOLUTE AUTH PRIORITY
                # -------------------------------
                if ip in authorized_ip:
                    expiry = authorized_ip[ip]

                    if time.time() < expiry:

                        print(f"[AUTHORIZED ACCESS] {ip} -> {port}")

                        try:
                            message = f"""
                            [AUTHORIZED USER LOGIN]
                            IP: {ip}
                            PORT: {port}
                            """
                            client.sendall(message.encode())
                            client.sendall(
                                b"Welcome back, authorized user!\n"
                            )
                        except OSError:
                            pass

                        timestamp = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        log_attack(
                            ip, port, timestamp,
                            "Authorized Access", 0, "AUTHORIZED",
                            "Local", "Internal", "authorized-user",
                            100, 0, 0,
                            "Authorized login", "Legitimate User",
                            f"Accessed real service on port {port}"
                        )

                        forward_to_real_service(client, port)
                        continue

                # -------------------------------
                # INIT TRACKER
                # -------------------------------
                if ip not in scan_tracker:
                    scan_tracker[ip] = []

                # -------------------------------
                # PORT KNOCKING
                # -------------------------------
                if port in knock_sequence:

                    if ip not in knock_state:
                        knock_state[ip] = {
                            "step": 0,
                            "last_time": 0
                        }

                    state = knock_state[ip]
                    current_time = time.time()

                    if current_time - state["last_time"] > 15:
                        state["step"] = 0

                    expected_port = knock_sequence[state["step"]]

                    if port == expected_port:

                        print(
                            f"[KNOCK {state['step'] + 1}/3] {ip}"
                        )

                        state["step"] += 1
                        state["last_time"] = current_time

                        if state["step"] == len(knock_sequence):

                            print(f"[PORT KNOCK SUCCESS] {ip}")

                            authorized_ip[ip] = (
                                time.time() + AUTH_WINDOW
                            )

                            del knock_state[ip]

                            timestamp = datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )

                            log_attack(
                                ip, 0, timestamp,
                                "Port Knock Success", 0, "AUTHORIZED",
                                "Local", "Internal", "authorized-user",
                                100, 0, 0,
                                "Port Knocking", "Legitimate User",
                                "Sequence completed"
                            )

                            # GUI UPDATE
                            try:
                                import gui_dashboard

                                if (
                                    hasattr(gui_dashboard, "window")
                                    and gui_dashboard.window
                                ):
                                    gui_dashboard.window.show_knock_success(ip)
                                    gui_dashboard.window.attack_signal.emit()
                                    gui_dashboard.window.load_data()

                            except Exception as e:
                                print("GUI error:", e)

                        client.close()
                        continue

                    else:
                        if ip in knock_state:
                            del knock_state[ip]

                        client.close()
                        continue

                # -------------------------------
                # SCAN TRACKING
                # -------------------------------
                scan_tracker[ip].append(time.time())

                scan_tracker[ip] = [
                    t for t in scan_tracker[ip]
                    if time.time() - t < 15
                ]

                attack_counter[ip] = (
                    attack_counter.get(ip, 0) + 1
                )

                behavior = analyze_behavior(ip, port)

                confidence, reports = check_abuse_ip(ip)

                intel = enrich_threat(
                    ip, confidence, reports, behavior, is_vpn
                )

                risk_score = intel["risk_score"]
                scan_count = len(scan_tracker[ip])
                attack_count = attack_counter[ip]

                risk_factor = 0

                # Behavior weight
                if behavior == "ATTACKER":
                    risk_factor += 30

                # Scan intensity
                if scan_count > 10:
                    risk_factor += 25
                elif scan_count > 5:
                    risk_factor += 15

                # Threat intelligence
                risk_factor += min(risk_score, 30)

                # Persistence
                if attack_count > 10:
                    risk_factor += 20

                # Final decision
                if risk_factor > 60:
                    threat = "HIGH"
                elif risk_factor > 30:
                    threat = "MEDIUM"
                else:
                    threat = "LOW"

                print(f"[ATTACK] {ip} -> {port} ({threat})")

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                country, city, hostname = get_ip_intelligence(ip)

                vpn_keywords = [
                    "vpn", "proxy", "tor", "relay",
                    "cloud", "hosting", "vps",
                    "aws", "azure", "google", "digitalocean"
                ]

                if hostname and any(
                    x in hostname.lower() for x in vpn_keywords
                ):
                    is_vpn = True
                    print(f"[SECURITY] VPN DETECTED: {ip}")

                intent = analyze_intent(
                    ip,
                    attack_counter.get(ip, 0),
                    ""
                )

                attacker = classify_attacker(
                    intent=intent,
                    confidence=confidence,
                    threat=threat,
                    attack_count=attack_counter.get(ip, 0),
                    commands=""
                )

                vpn_status = "VPN" if is_vpn else "NORMAL"

                attack_id = log_attack(
                    ip, port, timestamp,
                    "Port Scan", 50, threat,
                    country, city, hostname,
                    confidence, reports, 2,
                    "Scan", attacker, vpn_status
                )

                # -------------------------------
                # ADAPTIVE DECEPTION ENGINE
                # -------------------------------
                if threat == "HIGH":

                    print(f"[DECEPTION] HIGH → SANDBOX {ip}")

                    commands = start_sandbox(
                        client, ip, attack_id
                    )

                    update_commands(attack_id, commands)
                    update_attacker_type(attack_id, attacker)

                    continue

                elif threat == "MEDIUM":

                    print(f"[DECEPTION] MEDIUM → DECISION {ip}")

                    if (
                        "Credential" in intent
                        or "Command" in intent
                    ):
                        commands = start_sandbox(
                            client, ip, attack_id
                        )
                    else:
                        commands = send_fake_banner(
                            client, attack_id
                        )

                else:

                    print(f"[DECEPTION] LOW → FAKE {ip}")

                    commands = send_fake_banner(
                        client, attack_id
                    )

                intent = analyze_intent(
                    ip,
                    attack_counter.get(ip, 0),
                    commands
                )

                attacker = classify_attacker(
                    intent=intent,
                    confidence=confidence,
                    threat=threat,
                    attack_count=attack_counter.get(ip, 0),
                    commands=commands
                )

                update_commands(attack_id, commands)
                update_attacker_type(attack_id, attacker)

                # GUI notification
                try:
                    import gui_dashboard

                    if gui_dashboard.window:
                        gui_dashboard.window.attack_signal.emit()

                except Exception:
                    pass

            except Exception as e:
                print("Monitor error:", e)

            finally:
                try:
                    client.close()
                except OSError:
                    pass

    finally:
        server.close()
        print(f"[MONITOR] Listener stopped on port {port}")

def start_background_monitor(enabled_services=None):
    global running, monitor_threads

    if running:
        print("[MONITOR] Already running.")
        return

    running = True
    monitor_threads = []

    ports = generate_ports(enabled_services)

    for port in ports:
        thread = threading.Thread(
            target=monitor_port,
            args=(port,),
            daemon=True
        )
        monitor_threads.append(thread)
        thread.start()

    print(f"[MONITOR] Started {len(ports)} monitoring listeners.")


def stop_background_monitor():
    global running

    running = False

    for thread in monitor_threads:
        thread.join(timeout=2)

    print("[MONITOR] Background monitoring stopped.")

