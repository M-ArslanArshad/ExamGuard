import pandas as pd
import os
import time
from ipaddress import ip_address, ip_network
from config import Config
from datetime import datetime
import json

# =====================================================
# 🛡️ IP Restriction
# =====================================================

def is_ip_allowed(ip_str):
    """Check if IP address is in allowed ranges"""
    if not Config.ENABLE_IP_RESTRICTION:
        return True

    try:
        client_ip = ip_address(ip_str)
        for allowed_range in Config.ALLOWED_IPS:
            if '/' in allowed_range:
                if client_ip in ip_network(allowed_range):
                    return True
            else:
                if str(client_ip) == allowed_range:
                    return True
        return False
    except ValueError:
        return False

# =====================================================
# 👤 Student Authentication
# =====================================================

def load_students():
    """Load student credentials from Excel file (roll_no and password only)"""
    if not os.path.exists(Config.STUDENTS_FILE):
        raise FileNotFoundError(f"❌ {Config.STUDENTS_FILE} not found!")
    
    try:
        df = pd.read_excel(Config.STUDENTS_FILE)
        # Convert to dictionary for easy lookup: {roll_no: password}
        students = {}
        for _, row in df.iterrows():
            roll_no = str(row["roll_no"]).strip().upper()
            password = str(row["password"]).strip()
            students[roll_no] = password
        return students
    except Exception as e:
        print(f"❌ Error loading students: {e}")
        return {}


def verify_student_credentials(roll_no, password):
    """
    Verify student login credentials
    Returns: (success: bool, message: str)
    """
    try:
        students = load_students()
        roll_no = roll_no.strip().upper()
        
        if roll_no not in students:
            return False, "Invalid Roll Number"
        
        # Verify password
        if students[roll_no] != password:
            return False, "Incorrect Password"
        
        return True, "Login successful"
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False, "System error. Contact administrator."
    

# =====================================================
# 📘 Question Loading
# =====================================================

def load_questions():
    """Load questions from Excel file"""
    if not os.path.exists(Config.QUEST_FILE):
        raise FileNotFoundError(f"❌ {Config.QUEST_FILE} not found!")
    
    df = pd.read_excel(Config.QUEST_FILE)
    questions = []
    
    for _, row in df.iterrows():
        img_name = str(row["img"]).strip() if "img" in df.columns and pd.notna(row["img"]) else ""
        
        # ✅ Support both formats:
        # 1. Just filename: "image1.jpg" -> "/images/image1.jpg"
        # 2. Full path already: "/images/image1.jpg" -> "/images/image1.jpg"
        if img_name:
            if img_name.startswith("/images/"):
                img_path = img_name  # Already has correct format
            else:
                img_path = f"/images/{img_name}"  # Add /images/ prefix
        else:
            img_path = None

        questions.append({
            "id": int(row["id"]),
            "q": row["question"],
            "img": img_path,
            "options": [
                row["option1"],
                row["option2"],
                row["option3"],
                row["option4"]
            ],
            "correct": str(row["correct"]).strip().upper()
        })
    
    return questions
# =====================================================
# 🧾 Responses and Scoring
# =====================================================

def init_response_file():
    """Create responses file with proper headers if it doesn't exist"""
    os.makedirs(os.path.dirname(Config.RESP_FILE), exist_ok=True)
    
    if not os.path.exists(Config.RESP_FILE):
        df = pd.DataFrame(columns=[
            "student_id",
            "question_id",
            "selected_option",
            "correct_option",
            "is_correct",
            "timestamp",
            "ip",
            "workstation",   # ✅ new column
            "status"
        ])
        df.to_csv(Config.RESP_FILE, index=False)




def save_response(student_id, qid, selected, correct, ip, status="ok"):
    """Append a response row to CSV and update marksheet"""
    try:
        if os.path.exists(Config.RESP_FILE):
            df = pd.read_csv(Config.RESP_FILE)
        else:
            init_response_file()
            df = pd.read_csv(Config.RESP_FILE)
    except Exception as e:
        print(f"⚠️ Response file error: {e}")
        print("📄 Recreating responses file...")
        init_response_file()
        df = pd.read_csv(Config.RESP_FILE)
    
    # ✅ Check if this student already answered this question
    existing = df[(df['student_id'] == student_id) & (df['question_id'] == qid)]
    if not existing.empty:
        print(f"⚠️ Duplicate response detected for {student_id} - Question {qid}. Skipping.")
        return
    
    # ✅ Normalize answers
    selected_clean = str(selected).strip().upper()
    correct_clean = str(correct).strip().upper()
    is_correct = (selected_clean == correct_clean)
    
    # ✅ Normalize IP and map to workstation
    clean_ip = ip.replace("::ffff:", "").strip()
    workstation = Config.WORKSTATION_MAP.get(clean_ip, "Unknown")
    
    # ✅ Append new row
    new_row = pd.DataFrame([{
        "student_id": student_id,
        "question_id": qid,
        "selected_option": selected_clean,
        "correct_option": correct_clean,
        "is_correct": is_correct,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ip": clean_ip,
        "workstation": workstation,
        "status": status
    }])
    
    df = pd.concat([df, new_row], ignore_index=True)
    
    try:
        df.to_csv(Config.RESP_FILE, index=False)
    except Exception as e:
        print(f"❌ Error saving response: {e}")
        backup_file = Config.RESP_FILE.replace('.csv', f'_backup_{int(time.time())}.csv')
        df.to_csv(backup_file, index=False)
        print(f"💾 Saved to backup file: {backup_file}")

    # ✅ After each response, update marksheet
    generate_marksheet()
