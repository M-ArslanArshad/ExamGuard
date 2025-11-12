from flask import Flask, request, redirect, session, render_template_string, abort, send_from_directory
import random
import time
from functools import wraps
import pandas as pd
import os


from config import Config
from utils import (
    is_ip_allowed, load_questions, init_response_file,
    save_response, calculate_score, get_all_results,
    backup_and_delete_responses, generate_retake_token,
    check_retake_token, consume_retake_token,
    verify_student_credentials  # ✅ ADD THIS
)
from templates import login_template, quiz_template, result_template,render_question

app = Flask(__name__)
app.config.from_object(Config)

# Active users set to prevent multiple logins
ACTIVE_USERS = set()

# Load questions at startup
try:
    QUESTIONS = load_questions()
    init_response_file()
    print(f"✅ Loaded {len(QUESTIONS)} questions")
except Exception as e:
    print(f"❌ Error loading questions: {e}")
    QUESTIONS = []


# ================= Middleware ===================
def get_client_ip():
    """Get real client IP, handling ngrok forwarding"""
    if "X-Forwarded-For" in request.headers:
        # Sometimes multiple IPs are listed, first one is real client
        ip = request.headers["X-Forwarded-For"].split(",")[0].strip()
    else:
        ip = request.remote_addr
    return ip


