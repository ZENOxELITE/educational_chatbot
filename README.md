# Educational Assistant Chatbot!!!

A text-based educational assistant chatbot built with Python, Flask, and MySQL. The chatbot helps students with academic questions, study tips, scheduling, and note-taking.

## Features

- **Text-based Chat Interface**: Interactive chatbot for educational assistance
- **User Authentication**: Secure user registration and login system
- **Academic Q&A**: Answer questions across multiple subjects (Math, Science, History, English)
- **Study Tips**: Personalized study advice and learning strategies
- **Note Management**: Create, store, and search personal study notes
- **Study Scheduling**: Plan and track study sessions
- **Reminders**: Set reminders for assignments and study sessions
- **Natural Language Processing**: Uses spaCy for understanding user queries
- **Local Database**: All data stored locally in MySQL via XAMPP

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **Database**: MySQL (via XAMPP)
- **NLP**: spaCy
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Session with bcrypt password hashing

## Prerequisites

1. **Python 3.8 or higher**
2. **XAMPP** (for MySQL database)
3. **Git** (optional, for cloning)

## Installation & Setup

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd educational_chatbot
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Set Up MySQL Database

1. **Start XAMPP**:
   - Open XAMPP Control Panel
   - Start Apache and MySQL services

2. **Create Database**:
   - Open phpMyAdmin (http://localhost/phpmyadmin)
   - Create a new database named `educational_chatbot`
   - Import the database schema by running the SQL script in `database_setup.sql`

   Or run the SQL commands manually:
   ```sql
   CREATE DATABASE educational_chatbot;
   USE educational_chatbot;
   -- Then copy and paste the contents of database_setup.sql
   ```

### 6. Configure Environment Variables

1. Copy the `.env` file and update if needed:
   ```
   SECRET_KEY=your-super-secret-key-change-this-in-production
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=
   MYSQL_DB=educational_chatbot
   DEBUG=True
   ```

2. If your MySQL setup is different, update the values accordingly.

### 7. Run the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## Usage

### First Time Setup

1. **Access the Application**: Open your browser and go to `http://localhost:5000`

2. **Register a New Account**:
   - Click "Register" on the login page
   - Fill in your details (username, email, password, first name, last name)
   - Optionally add your grade level
   - Click "Register"

3. **Login**:
   - Use your username and password to login
   - You'll be redirected to the chat interface

### Using the Chatbot

#### Chat Interface
- Type messages in the chat input field
- Ask questions like:
  - "What is the Pythagorean theorem?"
  - "How do I study for math?"
  - "Explain photosynthesis"
  - "Give me study tips for history"

#### Notes Management
- Click on "Notes" tab
- Create new notes by clicking "New Note"
- Organize notes by subject and topic
- Search through your notes

#### Study Scheduling
- Click on "Schedule" tab
- Add study sessions with date, time, and duration
- Track your study progress
- View upcoming sessions

#### Reminders
- Click on "Reminders" tab
- Set reminders for assignments, exams, or study sessions
- Include title, description, date, and time

## Project Structure

```
educational_chatbot/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User model
│   │   ├── chat.py             # Chat and session models
│   │   └── knowledge_base.py   # Knowledge base models
│   ├── routes/                  # API routes
│   │   ├── auth.py             # Authentication routes
│   │   └── chat.py             # Chat and data routes
│   ├── services/                # Business logic
│   │   ├── nlp_service.py      # Natural language processing
│   │   ├── chat_service.py     # Chat handling
│   │   └── knowledge_service.py # Knowledge management
│   └── utils/
│       └── db.py               # Database utilities
├── static/                      # Static files
│   ├── css/style.css           # Styles
│   └── js/script.js            # Frontend JavaScript
├── templates/
│   └── index.html              # Main HTML template
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
├── database_setup.sql          # Database schema
├── .env                        # Environment variables
└── run.py                      # Application entry point
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Chat & Knowledge
- `POST /api/chat/message` - Send message to chatbot
- `GET /api/chat/history` - Get chat history
- `GET /api/chat/search` - Search chat history
- `GET /api/chat/subjects` - Get available subjects
- `GET /api/chat/knowledge/search` - Search knowledge base

### Notes
- `GET /api/chat/notes` - Get user notes
- `POST /api/chat/notes` - Create new note
- `GET /api/chat/notes/search` - Search notes

### Schedule & Reminders
- `GET /api/chat/schedule` - Get study schedule
- `POST /api/chat/schedule` - Create study session
- `GET /api/chat/reminders` - Get reminders
- `POST /api/chat/reminders` - Create reminder

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure XAMPP MySQL is running
   - Check database credentials in `.env`
   - Verify database `educational_chatbot` exists

2. **spaCy Model Not Found**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Module Import Errors**:
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

4. **Port Already in Use**:
   - Change port in `run.py` or stop other applications using port 5000

### Database Reset

To reset the database:
1. Drop the database in phpMyAdmin
2. Create a new database named `educational_chatbot`
3. Run the `database_setup.sql` script again

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Feel free to modify and use as needed.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code documentation
3. Create an issue in the repository

## Future Enhancements

- Voice input/output capabilities
- Mobile app version
- Advanced AI integration
- Collaborative study features
- Progress tracking and analytics
- Integration with external educational APIs
