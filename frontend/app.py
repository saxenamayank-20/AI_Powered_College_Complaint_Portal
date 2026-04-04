import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="College Complaint Portal",
    page_icon="🎓",
    layout="centered"
)

# ─────────────────────────────────────────────
#  Session State Init
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "name" not in st.session_state:
    st.session_state.name = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "page" not in st.session_state:
    st.session_state.page = "login"


# ─────────────────────────────────────────────
#  Helper: Priority color badge
# ─────────────────────────────────────────────
def priority_color(priority):
    colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
    return colors.get(priority, "⚪")


def status_color(status):
    colors = {"Pending": "🔴", "In Progress": "🟡", "Resolved": "🟢"}
    return colors.get(status, "⚪")


# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
def login_page():
    st.markdown("## 🎓 College Complaint Portal")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", use_container_width=True):
            if not email or not password:
                st.error("Please fill all fields")
            else:
                try:
                    res = requests.post(f"{API_URL}/login", json={
                        "email": email,
                        "password": password
                    })
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.logged_in = True
                        st.session_state.user_id = data["user_id"]
                        st.session_state.name = data["name"]
                        st.session_state.role = data["role"]
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Login failed"))
                except Exception:
                    st.error("Cannot connect to server. Make sure FastAPI is running.")

    with tab2:
        st.subheader("Register")
        name = st.text_input("Full Name", key="reg_name")
        email_r = st.text_input("Email", key="reg_email")
        password_r = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register", use_container_width=True):
            if not name or not email_r or not password_r:
                st.error("Please fill all fields")
            else:
                try:
                    res = requests.post(f"{API_URL}/register", json={
                        "name": name,
                        "email": email_r,
                        "password": password_r,
                        "role": "student"
                    })
                    if res.status_code == 200:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(res.json().get("detail", "Registration failed"))
                except Exception:
                    st.error("Cannot connect to server. Make sure FastAPI is running.")


# ─────────────────────────────────────────────
#  STUDENT DASHBOARD
# ─────────────────────────────────────────────
def student_dashboard():
    # Greeting
    st.markdown(f"## 👋 Welcome back, {st.session_state.name}!")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Submit Complaint", "My Tickets"])

    # ── Submit Complaint ──
    with tab1:
        st.subheader("Submit a New Complaint")
        complaint_text = st.text_area(
            "Describe your complaint in detail",
            height=150,
            placeholder="e.g. The hostel mess food quality has been very poor for the last 3 days..."
        )

        if st.button("Submit Complaint", use_container_width=True):
            if not complaint_text.strip():
                st.error("Please write your complaint first")
            else:
                with st.spinner("Analyzing your complaint with AI..."):
                    try:
                        res = requests.post(f"{API_URL}/complaint/submit", json={
                            "user_id": st.session_state.user_id,
                            "complaint_text": complaint_text
                        })
                        if res.status_code == 200:
                            data = res.json()
                            st.success("✅ Complaint submitted successfully!")
                            st.markdown("### Your Ticket Details")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.info(f"🎫 **Ticket ID:** {data['ticket_id']}")
                                st.info(f"📂 **Category:** {data['category']}")
                            with col2:
                                st.info(f"{priority_color(data['priority'])} **Priority:** {data['priority']}")
                                st.info(f"📝 **Summary:** {data['summary']}")
                        else:
                            st.error(res.json().get("detail", "Submission failed"))
                    except Exception:
                        st.error("Cannot connect to server.")

    # ── My Tickets ──
    with tab2:
        st.subheader("My Complaint Tickets")
        if st.button("Refresh", key="refresh_student"):
            st.rerun()

        try:
            res = requests.get(f"{API_URL}/complaint/my/{st.session_state.user_id}")
            if res.status_code == 200:
                complaints = res.json()["complaints"]
                if not complaints:
                    st.info("No complaints submitted yet.")
                else:
                    for c in complaints:
                        with st.expander(
                            f"🎫 {c['ticket_id']}  |  {priority_color(c['priority'])} {c['priority']}  |  {status_color(c['status'])} {c['status']}"
                        ):
                            st.write(f"**Category:** {c['category']}")
                            st.write(f"**Summary:** {c['summary']}")
                            st.write(f"**Your complaint:** {c['complaint_text']}")
                            st.write(f"**Submitted on:** {c['created_at'][:10]}")
        except Exception:
            st.error("Cannot connect to server.")


# ─────────────────────────────────────────────
#  ADMIN DASHBOARD
# ─────────────────────────────────────────────
def admin_dashboard():
    st.markdown(f"## 👋 Welcome, {st.session_state.name}!")
    st.markdown("*Admin Dashboard*")
    st.markdown("---")

    st.subheader("All Complaints")

    col1, col2 = st.columns([3, 1])
    with col2:
        filter_status = st.selectbox("Filter by status", ["All", "Pending", "In Progress", "Resolved"])

    if st.button("Refresh", key="refresh_admin"):
        st.rerun()

    try:
        res = requests.get(f"{API_URL}/complaint/all")
        if res.status_code == 200:
            complaints = res.json()["complaints"]

            # Apply filter
            if filter_status != "All":
                complaints = [c for c in complaints if c["status"] == filter_status]

            if not complaints:
                st.info("No complaints found.")
            else:
                st.markdown(f"**Total: {len(complaints)} complaints**")
                for c in complaints:
                    with st.expander(
                        f"🎫 {c['ticket_id']}  |  👤 {c['student_name']}  |  {priority_color(c['priority'])} {c['priority']}  |  {status_color(c['status'])} {c['status']}"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Category:** {c['category']}")
                            st.write(f"**Summary:** {c['summary']}")
                            st.write(f"**Complaint:** {c['complaint_text']}")
                            st.write(f"**Date:** {c['created_at'][:10]}")
                        with col2:
                            new_status = st.selectbox(
                                "Update Status",
                                ["Pending", "In Progress", "Resolved"],
                                index=["Pending", "In Progress", "Resolved"].index(c["status"]),
                                key=f"status_{c['ticket_id']}"
                            )
                            if st.button("Update", key=f"btn_{c['ticket_id']}"):
                                update_res = requests.put(f"{API_URL}/complaint/status", json={
                                    "ticket_id": c["ticket_id"],
                                    "status": new_status
                                })
                                if update_res.status_code == 200:
                                    st.success("Status updated!")
                                    st.rerun()
    except Exception:
        st.error("Cannot connect to server.")


# ─────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────
def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.name = ""
    st.session_state.role = ""
    st.session_state.page = "login"
    st.rerun()


# ─────────────────────────────────────────────
#  MAIN APP ROUTER
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"**👤 {st.session_state.name}**")
        st.markdown(f"Role: `{st.session_state.role}`")
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()

    # Route based on role
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        student_dashboard()
