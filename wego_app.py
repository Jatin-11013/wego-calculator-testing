import streamlit as st
import sqlite3
import hashlib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Booking Safety Calculator", layout="wide")

# ---------------- DB SETUP ----------------
DB_NAME = "users.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(p):
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def verify_password(p, h):
    return hash_password(p) == h

def user_exists():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def create_user(username, password, role):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role)
    )
    conn.commit()
    conn.close()

def get_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username, password_hash, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def update_role(username, role):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
    conn.commit()
    conn.close()

def update_password(username, new_password):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hash_password(new_password), username)
    )
    conn.commit()
    conn.close()

init_db()

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.login_role = None

def go(page):
    st.session_state.page = page
    st.rerun()

# ---------------- FIRST TIME ADMIN ----------------
def first_time_admin():
    st.title("🔐 Create First Admin")

    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")
    password2 = st.text_input("Confirm Password", type="password")

    if st.button("Create Admin"):
        if not username or not password:
            st.error("Username and password required")
        elif password != password2:
            st.error("Passwords do not match")
        else:
            create_user(username, password, "admin")
            st.success("Admin created! Refresh the page.")
            st.stop()

# ---------------- PAGES ----------------
def landing_page():
    st.title("🚀 Welcome")
    st.subheader("Login as:")

    col1, col2 = st.columns(2)
    if col1.button("👤 User"):
        st.session_state.login_role = "user"
        go("login")
    if col2.button("🛠️ Admin"):
        st.session_state.login_role = "admin"
        go("login")

def login_page():
    st.title(f"🔐 Login as {st.session_state.login_role.capitalize()}")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(username)
        if user is None:
            st.error("Invalid username or password")
        else:
            _, password_hash, role = user
            if role != st.session_state.login_role:
                st.error("You are not allowed to login as this role")
            elif verify_password(password, password_hash):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                go("calculator")
            else:
                st.error("Invalid username or password")

    if st.button("⬅ Back"):
        go("landing")

def sidebar():
    with st.sidebar:
        st.write(f"👤 {st.session_state.username} ({st.session_state.role})")

        if st.session_state.role == "admin":
            if st.button("🛠️ Admin Panel"):
                go("admin_panel")

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            go("landing")

