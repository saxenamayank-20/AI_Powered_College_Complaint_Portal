from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.database import get_connection
from backend.utils import generate_ticket_id, hash_password, verify_password
from backend.ai_service import analyze_complaint

app = FastAPI(title="College Complaint Portal API")


# ─────────────────────────────────────────────
#  Pydantic Models (Request bodies)
# ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "student"


class LoginRequest(BaseModel):
    email: str
    password: str


class ComplaintRequest(BaseModel):
    user_id: int
    complaint_text: str


class StatusUpdateRequest(BaseModel):
    ticket_id: str
    status: str


# ─────────────────────────────────────────────
#  Auth Routes
# ─────────────────────────────────────────────

@app.post("/register")
def register(req: RegisterRequest):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor(dictionary=True)

    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (req.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(req.password)
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (req.name, req.email, hashed, req.role)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Registration successful"}


@app.post("/login")
def login(req: LoginRequest):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s", (req.email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user_id": user["id"],
        "name": user["name"],
        "role": user["role"]
    }


# ─────────────────────────────────────────────
#  Complaint Routes
# ─────────────────────────────────────────────

@app.post("/complaint/submit")
def submit_complaint(req: ComplaintRequest):
    if not req.complaint_text.strip():
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty")

    # Step 1: Analyze with Groq AI
    ai_result = analyze_complaint(req.complaint_text)

    # Step 2: Generate unique ticket ID
    ticket_id = generate_ticket_id()

    # Step 3: Save to MySQL
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints (ticket_id, user_id, complaint_text, category, priority, summary, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
    """, (
        ticket_id,
        req.user_id,
        req.complaint_text,
        ai_result["category"],
        ai_result["priority"],
        ai_result["summary"]
    ))
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Complaint submitted successfully",
        "ticket_id": ticket_id,
        "category": ai_result["category"],
        "priority": ai_result["priority"],
        "summary": ai_result["summary"]
    }


@app.get("/complaint/my/{user_id}")
def get_my_complaints(user_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT ticket_id, complaint_text, category, priority, summary, status, created_at
        FROM complaints
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    complaints = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert datetime to string for JSON
    for c in complaints:
        c["created_at"] = str(c["created_at"])

    return {"complaints": complaints}


@app.get("/complaint/all")
def get_all_complaints():
    """Admin only - get all complaints"""
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.ticket_id, u.name as student_name, c.complaint_text,
               c.category, c.priority, c.summary, c.status, c.created_at
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    """)
    complaints = cursor.fetchall()
    cursor.close()
    conn.close()

    for c in complaints:
        c["created_at"] = str(c["created_at"])

    return {"complaints": complaints}


@app.put("/complaint/status")
def update_status(req: StatusUpdateRequest):
    """Admin updates complaint status"""
    valid_statuses = ["Pending", "In Progress", "Resolved"]
    if req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status = %s WHERE ticket_id = %s",
        (req.status, req.ticket_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": f"Status updated to {req.status}"}


@app.get("/")
def root():
    return {"message": "College Complaint Portal API is running"}
