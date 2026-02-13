import streamlit as st
import sqlite3
import hashlib

# ===================== AUTH / DB LAYER =====================

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

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

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

# ---------------- INIT ----------------
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = "calculator"  # or "admin"

# ---------------- AUTH SCREENS ----------------
def show_create_admin():
    st.title("🔐 Create First Admin")
    st.info("First time setup: Create your admin account")

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
            st.success("Admin created! Please refresh the page.")
            st.stop()

def show_login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(username)
        if user is None:
            st.error("Invalid username or password")
        else:
            _, password_hash, role = user
            if verify_password(password, password_hash):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.session_state.page = "calculator"
                st.rerun()
            else:
                st.error("Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.page = "calculator"
    st.rerun()

# ---------------- ADMIN PANEL ----------------
def admin_panel():
    st.title("🛠️ Admin Panel - User Management")

    if st.button("⬅ Back to Calculator"):
        st.session_state.page = "calculator"
        st.rerun()

    st.divider()

    with st.expander("➕ Add New User"):
        new_user = st.text_input("New Username", key="new_user")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        new_role = st.selectbox("Role", ["admin", "user"], key="new_role")

        if st.button("Create User"):
            if not new_user or not new_pass:
                st.error("Username and password required")
            else:
                try:
                    create_user(new_user, new_pass, new_role)
                    st.success("User created successfully")
                except sqlite3.IntegrityError:
                    st.error("Username already exists")

    st.subheader("👥 Existing Users")

    users = get_all_users()
    for u, r in users:
        cols = st.columns([3, 2, 2, 2])
        cols[0].write(u)
        cols[1].write(r)

        if cols[2].button("Make Admin" if r != "admin" else "Make User", key=f"role_{u}"):
            new_r = "admin" if r != "admin" else "user"
            update_role(u, new_r)
            st.rerun()

        if cols[3].button("Delete", key=f"del_{u}"):
            if u == st.session_state.username:
                st.error("You cannot delete yourself")
            else:
                delete_user(u)
                st.rerun()

    with st.expander("🔑 Reset User Password"):
        ru = st.text_input("Username to reset")
        np = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if get_user(ru) is None:
                st.error("User not found")
            else:
                update_password(ru, np)
                st.success("Password updated")

# ===================== GATE =====================

if not user_exists():
    show_create_admin()
    st.stop()

if not st.session_state.logged_in:
    show_login()
    st.stop()

# ---------------- TOP BAR ----------------
st.markdown(
    f"""
    <div style="display:flex; justify-content: space-between; align-items:center;">
        <div>👤 Logged in as: <b>{st.session_state.username}</b> ({st.session_state.role})</div>
    </div>
    """,
    unsafe_allow_html=True
)

c_top1, c_top2 = st.columns([1,1])

if st.session_state.role == "admin":
    if c_top1.button("🛠️ Admin Panel"):
        st.session_state.page = "admin"
        st.rerun()

if c_top2.button("🚪 Logout"):
    logout()

st.divider()

# ---------------- PAGE ROUTER ----------------
if st.session_state.page == "admin" and st.session_state.role == "admin":
    admin_panel()
    st.stop()

# ===================== CALCULATOR APP =====================

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Booking Safety Calculator",
    layout="wide"
)

# -------- REMOVE EXTRA TOP SPACE & SMALLER FONTS --------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
    }
    .summary-box p {
        font-size: 12px;
        margin-bottom: 3px;
    }
    .summary-box h3 {
        font-size: 14px;
        margin-bottom: 5px;
    }
    .stSelectbox label, .stNumberInput label {
        font-size: 13px;
    }
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
    # ZERO DI suppliers
    "Consulate General of Indonesia-Mumbai": 0,
    "RIYA HAP 6A4T": 0,
    "Consulate Genenal Of Hungary - Visa": 0,
    "MUSAFIR.COM INDIA PVT LTD": 0,
    "MASTER BSP": 0,
    "Japan vfs": 0,
    "VFS Global Georgia - Visa": 0,
    "Akbar Travels HAP 3OT9": 0,
    "GRNConnect": 0,
    "CHINA VFS": 0,
    "FLYCREATIVE ONLINE PVT. LTD (LCC)": 0,
    "Bajaj Allianz General Insurance": 0,
    "South Africa VFS": 0,
    "MakeMyTrip (India) Private Limited": 0,
    "Travelport Universal Api": 0,
    "Deputy High Commission of Bangladesh, Mumbai": 0,
    "Bajaj Allianz General Insurance - Aertrip A/C": 0,
    "Germany Visa": 0,
    "Cleartrip Private Limited - AB 1": 0,
    "CDV HOLIDAYS PRIVATE LIMITED": 0,
    "Rudraa Tours And Travels Jayashree Patil": 0,
    "France Vfs": 0,
    "Vietnam Embassy New Delhi": 0,
    "Srilanka E Visa": 0,
    "Morocco Embassy New Delhi": 0,
    "Regional Passport Office-Mumbai": 0,
    "Klook Travel Tech Ltd Hong Kong HK": 0,
    "VANDANA VISA SERVICES": 0,
    "Consulate General of the Republic of Poland": 0,
    "Akbar Travel online AG43570": 0,
    "Just Click N Pay": 0,
    "IRCTC": 0,
    "Akbar Travels of India Pvt Ltd - (AG004261)": 0,
    "Embassy of Gabon": 0,
    "Go Airlines (India) Limited ( Offline )": 0,
    "UK VFS": 0,
    "GO KITE TRAVELS AND TOURS LLP": 0,
    "Travel super Mall (IXBAIU9800)": 0,
    "AirIQ Flights series Supplier": 0
}

supplier_list = sorted(supplier_di.keys())
supplier_list.insert(0, "Other")

# ---------------- INPUTS ----------------
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

# ---------------- CALCULATE BUTTON ----------------
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
    if difference < 0:
        st.error(f"❌ Loss Booking: ₹ {difference}")
    else:
        st.success(f"✅ Safe Booking: ₹ {difference}")

# ---------------- FOOTER ----------------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 10px;
        bottom: 10px;
        color: #6c757d;
        font-size: 12px;
    }
    </style>
    <div class="footer">
        Auto-updated via GitHub | Last updated on 08 Feb 2026
    </div>
    """,
    unsafe_allow_html=True
)
