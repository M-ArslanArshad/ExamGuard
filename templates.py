from config import Config

# Replace the login_template() function in templates.py with this:

# Replace the login_template() function in templates.py with this:

def login_template():
    # Check if password authentication is enabled
    password_field = ""
    if Config.ENABLE_PASSWORD_AUTH:
        password_field = '''
        <div class="form-group">
            <label>Password:</label>
            <input type="password" name="password" placeholder="Enter your password" required>
        </div>
        '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Login - Quiz System</title>
        <style>
            body {
            font-family: Arial, sans-serif;
            background: url('/static/dept_bg.jpg') no-repeat center center fixed;
            background-size: 100% 100%;
            height: 100vh;
            width: 100%;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            }

            .overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.55);
                z-index: 1;
            }

            .login-container {
                position: relative;
                z-index: 2;
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
                width: 380px;
                color: white;
            }

            h2 {
                text-align: center;
                color: #fff;
                margin-bottom: 30px;
                font-weight: 600;
            }

            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: none;
                border-radius: 5px;
                box-sizing: border-box;
                font-size: 16px;
                background: rgba(255,255,255,0.9);
            }

            input[type="submit"] {
                width: 100%;
                padding: 12px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 10px;
                transition: background 0.3s ease;
            }

            input[type="submit"]:hover {
                background: #45a049;
            }

            .info {
                background: rgba(255,255,255,0.2);
                color: #f1f1f1;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-size: 14px;
            }

            ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
            
            label {
                display: block;
                margin-bottom: 5px;
                font-size: 14px;
                color: #f1f1f1;
                font-weight: 500;
            }
        </style>
        
        <script>
            // 🔒 Disable right-click
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                return false;
            });
            
            // 🔒 Disable F12, Ctrl+Shift+I, Ctrl+Shift+C, Ctrl+Shift+J, Ctrl+U
            document.addEventListener('keydown', function(e) {
                // F12
                if (e.keyCode == 123) {
                    e.preventDefault();
                    return false;
                }
                // Ctrl+Shift+I (Inspect)
                if (e.ctrlKey && e.shiftKey && e.keyCode == 73) {
                    e.preventDefault();
                    return false;
                }
                // Ctrl+Shift+C (Inspect Element)
                if (e.ctrlKey && e.shiftKey && e.keyCode == 67) {
                    e.preventDefault();
                    return false;
                }
                // Ctrl+Shift+J (Console)
                if (e.ctrlKey && e.shiftKey && e.keyCode == 74) {
                    e.preventDefault();
                    return false;
                }
                // Ctrl+U (View Source)
                if (e.ctrlKey && e.keyCode == 85) {
                    e.preventDefault();
                    return false;
                }
            });
            
            // 🔒 Disable text selection
            document.addEventListener('selectstart', function(e) {
                e.preventDefault();
                return false;
            });
            
            // 🔒 Disable copy, cut, paste
            document.addEventListener('copy', function(e) {
                e.preventDefault();
                return false;
            });
            document.addEventListener('cut', function(e) {
                e.preventDefault();
                return false;
            });
            document.addEventListener('paste', function(e) {
                e.preventDefault();
                return false;
            });
        </script>
    </head>
    <body oncontextmenu="return false" onselectstart="return false" oncopy="return false" oncut="return false" onpaste="return false">
        <div class="overlay"></div>

        <div class="login-container">
            <h2>🔐 Quiz Login</h2>
            <div class="info">
                <strong>Instructions:</strong>
                <ul>
                    <li>Enter your Roll Number''' + (' and Password' if Config.ENABLE_PASSWORD_AUTH else '') + '''</li>
                    <li>Quiz duration: ''' + str(Config.QUIZ_DURATION_MINUTES) + ''' minutes</li>
                    <li>Keep window maximized throughout</li>
                    <li>Do not switch tabs or minimize</li>
                </ul>
            </div>
            <form method="post">
                <div class="form-group">
                    <label>Roll Number:</label>
                    <input type="text" name="student_id" placeholder="e.g., 2021-EE-314" required autofocus>
                </div>
                ''' + password_field + '''
                <input type="submit" value="Login & Start Quiz">
            </form>
        </div>
    </body>
    </html>
    '''