def ip_check(f):
    """Decorator to check IP restrictions with ngrok support"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Config.ENABLE_IP_RESTRICTION:
            return f(*args, **kwargs)

        client_ip = get_client_ip()
        host = request.host.lower()  # domain used to access app

        # Allow if IP in allowed list OR request via current ngrok domain
        if client_ip not in Config.ALLOWED_IPS and Config.NGROK_DOMAIN.lower() not in host:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# ================= Routes ===================
@app.route('/')
def index():
    return redirect('/login')


# Replace the /login route in app.py with this:

# Replace the /login route in app.py with this:

@app.route('/login', methods=["GET", "POST"])
@ip_check
def login():
    if request.method == "POST":
        sid = request.form["student_id"].strip().upper()
        password = request.form.get("password", "").strip()

        # Validation
        if not sid:
            return render_template_string('''
                <script>
                    alert("Please enter your Roll Number!");
                    window.location.href = "/login";
                </script>
            ''')

        # 🔐 Check password only if authentication is enabled
        if Config.ENABLE_PASSWORD_AUTH:
            if not password:
                return render_template_string('''
                    <script>
                        alert("Please enter your Password!");
                        window.location.href = "/login";
                    </script>
                ''')
            
            # Authenticate student
            success, message = verify_student_credentials(sid, password)
            
            if not success:
                return render_template_string(f'''
                    <script>
                        alert("❌ {message}");
                        window.location.href = "/login";
                    </script>
                ''')

        # Check if already logged in
        if sid in ACTIVE_USERS:
            return render_template_string('''
                <html>
                <head><title>Already Logged In</title></head>
                <body style="font-family: Arial; text-align: center; padding-top: 100px;">
                    <h2>⚠️ Already Logged In</h2>
                    <p>This Student ID is already taking the quiz from another location.</p>
                    <p>Please contact the administrator if this is an error.</p>
                </body>
                </html>
            ''')

        # 📝 Check if student already attempted and handle retake
        has_taken = False
        if os.path.exists(Config.RESP_FILE):
            try:
                df = pd.read_csv(Config.RESP_FILE)
                has_taken = not df[df['student_id'] == sid].empty
            except Exception:
                has_taken = False

        token = check_retake_token(sid)

        if has_taken and not token:
            return render_template_string('''
                <html><body style="font-family: Arial; text-align: center; padding-top: 100px;">
                    <h2>❌ Attempt Already Recorded</h2>
                    <p>You have already taken the quiz. Please contact your instructor for a retake.</p>
                </body></html>
            ''')

        # If token exists, consume it so student can retake once
        if token:
            consume_retake_token(sid)

        # Check if enough questions available
        if len(QUESTIONS) < Config.NUM_QUESTIONS:
            return render_template_string('''
                <html>
                <body style="font-family: Arial; text-align: center; padding-top: 100px;">
                    <h2>❌ Error</h2>
                    <p>Not enough questions available in the database.</p>
                </body>
                </html>
            ''')

        # Initialize session
        session["student_id"] = sid
        session["start_time"] = time.time()
        session["quiz_order"] = random.sample(QUESTIONS, Config.NUM_QUESTIONS)
        ACTIVE_USERS.add(sid)

        return redirect('/quiz')

    return render_template_string(login_template())



@app.route('/quiz', methods=["GET", "POST"])
@ip_check
@login_required
def quiz():
    sid = session["student_id"]
    ip = request.remote_addr

    total_time = Config.QUIZ_DURATION_MINUTES * 60
    elapsed = int(time.time() - session["start_time"])
    remaining = max(total_time - elapsed, 0)
    """""
    # Time up - auto submit
    if remaining <= 0:
        ACTIVE_USERS.discard(sid)
        
        # ✅ Check if already submitted to prevent duplicates
        if os.path.exists(Config.RESP_FILE):
            try:
                df = pd.read_csv(Config.RESP_FILE)
                existing = df[df['student_id'] == sid]
                if len(existing) >= Config.NUM_QUESTIONS:
                    # Already submitted, just show result
                    score = calculate_score(sid)
                    session.clear()
                    if score:
                        return render_template_string(result_template(score, sid))
            except Exception as e:
                print(f"⚠️ Error checking existing responses: {e}")
        
        for q in session["quiz_order"]:
            save_response(sid, q["id"], "NO_ANSWER", q["correct"], ip, "timeout")

        score = calculate_score(sid)
        session.clear()

        if score:
            return render_template_string(result_template(score, sid))
        return render_template_string('''
            <html>
            <body style="font-family: Arial; text-align: center; padding-top: 100px;">
                <h2>⏰ Time Up!</h2>
                <p>Your quiz has been auto-submitted.</p>
            </body>
            </html>
        ''')
    """
    # Form submission
    if request.method == "POST":
        # ✅ Check if already submitted to prevent duplicates
        if os.path.exists(Config.RESP_FILE):
            try:
                df = pd.read_csv(Config.RESP_FILE)
                existing = df[df['student_id'] == sid]
                if len(existing) >= Config.NUM_QUESTIONS:
                    # Already submitted, just calculate and show result
                    ACTIVE_USERS.discard(sid)
                    score = calculate_score(sid)
                    session.clear()
                    if score:
                        return render_template_string(result_template(score, sid))
                    return render_template_string('''
                        <html>
                        <body style="font-family: Arial; text-align: center; padding-top: 100px;">
                            <h2>✅ Quiz Already Submitted!</h2>
                            <p>Thank you for participating.</p>
                        </body>
                        </html>
                    ''')
            except Exception as e:
                print(f"⚠️ Error checking existing responses: {e}")
        
        status = request.form.get("status", "ok")

        # Save all answers
        for q in session["quiz_order"]:
            ans = request.form.get(f"q{q['id']}", "NO_ANSWER")
            save_response(sid, q["id"], ans, q["correct"], ip, status)

        ACTIVE_USERS.discard(sid)
        score = calculate_score(sid)
        session.clear()

        if score:
            return render_template_string(result_template(score, sid))

        return render_template_string('''
            <html>
            <body style="font-family: Arial; text-align: center; padding-top: 100px;">
                <h2>✅ Quiz Submitted Successfully!</h2>
                <p>Thank you for participating.</p>
            </body>
            </html>
        ''')

    # ---------------------- Build quiz HTML ----------------------
    questions_html = ""
    for idx, q in enumerate(session["quiz_order"], 1):
        # ✅ Accept both /static/ and /images/ paths
        img_url = q.get("img")
        if img_url and (img_url.startswith("/static/") or img_url.startswith("/images/")):
            img_display = img_url
        else:
            img_display = None
            
        questions_html += render_question(
            q_text=q["q"],
            q_image_url=img_display,
            options=q["options"],
            q_number=idx,
            q_id=q["id"]
        )

    return render_template_string(quiz_template(questions_html, remaining))


@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from data/images folder"""
    images_dir = os.path.join(Config.BASE_DIR, "data", "images")
    
    # Security: prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        abort(404)
    
    try:
        return send_from_directory(images_dir, filename)
    except FileNotFoundError:
        abort(404)

