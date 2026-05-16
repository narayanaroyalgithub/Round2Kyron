import pandas as pd

# 1. LOAD DATA
# Load the original practice dataset (Deliverable 1)
df_master = pd.read_csv('orthopedic_practices_dataset.csv') 

# Load the manual call tracker (skip instruction rows)
df_tracker = pd.read_csv('orthopedic_call_tracker.csv', skiprows=3)

# 2. STANDARDIZE PHONE NUMBERS (MERGE KEY)
# Create a numeric 'phone_key' to ensure perfect matching
def clean_phone(p):
    return ''.join(filter(str.isdigit, str(p))) if pd.notna(p) else ""

df_master['phone_key'] = df_master['phone'].apply(clean_phone)
df_tracker['phone_key'] = df_tracker['Phone'].apply(clean_phone)

# 3. SELECT & RENAME TRACKER COLUMNS (MAPPING TO FINAL NAMES)
# We map the tracker's original names to your final audit column names
tracker_subset = df_tracker[[
    'phone_key', 
    'Called?', 
    'Date Called', 
    'Daytime Call\nTime', 
    'After Hrs\nCall Time',
    'A: Follow-up\n(Business Hrs)', 
    'B: New Patient\n(Business Hrs)',
    'C: Follow-up\n(After Hours)', 
    'D: New Patient\n(After Hours)',
    'General Notes', 
    'Caller Notes /\nNext Steps'
]].copy()

tracker_subset.columns = [
    'phone_key', 
    'Called_Status', 
    'Date Called', 
    'Daytime Call Time', 
    'After Hrs Call Time',
    'Category_A_FollowUp_WorkHours', 
    'Category_B_NewPatient_WorkHours',
    'Category_C_AfterHours_FollowUp', 
    'Category_D_AfterHrs_NewPatient',
    'Raw_General', 
    'Raw_Caller'
]

# 4. MERGE RESEARCH DATA INTO MASTER LIST
# Enrich the entire list of 10,000+ rows with your 46 call results
df_final = df_master.merge(tracker_subset, on='phone_key', how='left')

# 5. GENERATE PROFESSIONAL COLUMNS
# Create the 'Unified_Call_Notes' by combining your raw observation columns
def build_notes(row):
    if row['Called_Status'] != 'Yes': return ""
    return f"{row['Raw_General']} {row['Raw_Caller']}".strip()

# Classify the 'Overall_System_Type' based on Category A findings
def build_sys_type(row):
    if row['Called_Status'] != 'Yes': return ""
    val = str(row['Category_A_FollowUp_WorkHours']).lower()
    if 'ivr' in val or 'ai' in val: return "AI"
    if 'human' in val or 'voicemail' in val: return "Human"
    return "N/A"

df_final['Unified_Call_Notes'] = df_final.apply(build_notes, axis=1)
df_final['Overall_System_Type'] = df_final.apply(build_sys_type, axis=1)

# 6. SORT BY PRIORITY
# Push 'Called' rows to the top, then sort the rest by Physician Count
df_final['sort_order'] = df_final['Called_Status'].apply(lambda x: 1 if x == 'Yes' else 0)
df_final = df_final.sort_values(by=['sort_order', 'estimated_physician_count'], ascending=[False, False])

# 7. FINAL EXPORT
# Remove temporary helper columns before saving
final_cols = [c for c in df_final.columns if c not in ['phone_key', 'sort_order', 'Raw_General', 'Raw_Caller']]
df_final[final_cols].to_csv('orthopedic_audit_final.csv', index=False)