def quiz_template(questions_html, remaining_time):
    fullscreen_code = ""
    if Config.ENABLE_FULLSCREEN_CHECK:
        fullscreen_code = f"""
        // Fullscreen enforcement (robust version)
        let quizStarted = false;
        let violationCount = 0;
        let hasWarned = false;

        window.onload = () => {{
            const heightDiff = Math.abs(screen.height - window.outerHeight);
            const widthDiff  = Math.abs(screen.width - window.outerWidth);
            const isMaximized = (heightDiff <= 200 && widthDiff <= 200);
            
            if (!isMaximized && !hasWarned) {{
                alert("⚠️ Please maximize your browser window before starting the quiz.");
                hasWarned = true;
            }}
            
            quizStarted = true;
            startFullscreenMonitor();
            startTimer();
        }};

        function startFullscreenMonitor() {{
            setInterval(() => {{
                if (quizStarted && !isSubmitting) {{
                    const heightDiff = Math.abs(screen.height - window.outerHeight);
                    const widthDiff  = Math.abs(screen.width - window.outerWidth);
                    const isMaximized = (heightDiff <= 200 && widthDiff <= 200);

                    if (!isMaximized) {{
                        violationCount++;
                        console.log("Fullscreen violation. Count: " + violationCount);

                        if (violationCount >= 2) {{
                            showViolationWarning();
                            disableBeforeUnload();
                            isSubmitting = true;
                            document.getElementById("status-field").value = "fullscreen_violation";
                            setTimeout(() => {{
                                document.getElementById("quiz-form").submit();
                            }}, 1000);
                        }}
                    }} else {{
                        if (violationCount > 0) {{
                            console.log("Window restored. Reset violation count.");
                        }}
                        violationCount = 0;
                    }}
                }}
            }}, {Config.FULLSCREEN_CHECK_INTERVAL});
        }}
        """
    else:
        fullscreen_code = """
        let quizStarted = false;
        window.onload = () => {
            quizStarted = true;
            startTimer();
        };
        """

    tab_switch_code = ""
    if Config.ENABLE_TAB_SWITCH_DETECTION:
        tab_switch_code = """
        // Tab switch detection with countdown-based grace period
        let tabSwitchCount = 0;
        let graceTimer;
        let countdownInterval;
        const GRACE_PERIOD = 5000; // 5 seconds grace period

        function startGraceCountdown() {
            let remaining = GRACE_PERIOD / 1000;
            const overlay = document.getElementById('violation-overlay');
            overlay.innerHTML = `⚠️ You switched tabs! Returning in <b>${remaining}</b> seconds...`;
            overlay.style.display = 'block';

            countdownInterval = setInterval(() => {
                remaining--;
                overlay.innerHTML = `⚠️ You switched tabs! Returning in <b>${remaining}</b> seconds...`;
                if (remaining <= 0) {
                    clearInterval(countdownInterval);
                    if (document.hidden && !isSubmitting) {
                        overlay.innerHTML = "⚠️ VIOLATION DETECTED<br>AUTO-SUBMITTING...";
                        disableBeforeUnload();
                        isSubmitting = true;
                        document.getElementById("status-field").value = "tab_switch_timeout";
                        setTimeout(() => {
                            document.getElementById("quiz-form").submit();
                        }, 1000);
                    }
                }
            }, 1000);
        }

        document.addEventListener('visibilitychange', () => {
            if (document.hidden && quizStarted && !isSubmitting) {
                tabSwitchCount++;
                console.log("Tab switch detected. Count: " + tabSwitchCount);

                if (tabSwitchCount === 1) {
                    startGraceCountdown();
                    graceTimer = setTimeout(() => {
                        if (document.hidden && !isSubmitting) {
                            document.getElementById('violation-overlay').innerHTML = "⚠️ VIOLATION DETECTED<br>AUTO-SUBMITTING...";
                            disableBeforeUnload();
                            isSubmitting = true;
                            document.getElementById("status-field").value = "tab_switch_timeout";
                            setTimeout(() => {
                                document.getElementById("quiz-form").submit();
                            }, 1000);
                        }
                    }, GRACE_PERIOD);
                } 
                else if (tabSwitchCount >= 2) {
                    showViolationWarning();
                    disableBeforeUnload();
                    isSubmitting = true;
                    document.getElementById("status-field").value = "multiple_tab_switch";
                    setTimeout(() => {
                        document.getElementById("quiz-form").submit();
                    }, 1000);
                }
            } 
            else if (!document.hidden) {
                // User returned — clear grace period & overlay
                clearTimeout(graceTimer);
                clearInterval(countdownInterval);
                document.getElementById('violation-overlay').style.display = 'none';
            }
        });
        """

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quiz in Progress</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: #667eea;
                color: white;
                padding: 15px 20px;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .timer {{
                font-size: 20px;
                font-weight: bold;
            }}
            .content {{
                margin-top: 80px;
                max-width: 900px;
                margin-left: auto;
                margin-right: auto;
            }}
            .question {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .question-text {{
                font-weight: bold;
                margin-bottom: 15px;
                font-size: 18px;
            }}
            .option {{
                padding: 10px;
                margin: 8px 0;
                cursor: pointer;
            }}
            .option input {{
                margin-right: 10px;
                cursor: pointer;
            }}
            .submit-btn {{
                background: #28a745;
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 18px;
                display: block;
                margin: 30px auto;
            }}
            .submit-btn:hover {{
                background: #218838;
            }}
            .violation-warning {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #ff4444;
                color: white;
                padding: 30px 50px;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
                z-index: 9999;
                box-shadow: 0 5px 20px rgba(0,0,0,0.5);
                display: none;
                text-align: center;
            }}
        </style>
        <script>
        let remaining = {remaining_time};
        let isSubmitting = false;

        function showViolationWarning() {{
            const overlay = document.getElementById('violation-overlay');
            overlay.innerHTML = "⚠️ VIOLATION DETECTED<br>AUTO-SUBMITTING...";
            overlay.style.display = 'block';
        }}

        function startTimer() {{
            const timer = document.getElementById('timer');
            const interval = setInterval(() => {{
                if (remaining <= 0) {{
                    clearInterval(interval);
                    disableBeforeUnload();
                    isSubmitting = true;
                    setTimeout(() => {{
                        document.getElementById("quiz-form").submit();
                    }}, 100);
                }} else {{
                    let m = Math.floor(remaining / 60);
                    let s = remaining % 60;
                    timer.textContent = m + "m " + (s < 10 ? '0' : '') + s + "s";
                    remaining--;
                }}
            }}, 1000);
        }}

        // Safe unload handling
        function disableBeforeUnload() {{
            window.removeEventListener('beforeunload', beforeUnloadHandler);
        }}

        const beforeUnloadHandler = (e) => {{
            e.preventDefault();
            e.returnValue = '';
        }};

        window.addEventListener('beforeunload', beforeUnloadHandler);

        {fullscreen_code}

        {tab_switch_code}

        // Detect window blur
        let blurTimer;
        window.onblur = function() {{
            blurTimer = setTimeout(() => {{
                if (!isSubmitting) {{
                    showViolationWarning();
                    disableBeforeUnload();
                    document.getElementById("status-field").value = "window_blur";
                    setTimeout(() => {{
                        document.getElementById("quiz-form").submit();
                    }}, 1000);
                }}
            }}, 1500);
        }};
        window.onfocus = function() {{
            clearTimeout(blurTimer);
        }};

        document.addEventListener('contextmenu', e => e.preventDefault());
        document.addEventListener('copy', e => e.preventDefault());
        document.addEventListener('paste', e => e.preventDefault());
        document.addEventListener('cut', e => e.preventDefault());

        // Disable unload warning on manual submit
        document.addEventListener('DOMContentLoaded', () => {{
            document.getElementById('quiz-form').addEventListener('submit', () => {{
                disableBeforeUnload();
            }});
        }});
                
                 // Treat closing tab/window exactly like a violation (robust)
        window.addEventListener("beforeunload", function (e) {{
            if (!isSubmitting) {{
                isSubmitting = true;
                // mark as violation so backend treats it the same
                document.getElementById("status-field").value = "tab_closed";
                disableBeforeUnload();
                showViolationWarning();

                try {{
                    // Build form data and send via sendBeacon (reliable on unload)
                    const form = document.getElementById("quiz-form");
                    const formData = new FormData(form);
                    formData.set('status', 'tab_closed');

                    // Convert FormData -> URLSearchParams for sendBeacon
                    const params = new URLSearchParams();
                    for (const pair of formData.entries()) {{
                        params.append(pair[0], pair[1]);
                    }}

                    // sendBeacon is synchronous-friendly for unload
                    navigator.sendBeacon(form.action, params);
                }} catch (err) {{
                    console.error("sendBeacon failed on beforeunload:", err);
                    // Try last resort: delayed submit (may be cancelled by browser)
                    setTimeout(() => {{
                        try {{ form.submit(); }} catch (__){{}}
                    }}, 500);
                }}

                // Let browser show its generic unload dialog
                e.preventDefault();
                e.returnValue = '';
            }}
        }});


        </script>
    </head>
    <body oncontextmenu="return false" oncopy="return false" onpaste="return false">
        <div id="violation-overlay" class="violation-warning">
            ⚠️ VIOLATION DETECTED<br>AUTO-SUBMITTING...
        </div>
        
        <div class="header">
            <h2 style="margin: 0;">📝 Quiz in Progress</h2>
            <div class="timer">⏱️ Time left: <span id="timer"></span></div>
        </div>
        
        <div class="content">
            <form id="quiz-form" method="post" onsubmit="isSubmitting = true;">
                {questions_html}
                <input type="hidden" name="status" id="status-field" value="ok">
                <button type="submit" class="submit-btn">Submit Quiz</button>
            </form>
        </div>
    </body>
    </html>
    '''


def render_question(q_text, q_image_url, options, q_number, q_id):
    # Only show image if valid path
    img_html = ""
    if q_image_url and q_image_url.strip():
        img_html = f"""
        <div style="text-align:center; margin:10px 0;">
            <img src="{q_image_url}" alt="" 
                 style="max-width:90%; height:auto; border:1px solid #ccc; border-radius:8px;">
        </div>
        """

    # Each option shown vertically (one per line)
    options_html = ""
    for opt in options:
        options_html += f"""
        <label class='option' style="display:block; margin:6px 0; padding:4px 8px; border-radius:4px;">
            <input type='radio' name='q{q_id}' value='{opt}'> {opt}
        </label>
        """

    return f"""
    <div class='question' style="margin-bottom:20px;">
        <div class='question-text' style="margin-bottom:8px;"><b>{q_number}. {q_text}</b></div>
        {img_html}
        {options_html}
    </div>
    """





def result_template(score_data, student_id):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quiz Result</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
            }}
            .result-container {{
                background: white;
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
                min-width: 400px;
            }}
            .score {{
                font-size: 48px;
                font-weight: bold;
                color: #667eea;
                margin: 20px 0;
            }}
            .details {{
                font-size: 18px;
                color: #666;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="result-container">
            <h1>✅ Quiz Submitted Successfully!</h1>
            <p class="details">Student ID: <strong>{student_id}</strong></p>
            <div class="score">{score_data['correct']}/{score_data['total']}</div>
            <p class="details">Score: <strong>{score_data['percentage']}%</strong></p>
            <p style="margin-top: 30px; color: #888;">You may now close this window.</p>
        </div>
    </body>
    </html>
    '''