# ================= Admin Routes ===================
@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session["admin"] = True
            return redirect('/admin/results')
        else:
            return "Invalid credentials"

    return '''
        <html>
        <head><title>Admin Login</title></head>
        <body style="font-family: Arial; text-align: center; padding-top: 100px;">
            <h2>Admin Login</h2>
            <form method="post">
                Username: <input type="text" name="username" required><br><br>
                Password: <input type="password" name="password" required><br><br>
                <input type="submit" value="Login">
            </form>
        </body>
        </html>
    '''



# Replace the /admin/results route in app.py with this:

@app.route('/admin/results')
def admin_results():
    if not session.get("admin"):
        return redirect('/admin/login')

    results = get_all_results()

    # Group by student
    students = {}
    for r in results:
        sid = r['student_id']
        if sid not in students:
            students[sid] = []
        students[sid].append(r)

    html = '''
    <html>
    <head>
        <title>Quiz Results</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f5f5f5; }
            h1 { color: #667eea; }
            table { border-collapse: collapse; width: 100%; background: white; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #667eea; color: white; font-weight: bold; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f0f0f0; }
            a { text-decoration: none; padding: 5px 10px; border-radius: 4px; }
            .logout { margin-top: 20px; display: inline-block; background: #dc3545; color: white; padding: 10px 20px; }
            .logout:hover { background: #c82333; }
        </style>
    </head>
    <body>
        <h1>Quiz Results</h1>
        <table>
            <tr>
                <th>Student ID</th>
                <th>Workstation</th>
                <th>Correct</th>
                <th>Score %</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
    '''

    for sid, responses in students.items():
        correct = sum(1 for r in responses if r.get('is_correct'))
        total = len(responses)
        percentage = round((correct / total) * 100, 2) if total > 0 else 0
        status = responses[-1].get('status', 'ok')
        ip = responses[-1].get('ip', 'Unknown')

        # ✅ Handle float/NaN values from pandas
        if isinstance(ip, float) or ip is None or str(ip).lower() == 'nan':
            clean_ip = 'Unknown'
        else:
            clean_ip = str(ip).replace("::ffff:", "").strip()

        workstation = Config.WORKSTATION_MAP.get(clean_ip, "Unknown")

        html += f'''
            <tr>
                <td>{sid}</td>
                <td>{workstation}</td>
                <td>{correct}</td>
                <td>{percentage}%</td>
                <td>{status}</td>
                <td>
                    <a href="/admin/view_responses/{sid}" style="color: blue; margin-right: 10px;">📝 View Responses</a>
                    <a href="/admin/allow_retake?student_id={sid}" style="color: green;">🔄 Allow Retake</a>
                </td>
            </tr>
        '''

    html += '''
        </table>
        <a href="/admin/logout" class="logout">Logout</a>
    </body>
    </html>
    '''

    return html