# ---------------- CALCULATOR PAGE (YOUR CODE) ----------------
def show_calculator():
    # -------- REMOVE EXTRA TOP SPACE & SMALLER FONTS --------
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1rem; }
        .summary-box p { font-size: 12px; margin-bottom: 3px; }
        .summary-box h3 { font-size: 14px; margin-bottom: 5px; }
        .stSelectbox label, .stNumberInput label { font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🧮 Booking Safety Calculator")
    st.caption("Operation Team – Safe vs Loss Booking Tool")

    # ---------------- DI MASTER ----------------
    supplier_di = {
        "TBO Flights Online - BOMA774": 0.0064,
        "FlyShop Series Online API": 0.01,
        "Flyshop online API": 0.01,
        "Cleartrip Private Limited - AB 2": 0.01,
        "Travelopedia Series": 0.01,
        "Just Click N Pay Series": 0.01,
        "Fly24hrs Holiday Pvt. Ltd": 0.01,
        "Travelopedia": 0.01,
        "Etrave Flights": 0.01,
        "ETrav Tech Limited": 0.01,
        "Etrav Series Flights": 0.01,
        "Tripjack Pvt. Ltd.": 0.005,
        "Indigo Corporate Travelport Universal Api (KTBOM278)": 0.0045,
        "Indigo Regular Fare (Corporate)(KTBOM278)": 0.0045,
        "Indigo Retail Chandni (14354255C)": 0.0,
        "Indigo Regular Corp Chandni (14354255C)": 0.0,
        "BTO Bhasin Travels HAP OP7": 0.018,
        "Bhasin Travel Online HAP 7U63": 0.018,
        "AIR IQ": 0.01,
        "Tripjack Flights": 0.005,
        "Etrav HAP 58Y8": 0.01,
    }

    supplier_list = sorted(supplier_di.keys())
    supplier_list.insert(0, "Other")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        meta_partner = st.selectbox("Meta Partner", ["None", "Wego", "Wego Ads"])
    with c2:
        flight_type = st.selectbox("Flight Type", ["Domestic", "International"])
    with c3:
        supplier_name = st.selectbox("Supplier Name", supplier_list)
    with c4:
        pax_count = st.number_input("Pax Count", min_value=1, step=1)

    c5, c6, c7, c8, c9 = st.columns(5)
    with c5:
        base_fare = st.number_input("Base Fare (₹)", min_value=0.0, step=100.0)
    with c6:
        purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, step=100.0)
    with c7:
        booking_amount = st.number_input("Booking Amount (₹)", min_value=0.0, step=100.0)
    with c8:
        handling_fees = st.number_input("Handling Fees (₹)", min_value=0.0, step=10.0)
    with c9:
        pg_fees_input = st.number_input("PG Fees (₹)", min_value=0.0, step=10.0)

    def calculate_meta_fee(meta, flight, amount, pax):
        if meta == "None":
            return 0, 0, 0
        if flight == "Domestic":
            base_fee = 200 if pax <= 2 else 300
        else:
            base_fee = 400 if amount <= 30000 else 600
        ads_fee = 123 if meta == "Wego Ads" else 0
        return base_fee + ads_fee, base_fee, ads_fee

    if st.button("🧮 Calculate"):
        meta_fee, base_fee_calc, ads_fee = calculate_meta_fee(
            meta_partner, flight_type, purchase_amount, pax_count
        )
        handling_fees_net = round(handling_fees / 1.18, 2)
        di_rate = 0 if supplier_name == "Other" else supplier_di.get(supplier_name, 0)
        di_amount = round(purchase_amount * di_rate, 2)

        purchase_side = purchase_amount + meta_fee + pg_fees_input
        sale_side = booking_amount + di_amount + handling_fees_net
        difference = round(sale_side - purchase_side, 2)

        st.divider()
        st.subheader("📊 Calculation Summary")
        st.write(f"Difference: ₹ {difference}")
        if difference < 0:
            st.error("❌ Loss Booking")
        else:
            st.success("✅ Safe Booking")

# ---------------- ADMIN PANEL ----------------
def admin_panel_page():
    st.title("🛠️ Admin Panel")

    if st.button("⬅ Back to Calculator"):
        go("calculator")

    st.divider()

    st.subheader("➕ Add New User")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    new_role = st.selectbox("Role", ["user", "admin"])

    if st.button("Create User"):
        if not new_user or not new_pass:
            st.error("Username and password required")
        else:
            try:
                create_user(new_user, new_pass, new_role)
                st.success("User created successfully")
            except sqlite3.IntegrityError:
                st.error("Username already exists")

    st.divider()
    st.subheader("👥 Existing Users")

    users = get_all_users()
    for u, r in users:
        cols = st.columns([3, 2, 2, 2])
        cols[0].write(u)
        cols[1].write(r)

        if cols[2].button("Toggle Role", key=f"role_{u}"):
            new_r = "admin" if r == "user" else "user"
            update_role(u, new_r)
            st.rerun()

        if cols[3].button("Delete", key=f"del_{u}"):
            if u == st.session_state.username:
                st.error("You cannot delete yourself")
            else:
                delete_user(u)
                st.rerun()

    st.divider()
    st.subheader("🔑 Reset Password")

    ru = st.text_input("Username to reset")
    np = st.text_input("New Password", type="password")

    if st.button("Reset Password"):
        if get_user(ru) is None:
            st.error("User not found")
        else:
            update_password(ru, np)
            st.success("Password updated")

# ---------------- ROUTER ----------------
if not user_exists():
    first_time_admin()
    st.stop()

if st.session_state.page == "landing":
    landing_page()

elif st.session_state.page == "login":
    login_page()

elif st.session_state.page == "calculator":
    if not st.session_state.logged_in:
        go("landing")
    sidebar()
    show_calculator()

elif st.session_state.page == "admin_panel":
    if not st.session_state.logged_in or st.session_state.role != "admin":
        go("landing")
    sidebar()
    admin_panel_page()
