[Русская версия](README.ru.md)

# Physical Therapy Admin Panel (Flask Version)

Administrative web panel for managing physical therapy exercises and monitoring active user sessions.

The project was created as a study backend application using Flask and SQLite.
It provides CRUD functionality for exercise management, administrator authentication, pagination, and active session control.

## Features

* Authentication system for administrators
* CRUD operations for physical therapy exercises
* Exercise directory management
* User session monitoring
* Pagination support
* SQLite database integration
* Bootstrap-based UI

---

## Tech Stack

* **Language:** Python 3
* **Framework:** Flask
* **Database:** SQLite3
* **Frontend:** HTML, CSS, Bootstrap
* **Environment management:** python-dotenv

---

## Project Structure

```text
project/
│
├── app/                # Application package
│   ├── __init__.py     # Application initialization
│   ├── routes.py       # Application routes
│   ├── db.py           # Database logic and initialization
│   └── templates/      # HTML templates
│
├── instance/           # SQLite database files
├── config.py           # Application configuration
├── run.py              # Application entry point
├── requirements.txt
└── .env
```

---

## Installation and Setup

### 1. Clone repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create `.env` file in project root:

```env
SECRET_KEY=your-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

---

### 5. Run application

```bash
python run.py
```

---

## Future Improvements

* Add SQLAlchemy ORM
* Add Pydantic validation
* Improve mobile responsiveness
* Add REST API support
* Improve project architecture and modularization

---

## Educational Purpose

This project was created for backend development practice and Flask framework learning.
