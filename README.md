# AI_Enabled_College_Complaint_Portal

## Description
College Complaint Portal is a full-stack complaint management system built for students and administrators. Students can register, log in, submit complaints, and track their complaint status. Administrators can review all complaints, filter them, and update their progress. The project also uses AI to categorize complaints, assign priority, and generate a short summary for faster resolution.

## Tech Stack
- Python
- FastAPI
- Streamlit
- MySQL
- Groq API
- bcrypt

## Features
- Login and registration system
- Student dashboard for complaint submission and tracking
- Admin dashboard for reviewing and updating complaints
- AI-based complaint categorization and priority detection
- Auto-generated ticket IDs
- Complaint status management with Pending, In Progress, and Resolved states

## Learnings
This project helped in learning:
- Building a full-stack Python application
- Connecting a FastAPI backend with a Streamlit frontend
- Designing and using a MySQL database schema
- Implementing login logic and password hashing
- Integrating AI into a real-world workflow

## How to Run
1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up the MySQL database by running:

```sql
database/schema.sql
```

3. Update database credentials in `backend/database.py`.
4. Add your Groq API key in `backend/ai_service.py`.
5. Start the backend server:

```bash
py -m uvicorn backend.main:app --reload
```

6. Start the frontend in a new terminal:

```bash
py -m streamlit run frontend/app.py
```

7. Open the app:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

## Project Structure
```bash
AI_Enabled_College_Complaint_Portal/
+-- backend/
�   +-- ai_service.py
�   +-- database.py
�   +-- main.py
�   +-- utils.py
+-- database/
�   +-- schema.sql
+-- frontend/
�   +-- app.py
+-- start_local.ps1
+-- README.md
```
