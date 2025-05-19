import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime
"""
fake = Faker()

# --- PARAMETERS ---
NUM_USERS = 50
NUM_ROWS = 500
START_DATE = datetime.strptime("2025-05-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2025-05-19", "%Y-%m-%d")

# --- Roles and Users ---
roles = ['administrator', 'user', 'guest']
usernames = [fake.user_name() for _ in range(NUM_USERS)]
user_roles = np.random.choice(roles, size=NUM_USERS, p=[0.1, 0.7, 0.2])

# --- Activity and Success Probabilities ---
activity_types = ['login', 'logout', 'access', 'registration', 'login_attempt']
activity_success_rate = {
    'login': 0.85,
    'logout': 1.0,
    'access': 0.9,
    'registration': 0.95,
    'login_attempt': 0.3,
}

# --- IP + User Agent ---
def random_ip():
    return f"{random.randint(10, 255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (Linux; Android 10; SM-G970F)...",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)..."
]

# --- Details Templates ---
details_templates = {
    'login': ["User logged in successfully", "Invalid credentials", "Account locked", "Password expired"],
    'logout': ["User logged out"],
    'access': ["Accessed marketplace", "Unauthorized access attempt to marketplace", "Accessed admin panel", "Accessed profile page"],
    'registration': ["New user registered", "Username already exists", "Email already used"],
    'login_attempt': ["Invalid credentials", "User locked out", "Login attempt from new device"],
}

def get_detail(activity, status):
    if activity == 'login' and status == 'failed':
        return random.choice(details_templates['login'][1:])
    elif activity == 'registration' and status == 'failed':
        return random.choice(details_templates['registration'][1:])
    elif activity == 'access' and status == 'failed':
        return details_templates['access'][1]
    elif activity == 'login_attempt' and status == 'failed':
        return random.choice(details_templates['login_attempt'])
    elif activity == 'logout':
        return details_templates['logout'][0]
    else:
        return random.choice(details_templates.get(activity, ["Action performed successfully"]))

# --- Generate Normal Log Data ---
rows = []
for _ in range(NUM_ROWS):
    user_idx = random.randint(0, NUM_USERS - 1)
    username = usernames[user_idx]
    role = user_roles[user_idx]
    user_id = user_idx + 1

    activity = random.choices(activity_types, weights=[0.3, 0.2, 0.3, 0.1, 0.1])[0]
    success_prob = activity_success_rate.get(activity, 0.9)
    status = 'success' if random.random() < success_prob else 'failed'

    if role == 'guest' or (activity in ['login_attempt', 'access'] and status == 'failed'):
        username_out = 'N/A'
        user_id_out = 'N/A'
    else:
        username_out = username
        user_id_out = str(user_id)

    timestamp = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
    ip = random_ip()
    ua = random.choice(user_agents)
    details = get_detail(activity, status)

    rows.append({
        "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "Activity Type": activity,
        "Status": status,
        "Username": username_out,
        "User ID": user_id_out,
        "IP Address": ip,
        "User Agent": ua,
        "Details": details,
    })

# --- Save to CSV ---
df = pd.DataFrame(rows)
df.to_csv("user_act_logging.csv", index=False)
print(f"✅ Generated {len(df)} normal user activity logs in 'user_act_logging.csv'")

"""

import pandas as pd
from datetime import datetime, timedelta

# Load existing logs
df = pd.read_csv("user_act_logging.csv", parse_dates=["Timestamp"])

# Saif's user info
saif_user_id = "999"
saif_username = "saif"
base_time = datetime.strptime("2025-05-18 20:00:00", "%Y-%m-%d %H:%M:%S")

# Saif's user agent and IP
saif_ua = "Mozilla/5.0 (Windows NT 10.0; SQLInjectionTester)"
saif_ip = "192.168.1.199"

# Steps with exact payloads from your process
steps = [
    # Step 2: initial single quote test -> fail (error message)
    ("login_attempt", "failed", "Attempted category filter injection: Electronics'"),
    
    # Step 3: ORDER BY tests
    ("login_attempt", "failed", "Tested ORDER BY 1 - no error"),
    ("login_attempt", "failed", "Tested ORDER BY 2 - no error"),
    ("login_attempt", "failed", "Tested ORDER BY 3 - no error"),
    ("login_attempt", "failed", "Tested ORDER BY 4 - no error"),
    ("login_attempt", "failed", "Tested ORDER BY 5 - error received, columns = 4"),
    
    # Step 4: UNION SELECT test
    ("login_attempt", "failed", "Tested UNION SELECT 1,2,3,4 - additional products appeared"),
    
    # Step 5: Extract DB version
    ("login_attempt", "failed", "Extracted SQLite version with UNION SELECT"),
    
    # Step 6: Extract user data (username, password, id)
    ("login_attempt", "failed", "Extracted users data with UNION SELECT username,password,id,'users' FROM users"),
    
    # Step 7: Admin login success
    ("login", "success", "Logged in as administrator using extracted credentials"),
    
    # Step 7 continuation: Access admin panel (normal accesses after login)
    ("access", "success", "Viewed admin panel with all user data"),
    ("access", "success", "Viewed admin panel with all user data"),
    ("access", "success", "Modified system settings"),
]

# Generate logs with ~2 mins apart for failed attempts, then shorter intervals for final steps
saif_logs = []
time_pointer = base_time

for i, (activity, status, detail) in enumerate(steps):
    saif_logs.append({
        "Timestamp": time_pointer.strftime("%Y-%m-%d %H:%M:%S"),
        "Activity Type": activity,
        "Status": status,
        "Username": saif_username,
        "User ID": saif_user_id,
        "IP Address": saif_ip,
        "User Agent": saif_ua,
        "Details": detail,
    })
    # Increase time: big gaps between failed tests, shorter for success + access
    if activity == "login_attempt":
        time_pointer += timedelta(minutes=2)
    else:
        time_pointer += timedelta(seconds=30)

# Append Saif logs to dataframe and save
df = pd.concat([df, pd.DataFrame(saif_logs)], ignore_index=True)
df.to_csv("user_act_logging.csv", index=False)
print(f"Injected {len(saif_logs)} Saif logs simulating exact SQLi steps into 'user_act_logging.csv'")
