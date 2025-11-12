"""
Quick setup script for Quiz System
Run this to create necessary files and folders
"""

import os
import pandas as pd

def create_directory_structure():
    """Create necessary directories"""
    directories = ['data', 'flask_session']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")


def create_sample_questions():
    """Create sample questions.xlsx file"""
    questions_path = os.path.join('data', 'questions.xlsx')
    
    if os.path.exists(questions_path):
        response = input(f"⚠️  {questions_path} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Skipping questions file creation.")
            return
    
    # Sample questions
    sample_data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        'question': [
            'What is the capital of France?',
            'Which planet is known as the Red Planet?',
            'What is 2 + 2?',
            'Who wrote "Romeo and Juliet"?',
            'What is the largest ocean on Earth?',
            'How many continents are there?',
            'What is the chemical symbol for water?',
            'Who painted the Mona Lisa?',
            'What is the smallest prime number?',
            'In which year did World War II end?',
            'What is the speed of light?',
            'Who invented the telephone?',
            'What is the largest mammal?',
            'How many sides does a hexagon have?',
            'What is the boiling point of water in Celsius?'
        ],
        'option1': [
            'London', 'Venus', '3', 'Charles Dickens', 'Atlantic', '5', 'H2O', 'Van Gogh', '1', '1943',
            '300,000 km/s', 'Edison', 'Elephant', '5', '90°C'
        ],
        'option2': [
            'Berlin', 'Mars', '4', 'William Shakespeare', 'Pacific', '7', 'O2', 'Leonardo da Vinci', '2', '1945',
            '150,000 km/s', 'Alexander Graham Bell', 'Blue Whale', '6', '100°C'
        ],
        'option3': [
            'Paris', 'Jupiter', '5', 'Jane Austen', 'Indian', '6', 'CO2', 'Picasso', '3', '1944',
            '200,000 km/s', 'Tesla', 'Giraffe', '7', '110°C'
        ],
        'option4': [
            'Madrid', 'Saturn', '6', 'Mark Twain', 'Arctic', '8', 'N2', 'Michelangelo', '4', '1946',
            '250,000 km/s', 'Marconi', 'Rhino', '8', '120°C'
        ],
        'correct': [
            'Paris', 'Mars', '4', 'William Shakespeare', 'Pacific', '7', 'H2O', 'Leonardo da Vinci', '2', '1945',
            '300,000 km/s', 'Alexander Graham Bell', 'Blue Whale', '6', '100°C'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel(questions_path, index=False)
    print(f"✅ Created {questions_path} with {len(df)} sample questions")


def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = ['flask', 'pandas', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is NOT installed")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True


def get_local_ip():
    """Get local IP address"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to determine"


def display_config_help():
    """Display configuration help"""
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("🔧 CONFIGURATION GUIDE")
    print("="*60)
    
    print(f"\n📍 Your Local IP: {local_ip}")
    
    print("\n1️⃣  Edit config.py:")
    print("   - Update ALLOWED_IPS with your lab IP ranges")
    print(f"   - For testing locally, add: '{local_ip}'")
    print("   - For a network range, use: '192.168.1.0/24'")
    
    print("\n2️⃣  Change Admin Password:")
    print("   - Edit ADMIN_USERNAME and ADMIN_PASSWORD in config.py")
    
    print("\n3️⃣  Adjust Quiz Settings:")
    print("   - QUIZ_DURATION_MINUTES")
    print("   - NUM_QUESTIONS")
    print("   - ENABLE_IP_RESTRICTION")
    
    print("\n4️⃣  Run the application:")
    print("   python app.py")
    
    print("\n5️⃣  For ngrok exposure:")
    print("   ngrok http 5000")
    
    print("\n" + "="*60)


def main():
    print("="*60)
    print("🚀 QUIZ SYSTEM SETUP")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first!")
        print("Run: pip install -r requirements.txt")
        return
    
    print("\n📁 Setting up directory structure...")
    create_directory_structure()
    
    print("\n📝 Creating sample questions file...")
    create_sample_questions()
    
    display_config_help()
    
    print("\n✅ Setup complete! You're ready to go!")
    print("\n💡 Next steps:")
    print("   1. Review and edit config.py")
    print("   2. Add your own questions to data/questions.xlsx")
    print("   3. Run: python app.py")


if __name__ == "__main__":
    main()
