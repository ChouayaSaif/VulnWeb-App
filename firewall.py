import re
from datetime import datetime
import os

def run_firewall(username, password, remote_addr, http_user_agent):
    input_str = username + password
    ip = remote_addr if remote_addr else 'UNKNOWN'
    agent = http_user_agent if http_user_agent else 'UNKNOWN'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    severity = calculate_severity(input_str)
    is_suspicious = detect_sqli(input_str)

    if is_suspicious:
        # Text log
        txt_log = f"[{timestamp}] IP: {ip} | Payload: {input_str} | Agent: {agent} | Severity: {severity}\n"
        with open("log.txt", "a") as f:
            f.write(txt_log)

        # CSV log
        with open("log.csv", "a") as f:
            f.write(f'"{timestamp}","{ip}","{input_str}","{agent}","{severity}"\n')

        print(f'<p style="color:red">⚠️ ALERT: Suspicious input logged. Severity: {severity}</p>')

    update_ip_counter(ip)

def detect_sqli(input_str):
    return bool(re.search(r"(\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|--|#|OR|AND)\b|['\";=])", input_str, re.IGNORECASE))

def calculate_severity(input_str):
    score = 0
    patterns = {
        "' OR '1'='1": 3,
        "--": 2,
        "UNION": 3,
        "SELECT": 2,
        "#": 1,
        "=": 1,
        ";": 1,
        "DROP": 4,
        "INSERT": 2,
        "UPDATE": 2,
        "DELETE": 2
    }

    for pattern, value in patterns.items():
        if pattern.lower() in input_str.lower():
            score += value

    return min(score, 10)

def update_ip_counter(ip):
    file_path = "ip_hits.txt"
    ip_counts = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    logged_ip, count = line.split("|")
                    ip_counts[logged_ip] = int(count)

    ip_counts[ip] = ip_counts.get(ip, 0) + 1

    with open(file_path, "w") as f:
        for logged_ip, count in ip_counts.items():
            f.write(f"{logged_ip}|{count}\n")

    if ip_counts.get(ip, 0) >= 5:
        print(f'<p style="color:orange">⚠️ IP {ip} has attempted {ip_counts[ip]} times. Consider monitoring.</p>')