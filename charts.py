"""import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Load and prepare data
df = pd.read_csv('user_act_logging.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour
df['Day'] = df['Timestamp'].dt.day

# Set style for better visualizations
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# 1. General Activity Analysis
def plot_activity_analysis():
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Activity type distribution
    activity_counts = df['Activity Type'].value_counts()
    sns.barplot(x=activity_counts.values, y=activity_counts.index, ax=axes[0], palette="Blues_d")
    axes[0].set_title('Activity Type Distribution')
    axes[0].set_xlabel('Count')
    
    # Status distribution
    status_counts = df['Status'].value_counts()
    sns.barplot(x=status_counts.values, y=status_counts.index, ax=axes[1], palette="Greens_d")
    axes[1].set_title('Activity Status Distribution')
    axes[1].set_xlabel('Count')
    
    plt.tight_layout()
    plt.show()

# 2. Suspicious Activity Detection (SQL Injection)
def plot_sql_injection_evidence():
    # Identify SQL injection attempts
    sql_patterns = ['ORDER BY', 'UNION SELECT', 'injection', 'SQLInjection']
    df['SQL_Attempt'] = df['Details'].str.contains('|'.join(sql_patterns), case=False)
    sql_attempts = df[df['SQL_Attempt']]
    
    if not sql_attempts.empty:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Timeline of SQL injection attempts
        sql_timeline = sql_attempts.groupby('Hour').size()
        sql_timeline.plot(kind='bar', ax=axes[0], color='red')
        axes[0].set_title('SQL Injection Attempts by Hour')
        axes[0].set_ylabel('Attempt Count')
        
        # User agents used in SQL injection
        sql_agents = sql_attempts['User Agent'].value_counts().head(5)
        sql_agents.plot(kind='barh', ax=axes[1], color='red')
        axes[1].set_title('Top User Agents in SQL Injection')
        axes[1].set_xlabel('Count')
        
        plt.tight_layout()
        plt.show()
    else:
        print("No SQL injection attempts detected")

# 3. Attacker Identification (Saif)
def plot_attacker_identification():
    # Get all activities from the attacker
    attacker = df[df['Username'] == 'saif']
    
    if not attacker.empty:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Attacker's activity timeline
        attacker_timeline = attacker.groupby('Hour').size()
        attacker_timeline.plot(kind='bar', ax=axes[0,0], color='red')
        axes[0,0].set_title("Saif's Activity by Hour")
        axes[0,0].set_ylabel('Activity Count')
        
        # Attacker's activity types
        attacker_activities = attacker['Activity Type'].value_counts()
        attacker_activities.plot(kind='bar', ax=axes[0,1], color='red')
        axes[0,1].set_title("Saif's Activity Types")
        axes[0,1].set_ylabel('Count')
        
        # Attacker's attack progression
        attack_steps = attacker.sort_values('Timestamp')
        axes[1,0].plot(attack_steps['Timestamp'], attack_steps['Details'], 'r-o')
        axes[1,0].set_title("Saif's Attack Progression")
        axes[1,0].set_ylabel('Attack Step')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Attacker's successful accesses
        success_access = attacker[attacker['Status'] == 'success']
        if not success_access.empty:
            success_details = success_access['Details'].value_counts()
            success_details.plot(kind='barh', ax=axes[1,1], color='red')
            axes[1,1].set_title("Saif's Successful Access Details")
            axes[1,1].set_xlabel('Count')
        else:
            axes[1,1].axis('off')
            axes[1,1].text(0.5, 0.5, 'No successful accesses', 
                          ha='center', va='center')
        
        plt.tight_layout()
        plt.show()
    else:
        print("No attacker activity found")

# 4. Comparative Analysis (Saif vs Others)
def plot_comparative_analysis():
    if 'saif' in df['Username'].values:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Compare activity types
        df['IsAttacker'] = df['Username'] == 'saif'
        activity_compare = df.groupby(['IsAttacker', 'Activity Type']).size().unstack()
        activity_compare.plot(kind='bar', ax=axes[0], color=['blue', 'red'])
        axes[0].set_title('Activity Type Comparison')
        axes[0].set_ylabel('Count')
        axes[0].set_xticks([0, 1])
        axes[0].set_xticklabels(['Others', 'Saif'], rotation=0)
        
        # Compare IP addresses
        attacker_ip = df[df['Username'] == 'saif']['IP Address'].iloc[0]
        ip_compare = df['IP Address'].value_counts().head(10)
        ip_compare.plot(kind='bar', ax=axes[1], color=['blue' if ip != attacker_ip else 'red' for ip in ip_compare.index])
        axes[1].set_title('Top IP Addresses (Red = Saif)')
        axes[1].set_ylabel('Count')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    else:
        print("No attacker data for comparison")

# Run all visualizations
plot_activity_analysis()
plot_sql_injection_evidence()
plot_attacker_identification()
plot_comparative_analysis()

"""