def calculate_score(student_id):
    """Calculate total score for a student"""
    try:
        df = pd.read_csv(Config.RESP_FILE)
        student_responses = df[df['student_id'] == student_id]
        
        if len(student_responses) == 0:
            return None
        
        total_correct = student_responses['is_correct'].sum()
        total_questions = len(student_responses)
        
        return {
            'correct': int(total_correct),
            'total': total_questions,
            'percentage': round((total_correct / total_questions) * 100, 2)
        }
    except (FileNotFoundError, Exception) as e:
        print(f"⚠️ Error calculating score: {e}")
        return None


def get_all_results():
    """Get all quiz results as list of dicts"""
    try:
        df = pd.read_csv(Config.RESP_FILE)
        return df.to_dict('records')
    except (FileNotFoundError, Exception) as e:
        print(f"⚠️ Error reading results: {e}")
        return []


def generate_marksheet():
    """Generate marksheet in both CSV and Excel format (with workstation info)."""
    try:
        df = pd.read_csv(Config.RESP_FILE)
        if df.empty:
            return

        # Aggregate results
        summary = (
            df.groupby("student_id")
            .agg({
                "is_correct": "sum",
                "workstation": "last",
                "status": "last"
            })
            .reset_index()
            .rename(columns={"is_correct": "total_score"})
        )

        data_dir = os.path.dirname(Config.RESP_FILE)
        csv_path = os.path.join(data_dir, "marksheet.csv")
        xlsx_path = os.path.join(data_dir, "marksheet.xlsx")

        # Save both versions
        summary.to_csv(csv_path, index=False)
        summary.to_excel(xlsx_path, index=False, engine='openpyxl')

        print(f"✅ Marksheet updated: {csv_path}")
        print(f"📊 Excel version saved: {xlsx_path}")

    except Exception as e:
        print(f"⚠️ Error generating marksheet: {e}")


# =====================================================
# 🔁 Retake management helpers
# =====================================================

RETOKEN_FILE = os.path.join(os.path.dirname(Config.RESP_FILE), "retake_tokens.json")

def _ensure_retoken_file():
    folder = os.path.dirname(RETOKEN_FILE)
    os.makedirs(folder, exist_ok=True)
    if not os.path.exists(RETOKEN_FILE):
        with open(RETOKEN_FILE, "w") as f:
            json.dump({}, f)


def generate_retake_token(student_id):
    """Create a single-use token allowing student to retake the quiz."""
    _ensure_retoken_file()
    with open(RETOKEN_FILE, "r") as f:
        tokens = json.load(f)
    token = f"RT-{student_id}-{int(time.time())}"
    tokens[student_id] = {
        "token": token,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(RETOKEN_FILE, "w") as f:
        json.dump(tokens, f)
    return token


def check_retake_token(student_id):
    """Return token if exists, else None."""
    _ensure_retoken_file()
    with open(RETOKEN_FILE, "r") as f:
        tokens = json.load(f)
    entry = tokens.get(student_id)
    return entry.get("token") if entry else None


def consume_retake_token(student_id):
    """Consume (delete) a retake token after used. Returns True if consumed."""
    _ensure_retoken_file()
    with open(RETOKEN_FILE, "r") as f:
        tokens = json.load(f)
    if student_id in tokens:
        tokens.pop(student_id)
        with open(RETOKEN_FILE, "w") as f:
            json.dump(tokens, f)
        return True
    return False


def backup_and_delete_responses(student_id):
    """
    Backup a student's responses and remove them from responses.csv.
    Returns (backup_path, deleted_count).
    """
    if not os.path.exists(Config.RESP_FILE):
        return (None, 0)

    try:
        df = pd.read_csv(Config.RESP_FILE)
    except Exception as e:
        print(f"⚠️ Error reading responses: {e}")
        return (None, 0)

    student_rows = df[df['student_id'] == student_id]
    if student_rows.empty:
        return (None, 0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.dirname(Config.RESP_FILE)
    backup_path = os.path.join(
        backup_dir, f"responses_backup_{student_id}_{timestamp}.csv"
    )
    student_rows.to_csv(backup_path, index=False)

    # keep only others
    df_remaining = df[df['student_id'] != student_id]
    df_remaining.to_csv(Config.RESP_FILE, index=False)

    # regenerate marksheet if available
    try:
        generate_marksheet()
    except Exception as e:
        print(f"⚠️ Could not regenerate marksheet: {e}")

    print(f"✅ Backed up {len(student_rows)} rows to {backup_path} and deleted them.")
    return (backup_path, len(student_rows))