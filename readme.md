# ExamGuard 🛡️

A secure, proctored online quiz/examination system with fullscreen enforcement, tab-switch detection, and comprehensive admin controls for academic integrity. Currently deployed and actively used by the **Electrical Engineering Department**.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Features

### Security & Proctoring
- ✅ **Fullscreen Enforcement** - Automatically detects window minimization/resizing
- ✅ **Tab Switch Detection** - Grace period countdown with auto-submission on violations
- ✅ **IP Restriction** - Whitelist-based access control for lab workstations
- ✅ **Password Authentication** - Optional secure login with student credentials
- ✅ **Anti-Cheat Measures** - Disabled right-click, copy/paste, inspect element, and DevTools
- ✅ **Session Management** - Prevents multiple simultaneous logins per student

### Quiz Management
- 📝 **Dynamic Question Loading** - Excel-based question bank with image support
- ⏱️ **Timed Exams** - Configurable duration with countdown timer
- 🎲 **Randomization** - Questions randomly selected from the pool
- 🖼️ **Image Support** - Questions can include diagrams, circuits, or illustrations
- 💾 **Auto-Save Responses** - Prevents data loss on violations or timeouts

### Admin Dashboard
- 📊 **Results Overview** - View all student scores with workstation tracking
- 🔍 **Response Review** - Detailed question-by-question analysis for each student
- 🔄 **Retake Management** - Allow students to retake exams with token system
- 📈 **Automated Marksheet** - Generates Excel/CSV reports with scores
- 🗺️ **Workstation Mapping** - Track which lab station each student used

### Violation Tracking
- 🚨 Real-time detection of:
  - Fullscreen violations
  - Tab/window switching
  - Browser closing attempts
  - Window blur events
- 📝 All violations logged with timestamps and auto-submission

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/examguard.git
cd examguard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure the system**

Edit `config.py` to customize:
- Quiz duration
- Number of questions
- IP whitelist (lab workstations)
- Enable/disable proctoring features
- Admin credentials

4. **Prepare your data**

Create `data/` folder structure:
```
data/
├── questions.xlsx          # Question bank
├── passwords/
│   └── students.xlsx      # Student credentials
└── images/                # Question images (optional)
```

**Questions Format** (`questions.xlsx`):
| id | question | option1 | option2 | option3 | option4 | correct | img |
|----|----------|---------|---------|---------|---------|---------|-----|
| 1  | What is Ohm's Law? | V=IR | P=VI | I=V/R | V=P/I | A | circuit1.png |

**Students Format** (`students.xlsx`):
| roll_no | password |
|---------|----------|
| 2021-EE-001 | pass123 |
| 2021-EE-002 | secure456 |

5. **Run the application**
```bash
python app.py
```

Visit `http://localhost:8080` in your browser.

## 📋 Configuration

### Key Settings in `config.py`

```python
# Quiz Settings
QUIZ_DURATION_MINUTES = 30      # Exam duration
NUM_QUESTIONS = 20              # Questions per attempt

# Security
ENABLE_IP_RESTRICTION = True    # Lab-only access
ENABLE_PASSWORD_AUTH = True     # Require passwords
ENABLE_FULLSCREEN_CHECK = True  # Force fullscreen
ENABLE_TAB_SWITCH_DETECTION = True  # Monitor tab switches

# Admin Access
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'change_this_password'
```

### Workstation Mapping
Map lab IPs to readable names:
```python
WORKSTATION_MAP = {
    "192.168.1.1": "WS-01",
    "192.168.1.2": "WS-02",
    # ... add your lab IPs
}
```

## 🎓 Usage

### For Students
1. Navigate to the quiz URL
2. Enter Roll Number and Password
3. Complete quiz in fullscreen mode
4. Submit or wait for auto-submission
5. View instant results

### For Administrators
1. Visit `/admin/login`
2. Enter admin credentials
3. View all results and scores
4. Review individual responses
5. Issue retake tokens if needed

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Data Storage**: CSV + Excel (pandas)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Session Management**: Flask-Session
- **Security**: IP filtering, token-based authentication

## 📂 Project Structure

```
examguard/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── utils.py              # Helper functions
├── templates.py          # HTML templates
├── requirements.txt      # Python dependencies
├── data/
│   ├── questions.xlsx    # Question bank
│   ├── responses.csv     # Student responses
│   ├── marksheet.xlsx    # Generated scores
│   ├── passwords/
│   │   └── students.xlsx # Student credentials
│   └── images/          # Question images
└── static/
    └── dept_bg.jpg      # Login background
```

## 🔒 Security Features

- **No Client-Side Answer Storage** - Answers never visible in browser
- **Server-Side Validation** - All checks performed on backend
- **Encrypted Sessions** - Secure session management
- **Rate Limiting Ready** - Prepared for production deployment
- **Backup System** - Automatic response backups before retakes

## 🐛 Troubleshooting

**Issue**: Students can't login
- Check if their Roll Number exists in `students.xlsx`
- Verify password authentication is enabled/disabled correctly
- Check IP restrictions if enabled

**Issue**: Images not showing
- Ensure images are in `data/images/` folder
- Verify image filenames match those in `questions.xlsx`
- Check file permissions

**Issue**: Violations not detecting
- Confirm proctoring features are enabled in `config.py`
- Test in different browsers (Chrome/Firefox recommended)
- Check browser console for JavaScript errors

## 📈 Future Enhancements

- [ ] Camera-based proctoring
- [ ] Mobile device detection
- [ ] Analytics dashboard
- [ ] Email notifications
- [ ] Question categories/difficulty levels
- [ ] Practice mode
- [ ] PDF report generation

## 👥 Contributors

This project is maintained by the **Electrical Engineering Department** development team.

- **Department**: Electrical Engineering
- **Institution**: [University of Engineering and Technology,Lahore(New Campus)]
- **Year**: 2025

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](license.md) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the department IT team


## ⚠️ Disclaimer

This system is designed for educational purposes within controlled lab environments. Ensure compliance with your institution's academic integrity policies and data protection regulations.

---

**Made with ❤️ by the Electrical Engineering Department**

*Ensuring fair and secure examinations for all students*

---

## 📦 Additional Repository Files

### requirements.txt
```
Flask==2.3.0
pandas==2.0.0
openpyxl==3.1.2
Werkzeug==2.3.0
```

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Flask
instance/
.webassets-cache
flask_session/

# Data files (keep structure, ignore content)
data/responses.csv
data/marksheet.csv
data/marksheet.xlsx
data/retake_tokens.json
data/passwords/students.xlsx
data/questions.xlsx
data/images/*
!data/images/.gitkeep
data/*_backup_*.csv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment variables
.env
.env.local

# Secrets
config_local.py
```

### LICENSE (MIT)
```
MIT License

Copyright (c) 2025 Electrical Engineering Department

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