@app.route('/admin/view_responses/<student_id>')
def view_responses(student_id):
    if not session.get("admin"):
        return redirect('/admin/login')
    
    # Get student's responses
    try:
        df = pd.read_csv(Config.RESP_FILE)
        student_responses = df[df['student_id'] == student_id].to_dict('records')
        
        if not student_responses:
            return f'''
            <div style="font-family:Arial; text-align:center; padding-top:100px;">
                <h3>⚠️ No responses found for {student_id}</h3>
                <a href="/admin/results">Back to Results</a>
            </div>
            '''
        
        # Calculate score
        correct_count = sum(1 for r in student_responses if r.get('is_correct'))
        total_count = len(student_responses)
        percentage = round((correct_count / total_count) * 100, 2) if total_count > 0 else 0
        status = student_responses[-1].get('status', 'ok')
        workstation = student_responses[-1].get('workstation', 'Unknown')
        timestamp = student_responses[-1].get('timestamp', 'Unknown')
        
        # Build HTML
        html = f'''
        <html>
        <head>
            <title>Response Review - {student_id}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    background: #f5f5f5;
                }}
                .header {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    color: #667eea;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                    margin-top: 15px;
                }}
                .info-item {{
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #555;
                }}
                .question-card {{
                    background: white;
                    padding: 20px;
                    margin-bottom: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid #ddd;
                }}
                .question-card.correct {{
                    border-left-color: #28a745;
                }}
                .question-card.incorrect {{
                    border-left-color: #dc3545;
                }}
                .question-number {{
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 10px;
                }}
                .answer-row {{
                    margin: 8px 0;
                    padding: 8px;
                    border-radius: 4px;
                }}
                .student-answer {{
                    background: #fff3cd;
                    padding: 8px;
                    border-radius: 4px;
                    display: inline-block;
                }}
                .correct-answer {{
                    background: #d4edda;
                    padding: 8px;
                    border-radius: 4px;
                    display: inline-block;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                .status-ok {{
                    background: #d4edda;
                    color: #155724;
                }}
                .status-violation {{
                    background: #f8d7da;
                    color: #721c24;
                }}
                .btn {{
                    display: inline-block;
                    padding: 10px 20px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .btn:hover {{
                    background: #5568d3;
                }}
                .print-btn {{
                    background: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-left: 10px;
                }}
                .print-btn:hover {{
                    background: #218838;
                }}
                @media print {{
                    .no-print {{ display: none; }}
                    body {{ background: white; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📝 Response Review</h1>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Student ID:</span> {student_id}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Score:</span> {correct_count}/{total_count} ({percentage}%)
                    </div>
                    <div class="info-item">
                        <span class="info-label">Workstation:</span> {workstation}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Submitted:</span> {timestamp}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Status:</span> 
                        <span class="status-badge {'status-ok' if status == 'ok' else 'status-violation'}">
                            {status.replace('_', ' ').title()}
                        </span>
                    </div>
                </div>
                <div class="no-print">
                    <a href="/admin/results" class="btn">← Back to Results</a>
                    <button onclick="window.print()" class="print-btn">🖨️ Print</button>
                </div>
            </div>
        '''
        
        # Add each question
        for idx, response in enumerate(student_responses, 1):
            is_correct = response.get('is_correct', False)
            question_id = response.get('question_id', 'N/A')
            selected = response.get('selected_option', 'NO_ANSWER')
            correct = response.get('correct_option', 'N/A')
            
            # Try to get question text from loaded questions
            question_text = f"Question {question_id}"
            try:
                for q in QUESTIONS:
                    if q['id'] == question_id:
                        question_text = q['q']
                        break
            except:
                pass
            
            card_class = "correct" if is_correct else "incorrect"
            result_icon = "✅" if is_correct else "❌"
            
            html += f'''
            <div class="question-card {card_class}">
                <div class="question-number">{result_icon} Question {idx}</div>
                <p><strong>{question_text}</strong></p>
                <div class="answer-row">
                    <strong>Student's Answer:</strong> 
                    <span class="student-answer">{selected}</span>
                </div>
                <div class="answer-row">
                    <strong>Correct Answer:</strong> 
                    <span class="correct-answer">{correct}</span>
                </div>
            </div>
            '''
        
        html += '''
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f'''
        <div style="font-family:Arial; text-align:center; padding-top:100px;">
            <h3>❌ Error loading responses</h3>
            <p>{str(e)}</p>
            <a href="/admin/results">Back to Results</a>
        </div>
        '''
    

@app.route('/admin/allow_retake', methods=['GET', 'POST'])
def admin_allow_retake():
    if not session.get('admin'):
        return redirect('/admin/login')

    # Step 1: Read the student_id from query or form
    student_id = request.args.get('student_id') or request.form.get('student_id', '')
    student_id = student_id.strip()

    # If no student ID provided, redirect safely
    if not student_id:
        return '''
            <div style="font-family:Arial; text-align:center; padding-top:100px;">
                <h3>⚠️ No Student ID Provided</h3>
                <p>Go back to <a href="/admin/results">Results</a>.</p>
            </div>
        '''

    # Step 2: If confirmation form submitted
    if request.method == 'POST' and request.form.get('confirm') == 'yes':
        backup_path, deleted = backup_and_delete_responses(student_id)
        token = generate_retake_token(student_id)
        msg = (
            f"✅ Deleted {deleted} responses for {student_id}. "
            f"Backup saved at: {backup_path}. Retake token issued successfully."
            if deleted > 0 else
            f"No previous responses found for {student_id}, but retake token issued."
        )
        return f'''
        <div style="max-width:700px;margin:40px auto;font-family:Arial;text-align:center">
          <h2>Retake Approved</h2>
          <p style="color:green">{msg}</p>
          <a href="/admin/results" style="display:inline-block;padding:10px 20px;background:#667eea;color:white;
          text-decoration:none;border-radius:5px;">Back to Dashboard</a>
        </div>
        '''

    # Step 3: If GET request → show confirmation prompt
    return f'''
    <div style="max-width:700px;margin:100px auto;font-family:Arial;text-align:center;">
      <h2>Confirm Retake for {student_id}</h2>
      <p style="font-size:16px;">
        ⚠️ This will permanently delete all previous responses and marks 
        for this student. The student will be able to take the quiz again 
        as a new attempt.
      </p>
      <form method="post" style="margin-top:30px;">
        <input type="hidden" name="student_id" value="{student_id}">
        <button type="submit" name="confirm" value="yes" 
          style="padding:10px 20px;margin:5px;background-color:#d9534f;color:white;
          border:none;border-radius:5px;cursor:pointer;">
          Confirm Retake
        </button>
        <a href="/admin/results" 
          style="padding:10px 20px;margin:5px;background-color:#6c757d;color:white;
          border-radius:5px;text-decoration:none;">
          Cancel
        </a>
      </form>
    </div>
    '''



@app.route('/admin/logout')
def admin_logout():
    session.pop("admin", None)
    return redirect('/admin/login')


# ================= Error Pages ===================
@app.errorhandler(403)
def forbidden(e):
    return render_template_string('''
        <html>
        <body style="font-family: Arial; text-align: center; padding-top: 100px;">
            <h2>🚫 Access Denied</h2>
            <p>Your IP address is not authorized to access this quiz system.</p>
            <p>Please contact the administrator if you believe this is an error.</p>
        </body>
        </html>
    '''), 403


@app.errorhandler(404)
def not_found(e):
    return "Page Not Found", 404


# ================= Run Server ===================
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Quiz System Starting...")
    print(f"📚 Questions loaded: {len(QUESTIONS)}")
    print(f"🔒 IP Restriction: {'Enabled' if Config.ENABLE_IP_RESTRICTION else 'Disabled'}")
    print(f"🔑 Password Auth: {'Enabled' if Config.ENABLE_PASSWORD_AUTH else 'Disabled'}")  # ✅ ADD THIS
    print(f"🖥️ Fullscreen Check: {'Enabled' if Config.ENABLE_FULLSCREEN_CHECK else 'Disabled'}")
    print(f"📄 Tab Switch Detection: {'Enabled' if Config.ENABLE_TAB_SWITCH_DETECTION else 'Disabled'}")
    print("=" * 50)

    app.run(host='0.0.0.0', port=8080, debug=True)