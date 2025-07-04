# Quick Start Guide - Educational Chatbot

## 🚀 Fast Setup (Windows)

### Option 1: Automated Setup
1. **Run the setup script**:
   ```cmd
   setup.bat
   ```
   This will automatically create virtual environment and install dependencies.

### Option 2: Manual Setup
1. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## 🗄️ Database Setup

1. **Start XAMPP**:
   - Open XAMPP Control Panel
   - Start **Apache** and **MySQL**

2. **Create Database**:
   - Open http://localhost/phpmyadmin
   - Create database: `educational_chatbot`
   - Import `database_setup.sql` or copy-paste the SQL content

## 🧪 Test Installation

```cmd
python test_installation.py
```

## 🎯 Run the Application

### Web Interface (Recommended)
```cmd
python run.py
```
Then open: http://localhost:5000

### Command Line Interface (Testing)
```cmd
python cli_chatbot.py
```

## 📱 First Use

1. **Register**: Create your account
2. **Login**: Use your credentials
3. **Chat**: Start asking questions!

### Example Questions:
- "What is the Pythagorean theorem?"
- "How do I study for math?"
- "Explain photosynthesis"
- "Give me study tips"
- "Help me with history"

## 🔧 Troubleshooting

### Database Issues:
- Ensure XAMPP MySQL is running
- Check if database `educational_chatbot` exists
- Verify `.env` file settings

### Module Issues:
```cmd
pip install flask pymysql bcrypt python-dotenv flask-session spacy
python -m spacy download en_core_web_sm
```

### Port Issues:
- Change port in `run.py` if 5000 is busy
- Or stop other applications using port 5000

## 📚 Features

- ✅ **Academic Q&A**: Math, Science, History, English
- ✅ **Study Tips**: Personalized learning advice
- ✅ **Notes**: Create and organize study notes
- ✅ **Scheduling**: Plan study sessions
- ✅ **Reminders**: Set academic reminders
- ✅ **Chat History**: Track conversations
- ✅ **User Authentication**: Secure login system

## 🎓 Usage Tips

1. **Be Specific**: Ask detailed questions for better responses
2. **Use Keywords**: Include subject names in your questions
3. **Explore Features**: Try notes, scheduling, and reminders
4. **Regular Use**: The more you use it, the better it gets

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Run `python test_installation.py` to diagnose issues
3. Review error messages in the terminal
4. Ensure all prerequisites are installed

---
**Happy Learning! 🎉**
